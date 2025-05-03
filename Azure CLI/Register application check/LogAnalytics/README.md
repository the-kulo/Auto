# Azure 应用程序注册过期检查工具

此脚本用于检查 Azure 中即将过期的应用程序注册凭据，并将结果保存到本地 JSON 文件以及上传到 Azure Log Analytics 工作区。

## 功能

- 连接到 Azure China 云获取所有应用程序注册信息
- 识别 30 天内即将过期的客户端密钥
- 将过期应用信息保存到本地 JSON 文件
- 将过期应用信息上传到 Azure Log Analytics 工作区

## 配置

在使用脚本前，需要正确配置 `config.json` 文件：

```json
{
    "azure": {
        "tenant_id": "YOUR_TENANT_ID",
        "client_id": "YOUR_CLIENT_ID",
        "client_secret": "YOUR_CLIENT_SECRET"
    },
    "warning_days": 30,
    "log_analytics": {
        "workspace_id": "YOUR_WORKSPACE_ID",
        "shared_key": "YOUR_SHARED_KEY",
        "log_type": "AppRegistrationExpiry"
    }
}
```

### 配置项说明

- **azure**: Azure 服务主体凭据
  - **tenant_id**: Azure 租户 ID
  - **client_id**: 应用程序（客户端）ID
  - **client_secret**: 客户端密钥
- **warning_days**: 警告天数阈值（默认为 30 天）
- **log_analytics**: Log Analytics 工作区配置
  - **workspace_id**: Log Analytics 工作区 ID
  - **shared_key**: Log Analytics 工作区共享密钥
  - **log_type**: 自定义日志类型名称（默认为 AppRegistrationExpiry）

## 使用方法

1. 安装所需依赖：

   ```bash

    pip install azure-identity msgraph-sdk python-dateutil requests

    ```

2. 配置 `config.json` 文件，填入正确的凭据信息
3. 运行脚本：

```bash
python app_registration_check.py
```

## Log Analytics 查询

上传到 Log Analytics 后，可以使用以下 KQL 查询查看数据：

```kusto
AppRegistrationExpiry_CL
| where TimeGenerated > ago(1d)
| where days_to_expire_d <= 30
| project display_name_s, app_id_s, days_to_expire_d, end_date_t
| sort by days_to_expire_d asc
```

## 注意事项

- 确保服务主体具有足够的权限读取应用程序注册信息
- 确保 Log Analytics 工作区共享密钥保密且安全存储
- 脚本默认使用 Azure China 云环境，如需使用全球 Azure，请修改相应的端点
