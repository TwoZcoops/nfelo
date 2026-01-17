import pandas as pd
from pathlib import Path

out_dir = Path('output_data')
out_dir.mkdir(parents=True, exist_ok=True)

# load files
hp = pd.read_csv(out_dir / 'historic_projected_spreads.csv')
nf = pd.read_csv(out_dir / 'nfelo_games.csv')
cf = pd.read_csv('nfelo/Data/Formatted Data/current_file_with_analytics.csv')
md = pd.read_csv('nfelo/Data/Intermediate Data/market_data.csv')

# filter week 20, 2025
hp20 = hp[(hp['season'] == 2025) & (hp['week'] == 20)].copy()
nf20 = nf[nf['game_id'].str.contains('_20_')].copy()
cf20 = cf[(cf['season'] == 2025) & (cf['week'] == 20)].copy()
md20 = md[(md['season'] == 2025) & (md['week'] == 20)].copy()

# merge datasets
if hp20.empty:
    print('No Week 20 rows found in historic_projected_spreads.csv')

# merge nf
merge_cols_nf = ['game_id','starting_nfelo_home','starting_nfelo_away','nfelo_home_probability_close','home_ev','away_ev']
merge_cols_nf = [c for c in merge_cols_nf if c in nf20.columns]
df = hp20.merge(nf20[merge_cols_nf], on='game_id', how='left')

# analytics columns (only keep those that exist)
analytics_cols = ['home_net_wepa','away_net_wepa','home_pff_point_margin','away_pff_point_margin','home_538_qb_adj','away_538_qb_adj']
available_analytics = [c for c in analytics_cols if c in cf20.columns]
if available_analytics:
    df = df.merge(cf20[['game_id'] + available_analytics], on='game_id', how='left')

# market columns
mdcols = ['home_line_close','home_line_close_price','home_ml_close','away_ml_close','home_ats_pct']
available_mdcols = [c for c in mdcols if c in md20.columns]
if available_mdcols:
    df = df.merge(md20[['game_id'] + available_mdcols], on='game_id', how='left')

# select compact column set
cols = [
    'game_id','season','week','home_team','away_team','gameday','gametime',
    'home_line_close','home_line_close_price','home_probability_nfelo','home_nfelo_elo','away_nfelo_elo','home_538_qb','away_538_qb',
    'starting_nfelo_home','starting_nfelo_away','nfelo_home_probability_close','home_ev','away_ev'
]
# include available analytics and market columns
cols += available_analytics + available_mdcols
cols = [c for c in cols if c in df.columns]

out_csv = out_dir / 'week20_payload.csv'
out_json = out_dir / 'week20_payload.json'

if df.empty:
    print('No merged Week 20 rows to write. Check datasets.')
else:
    # remove duplicate columns (keep first occurrence)
    # but check for duplicates first for debugging
    dup_cols = df.columns[df.columns.duplicated()].tolist()
    if dup_cols:
        print('Duplicate columns detected before dedupe:', dup_cols)
    df = df.loc[:, ~df.columns.duplicated()]
    dup_cols_after = df.columns[df.columns.duplicated()].tolist()
    if dup_cols_after:
        print('Duplicate columns still present after dedupe:', dup_cols_after)
        # make column names unique by appending counters
        new_cols = []
        counter = {}
        for c in df.columns:
            if c in counter:
                counter[c] += 1
                new_cols.append(f"{c}_{counter[c]}")
            else:
                counter[c] = 0
                new_cols.append(c)
        df.columns = new_cols
        print('Columns renamed to be unique. New columns list:')
        print(df.columns.tolist())

    # ensure we only write columns that exist after dedupe/rename
    write_cols = [c for c in cols if c in df.columns]
    write_df = df[write_cols]
    write_df.to_csv(out_csv, index=False)
    # write JSON using json.dump to avoid pandas unique-column restriction
    import json
    records = write_df.to_dict(orient='records')
    with open(out_json, 'w', encoding='utf-8') as f:
        json.dump(records, f, indent=2)
    print('Wrote:', out_csv)
    print('Wrote:', out_json)
    print('\nPayload preview:\n')
    print(write_df.to_string(index=False))
