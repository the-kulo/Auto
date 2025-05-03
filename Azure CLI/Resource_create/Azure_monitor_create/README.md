# Azure_monitor_create

## 概述

基于 ARM 模板实现自动化创建 Azure 监控告警规则，支持多种资源指标监控。

## 功能特点

- 支持 CPU 使用率监控
- 支持内存使用率监控
- 支持磁盘空间监控
- 支持 IOPS 性能监控
- 可自定义告警阈值
- 可配置告警严重程度
- 支持自定义操作组（邮件通知等）

## 前提条件

- 安装 Azure CLI
- 安装 Azure bicep
- 已配置 Azure 账号
- PowerShell 5.1 或更高版本

## 目录结构

``` text
Azure_monitor_create/
├── scripts/
│   └── azure_monitor_create_bicep.ps1    # 部署脚本
├── templates/
│   └── metric-alert.bicep          # ARM 模板文件
└── README.md
```

## 使用方法

### 1. 配置参数

在 `azure_monitor_create_bicep.ps1` 中设置以下参数：

```powershell
$RESOURCE_GROUP = "资源组名称"
$TARGET_RESOURCE_ID = "目标资源ID"
$ACTION_GROUP_ID = "操作组ID"
```

### 2. 执行部署

```powershell
cd scripts
.\azure_monitor_create_bicep.ps1
```

## 监控指标说明

### CPU 告警

- 指标：Percentage CPU
- 默认阈值：90%
- 评估频率：5分钟
- 时间窗口：15分钟

### 内存告警

- 指标：Available Memory Bytes
- 默认阈值：90%
- 评估频率：5分钟
- 时间窗口：15分钟

### 磁盘告警

- 指标：OS Disk Space Used Percentage
- 默认阈值：90%
- 评估频率：5分钟
- 时间窗口：15分钟

### IOPS 告警

- 指标：OS Disk IOPS Consumed Percentage
- 默认阈值：95%
- 评估频率：5分钟
- 时间窗口：15分钟

## 告警严重程度说明

- 0 = 严重
- 1 = 错误
- 2 = 警告
- 3 = 信息
- 4 = 详细

## 注意事项

1. 确保有足够的权限创建告警规则
2. 确保操作组已正确配置
3. 资源 ID 格式必须正确
4. 建议在生产环境部署前先在测试环境验证

## 常见问题

1. 部署失败检查清单：
   - 确认资源组存在
   - 确认资源 ID 正确
   - 确认操作组 ID 正确
   - 检查 Azure CLI 登录状态

2. 告警未触发检查清单：
   - 确认阈值设置合理
   - 确认指标数据正常采集
   - 检查操作组配置
