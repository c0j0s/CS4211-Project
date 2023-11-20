# %%
import pandas as pd
import os

betting_input='../betting_simulation/betting_dataset/'
original_prob_input='../betting_simulation/original_probabilities/'
new_prob_input='./new_probabilities/'
output='./merged/'

description = [
    'home_win',
    'away_win',
    'draw'
]

def read_directory(path, extension='.csv'):
    return [f for f in os.listdir(path) if f.endswith(extension)]

def write_csv(path, dataset):
    dataset.to_csv(path, index=False)

# %%

files = set([
    *read_directory(betting_input),
    *read_directory(new_prob_input),
    *read_directory(original_prob_input)
])

# %%
if not os.path.exists(output):
    os.makedirs(output)

for file in files:
    df_betting  = pd.read_csv(f'{betting_input}/{file}' )
    df_new_prob = pd.read_csv(f'{new_prob_input}/{file}')
    df_new_prob = df_new_prob.rename(columns={'home_prob_softmax': 'new_home_prob_softmax'})
    df_original_prob = pd.read_csv(f'{original_prob_input}/{file}')
    df_original_prob = df_original_prob.rename(columns={'home_prob_softmax': 'original_home_prob_softmax'})

    merged_df = pd.merge(df_betting, df_new_prob, on='match_url', how='inner')
    merged_df = pd.merge(merged_df, df_original_prob, on='match_url', how='inner')
    merged_df['desc'] = merged_df['result'].apply(lambda x: description[int(x)])
    merged_df['delta'] = merged_df['new_home_prob_softmax'].astype(float) - merged_df['original_home_prob_softmax'].astype(float)

    write_csv(f'{output}/{file}', merged_df[['match_url', 'new_home_prob_softmax', 'original_home_prob_softmax', 'result', 'desc', 'delta']])
