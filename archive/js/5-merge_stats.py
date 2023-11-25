# %%
import glob
import pandas as pd

model_pattern = './model_*/merged/' 
model_folders = glob.glob(model_pattern)

# %%
dfs = []
# Iterate over the matching files and read them
for model_path in model_folders:
    model_name = model_path.split('\\')[1].replace('model_','')
    season_pattern = f'{model_path}/*.csv'
    season_folders = glob.glob(season_pattern)
    for season_path in season_folders:
        season_name = season_path.split('\\')[3].replace('.csv','')
        
        print(f'{model_name}: {season_name}')
        df = pd.read_csv(season_path)
        
        df['model'] = model_name
        df['season'] = season_name

        dfs.append(df)
# %%
result = pd.concat(dfs, ignore_index=True)
# %%
result.to_csv('stat_summary.csv')
# %%
