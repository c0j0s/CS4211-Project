import os
import re
import csv

path = "./outputs"
pattern = r"(?<=\[).*(?=\])"
mode = 'avg'
# output = "./data"
model = input("model: ")

def read_directory(path, extension='.txt'):
    return [f for f in os.listdir(path) if f.endswith(extension)]

def write_csv(file_path, dataset, headers):
    with open(file_path, 'w', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(dataset)

def main():
    files = read_directory(path)
    print(f'Found {len(files)} txt files in {path}, extracting probabilities...')

    away_dataset = []
    home_dataset = []
    for file in files:
        with open(f'{path}/{file}', 'r') as f:
            meta = file.replace(".txt", "").split("_")
            text = f.read()
            matches = re.findall(pattern, text)
            probs_raw = [p.split(",") for p in matches]
            probs = []
            for rates in probs_raw:
                prob = {
                    'min': float(rates[0]),
                    'max': float(rates[1]),
                    'avg': (float(rates[0]) + float(rates[1])) / 2.0
                }
                probs.append(prob)
            print(f'match:{meta[0]}[away]: {mode}[{probs[0][mode]}] min[{probs[0]["min"]}] max[{probs[0]["max"]}]')
            print(f'match:{meta[0]}[home]: {mode}[{probs[1][mode]}] min[{probs[1]["min"]}] max[{probs[1]["max"]}]')
            
            away_dataset.append({
                "match_id"  :meta[0],
                "away_prob"      :probs[0][mode],
                "away_prob_min"  :probs[0]['min'],
                "away_prob_max"  :probs[0]['max'],
                "model"     :model
            })
        
            home_dataset.append({
                "match_id"  :meta[0],
                "home_prob"      :probs[1][mode],
                "home_prob_min"  :probs[1]['min'],
                "home_prob_max"  :probs[1]['max'],
                "model"     :model
            })
            
    write_csv(f'./away_probs.csv', away_dataset, headers=['match_id', 'away_prob', "away_prob_min", "away_prob_max", 'model'])
    write_csv(f'./home_probs.csv', home_dataset, headers=['match_id', 'home_prob', "home_prob_min", "home_prob_max", 'model'])

if __name__ == '__main__':
    main()