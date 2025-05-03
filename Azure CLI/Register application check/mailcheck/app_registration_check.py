import os
import sys
import json
import datetime
import smtplib
import asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from azure.identity import ClientSecretCredential, AzureAuthorityHosts
from msgraph import GraphServiceClient
from dateutil.parser import parse
from tabulate import tabulate

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

def generate_report(app_info):
    """
    Generate report content
    """
    app_info.sort(key=lambda x: x["days_to_expire"] if isinstance(x["days_to_expire"], int) else float('inf'))
    
    headers = ["Display Name", "Application ID", "Creation Time", "Client Secret", "Expiration Date", "Days to Expire"]
    table_data = []
    html_rows = ""
    
    for app in app_info:
        days = app["days_to_expire"]
        days_str = f"{days} days" if isinstance(days, int) else days
        
        row_class = ""
        if isinstance(days, int):
            if days < 0:
                row_class = "expired"
            elif days <= 30:  # Highlight passwords expiring within 30 days
                row_class = "warning"
        
        # Text report data
        text_row = [
            app["display_name"],
            app["app_id"],
            app["created_time"],
            app["password"],
            app["end_date"],
            days_str
        ]
        table_data.append(text_row)
        
        # HTML report data (with class)
        html_rows += f"<tr class='{row_class}'><td>{app['display_name']}</td><td>{app['app_id']}</td><td>{app['created_time']}</td><td>{app['password']}</td><td>{app['end_date']}</td><td>{days_str}</td></tr>\n"
    
    # Manually generate HTML table to support class attributes
    html_table = f"""
    <table>
        <thead>
            <tr><th>{'</th><th>'.join(headers)}</th></tr>
        </thead>
        <tbody>
            {html_rows}
        </tbody>
    </table>
    """
    
    html_report = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            table {{ border-collapse: collapse; width: 100%; font-family: sans-serif; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            tr:nth-child(even) {{ background-color: #f9f9f9; }}
            tr.warning {{ background-color: #fffacd; }} /* Light yellow for warning */
            tr.expired {{ background-color: #ffcccc; }} /* Light red for expired */
            body {{ font-family: sans-serif; }}
        </style>
    </head>
    <body>
        <h2>Azure Application Registration Check Report</h2>
        <p>Generated at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        {html_table}
        <p>Note: Yellow background indicates expiring soon (<= 30 days), red background indicates expired client secrets.</p>
    </body>
    </html>
    """
    
    # Use tabulate to generate text report
    text_report = tabulate(table_data, headers=headers, tablefmt="grid")
    text_report = f"Azure Application Registration Check Report\nGenerated at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n{text_report}"
    
    return html_report, text_report

def send_email(html_content, text_content, config):
    """
    Send email
    """
    try:
        message = MIMEMultipart('alternative')
        message['From'] = config["email"]["sender"]
        # Ensure recipients is a list of strings
        recipients = config["email"]["recipients"]
        if isinstance(recipients, str):
            recipients = [recipients]
        message['To'] = ", ".join(recipients)
        message['Subject'] = Header(config["email"]["subject"], 'utf-8')
        
        part1 = MIMEText(text_content, 'plain', 'utf-8')
        part2 = MIMEText(html_content, 'html', 'utf-8')
        message.attach(part1)
        message.attach(part2)
        
        smtp_server = config["email"]["smtp_server"]
        smtp_port = config["email"]["smtp_port"]
        sender = config["email"]["sender"]
        password = config["email"]["password"]
        
        if not password:
            print("Warning: Email password not set, please configure in config.json file")
            return False
        
        # Use SMTP_SSL for implicit TLS/SSL connection, or starttls for explicit connection
        # Check your provider's requirements. Example using starttls:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.ehlo()  # Say hello to the server
        server.starttls()  # Start TLS encryption
        server.ehlo()  # Say hello again after TLS
        server.login(sender, password)
        server.sendmail(sender, recipients, message.as_string())
        server.quit()
        
        print(f"Email successfully sent to {', '.join(recipients)}")
        return True
    except smtplib.SMTPAuthenticationError:
        print(f"Error sending email: Authentication failed. Check sender email/password.")
        return False
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

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
    
    print(f"Found {len(app_info)} application registrations, generating report...")
    html_report, text_report = generate_report(app_info)
    
    # Check if email configuration exists before attempting to send email
    if "email" in config and config["email"].get("recipients"):
        print("Sending email...")
        if not send_email(html_report, text_report, config):
            print("\nEmail sending failed. Displaying text report:\n")
            print(text_report)
    else:
        print("Email configuration or recipients not found in config.json.")
        print("\nDisplaying text report:\n")
        print(text_report)

def main():
    """
    Main function - start async run
    """
    asyncio.run(async_main())

if __name__ == "__main__":
    main()