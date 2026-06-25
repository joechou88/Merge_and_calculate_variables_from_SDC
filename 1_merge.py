import pandas as pd
import glob
import os
import config

def merge_xlsx():
    input_folder = config.SDC_FOLDER
    output_name = config.MERGED_OUTPUT
    input_file_path = os.path.join(input_folder, "*.xlsx")
    file_list = [f for f in sorted(glob.glob(input_file_path)) if os.path.basename(f) != output_name]
    if not file_list:
        print(f"在 {input_folder} 資料夾中找不到任何 .xlsx 檔案。")
        return

    all_sheets = []
    processed_countries = set()
    
    print(f"開始處理，共找到 {len(file_list)} 個檔案...")

    for file in file_list:
        try:
            df = pd.read_excel(file, sheet_name=config.SHEET_NAME, header=2)
            for col in df.select_dtypes(include=['datetime']):
                df[col] = df[col].dt.strftime('%Y-%m-%d')
            year_col = df.columns[1]
            df[year_col] = pd.to_numeric(df[year_col], errors='coerce')
            df = df[df[year_col].between(config.START_YEAR, config.END_YEAR)]
            if not df.empty:
                country_name = os.path.splitext(os.path.basename(file))[0].split('_')[0]
                if country_name in config.EXCLUDE_COUNTRIES:
                    print(f"排除國家: {country_name} ({file})")
                    continue
                df.insert(loc=4, column='Country', value=country_name)
                all_sheets.append(df)
                processed_countries.add(country_name)
                print(f"成功處理: {file}")
            else:
                print(f"跳過檔案: {file} (找不到名為 'Request 3' 的工作表 or 無 {config.START_YEAR}-{config.END_YEAR} 之資料)")            
        except ValueError:
            print(f"跳過檔案: {file} (找不到名為 'Request 3' 的工作表)")
        except Exception as e:
            print(f"讀取檔案 {file} 時發生錯誤: {e}")
    if all_sheets:
        merged_df = pd.concat(all_sheets, ignore_index=True)
        merged_df.to_excel(output_name, index=False)
        print(f"\n合併完成！結果已儲存至: {output_name}，成功處理了 {len(processed_countries)} 個國家。")
    else:
        print("\n沒有可合併的資料。")

if __name__ == "__main__":
    merge_xlsx()