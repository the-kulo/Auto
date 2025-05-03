# 组账户监控统计工具

## 概述

这是一个用于统计和分析Azure AD组账户信息的工具。它提取指定组内账户信息并按类别统计,最终将结果输出到Excel表格中。

## 前提条件

- Python 3.x
- 安装依赖包:

```bash
pip install -r requirements.txt
```

- Azure PowerShell module
- 已配置Azure账号权限

## 使用方法

1. 准备组账户数据
2. 运行脚本:

```bash
python main.py
```

## 输出说明

脚本会生成一个Excel文件,包含多个工作表:

- 每个工作表对应一个账户分类
- 包含该分类下的账户统计信息
- 如果某个分类没有数据则跳过创建
