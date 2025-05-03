import os
import sys
import json
import datetime
import asyncio
import hashlib
import hmac
import base64
import requests
from azure.identity import ClientSecretCredential, AzureAuthorityHosts
from msgraph import GraphServiceClient
from dateutil.parser import parse

def get_azure_credentials(config):
    """
    Get Azure credentials from configuration file
    """
    tenant_id = config["azure"]["tenant_id"]
    client_id = config["azure"]["client_id"]
    client_secret = config["azure"]["client_secret"]
    
    if not all([tenant_id, client_id, client_secret]):
        print("Error: Missing Azure credential configuration, please check config.json file")
        sys.exit(1)
        
    # Use ClientSecretCredential and specify Azure China cloud authority
    try:
        credential = ClientSecretCredential(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret,
            authority=AzureAuthorityHosts.AZURE_CHINA  # Specify China cloud authority
        )
        return credential
    except Exception as e:
        print(f"Error creating Azure credentials: {str(e)}")
        sys.exit(1)

async def get_app_registrations(credentials, config):
    """
    Get all application registration information
    """
    try:
        # Define Graph API scopes
        scopes = ['https://microsoftgraph.chinacloudapi.cn/.default']  # Use China cloud Graph scope
        
        # Initialize GraphServiceClient for Azure China
        graph_client = GraphServiceClient(
            credentials=credentials,
            scopes=scopes
        )
        
        graph_client.request_adapter.base_url = "https://microsoftgraph.chinacloudapi.cn/v1.0"

        # Get applications - use await keyword to wait for async operation
        result = await graph_client.applications.get()
        
        app_info = []
        if hasattr(result, 'value'):
            for app in result.value:
                passwords = app.password_credentials if hasattr(app, 'password_credentials') else []
                
                created_time_str = "Unknown"
                if hasattr(app, 'created_date_time') and app.created_date_time:
                    # Ensure created_date_time is timezone aware
                    created_dt = app.created_date_time
                    if hasattr(created_dt, 'replace'):
                        created_dt_aware = created_dt.replace(tzinfo=datetime.timezone.utc).astimezone(tz=None)
                        created_time_str = created_dt_aware.strftime("%Y-%m-%d %H:%M:%S")
                
                if not passwords:
                    app_info.append({
                        "display_name": app.display_name if hasattr(app, 'display_name') else 'N/A',
                        "app_id": app.app_id if hasattr(app, 'app_id') else 'N/A',
                        "created_time": created_time_str,
                        "password": "None",
                        "end_date": "None",
                        "days_to_expire": "N/A"
                    })
                else:
                    for pwd in passwords:
                        end_date_str = "Unknown"
                        days_to_expire = "Unknown"
                        
                        if hasattr(pwd, 'end_date_time') and pwd.end_date_time:
                            end_dt = pwd.end_date_time
                            if hasattr(end_dt, 'replace'):
                                end_dt_aware = end_dt.replace(tzinfo=datetime.timezone.utc)
                                now_aware = datetime.datetime.now(datetime.timezone.utc)
                                days_to_expire = (end_dt_aware - now_aware).days
                                end_date_str = end_dt_aware.astimezone(tz=None).strftime("%Y-%m-%d %H:%M:%S")
                        
                        app_info.append({
                            "display_name": app.display_name if hasattr(app, 'display_name') else 'N/A',
                            "app_id": app.app_id if hasattr(app, 'app_id') else 'N/A',
                            "created_time": created_time_str,
                            "password": "Password" if hasattr(pwd, 'key_id') and pwd.key_id else "None",
                            "end_date": end_date_str,
                            "days_to_expire": days_to_expire
                        })
        
        return app_info
    except Exception as e:
        print(f"Error getting application registration information: {str(e)}")
        import traceback
        traceback.print_exc()
        return []

def save_expiring_apps_to_json(app_info, output_dir=None):
    """
    Save applications with expiring credentials (<30 days) to JSON file
    """
    # Filter applications with credentials expiring within 30 days
    expiring_apps = []
    for app in app_info:
        days = app["days_to_expire"]
        if isinstance(days, int) and days <= 30:
            expiring_apps.append(app)
    
    if not expiring_apps:
        print("No applications with credentials expiring within 30 days found")
        return False, []
    
    # Determine output directory
    if output_dir is None:
        output_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Create filename with timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"expiring_apps_{timestamp}.json")
    
    # Save data to JSON file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            # Convert datetime objects to strings for JSON serialization
            json_data = []
            for app in expiring_apps:
                app_copy = app.copy()
                json_data.append(app_copy)
            
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        
        print(f"Saved {len(expiring_apps)} applications with expiring credentials to: {output_file}")
        return True, expiring_apps
    except Exception as e:
        print(f"Error saving JSON file: {str(e)}")
        return False, []

def upload_to_log_analytics(expiring_apps, config):
    """
    Upload expiring applications data to Azure Log Analytics workspace
    """
    # Check if Log Analytics configuration exists
    if "log_analytics" not in config or not config["log_analytics"]:
        print("Log Analytics configuration not found in config.json, skipping upload")
        return False
    
    workspace_id = config["log_analytics"].get("workspace_id")
    shared_key = config["log_analytics"].get("shared_key")
    log_type = config["log_analytics"].get("log_type", "AppRegistrationExpiry")
    
    if not workspace_id or not shared_key:
        print("Error: Missing Log Analytics workspace ID or shared key in configuration")
        return False
    
    # Format the data for Log Analytics
    body = json.dumps(expiring_apps)
    
    # Build the API signature
    method = 'POST'
    content_type = 'application/json'
    resource = '/api/logs'
    rfc1123date = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
    content_length = len(body)
    signature = build_signature(
        workspace_id, shared_key, rfc1123date, content_length, method, content_type, resource
    )
    
    uri = f'https://{workspace_id}.ods.opinsights.azure.cn{resource}?api-version=2016-04-01'
    
    headers = {
        'content-type': content_type,
        'Authorization': signature,
        'Log-Type': log_type,
        'x-ms-date': rfc1123date
    }
    
    try:
        response = requests.post(uri, data=body, headers=headers)
        if response.status_code >= 200 and response.status_code <= 299:
            print(f"Successfully uploaded {len(expiring_apps)} records to Log Analytics workspace")
            return True
        else:
            print(f"Error uploading to Log Analytics: {response.status_code} {response.reason}")
            return False
    except Exception as e:
        print(f"Exception during upload to Log Analytics: {str(e)}")
        return False

def build_signature(workspace_id, shared_key, date, content_length, method, content_type, resource):
    """
    Build the API signature for Log Analytics
    """
    x_headers = f"x-ms-date:{date}"
    string_to_hash = f"{method}\n{content_length}\n{content_type}\n{x_headers}\n{resource}"
    bytes_to_hash = string_to_hash.encode('utf-8')
    decoded_key = base64.b64decode(shared_key)
    encoded_hash = base64.b64encode(hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest())
    authorization = f"SharedKey {workspace_id}:{encoded_hash.decode('utf-8')}"
    return authorization

async def async_main():
    """
    Async main function
    """
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"Error: Configuration file not found at {config_path}")
        return
    except json.JSONDecodeError as e:
        print(f"Error decoding configuration file {config_path}: {str(e)}")
        return
    except Exception as e:
        print(f"Error loading configuration file: {str(e)}")
        return
    
    credentials = get_azure_credentials(config)
    if not credentials:
        return  # Exit if credentials fail
    
    print("Getting Azure application registration information...")
    app_info = await get_app_registrations(credentials, config)  # Use await to wait for async function
    
    if not app_info:
        print("No application registration information found or error occurred during retrieval")
        return
    
    print(f"Found {len(app_info)} application registrations, checking for expiring client secrets...")
    
    # Save expiring applications to JSON file and get the list of expiring apps
    saved, expiring_apps = save_expiring_apps_to_json(app_info)
    
    # Upload to Log Analytics if there are expiring apps
    if saved and expiring_apps:
        print("Uploading expiring applications data to Azure Log Analytics...")
        upload_to_log_analytics(expiring_apps, config)
    
    print("Processing complete")

def main():
    """
    Main function - start async run
    """
    asyncio.run(async_main())

if __name__ == "__main__":
    main()