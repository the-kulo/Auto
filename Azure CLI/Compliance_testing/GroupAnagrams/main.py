import pandas as pd
import json

df = pd.read_csv('input-path')

config_path = 'config.json'
with open(config_path, 'r') as f:
    keywords = json.load(f)

Dictionary = {key :[] for key in keywords}

for _,row in df.iterrows():
    display_name = row['DisplayName']
    for key in keywords:
        if key in display_name:
            Dictionary[key].append(row)

import datetime

output_path = f'output-path'
with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
    df.to_excel(writer, sheet_name='All', index=False)
    for key, rows in Dictionary.items():
        if rows:
            pd.DataFrame(rows).to_excel(writer, sheet_name=key, index=False)
            print(f"successfully write {key} sheet")
        else:
            print(f"no data for {key} sheet")