# scripts/detect_conflicts.py
import pandas as pd
import json
import os
import sys

# Define base data folder
base_path = r"C:\Users\ASUS\OneDrive\Pictures\IntelliBlock\data"

# Input and output files
timetable_file = os.path.join(base_path, "timetable_sample.csv")   # switch to timetable.csv for full
topology_file = os.path.join(base_path, "section_topology_sample.json")
conflict_log_file = os.path.join(base_path, "conflicts.log")

def time_to_minutes(t):
    """Convert HH:MM:SS to minutes since midnight (ignores missing/NaN)"""
    try:
        if pd.isna(t) or str(t).strip() == "":
            return None
        h, m, s = map(int, str(t).split(":"))
        return h * 60 + m + s / 60
    except Exception:
        return None

def detect_platform_conflicts(timetable):
    """Detect conflicts at the same station/platform"""
    conflicts = []
    for station_id, group in timetable.groupby("station_id"):
        trains = group.to_dict("records")
        for i in range(len(trains)):
            for j in range(i + 1, len(trains)):
                t1, t2 = trains[i], trains[j]
                if (t1["arr_mins"] is not None and t2["arr_mins"] is not None and
                    t1["dep_mins"] is not None and t2["dep_mins"] is not None):

                    overlap = not (t1["dep_mins"] <= t2["arr_mins"] or
                                   t2["dep_mins"] <= t1["arr_mins"])
                    if overlap:
                        conflicts.append(
                            f"⚠ Platform conflict at {station_id}: "
                            f"Train {t1['train_id']} and Train {t2['train_id']} "
                            f"({t1['arr_time']}-{t1['dep_time']} vs {t2['arr_time']}-{t2['dep_time']})"
                        )
    return conflicts

def detect_block_conflicts(timetable):
    """Detect conflicts in the same block (using block_seq column)"""
    conflicts = []
    for block_id, group in timetable.groupby("block_seq"):
        trains = group.to_dict("records")
        for i in range(len(trains)):
            for j in range(i + 1, len(trains)):
                t1, t2 = trains[i], trains[j]
                if (t1["arr_mins"] is not None and t2["arr_mins"] is not None and
                    t1["dep_mins"] is not None and t2["dep_mins"] is not None):

                    overlap = not (t1["dep_mins"] <= t2["arr_mins"] or
                                   t2["dep_mins"] <= t1["arr_mins"])
                    if overlap:
                        conflicts.append(
                            f"⚠ Block conflict in {block_id}: "
                            f"Train {t1['train_id']} and Train {t2['train_id']} "
                            f"({t1['arr_time']}-{t1['dep_time']} vs {t2['arr_time']}-{t2['dep_time']})"
                        )
    return conflicts

def main():
    try:
        # ---- Load timetable ----
        if not os.path.exists(timetable_file):
            print(f"❌ Error: File not found -> {timetable_file}")
            sys.exit(1)

        timetable = pd.read_csv(timetable_file)
        if timetable.empty:
            print("❌ Error: timetable.csv is empty")
            sys.exit(1)

        # Convert times
        timetable["arr_mins"] = timetable["arr_time"].apply(time_to_minutes)
        timetable["dep_mins"] = timetable["dep_time"].apply(time_to_minutes)

        # ---- Load topology (optional, not used yet) ----
        if not os.path.exists(topology_file):
            print(f"❌ Error: File not found -> {topology_file}")
            sys.exit(1)

        with open(topology_file, "r") as f:
            topology = json.load(f)

        # ---- Detect conflicts ----
        platform_conflicts = detect_platform_conflicts(timetable)
        block_conflicts = detect_block_conflicts(timetable)
        all_conflicts = platform_conflicts + block_conflicts

        # ---- Save results ----
        with open(conflict_log_file, "w") as f:
            if all_conflicts:
                f.write("\n".join(all_conflicts))
                print(f"✅ Found {len(all_conflicts)} conflicts "
                      f"({len(platform_conflicts)} platform, {len(block_conflicts)} block).")
                print(f"Saved to {conflict_log_file}")
            else:
                f.write("No conflicts detected.\n")
                print("✅ No conflicts detected.")

    except Exception as e:
        print("❌ Unexpected error:", str(e))
        sys.exit(1)

if __name__ == "__main__":
    main()
# SIH_DATA_
