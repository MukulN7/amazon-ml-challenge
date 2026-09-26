import pandas as pd
excel_path = r"D:\amazon_hackathon\docs\official\Amazon ML Challenge 2026 - Query Form (Responses).xlsx"
df = pd.read_excel(excel_path)
print("Columns:", list(df.columns))
print("Shape:", df.shape)

# Let's inspect unique questions / responses
for col in df.columns:
    print(f"\n--- Column: {col} ---")
    val_counts = df[col].dropna().value_counts().head(20)
    print(val_counts)
