import os
import re

path = "./outputs"
pattern = r"(?<=\[).*(?=\])"

def read_directory(path, extension='.txt'):
    return [f for f in os.listdir(path) if f.endswith(extension)]

def main():
    files = read_directory(path)
    print(f'Found {len(files)} txt files in {path}, extracting probabilities...')

    for file in files:
        with open(f'{path}/{file}', 'r') as file:
            text = file.read()
            matches = re.findall(pattern, text)
            probs = [p.split(",") for p in matches]
            print(probs)


if __name__ == '__main__':
    main()