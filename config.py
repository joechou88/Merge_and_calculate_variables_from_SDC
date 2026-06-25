SHEET_NAME = 'Request 3'
START_YEAR = 2015
END_YEAR = 2019

# Folder name
SDC_FOLDER = "SDC_xlsx"

# File name
MERGED_OUTPUT = f"Merged_All_countries_SDC_{START_YEAR}-{END_YEAR}.xlsx"
FILTERED_OUTPUT = f"Filtered_All_countries_SDC_{START_YEAR}-{END_YEAR}.xlsx"
DUPLICATED_OUTPUT = "Duplicated_company_list.xlsx"
UNIQUE_OUTPUT     = f"Unique_All_countries_SDC_{START_YEAR}-{END_YEAR}.xlsx"
CALCULATED_OUTPUT = f"Calculated_All_countries_SDC_{START_YEAR}-{END_YEAR}.xlsx"
TOP25_UNDERWRITERS = "Top25_Bookrunner_League_Table_by_Proceeds_Amount_All_Markets.xlsx"

# Filter country
EXCLUDE_COUNTRIES = [
    "Ireland",
    "Japan",
    "China",
    "India",
    "Indonesia",
    "Switzerland",
    "Vietnam"
]

# Filter columns
TARGET_COLUMNS = [
    "Dates: Issue Date",
    "Dates: Offer Year (CCYY)",
    "Issuer/Borrower Name Full",
    "Country",
    "Issuer/Borrower Primary SIC (Code)",
    "Issuer/Borrower SEDOL",
    "ISIN",
    "Datastream",
    "Percent Change Offer Price to Closing Price at Offer/First Trade",
    "Issuer/Borrower Founded Date",
    "Proceeds Amount All Markets (USD Millions)",
    "Financials: Total Assets Before Offering (USD Millions)",
    "Venture Capital Backed IPO Issue Flag",
    "Offering Technique",
    "Pricing Technique",
    "Spinoff (Equity Carveout) Company: Pct Owned by Parent After Spinoff",
    "Bookrunner",
    "Offer Price (USD)",
    "Original IPO Flag",
    "Main Tranche within Package flag",
    "Blank Check (SPAC) Involvement Y/N:",
    "Unit Issues: Unit Issue Flag",
    "Depositary Issue Flag",
    "Issuer/Borrower REIT Type",
    "Closed-end Fund/Trust Flag",
    "Fund or Trust Issue Flag",
    "Limited Partnership Flag (Y/N)",
    "Private Placement Flag",
    "Spinoff (Equity Carveout) Type (Code)"
]
