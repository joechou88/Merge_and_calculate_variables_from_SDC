import pandas as pd
import config

COMPANY = "Issuer/Borrower Name Full"
COUNTRY  = "Country"

def check_uniqueness(filepath):
    print(f"Loading: {filepath}\n")
    df = pd.read_excel(filepath)

    total_rows = len(df)
    unique_count = df[COMPANY].nunique()
    print(f"Total records   : {total_rows}")
    print(f"Unique companies: {unique_count}\n")

    if total_rows == unique_count:
        print("✅  All companies are unique — each company has exactly one record.")
        return

    duplicates_df = df[df.duplicated(subset=[COMPANY], keep=False)].copy()

    duplicates = (
        duplicates_df.groupby([COMPANY, COUNTRY])
        .size()
        .reset_index(name="Record Count")
        .sort_values([COUNTRY, "Record Count"], ascending=[True, False])
        .reset_index(drop=True)
    )
    duplicates.index += 1

    print(f"⚠️  Found {len(duplicates)} companies with duplicate records "
          f"({duplicates['Record Count'].sum()} records total):\n")
    
    try:
        with pd.ExcelWriter(config.DUPLICATED_OUTPUT, engine='openpyxl') as writer:
            duplicates.to_excel(writer, sheet_name='Duplicate Summary', index=True, index_label="No.")
            duplicates_df.to_excel(writer, sheet_name='Raw Duplicate Rows', index=False)     
        print(f"💾 成功將重複清單匯出至: {config.DUPLICATED_OUTPUT}")
    except Exception as e:
        print(f"❌ 匯出 Excel 失敗: {e}")

    country_summary = (
        duplicates.groupby(COUNTRY)
        .agg(
            Duplicate_Companies=(COMPANY, "count"),
            Total_Records=("Record Count", "sum")
        )
        .sort_values("Total_Records", ascending=False)
    )

    print("=== Duplicate Records by Country ===")
    print(country_summary)
    print("\n=== Full Duplicate Company List ===")
    
    with pd.option_context("display.max_rows", None, "display.max_colwidth", 60, "display.width", 120):
        print(duplicates)

if __name__ == "__main__":
    check_uniqueness(config.FILTERED_OUTPUT)
