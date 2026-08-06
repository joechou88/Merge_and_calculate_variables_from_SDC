## Data Source
### SDC
- Download .csv files by country and put them under `SDC_xlsx` folder
- 2017 Manual: https://drive.google.com/file/d/1bq7LzHWOJbOkfsZx-fkoMGtvZUg4EGqw/view?usp=drive_link

## Python Scripts
#### 1. Country Integration (`merge.py`)
- **Objective**: combine all country files in `SDC_xlsx` folder to one single `Merged_All_countries_SDC_2015-2024.xlsx`, except for countries in `EXCLUDE_COUNTRIES`
- **Output**: `Merged_All_countries_SDC_2015-2024.xlsx`
#### 2. Filtering (`filter.py`)
- **Objective**:
  - filter dataframe columns to retain only the predefined `TARGET_COLUMNS`
  - Exclude Non-IPO records
    - `Original IPO Flag` = TRUE
    - `Main Tranche within Package flag` = TRUE
    - 排除空殼公司：Exclude `Blank Check (SPAC) Involvement Y/N:` = TRUE
    - 排除單位發行：Exclude `Unit Issues: Unit Issue Flag` = TRUE
    - 排除存託憑證：Exclude `Depositary Issue Flag` = TRUE
    - 排除不動產投資信託：Exclude `Issuer/Borrower REIT Type` 有值的
    - 排除封閉型基金：Exclude `Closed-end Fund/Trust Flag` = TRUE
    - 排除基金與信託：Exclude `Fund or Trust Issue Flag` = TRUE
    - 排除有限合夥：Exclude `Limited Partnership Flag (Y/N)` = TRUE
    - 排除私募：Exclude `Private Placement Flag` = TRUE
    - 排除公營事業民營化：Exclude `Spinoff (Equity Carveout) Type (Code)` = P
  - Exclude particular industries
    - 排除金融機構：Exclude `Issuer/Borrower Primary SIC (Code)` 介於 6000–6999 的公司
    - 排除公用事業：Exclude `Issuer/Borrower Primary SIC (Code)` 介於 4900–4949 的公司

- **Input**: `Merged_All_countries_SDC_2015-2024.xlsx`
- **Output**: `Filtered_All_countries_SDC_2015-2024.xlsx`
#### 3-1. Company Uniqueness Check (`check_company_uniqueness.py`)
- **Objective**:
  - Ensures each company should ideally have only one IPO record.
  - Identifies and list duplicate company to help a deeper investigation into why duplicates exist
- **Input**: `Sample_Filtered_All_countries_SDC_2015-2024.xlsx`
- **Output**: `Duplicated_company_list.xlsx`
#### 3-2. Ensure Company Uniqueness (`handle_duplicates.py`)
- **Objective**: Ensures each company only have one record in the Excel file.
- **Key Functions**:
  - Entries sharing the exact same `Issuer/Borrower Name Full` with an `Dates: Issue Date` that is either identical or within 3-day are treated as a single IPO event. We should sum `Proceeds Amount All Markets (USD Millions)` together and retain values from record that held the highest `Proceeds Amount All Markets (USD Millions)` for other columns.
  - If `Dates: Issue Date` for the same `Issuer/Borrower Name Full` are too far apart (beyond 3-day threshold), we only keep the first record.
  - You can see an example to understand how duplicate records are merged: https://docs.google.com/spreadsheets/d/14AC16w1ZYBycbO3lvXgmCCPowfnXYNCR/edit?usp=sharing&ouid=108393837815697167094&rtpof=true&sd=true
- **Input**: `Sample_Filtered_All_countries_SDC_2015-2024.xlsx`
- **Output**: `Unique_All_countries_SDC_2015-2024.xlsx`
#### 4. Variable Calculation (`calculate.py`)
- **Objective**: calculate variables to be served as statistical model input
- **Variables**
  - Underpricing: `Percent Change Offer Price to Closing Price at Offer/First Trade` ≈ (`Stock Price at Close of Offer/First Trade (USD)` - `Offer Price (USD)`) / `Offer Price (USD)`
  - Ln_Age: log(1 + (`Dates: Issue Date` - `Issuer/Borrower Founded Date`) / 365.25)
  - Relative_Offer_Size: `Proceeds Amount All Markets (USD Millions)`*1000，之後併進 Stata 再用 Worldscope 去年底的 `Total_assets` (USD thousands) 平減
  - VC_backed: encode 1 if `Venture Capital Backed IPO Issue Flag` is TRUE
  - Firm_Commitment: encode 1 if `Offering Technique` contains `Firm Commitment`
  - Underwriter_Reputation: encode 1 if `Bookrunner` is in the top-25 bookrunner league table ranked by `Proceeds Amount All Markets`
  - Integer_Offer_Price: encode 1 if `Offer Price (USD)` is an integer
  - Bookbuilt: encode 1 if `Pricing Technique` = "Bookbuilding"
  - IPO_count: total number of IPOs for a given country in the issue year，之後併進 Stata 再除以 Worldscope 當年該國的公司數取 log 就可以算出 `IPO_Activities`
  - Price_Stabilization: Difference in the number of IPOs with first-day returns between 0% and 1% and the number of IPOs with first-day returns between −1% and 0%, divided by the total number of IPOs issued in a country, where first-day returns = `Percent Change Offer Price to Closing Price at Offer/First Trade`
  - Equity_Carve_out: encode 1 if `Spinoff (Equity Carveout) Company: Pct Owned by Parent After Spinoff` > 20
- **Input**: `Unique_All_countries_SDC_2015-2024.xlsx`
- **Output**: `Calculated_All_countries_SDC_2015-2024.xlsx`
