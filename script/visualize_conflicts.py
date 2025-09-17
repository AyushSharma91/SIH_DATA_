# scripts/visualize_conflicts.py
import pandas as pd
import matplotlib.pyplot as plt
import os
import sys
import json

# Define base path
base_path = r"C:\Users\ASUS\OneDrive\Pictures\IntelliBlock\data"

# Input files
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

def main():
    try:
        # ---- Load timetable ----
        if not os.path.exists(timetable_file):
            print(f"❌ Error: File not found -> {timetable_file}")
            sys.exit(1)

        timetable = pd.read_csv(timetable_file, dtype={"train_id": str, "station_id": str})
        if timetable.empty:
            print("❌ Error: timetable.csv is empty")
            sys.exit(1)

        # Convert times
        timetable["arr_mins"] = timetable["arr_time"].apply(time_to_minutes)
        timetable["dep_mins"] = timetable["dep_time"].apply(time_to_minutes)

        # ---- Load topology for station names ----
        if not os.path.exists(topology_file):
            print(f"❌ Error: File not found -> {topology_file}")
            sys.exit(1)

        with open(topology_file, "r") as f:
            topology = json.load(f)

        station_names = {s["id"]: s.get("name", s["id"]) for s in topology.get("stations", [])}

        # ---- Prepare data for plotting ----
        N = 10  # limit trains for clarity
        sample_trains = timetable["train_id"].unique()[:N]
        plot_data = timetable[timetable["train_id"].isin(sample_trains)].copy()

        # Assign station indices (y-axis) safely
        station_index = {sid: i for i, sid in enumerate(plot_data["station_id"].unique())}
        plot_data.loc[:, "station_idx"] = plot_data["station_id"].map(station_index)

        # ---- Plot stringline chart ----
        plt.figure(figsize=(12, 6))

        for train_id, group in plot_data.groupby("train_id"):
            plt.plot(group["arr_mins"], group["station_idx"],
                     marker="o", label=f"Train {train_id}")

        plt.xlabel("Time (minutes since midnight)")
        plt.ylabel("Stations")
        plt.title("Train Movements with Conflicts (Stringline Chart)")
        plt.legend(loc="upper right", fontsize="small", ncol=2)
        plt.grid(True, linestyle="--", alpha=0.6)

        # Replace y-ticks with station names
        yticks = list(station_index.values())
        ylabels = [station_names.get(sid, sid) for sid in station_index.keys()]
        plt.yticks(yticks, ylabels)

        # ---- Highlight conflicts ----
        conflict_points = []
        if os.path.exists(conflict_log_file):
            with open(conflict_log_file, "r") as f:
                conflicts = [line.strip() for line in f.readlines() if line.strip()]

            if conflicts and "No conflicts" not in conflicts[0]:
                for line in conflicts:
                    # Example: "⚠ Platform conflict at XYZ: Train 101 and Train K123 ..."
                    parts = line.split("Train")
                    if len(parts) >= 3:
                        try:
                            t1 = parts[1].split()[0].strip()
                            t2 = parts[2].split()[0].strip()
                            conflict_points.append((t1, t2))
                        except Exception:
                            continue

        # Plot red markers at overlapping points
        for (t1, t2) in conflict_points:
            g1 = plot_data[plot_data["train_id"] == t1]
            g2 = plot_data[plot_data["train_id"] == t2]
            if not g1.empty and not g2.empty:
                x = (g1["arr_mins"].iloc[0] + g2["arr_mins"].iloc[0]) / 2
                y = (g1["station_idx"].iloc[0] + g2["station_idx"].iloc[0]) / 2
                plt.scatter(x, y, color="red", s=80, zorder=5, marker="x")

        # ---- Save figure ----
        fig_path = os.path.join(base_path, "conflicts_chart.png")
        plt.tight_layout()
        plt.savefig(fig_path)
        print(f"✅ Chart saved at {fig_path} (with conflict highlights)")

    except Exception as e:
        print("❌ Unexpected error:", str(e))
        sys.exit(1)

if __name__ == "__main__":
    main()
