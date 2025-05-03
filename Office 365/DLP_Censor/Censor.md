# Censor

针对DLP导出的日志做分析

## 逻辑

- 读取csv文件
- 检测AuditData这一列 ``` "Workload": ``` 对应的值，如果检测到```OneDrive```字段则放在Onedrive的文档，如果检测到```Exchange```字段则放在EXO的文档
- 根据模板生成html文件

## csv to html 对应字段

- csv:AuditData列的"CreationTime"-->html:时间
- csv:AuditData列的"RuleName"-->html:规则名称
- csv:AuditData列的"SharePointMetaData"：{}中的“FileName”-->html:文件名
- csv:AuditData列的"ExchangeMetaData"：{}中的“Subject”-->html:主题
- csv:AuditData列的"ExchangeMetaData"：{}中的“From”-->html:用户ID

## 模板

### EXO模板

标题： O365 EXO XX月 DLP Review

内容：

表1：触发最多的十个规则
| 排名 | 规则名称 | 触发次数 |
表2：触发规则最多的十个发件人
| 排名 | UserID | 触发次数 |
表3：DLP日志
| 时间 | 规则名称 | UserID | 主题 |

### OneDrive模板

标题： O365 OneDrive XX月 DLP Review

内容：

表1：触发最多的十个规则
| 排名 | 规则名称 | 触发次数 |
表2：触发规则最多的十个发件人
| 排名 | UserID | 触发次数 |
表3：DLP日志
| 时间 | 规则名称 | UserID | 文件名 |
