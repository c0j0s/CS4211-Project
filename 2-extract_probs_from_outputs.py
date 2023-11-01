import os
import re
import csv

path = "./outputs"
pattern = r"(?<=\[).*(?=\])"
mode = 'avg'
output = "./data"

def read_directory(path, extension='.txt'):
    return [f for f in os.listdir(path) if f.endswith(extension)]

def write_csv(file_path, dataset):
    with open(file_path, 'w', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=['match_id', 'prob', "prob_min", "prob_max", 'model'])
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
            print(f'probs of match:{meta[0]} for team {meta[1]} model[{meta[2:]}]:')
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
            print(f'{meta[1]} -> {probs}')
            if meta[1] == "home":
                home_dataset.append({
                    "match_id"  :meta[0],
                    "prob"      :probs[0][mode],
                    "prob_min"      :probs[0]['min'],
                    "prob_max"      :probs[0]['max'],
                    "model"     :"-".join(meta[2:])
                })
            else:
                away_dataset.append({
                    "match_id"  :meta[0],
                    "prob"      :probs[0][mode],
                    "prob_min"      :probs[0]['min'],
                    "prob_max"      :probs[0]['max'],
                    "model"     :"-".join(meta[2:])
                })
            
    write_csv(f'{output}/away_probs.csv', away_dataset)
    write_csv(f'{output}/home_probs.csv', home_dataset)

if __name__ == '__main__':
    main()