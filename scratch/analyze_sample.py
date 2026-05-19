import pandas as pd
import os

dir_path = "/Users/lisob/Desktop/project2/AutoPO_Project/sample/sam2"
files = [f for f in os.listdir(dir_path) if f.endswith('.xlsx') or f.endswith('.xls')]

for f in files:
    f_path = os.path.join(dir_path, f)
    print("="*50)
    print(f"File: {f}")
    try:
        df = pd.read_excel(f_path, nrows=30, header=None)
        print(df.dropna(how='all').to_string(max_rows=15))
    except Exception as e:
        print(f"Error: {e}")
