import pandas as pd
import config

COMPANY  = "Issuer/Borrower Name Full"
COUNTRY  = "Country"
DATE     = "Dates: Issue Date"
PROCEEDS = "Proceeds Amount All Markets (USD Millions)"

DATE_THRESHOLD_DAYS = 3

def _resolve_group(group: pd.DataFrame):
    if len(group) == 1:
        return group.iloc[0]

    dates = group[DATE].dropna()

    # Case A: If issue dates within 3-day window → merge as one IPO event
    if not dates.empty:
        date_spread = (dates.max() - dates.min()).days
    else:
        date_spread = 0  # no dates → treat as Case A (merge)

    if date_spread <= DATE_THRESHOLD_DAYS:
        anchor_idx = group[PROCEEDS].idxmax(skipna=True)
        merged = group.loc[anchor_idx].copy()
        merged[PROCEEDS] = group[PROCEEDS].sum(min_count=1)
        return merged

    # Case B: If issue dates too far apart → keep only the earliest issue date record
    first_idx = group[DATE].idxmin(skipna=True) if not dates.empty else group.index[0]
    return group.loc[first_idx].copy()


# ── Main ──────────────────────────────────────────────────────────────────────

def handle_duplicates(input_path: str, output_path: str) -> None:
    print(f"Loading : {input_path}\n")
    df = pd.read_excel(input_path)
    df[DATE] = pd.to_datetime(df[DATE], errors="coerce")

    total_before = len(df)
    unique_before = df[COMPANY].nunique()
    print(f"Records before dedup : {total_before}")
    print(f"Unique companies     : {unique_before}")

    if total_before == unique_before:
        print("\n✅  No duplicates found — saving file as-is.\n")
        df.to_excel(output_path, index=False)
        print(f"💾 Saved: {output_path}")
        return

    dup_mask = df.duplicated(subset=[COMPANY], keep=False)
    df_with_unique_company  = df[~dup_mask].copy()
    df_with_duplicate_company = df[dup_mask].copy()
    print(f"Companies with duplicates : {df_with_duplicate_company[COMPANY].nunique()}")
    print(f"Duplicate rows            : {len(df_with_duplicate_company)}\n")

    df_with_duplicate_company = df_with_duplicate_company.sort_values([COMPANY, DATE]).reset_index(drop=True)

    companies_consolidating_records, companies_preserving_first_record = [], []

    for company, grp in df_with_duplicate_company.groupby(COMPANY, sort=False):
        dates = grp[DATE].dropna()
        spread = (dates.max() - dates.min()).days if not dates.empty else 0
        if spread <= DATE_THRESHOLD_DAYS:
            companies_consolidating_records.append(company)
        else:
            companies_preserving_first_record.append(company)

    print(f"Issue dates are identical, merge multiple issue records: {len(companies_consolidating_records)} companies")
    print(f"Issue dates too far-apart, keep first issue record only: {len(companies_preserving_first_record)} companies\n")

    df_with_duplicate_company = (
        df_with_duplicate_company
        .groupby(COMPANY, sort=False)
        .apply(_resolve_group)
        .reset_index(drop=True)
    )

    df_final = pd.concat([df_with_unique_company, df_with_duplicate_company], ignore_index=True)
    df_final = df_final[df.columns]  # Restore original column order
    df_final[DATE] = df_final[DATE].dt.strftime('%Y-%m-%d')

    total_after = len(df_final)
    print(f"Records after dedup  : {total_after}  (removed {total_before - total_after})")
    assert df_final[COMPANY].nunique() == total_after, \
        "❌  Deduplication incomplete — some companies still have > 1 record!"
    print("✅  Every company now has exactly one record.\n")

    df_final.to_excel(output_path, index=False)
    print(f"💾 Saved: {output_path}")


if __name__ == "__main__":
    handle_duplicates(config.FILTERED_OUTPUT, config.UNIQUE_OUTPUT)
