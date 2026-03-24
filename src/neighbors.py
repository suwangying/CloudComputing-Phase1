import pandas as pd


def find_leader_vehicle(df):

    df = df.copy()

    df["leader_id"] = None
    df["gap_distance"] = None

    grouped = df.groupby(["Frame_ID", "Lane_ID"])

    results = []

    for (_, _), group in grouped:

        group = group.sort_values("Local_Y")

        vehicles = group.to_dict("records")

        for i in range(len(vehicles)):

            ego = vehicles[i]

            if i < len(vehicles) - 1:

                leader = vehicles[i+1]

                ego["leader_id"] = leader["Vehicle_ID"]
                ego["gap_distance"] = leader["Local_Y"] - ego["Local_Y"]

            else:

                ego["leader_id"] = None
                ego["gap_distance"] = None

            results.append(ego)

    return pd.DataFrame(results)
