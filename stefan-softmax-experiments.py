import os
import re
import math
import csv

regex_pattern_probabilities = r"(?<=\[).*(?=\])"


def get_season_from_match_id(match_id: str):
    match_id_number = int(match_id)

    if 12115 <= match_id_number and match_id_number <= 12494:
        return 1516
    if 14040 <= match_id_number and match_id_number <= 14419:
        return 1617
    if 22342 <= match_id_number and match_id_number <= 22721:
        return 1718
    if 38308 <= match_id_number and match_id_number <= 38687:
        return 1819
    if 46605 <= match_id_number and match_id_number <= 46984:
        return 1920
    if 58896 <= match_id_number and match_id_number <= 59275:
        return 2021
    raise Exception(f"match_id_number={match_id_number} is from an unknown season")


def get_home_prob_softmax(away_team_wins_prob: float, home_team_wins_prob: float):
    e_away = math.exp(away_team_wins_prob)
    e_home = math.exp(home_team_wins_prob)
    total = e_away + e_home
    return e_home / total


def get_match_url(match_id: int):
    return f"https://www.premierleague.com/match/{match_id}"


def get_average_of_two_floats(f1: float, f2: float):
    return (f1 + f2) / 2.0


def main():
    mapping_season_to_csv_rows: dict[int, list[dict[str, str]]] = {
        1516: [],
        1617: [],
        1718: [],
        1819: [],
        1920: [],
        2021: [],
    }

    PAT_verification_result_filenames = os.listdir("./outputs")

    for filename in PAT_verification_result_filenames:
        match_id = filename.replace(".txt", "")

        with open(f"./outputs/{filename}") as f:
            raw_text = f.read()
            regex_matches = re.findall(regex_pattern_probabilities, raw_text)
            raw_probabilities = [s.split(", ") for s in regex_matches]

            number_of_probability_values = len(raw_probabilities)

            if number_of_probability_values != 3:
                raise Exception(
                    f"Expected 3 probability values but only found {number_of_probability_values}"
                )

            away_team_wins_min_prob = float(raw_probabilities[0][0])
            away_team_wins_max_prob = float(raw_probabilities[0][1])
            home_team_wins_min_prob = float(raw_probabilities[1][0])
            home_team_wins_max_prob = float(raw_probabilities[1][1])
            game_ends_in_draw_min_prob = float(raw_probabilities[2][0])
            game_ends_in_draw_max_prob = float(raw_probabilities[2][1])

            away_team_wins_average_prob = get_average_of_two_floats(
                away_team_wins_min_prob, away_team_wins_max_prob
            )
            home_team_wins_average_prob = get_average_of_two_floats(
                home_team_wins_min_prob, home_team_wins_max_prob
            )
            game_ends_in_draw_average_prob = get_average_of_two_floats(
                game_ends_in_draw_min_prob, game_ends_in_draw_max_prob
            )

            home_prob_softmax = get_home_prob_softmax(
                away_team_wins_average_prob, 
                home_team_wins_average_prob,
            )

            csv_row = {
                "match_url": get_match_url(match_id),
                "home_prob_softmax": str(home_prob_softmax),
            }

            season = get_season_from_match_id(match_id)
            mapping_season_to_csv_rows[season].append(csv_row)

    for season, csv_rows in mapping_season_to_csv_rows.items():
        with open(
            f"./betting_simulation/stefan-softmax-experiments/{season}.csv",
            "w",
            newline="",
        ) as csv_file:
            writer = csv.DictWriter(
                csv_file,
                fieldnames=csv_rows[0].keys(),
            )
            writer.writeheader()
            writer.writerows(csv_rows)


if __name__ == "__main__":
    main()

# =====
# calculate softmax using home_prob, away_prob
# =====
# season 1516 net profit (original, new, difference): ($-3020.0, $-5613.0, $-2593.0)
# season 1617 net profit (original, new, difference): ($-373.0, $1100.0, $1473.0)
# season 1718 net profit (original, new, difference): ($-2135.0, $-5147.0, $-3012.0)
# season 1819 net profit (original, new, difference): ($920.0, $3703.0, $2783.0)
# season 1920 net profit (original, new, difference): ($1199.0, $-2119.0, $-3318.0)
# season 2021 net profit (original, new, difference): ($1182.0, $1669.0, $487.0)
# Original total: -2227.0
# New total: -6407.0
# Difference: -4180.0


# =====
# flip softmax calculations
# =====
# season 1516 net profit (original, new, difference): ($-3020.0, $5230.0, $8250.0)
# season 1617 net profit (original, new, difference): ($-373.0, $-6910.0, $-6537.0)
# season 1718 net profit (original, new, difference): ($-2135.0, $1285.0, $3420.0)
# season 1819 net profit (original, new, difference): ($920.0, $-2394.0, $-3314.0)
# season 1920 net profit (original, new, difference): ($1199.0, $2449.0, $1250.0)
# season 2021 net profit (original, new, difference): ($1182.0, $-467.0, $-1649.0)
# Original total: -2227.0
# New total: -807.0
# Difference: 1420.0


# =====
# write the value of home_prob directly to csv file
# =====
# season 1516 net profit (original, new, difference): ($-3020.0, $235.0, $3255.0)
# season 1617 net profit (original, new, difference): ($-373.0, $-6759.0, $-6386.0)
# season 1718 net profit (original, new, difference): ($-2135.0, $-5742.0, $-3607.0)
# season 1819 net profit (original, new, difference): ($920.0, $-427.0, $-1347.0)
# season 1920 net profit (original, new, difference): ($1199.0, $-1638.0, $-2837.0)
# season 2021 net profit (original, new, difference): ($1182.0, $3341.0, $2159.0)
# Original total: -2227.0
# New total: -10990.0
# Difference: -8763.0
