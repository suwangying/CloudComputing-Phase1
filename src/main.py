import pandas as pd

# Load your CSV file
file_path = r"C:\Users\suwan\Downloads\Next_Generation_Simulation_(NGSIM)_Vehicle_Trajectories_and_Supporting_Data_20260301.csv"

df = pd.read_csv(file_path, dtype=str, low_memory=False)

print("Dataset loaded successfully.")
print(df.head())

# Convert important columns to numeric
df["Global_Time"] = pd.to_numeric(df["Global_Time"], errors="coerce")
df["v_Vel"] = pd.to_numeric(df["v_Vel"], errors="coerce")
df["Lane_ID"] = pd.to_numeric(df["Lane_ID"], errors="coerce")
df["Vehicle_ID"] = pd.to_numeric(df["Vehicle_ID"], errors="coerce")

print("Unique Lane_ID values:")
print(sorted(df["Lane_ID"].dropna().unique()))

print("\nVelocity statistics:")
print(df["v_Vel"].describe())

# Get vehicle with most frames
counts = df["Vehicle_ID"].value_counts()
vehicle_id = counts.index[0]

print("Selected vehicle ID:", vehicle_id)
print("Number of rows for this vehicle:", counts.iloc[0])

vehicle_data = df[df["Vehicle_ID"] == vehicle_id]
vehicle_data = vehicle_data.sort_values("Global_Time")

time_diffs = vehicle_data["Global_Time"].diff()

print("\nTime difference statistics (milliseconds):")
print(time_diffs.describe())

counts = df["Vehicle_ID"].value_counts()
print(counts.head(10))
