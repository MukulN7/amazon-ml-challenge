import pandas as pd
excel_path = r"D:\amazon_hackathon\docs\official\Amazon ML Challenge 2026 - Query Form (Responses).xlsx"
df = pd.read_excel(excel_path)
print("Columns:", list(df.columns))

# Find columns containing queries/questions and official answers
for i, col in enumerate(df.columns):
    print(f"Col {i}: {col}")

# Let's inspect the unique official responses
if len(df.columns) >= 6:
    resp_col = df.columns[5] # Column index for official response if present
    print(f"\nUnique values in response column '{resp_col}':")
    for idx, val in enumerate(df[resp_col].dropna().unique()):
        print(f"\n--- RESPONSE #{idx+1} ---")
        print(val)
