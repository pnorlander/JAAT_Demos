#!/usr/bin/env python3
"""Merge all occupational coding tool results into a single analysis file.

Inputs:
    raw_titles_analysis.csv     — base data with TitleMatch + SOCkit
    results/nioccs_coded.csv    — NIOCCS results (may not exist yet)
    results/soccer_upload_soccerNet_results.xlsx — SOCcer results

Output:
    results/all_tools_comparison.csv — merged file with all match indicators

Usage:
    python3 build_comparison.py
    python3 build_comparison.py --skip-nioccs   # if NIOCCS not yet complete
"""

import argparse
import os

import numpy as np
import pandas as pd


# ── Helpers ──────────────────────────────────────────────────────────────

def code_to_str(code, width=6):
    """Convert numeric SOC code to zero-padded string."""
    if pd.isna(code):
        return None
    try:
        s = str(int(float(code))).zfill(width)
        return s if len(s) == width else None
    except (ValueError, OverflowError):
        return None


def match_at_digits(code1, code2, n):
    """Check if two 6-digit SOC code strings match at n-digit level."""
    if code1 is None or code2 is None:
        return None
    if not isinstance(code1, str) or not isinstance(code2, str):
        return None
    return code1[:n] == code2[:n]


TOOLS = ['tm', 'sockit', 'nioccs', 'soccer']
DIGITS = [2, 4, 6]


# ── Main ─────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description='Merge occupational coding results')
    parser.add_argument('--base', default='raw_titles_analysis.csv')
    parser.add_argument('--nioccs', default='results/nioccs_coded.csv')
    parser.add_argument('--soccer', default='results/soccer_upload_soccerNet_results.xlsx')
    parser.add_argument('--crosswalk', default='results/soc_2010_to_2018_crosswalk.xlsx',
                        help='BLS SOC 2010→2018 crosswalk Excel file')
    parser.add_argument('--output', default='results/all_tools_comparison.csv')
    parser.add_argument('--skip-nioccs', action='store_true',
                        help='Skip NIOCCS merge if results not ready')
    args = parser.parse_args()

    # ── 1. Load base data ────────────────────────────────────────────────
    print('Loading base data...')
    df = pd.read_csv(args.base)
    print(f'  {len(df)} rows before dedup, {df["job_title"].nunique()} unique titles')

    # Deduplicate: collapse rows with same job_title + occupation_code,
    # summing count across years. Keep first row's other values.
    agg_cols = {'count': 'sum'}
    group_cols = ['job_title', 'occupation_code']
    # Columns to keep first value of
    first_cols = [c for c in df.columns if c not in group_cols and c != 'count']
    for c in first_cols:
        agg_cols[c] = 'first'
    df = df.groupby(group_cols, sort=False).agg(agg_cols).reset_index()
    print(f'  {len(df)} rows after dedup (collapsed across years)')

    # Recompute unique_occs_per_title after dedup
    occ_counts = df.groupby('job_title')['occupation_code'].nunique()
    df['unique_occs_per_title'] = df['job_title'].map(occ_counts)

    # Standardize existing boolean columns
    bool_cols = [c for c in df.columns if c.startswith(('tm_match_', 'sockit_match_', 'tm_vs_sockit_'))]
    for col in bool_cols:
        df[col] = df[col].astype(str).str.strip().map({'True': True, 'False': False})

    # Standardize code columns to 6-digit strings
    df['lca_code'] = df['cleaned_original_code'].apply(code_to_str)
    df['tm_code'] = df['cleaned_tm_code'].apply(code_to_str)
    df['sockit_code'] = df['cleaned_sockit_code'].apply(code_to_str)

    # ── 2. Merge NIOCCS ─────────────────────────────────────────────────
    if not args.skip_nioccs and os.path.exists(args.nioccs):
        print('Merging NIOCCS results...')
        nioccs = pd.read_csv(args.nioccs)
        nioccs = nioccs[['job_title', 'nioccs_code_clean', 'nioccs_probability']].copy()
        nioccs['nioccs_code'] = nioccs['nioccs_code_clean'].apply(code_to_str)
        # Treat "Insufficient Information" (009900) as missing
        nioccs.loc[nioccs['nioccs_code'] == '009900', 'nioccs_code'] = None
        nioccs = nioccs.drop(columns=['nioccs_code_clean'])
        # Deduplicate — one row per unique title
        nioccs = nioccs.drop_duplicates(subset='job_title', keep='first')
        df = df.merge(nioccs, on='job_title', how='left')
        n_nioccs = df['nioccs_code'].notna().sum()
        print(f'  {n_nioccs}/{len(df)} rows with NIOCCS codes')
    else:
        print('Skipping NIOCCS (not available)')
        df['nioccs_code'] = None
        df['nioccs_probability'] = None

    # ── 3. Merge SOCcer ──────────────────────────────────────────────────
    if os.path.exists(args.soccer):
        print('Merging SOCcer results...')
        soccer = pd.read_excel(args.soccer)

        # Build mapping: Id -> original job_title (same dedup order)
        unique_titles = df['job_title'].drop_duplicates().reset_index(drop=True)
        title_map = pd.DataFrame({
            'Id': range(1, len(unique_titles) + 1),
            'job_title': unique_titles,
        })
        soccer = soccer.merge(title_map, on='Id', how='left')

        # Clean SOCcer code (SOC 2010 format "11-1011" -> "111011")
        soccer['soccer_code'] = (soccer['soc2010_1'].astype(str)
                                 .str.replace('-', '', regex=False).str.strip())
        soccer['soccer_code'] = soccer['soccer_code'].apply(
            lambda x: x if x.isdigit() and len(x) == 6 else None)
        soccer['soccer_score'] = soccer['score_1']

        soccer = soccer[['job_title', 'soccer_code', 'soccer_score']].drop_duplicates(
            subset='job_title', keep='first')
        df = df.merge(soccer, on='job_title', how='left')
        n_soccer = df['soccer_code'].notna().sum()
        print(f'  {n_soccer}/{len(df)} rows with SOCcer codes')
    else:
        print(f'SOCcer file not found: {args.soccer}')
        df['soccer_code'] = None
        df['soccer_score'] = None

    # ── 3b. Apply SOC 2010→2018 crosswalk to SOCcer codes ──────────────
    crosswalk_path = args.crosswalk
    if os.path.exists(crosswalk_path) and 'soccer_code' in df.columns:
        print('Applying SOC 2010→2018 crosswalk to SOCcer codes...')
        xw = pd.read_excel(crosswalk_path, header=7)
        xw.columns = ['soc2010', 'title2010', 'soc2018', 'title2018']
        # Clean codes: "11-1011" -> "111011"
        xw['soc2010_clean'] = xw['soc2010'].astype(str).str.replace('-', '', regex=False).str.strip()
        xw['soc2018_clean'] = xw['soc2018'].astype(str).str.replace('-', '', regex=False).str.strip()
        xw = xw[xw['soc2010_clean'].str.isdigit() & xw['soc2018_clean'].str.isdigit()]

        # Build lookup: SOC 2010 code -> set of SOC 2018 codes
        soc2010_to_2018 = xw.groupby('soc2010_clean')['soc2018_clean'].apply(set).to_dict()

        # For each SOCcer code, get the primary 2018 mapping (first/only)
        # and store all possible 2018 codes for crosswalk-any-match
        def crosswalk_primary(code_2010):
            if code_2010 is None:
                return None
            codes_2018 = soc2010_to_2018.get(code_2010)
            if not codes_2018:
                return code_2010  # unmapped — assume unchanged
            return min(codes_2018)  # deterministic: lowest code

        df['soccer_code_2010'] = df['soccer_code']  # preserve original
        df['soccer_code'] = df['soccer_code_2010'].apply(crosswalk_primary)

        # Store all 2018 possibilities for crosswalk-any-match
        df['_soccer_2018_all'] = df['soccer_code_2010'].apply(
            lambda c: soc2010_to_2018.get(c, {c} if c else set()))

        n_multi = df['_soccer_2018_all'].apply(lambda s: len(s) > 1).sum()
        n_mapped = df['soccer_code_2010'].notna().sum()
        print(f'  {n_mapped} codes mapped, {n_multi} have 1-to-many crosswalk')
    else:
        if 'soccer_code' in df.columns:
            df['soccer_code_2010'] = df['soccer_code']
            df['_soccer_2018_all'] = df['soccer_code'].apply(
                lambda c: {c} if c else set())
        print('No crosswalk file — SOCcer codes used as-is')

    # ── 4. Compute strict match indicators for new tools ─────────────────
    print('Computing strict match indicators...')
    # NIOCCS: straightforward
    for n in DIGITS:
        df[f'nioccs_match_{n}_digit'] = [match_at_digits(tc, lc, n)
                                          for tc, lc in zip(df['nioccs_code'], df['lca_code'])]

    # SOCcer: use crosswalk-any-match (if 2010 code maps to multiple 2018 codes,
    # count as match if LCA code matches ANY of them)
    if '_soccer_2018_all' in df.columns:
        for n in DIGITS:
            results = []
            for codes_2018, lca in zip(df['_soccer_2018_all'], df['lca_code']):
                if not codes_2018 or lca is None:
                    results.append(None)
                else:
                    results.append(any(match_at_digits(c, lca, n) for c in codes_2018))
            df[f'soccer_match_{n}_digit'] = results
    else:
        for n in DIGITS:
            df[f'soccer_match_{n}_digit'] = [match_at_digits(tc, lc, n)
                                              for tc, lc in zip(df['soccer_code'], df['lca_code'])]

    # ── 5. Build title-level lookup tables ───────────────────────────────
    print('Building title-level lookups...')

    # All attested codes per title (for any-match)
    title_codes = df.groupby('job_title')['lca_code'].apply(
        lambda x: set(v for v in x if v is not None)).to_dict()

    # Modal code per title (for best-match): highest count, ties broken by lowest code
    modal_df = (df[df['lca_code'].notna()]
                .sort_values(['job_title', 'count', 'lca_code'],
                             ascending=[True, False, True])
                .groupby('job_title')['lca_code'].first())
    title_modal = modal_df.to_dict()

    # ── 6. Compute any-match and best-match for all tools ────────────────
    print('Computing any-match and best-match indicators...')

    # Pre-map title -> all_codes and title -> modal_code as series for vectorized lookup
    df['_all_codes'] = df['job_title'].map(title_codes)
    df['_modal_code'] = df['job_title'].map(title_modal)

    for tool in TOOLS:
        code_col = f'{tool}_code'
        if code_col not in df.columns:
            continue

        tool_codes = df[code_col].tolist()
        all_codes_list = df['_all_codes'].tolist()
        modal_codes = df['_modal_code'].tolist()

        for n in DIGITS:
            # Any-match
            any_results = []
            for tc, ac in zip(tool_codes, all_codes_list):
                if tc is None:
                    any_results.append(None)
                elif not ac:
                    any_results.append(None)
                else:
                    any_results.append(any(match_at_digits(tc, c, n) for c in ac))
            df[f'{tool}_any_match_{n}_digit'] = any_results

            # Best-match
            best_results = []
            for tc, mc in zip(tool_codes, modal_codes):
                best_results.append(match_at_digits(tc, mc, n))
            df[f'{tool}_best_match_{n}_digit'] = best_results

    df = df.drop(columns=['_all_codes', '_modal_code'])

    # ── 7. Drop 3-digit columns and temp columns ──────────────────────
    drop_cols = [c for c in df.columns if '_3_digit' in c]
    drop_cols += [c for c in df.columns if c.startswith('_')]  # temp columns
    df = df.drop(columns=[c for c in drop_cols if c in df.columns])
    print(f'  Dropped {len(drop_cols)} columns')

    # ── 8. Save ──────────────────────────────────────────────────────────
    os.makedirs(os.path.dirname(args.output) or '.', exist_ok=True)
    df.to_csv(args.output, index=False)
    print(f'\nSaved {args.output}')
    print(f'  {len(df)} rows, {len(df.columns)} columns')

    # Summary
    print('\n=== Strict Match Rates (unweighted) ===')
    for tool in TOOLS:
        for n in [2, 6]:
            col = f'{tool}_match_{n}_digit'
            if col in df.columns:
                valid = df[col].notna()
                if valid.any():
                    rate = df.loc[valid, col].mean() * 100
                    print(f'  {tool:10s} {n}-digit: {rate:.1f}% (n={valid.sum():,})')

    print('\n=== Any-Match Rates (unweighted, 6-digit) ===')
    for tool in TOOLS:
        col = f'{tool}_any_match_6_digit'
        if col in df.columns:
            valid = df[col].notna()
            if valid.any():
                rate = df.loc[valid, col].mean() * 100
                print(f'  {tool:10s}: {rate:.1f}%')


if __name__ == '__main__':
    main()
