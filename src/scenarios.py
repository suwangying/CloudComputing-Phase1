import numpy as np
import pandas as pd

# -----------------------------
# Thresholds (tune later)
# -----------------------------
TTC_NEAR_COLLISION_S = 1.5        # near-collision if TTC < 1.5s
# sudden braking if acceleration <= -3 (ft/s^2 in NGSIM)
BRAKE_ACCEL_THRESH = -3.0
BRAKE_MIN_FRAMES = 3              # require 3 consecutive frames (0.3s at 10Hz)

CAR_FOLLOW_HEADWAY_MIN_S = 0.5    # car-following headway range
CAR_FOLLOW_HEADWAY_MAX_S = 2.0
# require 2 seconds sustained (20 frames at 10Hz)
CAR_FOLLOW_MIN_FRAMES = 20

LANE_CHANGE_STABLE_FRAMES = 3     # require lane stays in new lane for a few frames


# -----------------------------
# Per-row detectors (boolean masks)
# -----------------------------
def detect_near_collision(df: pd.DataFrame) -> pd.Series:
    """Near-collision: leader exists + ego closing in + TTC below threshold."""
    return (
        df["leader_id"].notna()
        & np.isfinite(df["ttc_s"])
        & (df["ttc_s"] < TTC_NEAR_COLLISION_S)
        & (df["rel_vel"] > 0)
        & df["gap_distance"].notna()
        & (df["gap_distance"] > 0)
    )


def detect_sudden_braking(df: pd.DataFrame) -> pd.Series:
    """Sudden braking: strong negative acceleration."""
    if "v_Acc" not in df.columns:
        return pd.Series(False, index=df.index)
    return df["v_Acc"].notna() & (df["v_Acc"] <= BRAKE_ACCEL_THRESH)


def detect_lane_change_point(df: pd.DataFrame) -> pd.Series:
    """Lane change point: Lane_ID changes from previous frame (per vehicle)."""
    prev_lane = df.groupby("Vehicle_ID")["Lane_ID"].shift(1)
    return prev_lane.notna() & (df["Lane_ID"] != prev_lane)


def detect_car_following_candidate(df: pd.DataFrame) -> pd.Series:
    """Car-following candidate: leader exists + headway within range."""
    return (
        df["leader_id"].notna()
        & np.isfinite(df["time_headway_s"])
        & (df["time_headway_s"] >= CAR_FOLLOW_HEADWAY_MIN_S)
        & (df["time_headway_s"] <= CAR_FOLLOW_HEADWAY_MAX_S)
    )


# -----------------------------
# Attach flags to dataframe
# -----------------------------
def add_scenario_flags(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds columns:
      - is_near_collision
      - is_sudden_braking
      - is_lane_change_point
      - is_car_following_candidate
    """
    out = df.copy()
    out = out.sort_values(["Vehicle_ID", "Frame_ID"]).reset_index(drop=True)

    out["is_near_collision"] = detect_near_collision(out)
    out["is_sudden_braking"] = detect_sudden_braking(out)
    out["is_lane_change_point"] = detect_lane_change_point(out)
    out["is_car_following_candidate"] = detect_car_following_candidate(out)

    return out


# -----------------------------
# Helper: find consecutive True runs
# -----------------------------
def _find_true_runs(mask: pd.Series, min_len: int):
    """
    Returns list of (start_idx, end_idx) inclusive for consecutive True runs
    with length >= min_len.
    """
    runs = []
    start = None
    vals = mask.values

    for i, v in enumerate(vals):
        if v and start is None:
            start = i
        elif (not v) and start is not None:
            if i - start >= min_len:
                runs.append((start, i - 1))
            start = None

    if start is not None and len(vals) - start >= min_len:
        runs.append((start, len(vals) - 1))

    return runs


# -----------------------------
# Extract event list per scenario
# -----------------------------
def extract_events(df: pd.DataFrame) -> dict:
    """
    Produces event lists for each scenario type.
    Each event: {vehicle_id, start_frame, end_frame, mid_frame}
    """
    df = df.sort_values(["Vehicle_ID", "Frame_ID"]).reset_index(drop=True)

    events = {
        "near_collision": [],
        "sudden_braking": [],
        "lane_change": [],
        "car_following": [],
    }

    for vid, g in df.groupby("Vehicle_ID"):
        g = g.reset_index(drop=True)

        # Near collision: allow short bursts but require >= 2 frames to reduce noise
        for a, b in _find_true_runs(g["is_near_collision"], min_len=2):
            start_f = int(g.loc[a, "Frame_ID"])
            end_f = int(g.loc[b, "Frame_ID"])
            mid_f = int(g.loc[(a + b) // 2, "Frame_ID"])
            events["near_collision"].append({"vehicle_id": int(
                vid), "start_frame": start_f, "end_frame": end_f, "mid_frame": mid_f})

        # Sudden braking: require BRAKE_MIN_FRAMES consecutive frames
        for a, b in _find_true_runs(g["is_sudden_braking"], min_len=BRAKE_MIN_FRAMES):
            start_f = int(g.loc[a, "Frame_ID"])
            end_f = int(g.loc[b, "Frame_ID"])
            mid_f = int(g.loc[(a + b) // 2, "Frame_ID"])
            events["sudden_braking"].append({"vehicle_id": int(
                vid), "start_frame": start_f, "end_frame": end_f, "mid_frame": mid_f})

        # Lane change: detect the frame where lane changes, then require stability
        change_points = g.index[g["is_lane_change_point"]].tolist()
        for idx in change_points:
            # Make sure we have enough frames ahead to check stability
            if idx + LANE_CHANGE_STABLE_FRAMES < len(g):
                new_lane = g.loc[idx, "Lane_ID"]
                stable = (
                    g.loc[idx: idx + LANE_CHANGE_STABLE_FRAMES, "Lane_ID"] == new_lane).all()
                if stable:
                    f = int(g.loc[idx, "Frame_ID"])
                    events["lane_change"].append(
                        {"vehicle_id": int(vid), "start_frame": f, "end_frame": f, "mid_frame": f})

        # Car-following: require sustained candidate frames
        for a, b in _find_true_runs(g["is_car_following_candidate"], min_len=CAR_FOLLOW_MIN_FRAMES):
            start_f = int(g.loc[a, "Frame_ID"])
            end_f = int(g.loc[b, "Frame_ID"])
            mid_f = int(g.loc[(a + b) // 2, "Frame_ID"])
            events["car_following"].append({"vehicle_id": int(
                vid), "start_frame": start_f, "end_frame": end_f, "mid_frame": mid_f})

    return events
