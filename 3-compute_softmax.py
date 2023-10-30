# %%
import pandas as pd
import numpy as np

away_input='data/away_probs.csv'
home_input='data/home_probs.csv'
output='probabilities/'

# %%
df_away = pd.read_csv(away_input)
df_away = df_away.rename(columns={'prob': 'prob_away'})
df_home = pd.read_csv(home_input)
df_home = df_home.rename(columns={'prob': 'prob_home'})

# %%
def softmax(column):
    e_x = np.exp(column - np.max(column))  # Subtracting the max value for numerical stability
    return e_x / e_x.sum()

def write_csv(path, dataset):
    dataset.to_csv(path, index=False)

# %%
merged_df = pd.merge(df_away, df_home, on=['match_id', 'model'], how='inner')

# %%
softmax_df = merged_df.copy()

# %%
softmax_df['match_url'] = merged_df['match_id'].apply(lambda x: f'https://www.premierleague.com/match/12301/{x}')
softmax_df[['away_prob_softmax', 'home_prob_softmax']] = merged_df[['prob_away', 'prob_home']].apply(softmax, axis=1)

# %%
write_csv(f'{output}/away.csv', softmax_df[['match_url', 'away_prob_softmax','model']])
write_csv(f'{output}/home.csv', softmax_df[['match_url', 'home_prob_softmax', 'model']])
