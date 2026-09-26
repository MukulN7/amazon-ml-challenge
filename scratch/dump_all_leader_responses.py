import pandas as pd
excel_path = r"D:\amazon_hackathon\docs\official\Amazon ML Challenge 2026 - Query Form (Responses).xlsx"
df = pd.read_excel(excel_path)
col_name = "Response from Amazon Leaders"
responses = df[col_name].dropna().unique()

print(f"Total Unique Official Responses: {len(responses)}\n")
for i, resp in enumerate(responses, 1):
    print(f"==================================================")
    print(f"RESPONSE #{i}")
    print(f"==================================================")
    print(str(resp).strip())
    print()
