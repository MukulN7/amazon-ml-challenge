import pandas as pd
excel_path = r"D:\amazon_hackathon\docs\official\Amazon ML Challenge 2026 - Query Form (Responses).xlsx"
df = pd.read_excel(excel_path)
print("Shape:", df.shape)
print("Columns:")
for col in df.columns:
    print(" -", col)

for col in df.columns:
    texts = df[col].dropna().astype(str)
    non_link_texts = [t for t in texts if not t.startswith("http") and len(t) > 20]
    if non_link_texts:
        print(f"\n==========================================")
        print(f"COLUMN: {col}")
        print(f"Sample non-link text entries ({len(non_link_texts)} found):")
        for t in non_link_texts[:10]:
            print("------------------------------------------")
            print(t)
