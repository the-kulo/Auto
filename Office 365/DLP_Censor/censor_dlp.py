import json
import pandas as pd
import os
import re
from collections import defaultdict
from jinja2 import Template
from datetime import datetime

def parse_dlp_logs(log_file):
    """解析DLP日志文件，区分OneDrive和EXO类型的日志"""
    # 读取CSV文件
    try:
        df = pd.read_csv(log_file, encoding='utf-8')
    except UnicodeDecodeError:
        # 如果UTF-8解码失败，尝试其他编码
        df = pd.read_csv(log_file, encoding='gbk')
    
    # 初始化数据结构
    onedrive_logs = []
    exo_logs = []
    
    # 规则和用户计数器
    onedrive_rule_counts = defaultdict(int)
    onedrive_user_counts = defaultdict(int)
    exo_rule_counts = defaultdict(int)
    exo_user_counts = defaultdict(int)
    
    # 处理每一行数据
    for _, row in df.iterrows():
        # 解析AuditData列中的JSON数据
        if isinstance(row['AuditData'], str):
            try:
                audit_data = json.loads(row['AuditData'])
            except json.JSONDecodeError:
                print(f"警告: 无法解析AuditData JSON: {row['AuditData'][:100]}...")
                continue
        else:
            audit_data = row['AuditData']
        
        # 获取用户ID
        user_id = row.get('UserId', '')
        
        # 获取创建时间
        creation_time = audit_data.get('CreationTime', '')
        
        # 获取规则名称
        rule_name = ''
        if 'RuleName' in audit_data:
            rule_name = audit_data['RuleName']
        elif 'PolicyDetails' in audit_data and audit_data['PolicyDetails']:
            for policy in audit_data['PolicyDetails']:
                if 'Rules' in policy and policy['Rules']:
                    rule_name = policy['Rules'][0].get('RuleName', '')
                    break
        
        # 检查Workload字段，区分OneDrive和Exchange(EXO)
        workload = ''
        if 'Workload' in audit_data:
            workload = audit_data['Workload']
        
        # 根据Workload分类
        if workload == 'OneDrive':
            # OneDrive类型的日志
            file_name = ''
            if 'SharePointMetaData' in audit_data and audit_data['SharePointMetaData']:
                file_name = audit_data['SharePointMetaData'].get('FileName', '')
            
            # 添加到OneDrive日志列表
            onedrive_logs.append({
                '时间': creation_time,
                '规则名称': rule_name,
                'UserID': user_id,
                '文件名': file_name
            })
            
            # 更新计数器
            onedrive_rule_counts[rule_name] += 1
            onedrive_user_counts[user_id] += 1
            
        elif workload == 'Exchange':
            # EXO类型的日志
            subject = ''
            exchange_user_id = user_id
            if 'ExchangeMetaData' in audit_data and audit_data['ExchangeMetaData']:
                subject = audit_data['ExchangeMetaData'].get('Subject', '')
                # 从ExchangeMetaData的From字段获取用户ID
                if 'From' in audit_data['ExchangeMetaData']:
                    exchange_user_id = audit_data['ExchangeMetaData'].get('From', user_id)
            
            # 添加到EXO日志列表
            exo_logs.append({
                '时间': creation_time,
                '规则名称': rule_name,
                'UserID': exchange_user_id,
                '主题': subject
            })
            
            # 更新计数器
            exo_rule_counts[rule_name] += 1
            exo_user_counts[exchange_user_id] += 1
    
    # 返回处理结果
    return {
        'onedrive': {
            'logs': onedrive_logs,
            'rule_counts': onedrive_rule_counts,
            'user_counts': onedrive_user_counts
        },
        'exo': {
            'logs': exo_logs,
            'rule_counts': exo_rule_counts,
            'user_counts': exo_user_counts
        }
    }

def generate_top_items(counts_dict, limit=10):
    """生成排名前N的项目列表"""
    # 按计数降序排序
    sorted_items = sorted(counts_dict.items(), key=lambda x: x[1], reverse=True)
    
    # 返回前N个项目，每个项目包含排名、名称和计数
    return [{'排名': i+1, '名称': item[0], '计数': item[1]} 
            for i, item in enumerate(sorted_items[:limit])]

def generate_html_report(data, report_type, month):
    """根据数据和报告类型生成HTML报告"""
    # 确定报告标题和模板
    if report_type == 'onedrive':
        title = f"O365 OneDrive {month}月 DLP Review"
        template_file = "onedrive_template.html"
    else:  # exo
        title = f"O365 EXO {month}月 DLP Review"
        template_file = "exo_template.html"
    
    # 生成前10名规则和用户
    top_rules = generate_top_items(data[report_type]['rule_counts'])
    top_users = generate_top_items(data[report_type]['user_counts'])
    
    # 获取日志详情
    logs = data[report_type]['logs']
    
    # 创建HTML模板
    template_content = create_html_template(report_type, title)
    template = Template(template_content)
    
    # 渲染模板
    html = template.render(
        title=title,
        generated_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        top_rules=top_rules,
        top_users=top_users,
        logs=logs
    )
    
    # 返回生成的HTML内容
    return html

def create_html_template(report_type, title):
    """创建HTML模板"""
    # 基础模板
    template = '''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{{ title }}</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }
            h1 {
                color: #2c3e50;
                text-align: center;
                margin-bottom: 10px;
            }
            h2 {
                color: #e74c3c;
                margin-top: 30px;
                border-bottom: 2px solid #e74c3c;
                padding-bottom: 5px;
            }
            table {
                border-collapse: collapse;
                width: 100%;
                margin-bottom: 30px;
                box-shadow: 0 2px 3px rgba(0, 0, 0, 0.1);
            }
            th, td {
                border: 1px solid #ddd;
                padding: 10px;
                text-align: left;
                word-wrap: break-word;
            }
            th {
                background: linear-gradient(to bottom, #1a9bf1, #2980b9);
                color: white;
                font-weight: bold;
            }
            tr:nth-child(even) {
                background-color: #f2f7ff;
            }
            tr:hover {
                background-color: #e8f4fc;
            }
            .timestamp {
                font-size: 0.8em;
                color: #7f8c8d;
                text-align: right;
                margin-bottom: 20px;
            }
            .top-tables-container {
                display: flex;
                justify-content: space-between;
                margin-bottom: 30px;
            }
            .top-table {
                width: 48%;
            }
        </style>
    </head>
    <body>
        <h1>{{ title }}</h1>
        <div class="timestamp">Create time: {{ generated_time }}</div>
        
        <div class="top-tables-container">
            <div class="top-table">
                <h2>Top 10 Rule</h2>
                <table>
                    <tr>
                        <th>Rank</th>
                        <th>Rule</th>
                        <th>Count</th>
                    </tr>
                    {% for rule in top_rules %}
                    <tr>
                        <td>{{ rule.排名 }}</td>
                        <td>{{ rule.名称 }}</td>
                        <td>{{ rule.计数 }}</td>
                    </tr>
                    {% endfor %}
                </table>
            </div>
            
            <div class="top-table">
                <h2>Top 10 User</h2>
                <table>
                    <tr>
                        <th>Rank</th>
                        <th>User</th>
                        <th>Count</th>
                    </tr>
                    {% for user in top_users %}
                    <tr>
                        <td>{{ user.排名 }}</td>
                        <td>{{ user.名称 }}</td>
                        <td>{{ user.计数 }}</td>
                    </tr>
                    {% endfor %}
                </table>
            </div>
        </div>
        
        <h2>All</h2>
        <table>
            <tr>
                <th>Time</th>
                <th>Rule</th>
                <th>User</th>
    '''
    
    # 根据报告类型添加特定列
    if report_type == 'onedrive':
        template += '''
                <th>File Name</th>
            </tr>
            {% for log in logs %}
            <tr>
                <td>{{ log.时间 }}</td>
                <td>{{ log.规则名称 }}</td>
                <td>{{ log.UserID }}</td>
                <td>{{ log.文件名 }}</td>
            </tr>
            {% endfor %}
        '''
    else:  # exo
        template += '''
                <th>Mail</th>
            </tr>
            {% for log in logs %}
            <tr>
                <td>{{ log.时间 }}</td>
                <td>{{ log.规则名称 }}</td>
                <td>{{ log.UserID }}</td>
                <td>{{ log.主题 }}</td>
            </tr>
            {% endfor %}
        '''
    
    # 完成模板
    template += '''
        </table>
    </body>
    </html>
    '''
    
    return template

def save_html_report(html_content, output_file):
    """保存HTML报告到文件"""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"The report has been saved to: {output_file}")

def main():
    # 获取当前月份
    current_month = datetime.now().strftime('%m')
    
    # 输入文件路径
    log_file = r""
    
    # 解析日志
    print("DLP logs are being parsed...")
    data = parse_dlp_logs(log_file)
    
    # 检查是否有OneDrive和EXO日志
    has_onedrive = len(data['onedrive']['logs']) > 0
    has_exo = len(data['exo']['logs']) > 0
    
    # 输出目录
    output_dir = r"outputpath"
    
    # 生成并保存报告
    if has_onedrive:
        print("OneDrive DLP reports are being generated...")
        onedrive_html = generate_html_report(data, 'onedrive', current_month)
        onedrive_output = os.path.join(output_dir, f"O365_OneDrive_{current_month}月_DLP_Review.html")
        save_html_report(onedrive_html, onedrive_output)
    
    if has_exo:
        print("EXO DLP report is being generated...")
        exo_html = generate_html_report(data, 'exo', current_month)
        exo_output = os.path.join(output_dir, f"O365_EXO_{current_month}月_DLP_Review.html")
        save_html_report(exo_html, exo_output)
    
    if not has_onedrive and not has_exo:
        print("WARNING: No OneDrive or EXO-related DLP logs found")
    
    print("Done!")

if __name__ == "__main__":
    main()