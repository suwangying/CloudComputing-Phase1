from preprocess import load_and_clean_data
from neighbors import find_leader_vehicle
from metrics import add_safety_metrics
from scenarios import add_scenario_flags, extract_events
from windowing import save_event_windows


file_path = r"C:\Users\suwan\Downloads\us101_1118847220800_1118847821000.csv"

df = load_and_clean_data(file_path)
df = find_leader_vehicle(df)
df = add_safety_metrics(df)
df = add_scenario_flags(df)
events = extract_events(df)
for k, v in events.items():
    print(k, len(v))

summary_df = save_event_windows(
    df,
    events,
    output_dir="outputs_windows",
    max_per_type=100
)


print("Leader detection completed")
print(df[["Vehicle_ID", "Frame_ID", "Lane_ID", "leader_id", "gap_distance"]].head())
print("Clean dataset size:", len(df))
print("Metrics added.")
print(df[["Vehicle_ID", "Frame_ID", "Lane_ID", "leader_id", "gap_distance",
      "v_Vel", "leader_vel", "rel_vel", "time_headway_s", "ttc_s"]].head(10))
print(df.head())
print("\nExamples:")
print("near_collision:", events["near_collision"][:3])
print("sudden_braking:", events["sudden_braking"][:3])
print("lane_change:", events["lane_change"][:3])
print("car_following:", events["car_following"][:3])
print("\nSaved window summary:")
print(summary_df.head())
