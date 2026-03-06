import os
import pandas as pd

FRAMES_PER_SECOND = 10
WINDOW_SECONDS = 5
WINDOW_FRAMES = FRAMES_PER_SECOND * WINDOW_SECONDS   # 50
HALF_WINDOW = WINDOW_FRAMES // 2                     # 25

SURROUNDING_DISTANCE_FT = 100.0


def get_frame_window(mid_frame: int):
    start_frame = mid_frame - HALF_WINDOW
    end_frame = mid_frame + HALF_WINDOW - 1
    return start_frame, end_frame


def extract_scenario_window(df: pd.DataFrame, vehicle_id: int, mid_frame: int, scenario_label: str) -> pd.DataFrame:
    """
    Extract a 5-second scenario window containing:
    - ego vehicle
    - surrounding vehicles within distance threshold
    - scenario label
    """

    start_frame, end_frame = get_frame_window(mid_frame)

    # ego trajectory in the 5-second window
    ego_window = df[
        (df["Vehicle_ID"] == vehicle_id) &
        (df["Frame_ID"] >= start_frame) &
        (df["Frame_ID"] <= end_frame)
    ].copy()

    if ego_window.empty:
        return pd.DataFrame()

    # get ego position by frame
    ego_positions = ego_window[["Frame_ID", "Local_Y"]].rename(columns={"Local_Y": "ego_Local_Y"})

    # all vehicles in the same frame window
    frame_window_df = df[
        (df["Frame_ID"] >= start_frame) &
        (df["Frame_ID"] <= end_frame)
    ].copy()

    # join ego position onto all rows for matching frames
    merged = frame_window_df.merge(ego_positions, on="Frame_ID", how="inner")

    # keep ego + nearby surrounding vehicles
    scenario_window = merged[
        (merged["Vehicle_ID"] == vehicle_id) |
        ((merged["Local_Y"] - merged["ego_Local_Y"]).abs() <= SURROUNDING_DISTANCE_FT)
    ].copy()

    # mark ego vehicle
    scenario_window["is_ego"] = scenario_window["Vehicle_ID"] == vehicle_id

    # add scenario label
    scenario_window["scenario_label"] = scenario_label

    # optional: distance from ego at each frame
    scenario_window["distance_from_ego_y"] = scenario_window["Local_Y"] - scenario_window["ego_Local_Y"]

    # clean ordering
    scenario_window = scenario_window.sort_values(["Frame_ID", "Vehicle_ID"]).reset_index(drop=True)

    return scenario_window


def save_event_windows(df: pd.DataFrame, events: dict, output_dir="outputs_windows", max_per_type=100):
    """
    Save scenario windows to disk.
    Each file now contains:
    - ego vehicle
    - surrounding vehicles
    - scenario label
    """
    os.makedirs(output_dir, exist_ok=True)

    summary = []

    for scenario, event_list in events.items():
        scenario_dir = os.path.join(output_dir, scenario)
        os.makedirs(scenario_dir, exist_ok=True)

        for event in event_list[:max_per_type]:
            vehicle_id = int(event["vehicle_id"])
            mid_frame = int(event["mid_frame"])

            start_frame, end_frame = get_frame_window(mid_frame)

            window_df = extract_scenario_window(df, vehicle_id, mid_frame, scenario)

            if window_df.empty:
                continue

            filename = f"{scenario}_veh{vehicle_id}_mid{mid_frame}.csv"
            filepath = os.path.join(scenario_dir, filename)

            window_df.to_csv(filepath, index=False)

            summary.append({
                "scenario": scenario,
                "vehicle_id": vehicle_id,
                "mid_frame": mid_frame,
                "start_frame": start_frame,
                "end_frame": end_frame,
                "rows_saved": len(window_df),
                "unique_vehicles": window_df["Vehicle_ID"].nunique(),
                "file": filepath
            })

    summary_df = pd.DataFrame(summary)
    summary_df.to_csv(os.path.join(output_dir, "windows_summary.csv"), index=False)

    return summary_df
