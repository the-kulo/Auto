# Azure AD MFA 状态检查工具

## 简介

此脚本用于检查 Azure AD 中用户的 MFA 状态，并生成合规性报告。

## MFA验证方式

Azure AD MFA验证方式：

1. **OneWaySMS** (单向短信验证)：
   - 系统向用户注册的手机号发送包含验证码的短信
   - 用户需要在登录界面输入收到的验证码

2. **TwoWayVoiceMobile** (双向语音验证)：
   - 系统拨打用户注册的电话号码
   - 用户需要按电话键盘上的"#"键确认身份

3. **PhoneAppOTP** (应用验证码)：
   - 通过Microsoft Authenticator应用生成6位数验证码
   - 用户需要手动输入验证码完成验证
   - 验证码每30秒自动刷新

4. **PhoneAppNotification** (应用推送通知)：
   - 登录时向Microsoft Authenticator应用发送推送通知
   - 用户只需点击"批准"即可完成验证

## 前置要求

### 安装必要模块

以管理员身份运行 PowerShell 并执行：

```powershell
Install-Module MSOnline -Force
```

### 权限要求

- 需要 Azure AD 管理员权限

## 使用方法

1. 连接到 Azure AD：

    ```powershell
    Connect-MsolService -AzureEnvironment AzureChinaCloud
    ```

2. 运行脚本：

    ```powershell
    .\MFA.ps1
    ```

## 使用限制

- 脚本无法检查从未登录过 Azure AD 的用户的 MFA 状态
- 对于无法检查的用户需要通过 Azure 门户手动确认
- 如果只能检测到登录账号的 MFA 绑定状态，请确认使用的账号是否具有 Conditional Access Administrator 权限
