import pandas as pd
from typing import *


CHECK_MAX_STEP = "[step >= MAX_STEP]game_ends -> Skip []"

POSITIONS = ["L", "LR", "CL", "C", "CR", "RL", "R"]

ratings = pd.read_csv("./Datasets/ratings/epl_ratings_20152016.csv")
matches = pd.read_csv("./Datasets/matches/epl_matches_20152016.csv")

# the first column is the row number (0-indexed)
# drop the first column since we don't need it
ratings.drop(columns=ratings.columns[0], axis=1, inplace=True)
matches.drop(columns=matches.columns[0], axis=1, inplace=True)

# fill in all empty cells with 0 (e.g., defenders have blank gk_* stats)
ratings.fillna(0, inplace=True)
matches.fillna(0, inplace=True)

# speed up indexing into dataframe
ratings.set_index("sofifa_id", inplace=True)
matches.set_index("match_url", inplace=True)


def main():
    # the output pcsp file should match `12115_away.pcsp`
    match = matches.loc["https://www.premierleague.com/match/12115"]

    away_df_sofifa_ids = get_df_sofifa_ids(match, "away")
    home_df_sofifa_ids = get_df_sofifa_ids(match, "home")

    # pcsp_homeForPos = f"var homeForPos = {get_pos_array_string_from_df_sofifa_ids(home_df_sofifa_ids, row='for')};"
    # pcsp_homeMidPos = f"var homeMidPos = {get_pos_array_string_from_df_sofifa_ids(home_df_sofifa_ids, row='mid')};"
    # pcsp_homeDefPos = f"var homeDefPos = {get_pos_array_string_from_df_sofifa_ids(home_df_sofifa_ids, row='def')};"
    # pcsp_homeKepPos = f"var homeKepPos = {get_pos_array_string_from_df_sofifa_ids(home_df_sofifa_ids, row='kep')};"

    print(away_df_sofifa_ids)

    z = get_KepPass_parameters(away_df_sofifa_ids, home_df_sofifa_ids, our_team="away")
    print(f"z = {z}")
    z = get_KepPass_parameters(away_df_sofifa_ids, home_df_sofifa_ids, our_team="home")
    print(f"z = {z}")

    z = get_KepSave_parameters(away_df_sofifa_ids, home_df_sofifa_ids, our_team="away")
    print(f"z = {z}")
    z = get_KepSave_parameters(away_df_sofifa_ids, home_df_sofifa_ids, our_team="home")
    print(f"z = {z}")
    
    z = get_MidPass_parameters(away_df_sofifa_ids, home_df_sofifa_ids, our_team="away")
    print(f"z = {z}")
    z = get_MidPass_parameters(away_df_sofifa_ids, home_df_sofifa_ids, our_team="home")
    print(f"z = {z}")

    z = get_For_parameters(away_df_sofifa_ids, home_df_sofifa_ids, our_team="away")
    print(f"z = {z}")
    z = get_For_parameters(away_df_sofifa_ids, home_df_sofifa_ids, our_team="home")
    print(f"z = {z}")

    z = get_DefPass_parameters(away_df_sofifa_ids, home_df_sofifa_ids, our_team="away")
    print(f"z = {z}")
    z = get_DefPass_parameters(away_df_sofifa_ids, home_df_sofifa_ids, our_team="home")
    print(f"z = {z}")

    with open("./template.pcsp", "r") as pcsp_template_file:
        lines = pcsp_template_file.readlines()
        output: list[str] = []

        # TODO: remove byte order mark

        output.extend(lines[1 - 1 : 17 - 1])

        # TODO: add awayForPos, etc.

        output.extend(lines[28 - 1 : 35 - 1])

        # TODO: add the various functions that we've created

        output.extend(lines[80 - 1 :])

        with open("./out.pcsp", "w") as output_file:
            output_file.writelines(output)


def get_df_sofifa_ids(match: pd.Series, team: Literal["away", "home"]):
    """
    Returns a variant of

    ```python
                L      LR      CL       C      CR      RL       R
    "for"       0  169214       0  164469       0  197756       0
    "mid"       0  193474       0  189280       0  201519       0
    "def"  219681       0  183129       0  169721       0  198133
    "kep"       0       0       0  164505       0       0       0
    ```

    https://www.premierleague.com/match/12115

    """
    dictionary = {
        "formation": match[f"{team}_formation"],
        "xi_sofifa_ids": match[f"{team}_xi_sofifa_ids"],
    }

    dictionary["formation_numbers"] = convert_formation_to_formation_numbers(
        dictionary["formation"]
    )

    dictionary["formation_numbers"] = combine_midfielder_formation_numbers_if_needed(
        dictionary["formation_numbers"]
    )

    dictionary["xi_sofifa_ids"] = convert_xi_sofifa_ids_string_to_xi_sofifa_ids_number(
        dictionary["xi_sofifa_ids"]
    )

    df_sofifa_ids = pd.DataFrame(
        get_empty_2d_sofifa_id_array(),
        columns=[
            "L",
            "LR",
            "CL",
            "C",
            "CR",
            "RL",
            "R",
        ],
        index=["for", "mid", "def", "kep"],
    )

    # =========================================================================
    # populating df_sofifa_ids
    # =========================================================================

    xi_sofifa_id_index = 0

    # indexing into a dataframe uses `at[row, col]`
    df_sofifa_ids.at["kep", "C"] = dictionary["xi_sofifa_ids"][xi_sofifa_id_index]
    xi_sofifa_id_index += 1

    formation_numbers = dictionary["formation_numbers"]

    #    0      1      2     <-- index
    # [  4  ,   4  ,   3  ]  <-- formation_number
    #  "def", "mid", "for"   <-- row
    for index, formation_number in enumerate(formation_numbers):
        row = get_row(index)

        positions = get_positions_from_formation_number(formation_number)
        for col in positions:
            df_sofifa_ids.at[row, col] = dictionary["xi_sofifa_ids"][xi_sofifa_id_index]
            xi_sofifa_id_index += 1

    return df_sofifa_ids


# =============================================================================
# pcsp parameters
# =============================================================================


def get_KepPass_parameters(
    away_df_sofifa_ids: pd.DataFrame,
    home_df_sofifa_ids: pd.DataFrame,
    our_team: Literal["away", "home"],
):
    """
    Wrapper around `get_GenericKepPass_parameters()` to pass in the correct
    "our_team" and "opponent_team" information
    """
    if our_team == "away":
        return get_GenericKepPass_parameters(away_df_sofifa_ids, home_df_sofifa_ids)

    if our_team == "home":
        return get_GenericKepPass_parameters(home_df_sofifa_ids, away_df_sofifa_ids)

    raise Exception(f"Unknown team={our_team}")


def get_GenericKepPass_parameters(
    our_df_sofifa_ids: pd.DataFrame,
    opponent_df_sofifa_ids: pd.DataFrame,
):
    """
    Returns a variant of

    ```python
    [
        "26, 34, 31, C"
    ]
    ```

    See line 106 of `12115_away.pcsp`
    """
    results: list[str] = []

    our_keeper_sofifa_id = our_df_sofifa_ids.at["kep", "C"]
    opponent_forward_sofifa_ids = opponent_df_sofifa_ids.loc["for"].to_list()

    aggregated_defending = get_aggregated_defending(opponent_forward_sofifa_ids)

    our_keeper_stats = ratings.loc[our_keeper_sofifa_id]
    our_keeper_stats_attacking_short_passing = int(
        our_keeper_stats["attacking_short_passing"]
    )
    our_keeper_stats_skill_long_passing = int(our_keeper_stats["skill_long_passing"])

    position = "C"

    params_string = convert_parameters_to_parameters_string(
        our_keeper_stats_attacking_short_passing,
        our_keeper_stats_skill_long_passing,
        aggregated_defending,
        position,
    )

    results.append(params_string)
    return results


def get_KepSave_parameters(
    away_df_sofifa_ids: pd.DataFrame,
    home_df_sofifa_ids: pd.DataFrame,
    our_team: Literal["away", "home"],
):
    """
    Returns a variant of

    ```python
    [
        "72, C"
    ]
    ```

    See line 117 of `12115_away.pcsp`
    """
    if our_team != "away" and our_team != "home":
        raise Exception(f"Unknown team={our_team}")

    results: list[str] = []
    
    df_sofifa_ids = away_df_sofifa_ids if our_team == "away" else home_df_sofifa_ids
    keeper_sofifa_id = df_sofifa_ids.at["kep", "C"]
    keeper_stats = ratings.loc[keeper_sofifa_id]

    # find the average of these stats
    # - gk_diving
    # - gk_handling
    # - gk_reflexes
    # - gk_speed
    # - gk_positioning

    all_gk_stats = [
        int(keeper_stats["gk_diving"]),
        int(keeper_stats["gk_handling"]),
        int(keeper_stats["gk_reflexes"]),
        int(keeper_stats["gk_speed"]),
        int(keeper_stats["gk_positioning"]),
    ]

    aggregated_gk = get_average(all_gk_stats)
    position = "C"

    params_string = convert_parameters_to_parameters_string(
        aggregated_gk,
        position,
    )

    results.append(params_string)
    return results


# =============================================================================
# utilities
# =============================================================================


def combine_midfielder_formation_numbers_if_needed(
    formation_numbers: list[int],
):
    """
    Converts `[4, 1, 2, 1, 2]` to `[4, 4, 2]` (if needed)
    """
    if len(formation_numbers) < 3:
        raise Exception("Unable to handle soccer formations with less than 3 numbers")

    if len(formation_numbers) == 3:
        # no processing required
        return formation_numbers

    if len(formation_numbers) > 3:
        midfielder_formation_numbers_to_be_combined = formation_numbers[1:-1]

        combined_midfielder_formation_number = sum(
            midfielder_formation_numbers_to_be_combined
        )

        combined_formation_numbers = [
            formation_numbers[0],
            combined_midfielder_formation_number,
            formation_numbers[-1],
        ]

        return combined_formation_numbers

    raise Exception(f"Unknown error occurred :: formation_numbers={formation_numbers}")


def get_empty_2d_sofifa_id_array():
    return [
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
    ]


def get_row(index: int):
    match index:
        case 0:
            return "def"
        case 1:
            return "mid"
        case 2:
            return "for"
        case _:
            # default case
            # should never reach here
            raise Exception(f"Unknown index={index}")


def get_positions_from_formation_number(formation_number: int):
    """
    e.g., if `formation_number` is `4`, return `["R", "CR", "CL", "L"]`
    """
    match formation_number:
        case 1:
            return ["C"]
        case 2:
            return ["CR", "CL"]
        case 3:
            return ["RL", "C", "LR"]
        case 4:
            return ["R", "CR", "CL", "L"]
        case 5:
            return ["R", "CR", "C", "CL", "L"]
        case 6:
            # self-created
            return ["L", "LR", "CL", "CR", "RL", "R"]
        case 7:
            # self-created
            return ["L", "LR", "CL", "C", "CR", "RL", "R"]
        case _:
            # default case
            # should never reach here
            raise Exception(f"Unknown formation_number={formation_number}")


def get_average(lst: list[int]):
    """
    Returns the mean of all values in the list `lst`
    """
    return sum(lst) / len(lst)


def get_aggregated_defending(sofifa_ids: list[int]):
    """
    Input: `[111, 0, 222, 0, 333, 0, 444]`

    Output: `79`
    """

    sofifa_ids = remove_all_zeros(sofifa_ids)

    all_defending_stats = []
    for sofifa_id in sofifa_ids:
        opponent_stats = ratings.loc[sofifa_id]
        all_defending_stats.append(int(opponent_stats["mentality_interceptions"]))
        all_defending_stats.append(int(opponent_stats["defending_marking"]))
        all_defending_stats.append(int(opponent_stats["defending_standing_tackle"]))
        all_defending_stats.append(int(opponent_stats["defending_sliding_tackle"]))

    aggregated_defending = get_average(all_defending_stats)

    number_of_defenders = len(sofifa_ids)
    aggregated_defending = apply_defender_multiplier_bonus(
        aggregated_defending, number_of_defenders
    )

    return aggregated_defending


def apply_defender_multiplier_bonus(stat: int, number_of_defenders: int):
    """
    - 1 defender = 100%
    - 2 defender = 110%
    - 3 defender = 120%
    - ...
    """

    if number_of_defenders == 0:
        raise Exception("Unable to defend with 0 defenders!")

    multiplier = 100
    multiplier += (number_of_defenders - 1) * 10
    multiplier /= 100
    return int(round(stat * multiplier))


def get_aggregated_gk(sofifa_id: int):
    all_gk_stats = []
    gk_stats = ratings.loc[sofifa_id]
    all_gk_stats.append(
        int(gk_stats["gk_diving"])
    )
    all_gk_stats.append(
        int(gk_stats["gk_handling"])
    )
    all_gk_stats.append(
        int(gk_stats["gk_reflexes"])
    )
    all_gk_stats.append(
        int(gk_stats["gk_speed"])
    )
    all_gk_stats.append(
        int(gk_stats["gk_positioning"])
    )
    
    return get_average(all_gk_stats)


def get_attacking_short_passing(sofifa_id: int):
    player_stats = ratings.loc[sofifa_id]
    return int(player_stats["attacking_short_passing"])


def get_skill_long_passing(sofifa_id: int):
    player_stats = ratings.loc[sofifa_id]
    return int(player_stats["skill_long_passing"])


def get_power_long_shots(sofifa_id: int):
    player_stats = ratings.loc[sofifa_id]
    return int(player_stats["power_long_shots"])


def get_aggregated_aggression(sofifa_ids: List[int]):
    all_aggression_stats = []
    for sofifa_id in sofifa_ids:
        if sofifa_id == 0:
            continue
        
        opponent_defender_stats = ratings.loc[sofifa_id]
        all_aggression_stats.append(int(opponent_defender_stats["mentality_aggression"]))
    
    return int(round(get_average(all_aggression_stats)/4, 0))


def convert_formation_to_formation_numbers(formation: str):
    """
    Converts `"4-1-2-1-2"` to `[4, 1, 2, 1, 2]`
    """
    formation_strings = formation.split("-")
    formation_numbers = list(map(lambda x: int(x), formation_strings))
    return formation_numbers


def convert_xi_sofifa_ids_string_to_xi_sofifa_ids_number(xi_sofifa_ids_string: str):
    """
    Converts `"111.0,222.0,333.0"` to `[111, 222, 333]`
    """
    xi_sofifa_ids_strings = xi_sofifa_ids_string.split(",")
    xi_sofifa_ids_numbers = list(map(lambda x: int(float(x)), xi_sofifa_ids_strings))
    return xi_sofifa_ids_numbers


def convert_parameters_to_parameters_string(*args):
    """
    Joins the arguments into a single string separated by a `,`

    e.g.,

    Input arguments: `26`, `34`, `31`, `"C"`

    Output: `"26, 34, 31, C"`
    """
    return ", ".join(map(lambda x: str(x), args))


def remove_all_zeros(lst: list[int]):
    return list(filter(lambda x: x > 0, lst))


# =============================================================================
# unused
# =============================================================================


def get_pos_array_string_from_df_sofifa_ids(
    df_sofifa_ids: pd.DataFrame, row: Literal["kep", "def", "mid", "for"]
):
    """
    Returns a variant of `"[-1, -1, -1, -1, -1, -1, 0, 0, 1, 0, 1, 0, 0, -1, -1, -1, -1, -1, -1]"`
    """
    row_of_sofifa_ids = df_sofifa_ids.loc[row].to_list()

    # "cast" all cells that have a sofifa id to 1
    pos_array_middle = list(map(lambda x: 1 if x > 0 else 0, row_of_sofifa_ids))

    # need to add `-1`s on both sides
    left = [-1] * 6
    right = [-1] * 6
    pos_array = left + pos_array_middle + right

    pos_array_string = str(pos_array)
    return pos_array_string


# =============================================================================
# stefan defender
# =============================================================================


def get_DefPass_parameters(
    away_df_sofifa_ids: pd.DataFrame,
    home_df_sofifa_ids: pd.DataFrame,
    our_team: Literal["away", "home"],
):
    """
    Wrapper around `get_GenericDefPass_parameters()` to pass in the correct
    "our_team" and "opponent_team" information
    """

    if our_team == "away":
        return get_GenericDefPass_parameters(away_df_sofifa_ids, home_df_sofifa_ids)

    if our_team == "home":
        return get_GenericDefPass_parameters(home_df_sofifa_ids, away_df_sofifa_ids)

    raise Exception(f"Unknown team={our_team}")


def get_GenericDefPass_parameters(
    our_df_sofifa_ids: pd.DataFrame,
    opponent_df_sofifa_ids: pd.DataFrame,
):
    """
    Returns a variant of

    ```python
    [
        "73, 71, 71, R",
        "68, 63, 71, CR",
        ...
    ]
    ```

    See line 170 of `12115_away.pcsp`
    """
    results: list[str] = []

    our_defender_sofifa_ids = our_df_sofifa_ids.loc["def"]
    opponent_midfielder_sofifa_ids = opponent_df_sofifa_ids.loc["mid"].to_list()

    aggregated_defending = get_aggregated_defending(opponent_midfielder_sofifa_ids)

    for position in POSITIONS:
        our_defender_sofifa_id = our_defender_sofifa_ids[position]

        if our_defender_sofifa_id == 0:
            continue

        our_defender_stats = ratings.loc[our_defender_sofifa_id]
        our_defender_stats_attacking_short_passing = int(
            our_defender_stats["attacking_short_passing"]
        )
        our_defender_stats_skill_long_passing = int(
            our_defender_stats["skill_long_passing"]
        )

        params_string = convert_parameters_to_parameters_string(
            our_defender_stats_attacking_short_passing,
            our_defender_stats_skill_long_passing,
            aggregated_defending,
            position,
        )

        results.append(params_string)

    return results


# =============================================================================
# jun sheng midfielder
# =============================================================================
def get_MidPass_parameters(
    away_df_sofifa_ids: pd.DataFrame,
    home_df_sofifa_ids: pd.DataFrame,
    our_team: Literal["away", "home"],
):
    if our_team == "away":
        return get_GenericMidPass_parameters(away_df_sofifa_ids, home_df_sofifa_ids)

    if our_team == "home":
        return get_GenericMidPass_parameters(home_df_sofifa_ids, away_df_sofifa_ids)

    raise Exception(f"Unknown team={our_team}")
    

def get_GenericMidPass_parameters(
    our_df_sofifa_ids: pd.DataFrame,
    opponent_df_sofifa_ids: pd.DataFrame,
):
    """
    attacking_short_passing,
	skill_long_passing,
	power_long_shots,
	aggregated_defending,
	position
    output: 79, 76, 74, 71, RL
    """
    our_midfielder_sofifa_id = our_df_sofifa_ids.loc["mid"]
    our_midfielder_sofifa_id = our_midfielder_sofifa_id[our_midfielder_sofifa_id > 0]
    # our_midfielder_sofifa_id = remove_all_zeros(our_midfielder_sofifa_id)

    # our_attacking_short_passing = get_aggregated_gk(our_midfielder_sofifa_id)
    # our_skill_long_passing = get_aggregated_gk(our_midfielder_sofifa_id)
    # our_power_long_shots = get_aggregated_gk(our_midfielder_sofifa_id)
    
    # shared by all position
    opponent_midfielder_sofifa_ids = opponent_df_sofifa_ids.loc["mid"].to_list()
    opponent_midfielder_sofifa_ids = remove_all_zeros(opponent_midfielder_sofifa_ids)
    opponent_aggregated_defending = get_aggregated_defending(opponent_midfielder_sofifa_ids)

    our_midfielder_parameters = []
    for position, sofifa_id in our_midfielder_sofifa_id.items():
        our_midfielder_parameters.append(convert_parameters_to_parameters_string(
            get_attacking_short_passing(sofifa_id),
            get_skill_long_passing(sofifa_id),
            get_power_long_shots(sofifa_id),
            opponent_aggregated_defending,
            position
        ))

    return our_midfielder_parameters

# =============================================================================
# branda forward
# =============================================================================
def get_For_parameters(
    away_df_sofifa_ids: pd.DataFrame,
    home_df_sofifa_ids: pd.DataFrame,
    our_team: Literal["away", "home"],
):
    """ Wrapper around `get_GenericFor_parameters()` to pass in the correct
    "our_team" and "opponent_team" information
    """
    if our_team == "away":
        return get_GenericFor_parameters(away_df_sofifa_ids, home_df_sofifa_ids)
    
    if our_team == "home":
        return get_GenericFor_parameters(home_df_sofifa_ids, away_df_sofifa_ids)
    
    raise Exception(f"Unknown team={our_team}")

def get_GenericFor_parameters(
    our_df_sofifa_ids: pd.DataFrame,
    opponent_df_sofifa_ids: pd.DataFrame,
):
    """
    Returns an array of a variant of `"77, 75, 74, 77, 92, 18, 73, 71, RL"`
    
    See line 287 of `12115_away.pcsp`
    """
    
    positions = ["L", "LR", "CL", "C", "CR", "RL", "R"]
    
    opponent_keeper_sofifa_id = opponent_df_sofifa_ids.at["kep", "C"]
    opponent_aggregated_gk = get_aggregated_gk(opponent_keeper_sofifa_id)
    
    opponent_defender_sofifa_ids = opponent_df_sofifa_ids.loc["def"].to_list()
    opponent_defender_sofifa_ids = remove_all_zeros(opponent_defender_sofifa_ids)
    
    opponent_aggregated_defending = get_aggregated_defending(opponent_defender_sofifa_ids)
    opponent_aggregated_aggression = get_aggregated_aggression(opponent_defender_sofifa_ids)
    
    our_forward_stats_combined = []
    
    for i in range(7):
        our_forward_sofifa_id = our_df_sofifa_ids.at["for", positions[i]]
        if (our_forward_sofifa_id != 0):
            our_forward_stats = ratings.loc[our_forward_sofifa_id]
            our_forward_atk_fnsh = int(our_forward_stats["attacking_finishing"])
            our_forward_pwr_ls = int(our_forward_stats["power_long_shots"])
            our_forward_atk_volleys = int(our_forward_stats["attacking_volleys"])
            our_forward_atk_head = int(our_forward_stats["attacking_heading_accuracy"])
            our_forward_ment_pen = int(our_forward_stats["mentality_penalties"])
            our_forward_fk_accuracy = int(our_forward_stats["skill_fk_accuracy"])
            our_forward_aggregated_penalty_kick = int(round((our_forward_ment_pen + our_forward_fk_accuracy)/2, 0))
            
            params_string = convert_parameters_to_parameters_string(
                our_forward_atk_fnsh,
                our_forward_pwr_ls,
                our_forward_atk_volleys,
                our_forward_atk_head,
                opponent_aggregated_defending,
                opponent_aggregated_aggression,
                our_forward_aggregated_penalty_kick,
                opponent_aggregated_gk,
                positions[i],
            )
            
            our_forward_stats_combined.append(params_string)
    
    return our_forward_stats_combined

if __name__ == "__main__":
    main()



        
