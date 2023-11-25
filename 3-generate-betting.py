# %%
import os
import pandas as pd
import math

prob_file_away = "away_probs.csv"
prob_file_home = "home_probs.csv"
# prob_file_away = "./models/model_final/away_probs.csv"
# prob_file_home = "./models/model_final/home_probs.csv"

season_bins = [12000, 14000, 22000, 38000, 46000, 58000, 60000]
season_labels = ['1516', '1617', '1718', '1819', '1920', '2021']

# %%
def softmax(away, home):
    exp_away = math.exp(away)
    exp_home = math.exp(home)
    exp_sum = exp_away + exp_home
    softmax_away = exp_away / exp_sum
    softmax_home = exp_home / exp_sum
    return softmax_away, softmax_home

# %%
ori_df_away = pd.read_csv(prob_file_away)
ori_df_home = pd.read_csv(prob_file_home)

ori_df = pd.merge(ori_df_away,ori_df_home, on=['match_id','model'])
# %%
ori_df['season'] = pd.cut(ori_df['match_id'], bins=season_bins, labels=season_labels, right=False)
grouped = ori_df.groupby('season', observed=True)

# %%
ori_df['home_prob_softmax'] = ori_df.apply(lambda row: softmax(row['away_prob'], row['home_prob'])[1], axis=1)

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
    print(f"Convert {prob_file_away}, {prob_file_home} into {filename}")
# %%
