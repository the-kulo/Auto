import pandas as pd

# 数据源
input_file_path = r'D:\OneDrive\桌面\ferrero\ferrero.csv'

# 保留列
selected_columns = ['subscriptionName', 'recommendationDisplayName', 'resourceName', '说明', '严重性']

# 读取
df = pd.read_csv(input_file_path, usecols=selected_columns)

# 预设值
first_column = 'subscriptionName'
fifth_column = '严重性'

# 透视表
summary = df.groupby([first_column, fifth_column]).size().unstack(fill_value=0)

# 总和
summary['Total'] = summary.sum(axis=1)

# 输出数据
output_file_path = r'D:\OneDrive\桌面\ferrero\output.xlsx'
with pd.ExcelWriter(output_file_path, engine='xlsxwriter') as writer:

    # 筛选的数据保存到sheet1
    df.to_excel(writer, sheet_name='sheet1', index=False)

    # 筛选的数据保存到sheet2
    summary.to_excel(writer, sheet_name='Sheet2')

    workbook = writer.book
    worksheet1 = writer.sheets['sheet1']
    worksheet2 = writer.sheets['Sheet2']

    # 美化
    column_width = 20
    for worksheet in [worksheet1, worksheet2]:
        worksheet.set_column('A:Z', column_width)