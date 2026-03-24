import pandas as pd


def load_and_clean_data(file_path):

    df = pd.read_csv(file_path, low_memory=False)

    # Convert important columns
    numeric_cols = [
        "Vehicle_ID",
        "Frame_ID",
        "Global_Time",
        "Local_X",
        "Local_Y",
        "v_Vel",
        "v_Acc",
        "Lane_ID"
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Remove rows with missing key values
    df = df.dropna(subset=["Vehicle_ID", "Frame_ID",
                   "Global_Time", "Local_Y", "v_Vel"])

    # Sort so trajectories are ordered correctly
    df = df.sort_values(["Vehicle_ID", "Frame_ID"])

    # Convert Global_Time to seconds
    df["time_s"] = df["Global_Time"] / 1000.0

    return df
