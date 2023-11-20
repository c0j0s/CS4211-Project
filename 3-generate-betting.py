# %%
import os
import pandas as pd

prob_file = "home_probs.csv"
# prob_file = "model_of_to_sc_ko\home_probs.csv"

season_bins = [12000, 14000, 22000, 38000, 46000, 58000, 60000]
season_labels = ['1516', '1617', '1718', '1819', '1920', '2021']

ori_df = pd.read_csv(prob_file)
# %%
ori_df['season'] = pd.cut(ori_df['match_id'], bins=season_bins, labels=season_labels, right=False)
grouped = ori_df.groupby('season')

# %%
ori_df.rename(columns={'prob': 'home_prob_softmax'}, inplace=True)
ori_df['match_id'] = ori_df['match_id'].apply(lambda x: f'https://www.premierleague.com/match/{x}')
ori_df.rename(columns={'match_id': 'match_url'}, inplace=True)

# %%
if not os.path.exists("./new_probabilities"):
    os.makedirs("./new_probabilities")

for name, group in grouped:
    filename = f"./new_probabilities/{name}.csv"
    group = group.drop(columns=['season'])
    group.to_csv(filename, index=False)
    print(f"Convert {prob_file} into {filename}")
# %%
