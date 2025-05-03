# Azure 应用程序注册过期检查工具

此脚本用于检查 Azure 中即将过期的应用程序注册凭据，并将结果通过阿里云邮件转发

## 功能

- 连接到 Azure China 云获取所有应用程序注册信息
- 识别 30 天内即将过期的客户端密钥
- 将过期应用信息保存到本地 JSON 文件
- 将过期应用信息通过阿里云邮件转发

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
    "email": {
        "smtp_server": "SMTP address",
        "smtp_port": "SMTP port",
        "sender": "Sender email address",
        "password": "Sender email password",
        "recipients": ["Recipient email address"],
        "subject": "subject"
    }
}
```

### 配置项说明

- **azure**: Azure 服务主体凭据
  - **tenant_id**: Azure 租户 ID
  - **client_id**: 应用程序（客户端）ID
  - **client_secret**: 客户端密钥
- **warning_days**: 警告天数阈值（默认为 30 天）
- **email**: aliyun 邮件配置
  - **smtp_server**: "SMTP服务器地址",
  - **smtp_port**: SMTP端口,
  - **sender**: "发件人邮箱",
  - **password**: "邮箱密码",
  - **recipients**: ["收件人邮箱列表"],
  - **subject**: "邮件主题"

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
