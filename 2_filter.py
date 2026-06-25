import pandas as pd
import config

def filter():
    try:
        print(f"Reading file: {config.MERGED_OUTPUT}...")
        df = pd.read_excel(config.MERGED_OUTPUT)

        # 把 pandas 讀取時自作主張轉成 1.0 / 0.0 的欄位，還原回原生的 True / False
        flag_cols = [c for c in df.columns if "Flag" in c or "Y/N" in c or "flag" in c]
        df[flag_cols] = df[flag_cols].replace({1: True, 0: False})

        existing_cols = [col for col in config.TARGET_COLUMNS if col in df.columns]
        missing_cols = [col for col in config.TARGET_COLUMNS if col not in df.columns]

        if missing_cols:
            print(f"Warning: Cannot find columns:\n{missing_cols}")

        non_ipo_filters = [
            (
                "Original IPO Flag", 
                lambda d: d["Original IPO Flag"] == True, 
                "Original IPO Flag == TRUE"
            ),
            (
                "Main Tranche within Package flag", 
                lambda d: d["Main Tranche within Package flag"] == True, 
                "Main Tranche within Package flag == TRUE"
            ),
            (
                "Blank Check (SPAC) Involvement Y/N:", 
                lambda d: d["Blank Check (SPAC) Involvement Y/N:"] != True, 
                "Exclude 空殼公司 (SPAC == TRUE)"
            ),
            (
                "Unit Issues: Unit Issue Flag", 
                lambda d: d["Unit Issues: Unit Issue Flag"] != True, 
                "Exclude 單位發行 (Unit Issue == TRUE)"
            ),
            (
                "Depositary Issue Flag", 
                lambda d: d["Depositary Issue Flag"] != True, 
                "Exclude 存託憑證 (Depositary Issue == TRUE)"
            ),
            (
                "Issuer/Borrower REIT Type", 
                lambda d: d["Issuer/Borrower REIT Type"].isna() | (d["Issuer/Borrower REIT Type"].astype(str).str.strip() == ""), 
                "Exclude 不動產投資信託 (REIT Type 有值)"
            ),
            (
                "Closed-end Fund/Trust Flag", 
                lambda d: d["Closed-end Fund/Trust Flag"] != True, 
                "Exclude 封閉型基金 (Closed-end Fund == TRUE)"
            ),
            (
                "Fund or Trust Issue Flag", 
                lambda d: d["Fund or Trust Issue Flag"] != True, 
                "Exclude 基金與信託 (Fund or Trust == TRUE)"
            ),
            (
                "Limited Partnership Flag (Y/N)", 
                lambda d: d["Limited Partnership Flag (Y/N)"] != True, 
                "Exclude 有限合夥 (Limited Partnership == TRUE)"
            ),
            (
                "Private Placement Flag", 
                lambda d: d["Private Placement Flag"] != True, 
                "Exclude 私募 (Private Placement == TRUE)"
            ),
            (
                "Spinoff (Equity Carveout) Type (Code)", 
                lambda d: d["Spinoff (Equity Carveout) Type (Code)"] != "P", 
                "Exclude 公營事業民營化 (Spinoff Type == P)"
            )
        ]

        industry_filters = [
            (
                "Issuer/Borrower Primary SIC (Code)", 
                lambda d: ~pd.to_numeric(d["Issuer/Borrower Primary SIC (Code)"], errors='coerce').between(6000, 6999), 
                "Exclude 金融機構 (SIC 6000–6999)"
            ),
            (
                "Issuer/Borrower Primary SIC (Code)", 
                lambda d: ~pd.to_numeric(d["Issuer/Borrower Primary SIC (Code)"], errors='coerce').between(4900, 4949), 
                "Exclude 公用事業 (SIC 4900–4949)"
            )
        ]

        print("\n--- Filtering Non-IPO ---")
        for column, function, description in non_ipo_filters:
            if column in df.columns:
                initial_count = len(df)
                df = df[function(df)]
                final_count = len(df)
                print(f"Condition: {description}. Sample size reduced from {initial_count} to {final_count}.")
            else:
                print(f"Warning: Cannot find column '{column}', skip filtering for: {description}.")

        df_non_ipo = df[existing_cols]
        output_non_ipo = f"Filtered_non_ipo_{config.FILTERED_OUTPUT}"
        df_non_ipo.to_excel(output_non_ipo, index=False)
        print(f"-> Saved File 1 (Exclude Non-IPO): {output_non_ipo} | Total rows: {len(df_non_ipo)}")

        print("\n--- Filtering Industries ---")
        for column, function, description in industry_filters:
            if column in df.columns:
                initial_count = len(df)
                df = df[function(df)]
                final_count = len(df)
                print(f"Condition: {description}. Sample size reduced from {initial_count} to {final_count}.")
            else:
                print(f"Warning: Cannot find column '{column}', skip filtering for: {description}.")

        df_final = df[existing_cols]
        df_final.to_excel(config.FILTERED_OUTPUT, index=False)
        print(f"-> Saved File 2 (Exclude Non-IPO + Financial/Utilities): {config.FILTERED_OUTPUT} | Total rows: {len(df_final)}")
        
        print(f"\nComplete columns filtering. Remaining number of columns: {len(existing_cols)}")

    except FileNotFoundError:
        print(f"Error: Cannot find file: {config.MERGED_OUTPUT}.")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    filter()
