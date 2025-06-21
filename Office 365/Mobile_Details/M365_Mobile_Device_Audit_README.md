# M365 Mobile Device Audit

## 使用示例  

1. 基本使用（显示所有用户设备）:
   .\Quick_Mobile_Device_Report.ps1

2. 查看特定用户设备:
   .\Quick_Mobile_Device_Report.ps1 -UserPrincipalName "<user@company.com>"

3. 导出为CSV:
   .\Quick_Mobile_Device_Report.ps1 -ExportToCsv

4. 查看特定用户并导出:
   .\Quick_Mobile_Device_Report.ps1 -UserPrincipalName "<user@company.com>" -ExportToCsv

## 前置条件

- 已安装 ExchangeOnlineManagement 模块
- 已连接到 Exchange Online (Connect-ExchangeOnline -ExchangeEnvironmentName O365China)
- 具有适当的管理员权限
