import os
import pandas as pd

FRAMES_PER_SECOND = 10
WINDOW_SECONDS = 5
WINDOW_FRAMES = FRAMES_PER_SECOND * WINDOW_SECONDS  # 50
HALF_WINDOW = WINDOW_FRAMES // 2  # 25


def extract_window_for_vehicle(df: pd.DataFrame, vehicle_id: int, mid_frame: int) -> pd.DataFrame:
    """
    Returns a 5-second (50-frame) window for ONE vehicle around mid_frame.
    Window is [mid_frame-25, mid_frame+24] (50 frames total).
    """
    start_f = mid_frame - HALF_WINDOW
    end_f = mid_frame + HALF_WINDOW - 1  # inclusive

    w = df[
        (df["Vehicle_ID"] == vehicle_id) &
        (df["Frame_ID"] >= start_f) &
        (df["Frame_ID"] <= end_f)
    ].copy()

    return w


def save_event_windows(df: pd.DataFrame, events: dict, out_dir: str = "outputs_windows", max_per_type: int = 200):
    """
    Saves windows to disk by scenario type.
    events is from extract_events(df) in scenarios.py.
    max_per_type limits output size for testing.
    """
    os.makedirs(out_dir, exist_ok=True)

    summary_rows = []

    for scenario, ev_list in events.items():
        scenario_dir = os.path.join(out_dir, scenario)
        os.makedirs(scenario_dir, exist_ok=True)

        # limit for safety/testing
        for i, e in enumerate(ev_list[:max_per_type]):
            vid = int(e["vehicle_id"])
            mid = int(e["mid_frame"])
            start_f = mid - HALF_WINDOW
            end_f = mid + HALF_WINDOW - 1

            w = extract_window_for_vehicle(df, vid, mid)

            # We expect up to 50 rows. Sometimes near edges it might be less.
            filename = f"{scenario}_veh{vid}_mid{mid}_f{start_f}-{end_f}.csv"
            path = os.path.join(scenario_dir, filename)
            w.to_csv(path, index=False)

            summary_rows.append({
                "scenario": scenario,
                "vehicle_id": vid,
                "mid_frame": mid,
                "start_frame": start_f,
                "end_frame": end_f,
                "rows_saved": len(w),
                "file": path
            })

    summary_df = pd.DataFrame(summary_rows)
    summary_df.to_csv(os.path.join(
        out_dir, "windows_summary.csv"), index=False)
    return summary_df
