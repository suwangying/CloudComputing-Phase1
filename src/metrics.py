import numpy as np
import pandas as pd


def add_safety_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds:
      - leader_vel
      - rel_vel (ego - leader)
      - time_headway (s)
      - ttc (s)  (infinity if not closing in)
    Assumes df already has: Vehicle_ID, Frame_ID, Lane_ID, v_Vel, leader_id, gap_distance
    """
    out = df.copy()

    # Create a lookup table for leader speed at the same frame
    leader_lookup = out[["Vehicle_ID", "Frame_ID", "v_Vel"]].rename(
        columns={"Vehicle_ID": "leader_id", "v_Vel": "leader_vel"}
    )

    # Merge leader velocity onto each ego record
    out = out.merge(leader_lookup, on=["leader_id", "Frame_ID"], how="left")

    # Relative velocity: ego closing speed (positive means ego is faster)
    out["rel_vel"] = out["v_Vel"] - out["leader_vel"]

    # Time headway: gap / ego speed (avoid divide-by-zero)
    out["time_headway_s"] = np.where(
        out["v_Vel"] > 0,
        out["gap_distance"] / out["v_Vel"],
        np.nan
    )

    # TTC: gap / rel_vel only if rel_vel > 0 and gap exists
    out["ttc_s"] = np.where(
        (out["rel_vel"] > 0) & (out["gap_distance"].notna()),
        out["gap_distance"] / out["rel_vel"],
        np.inf
    )

    return out
