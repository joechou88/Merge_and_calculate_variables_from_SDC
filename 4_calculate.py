import pandas as pd
import numpy as np
import config

df = pd.read_excel(config.UNIQUE_OUTPUT)
underwriter_df = pd.read_excel(config.TOP25_UNDERWRITERS)
top_25_underwriters = {}
current_year = None

for val in underwriter_df.iloc[:, 0].dropna():
    val_str = str(val).strip()
    if val_str.isdigit() and len(val_str) == 4:
        current_year = int(val_str)
        top_25_underwriters[current_year] = set()
    elif current_year is not None:
        if not val_str.startswith(('Subtotal', 'Industry', 'Source', 'Managing', 'Full', 'Sector')):
            top_25_underwriters[current_year].add(val_str.upper())

print(f"Columns in filtered SDC file: {df.columns.tolist()}\n")
print(f"Top 25 underwriters: {top_25_underwriters}\n")

def get_col(df, name):
    return df[name] if name in df.columns else pd.Series([np.nan] * len(df))

# 1. Underpricing
df['Underpricing'] = get_col(df, 'Percent Change Offer Price to Closing Price at Offer/First Trade')

# 2. Ln_Age
issue_date = pd.to_datetime(get_col(df, 'Dates: Issue Date'), errors='coerce')
founded_date = pd.to_datetime(get_col(df, 'Issuer/Borrower Founded Date'), errors='coerce')
age = (issue_date - founded_date).dt.days / 365.25
df['Age'] = age
df['Ln_Age'] = age.apply(lambda x: np.log1p(x) if pd.notna(x) and x >= 0 else (np.nan if pd.isna(x) else 0))

# 3. Relative_Offer_Size
proceeds = pd.to_numeric(get_col(df, 'Proceeds Amount All Markets (USD Millions)'), errors='coerce')
df['Relative_Offer_Size'] = proceeds * 1000
df['Relative_Offer_Size'] = df['Relative_Offer_Size'].replace([np.inf, -np.inf], np.nan)    # Replace infinite values with NaN since Stata cannot handle inf

# 4. VC_backed
def check_vc_backed(x):
    if pd.isna(x) or str(x).strip() == '':
        return np.nan
    return 1 if str(x).strip().upper() in ['TRUE', '1', '1.0', 'YES', 'Y'] else 0
df['VC_backed'] = get_col(df, 'Venture Capital Backed IPO Issue Flag').apply(check_vc_backed)

# 5. Firm_Commitment
def check_firm_commitment(tech):
    if pd.isna(tech):
        return np.nan
    tech_str = str(tech).upper().replace(" ", "")
    return 1 if 'FIRMCOMMITMENT' in tech_str else 0
df['Firm_Commitment'] = get_col(df, 'Offering Technique').apply(check_firm_commitment)

# 6. Underwriter_Reputation
def check_reputation(bookrunner, year):
    if pd.isna(bookrunner) or str(bookrunner).strip() == ''or pd.isna(year): 
        return np.nan
    try:
        offer_year = int(year)
    except (ValueError, TypeError):
        return np.nan

    top_25_underwriters_this_year = top_25_underwriters.get(offer_year, set())
    bookrunners = [r.strip().upper() for r in str(bookrunner).split(';')]
    for runner in bookrunners:
        for underwriter in top_25_underwriters_this_year:
            if underwriter == runner: 
                return 1
    return 0
    
bookrunners = get_col(df, 'Bookrunner')
offer_years = get_col(df, 'Dates: Offer Year (CCYY)')
df['Underwriter_Reputation'] = [check_reputation(b, y) for b, y in zip(bookrunners, offer_years)]

# 7. Integer_Offer_Price
def is_integer_price(price):
    if pd.isna(price): return np.nan
    try:
        val = float(price)
        return 1 if round(val, 6).is_integer() else 0
    except (ValueError, TypeError) as e:
        print(f"Warning: Cannot convert '{price}' to float. Error: {e}")
        return np.nan
df['Integer_Offer_Price'] = get_col(df, 'Offer Price (USD)').apply(is_integer_price)

# 8. Bookbuilt
def check_bookbuilt(tech):
    if pd.isna(tech):
        return np.nan
    return 1 if 'BOOKBUILDING' in str(tech).upper() else 0
df['Bookbuilt'] = get_col(df, 'Pricing Technique').apply(check_bookbuilt)

# 9. IPO_Activities
offer_year = 'Dates: Offer Year (CCYY)'
country = 'Country'
df['IPO_count'] = df.groupby([country, offer_year])[country].transform('count')

# 10. Price_Stabilization
small_pos = ((df['Underpricing'] > 0) & (df['Underpricing'] <= 1)).astype(int)
small_neg = ((df['Underpricing'] < 0) & (df['Underpricing'] >= -1)).astype(int)
small_pos_sum = small_pos.groupby([df[country], df[offer_year]]).transform('sum')
small_neg_sum = small_neg.groupby([df[country], df[offer_year]]).transform('sum')
df['Price_Stabilization'] = (small_pos_sum - small_neg_sum) / df['IPO_count']

# 11. Equity_Carve_out
def check_equity_carve_out(pct):
    if pd.isna(pct):
        return np.nan
    return 1 if pct > 20 else 0
pct_owned = pd.to_numeric(get_col(df, 'Spinoff (Equity Carveout) Company: Pct Owned by Parent After Spinoff'), errors='coerce')
df['Equity_Carve_out'] = pct_owned.apply(check_equity_carve_out)

calculated_cols = ['Country', 'Underpricing', 'Age', 'Ln_Age', 'Relative_Offer_Size', 'VC_backed', 
                   'Firm_Commitment', 'Underwriter_Reputation', 'Integer_Offer_Price',
                   'Bookbuilt', 'IPO_count', 'Price_Stabilization', 'Equity_Carve_out']
id_cols = ['Issuer/Borrower SEDOL', 'ISIN', 'Datastream']
necessary_cols = ['Dates: Issue Date', 'Dates: Offer Year (CCYY)', 'Offer Price (USD)']
output_cols = calculated_cols + id_cols + necessary_cols

df_final = df[output_cols]
df_final.to_excel(config.CALCULATED_OUTPUT, index=False)
print(f"Results saved as: {config.CALCULATED_OUTPUT}")
