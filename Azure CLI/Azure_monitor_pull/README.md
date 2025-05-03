# Azure_monitor_pull

## 概述

基于小规模虚拟机的监控拉取

## 前提条件

1. 安装Azure CLI
2. 确保已登录 Azure 账户，可以使用 `Login-AzAccount -Environment Azurecloud` 命令登录

### 脚本说明

该脚本用于拉取较小资源组的 CPU 和内存使用率的最大值和平均值

## 参数

- `$startTime`：监控开始时间，默认为上周一
- `$endTime`：监控结束时间，默认为上周日
- `$resources`：资源组列表，需要替换为实际的订阅 ID
- `$metrics`：监控指标列表，默认为 `cpu_percent` 和 `memory_percent`

## 输出

脚本将输出每个资源的指标的最大值和平均值

## 使用方法

1. 打开 PowerShell
2. 运行脚本 `azure_monitor_pull.ps1`
3. 查看输出结果
