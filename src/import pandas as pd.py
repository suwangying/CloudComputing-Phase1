import pandas as pd

df = pd.read_csv("outputs_windows/lane_change/lane_change_veh954_mid2430.csv")

print("Total rows:", len(df))
print("Unique frames:", df["Frame_ID"].nunique())
print("Frame range:", df["Frame_ID"].min(), "to", df["Frame_ID"].max())
