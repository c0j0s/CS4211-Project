# This script automatically simulates 1x2 betting ($100 per match) based on Bet365 odds on all of the EPL seasons
# Directory betting_dataset containts the odds for the matches from each EPL season
# Directory original_probabilities and new_probabilities contains the probabilities for each season 
# Original represents the original soccer PAT model probabilities and new represents probabilities from your improved PAT model
# Currently the csv files in new_probabilities directory is just a copy of the files in original_probabilities
# Replace the files in the new_probabilities directory with your respective files in the same csv format, with the same file name and columns etc.
# home_prob_softmax represents the home win probabilities with the away win probabilities being 1 - home_prob_softmax
# To get such a probability distribution, you can use the softmax function to combine the probabilities from the home PAT model and away PAT model
# To run the file, first install pandas, then simply: python simulate.py
# %%
import pandas as pd
import glob

summary = pd.DataFrame(columns=[
    'season',
    'original_net',
    'new_net'
])

# %%
def simulate_betting(season, model_season_path):
    global summary

    df_betting = pd.read_csv(f"betting_simulation/betting_dataset/{season}.csv")
    df_original = pd.read_csv(f"betting_simulation/original_probabilities/{season}.csv")
    df_new = pd.read_csv(model_season_path)

    # bet $100 for every match
    original_net, new_net = 0, 0
    for index, row in df_betting.iterrows():
        match_url = row['match_url']
        home_odds = row['B365H']
        away_odds = row['B365A']
        draw_odds = row['B365D']
        # 0 = home_win, 1 = away_win, 2 = draw
        result = row['result']

        original_home_prob = df_original.loc[df_original['match_url'] == match_url]['home_prob_softmax'].values[0]
        new_home_prob = df_new.loc[df_new['match_url'] == match_url]['home_prob_softmax'].values[0]

        # predict draw
        if abs((1-original_home_prob) - original_home_prob) < 0.001:
            if result == 2: original_net += (draw_odds * 100) - 100
            else: original_net -= 100
        # predict home win
        elif original_home_prob > (1-original_home_prob):
            if result == 0: original_net += (home_odds * 100) - 100
            else: original_net -= 100
        # predict away win
        elif original_home_prob < (1-original_home_prob):
            if result == 1: original_net += (away_odds * 100) - 100
            else: original_net -= 100

        # predict draw
        if abs((1-new_home_prob) - new_home_prob) < 0.001:
            if result == 2: new_net += (draw_odds * 100) - 100
            else: new_net -= 100
        # predict home win
        elif new_home_prob > (1-new_home_prob):
            if result == 0: new_net += (home_odds * 100) - 100
            else: new_net -= 100
        # predict away win
        elif new_home_prob < (1-new_home_prob):
            if result == 1: new_net += (away_odds * 100) - 100
            else: new_net -= 100
    difference = new_net - original_net
    print(f"season {season} net profit (original, new, difference): (${original_net}, ${new_net}, ${difference})")

    summary = summary._append({
        'model': model_name,
        'season': season,
        'original_net': original_net,
        'new_net': new_net
    }, ignore_index=True)
    return((original_net, new_net))

if __name__ == "__main__":
    model_pattern = './models/model_*' 
    model_folders = glob.glob(model_pattern)

    for model_path in model_folders:
        model_name = model_path.split('/')[2].replace('model_','')
        season_pattern = f'{model_path}/new_probabilities/*.csv'
        season_folders = glob.glob(season_pattern)

        original_total = 0
        new_total = 0
        for season_path in season_folders:
            season_name = season_path.split('/')[4].replace('.csv','')
            print(f'Simulating {model_name}: {season_name} in {season_path}')
            original_net, new_net = simulate_betting(season_name, season_path)
            original_total += original_net
            new_total += new_net
            print("Original total:", original_total)
            print("New total:", new_total)
            print("Difference:", new_total - original_total)
    summary.to_excel('summary.xlsx')
    # summary.to_markdown('summary.md')