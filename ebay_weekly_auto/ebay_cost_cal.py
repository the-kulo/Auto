import pandas as pd
import matplotlib.pyplot as plt
import requests
from openpyxl import Workbook

# 台币对美元
url = 'https://v6.exchangerate-api.com/v6/87ac86d5b5c524cf3beefc7e/latest/USD'

# get
response = requests.get(url)

# t
if response.status_code == 200:
    data0 = response.json()
    # 汇率
    usd_rate = round(data0['conversion_rates']['TWD'], 2)

    print('美元兑台币：' + str(usd_rate))

    # 本地环境
    file_path = r'D:\OneDrive\桌面\ebay\ebay202407008-202407014.xlsx'

    # 读取
    data1 = pd.read_excel(file_path, sheet_name='Sheet1')

    # 总金额求和 (188285.6898)
    sum_total = round(data1['BillingPreTaxTotal'].sum(axis=0) / usd_rate + 5040, 1)
    print('总金额为：' + str(sum_total))

    # 筛选vm并求和
    filtered_df = data1[data1['MeterCategory'] == 'Virtual Machines']
    sum_vm = round(filtered_df['BillingPreTaxTotal'].sum(axis=0) / usd_rate + 4032, 1)
    print('VM总金额为：' + str(sum_vm))

    # 筛选database并求和
    filtered_df = data1[data1['MeterCategory'] == 'Azure Database for MySQL']
    sum_database = round(filtered_df['BillingPreTaxTotal'].sum(axis=0) / usd_rate, 1)
    print('database总金额为：' + str(sum_database))

    # 筛选network并求和
    filtered_df = data1[data1['MeterCategory'] == 'Virtual Network']
    sum_network = round(filtered_df['BillingPreTaxTotal'].sum(axis=0) / usd_rate, 1)
    print('net总金额为：' + str(sum_network))

    # 筛选redis并求和
    filtered_df = data1[data1['MeterCategory'] == 'Redis Cache']
    sum_redis = round(filtered_df['BillingPreTaxTotal'].sum(axis=0) / usd_rate, 1)
    print('redis总金额为：' + str(sum_redis))

    # 快照及其他
    sum_other = sum_total - sum_vm - sum_database - sum_network - sum_redis
    print('其余总金额为：' + str(sum_other))

# f
else:
    print("请求失败，状态码：" + str(response.status_code))
