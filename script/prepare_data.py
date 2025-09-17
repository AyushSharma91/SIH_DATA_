# scripts/prepare_data.py
import pandas as pd
import json
import os
import sys

# Define base data folder safely
base_path = r"C:\Users\ASUS\OneDrive\Pictures\IntelliBlock\data"

# Input and output file paths
raw_file = os.path.join(base_path, "Train_details_22122017.csv")
timetable_file = os.path.join(base_path, "timetable.csv")
topology_file = os.path.join(base_path, "section_topology.json")
timetable_sample_file = os.path.join(base_path, "timetable_sample.csv")
topology_sample_file = os.path.join(base_path, "section_topology_sample.json")


def create_files(df, timetable_path, topology_path, subset=False):
    """Generate timetable.csv and section_topology.json"""
    # ---- Clean station names/codes ----
    df["Station Name"] = df["Station Name"].astype(str).str.strip()
    df["Station Code"] = df["Station Code"].astype(str).str.strip()

    # ---- Create timetable ----
    timetable = df.rename(columns={
        "Train No": "train_id",
        "Station Code": "station_id",
        "Arrival time": "arr_time",
        "Departure Time": "dep_time"
    })[["train_id", "station_id", "arr_time", "dep_time"]]

    # Add a placeholder block sequence (to refine later)
    timetable["block_seq"] = "B1"

    timetable.to_csv(timetable_path, index=False)
    print(f"✅ timetable.csv ({'sample' if subset else 'full'}) created with {len(timetable)} rows at {timetable_path}")

    # ---- Create section topology ----
    stations = df[["Station Code", "Station Name"]].drop_duplicates()
    station_list = [
        {"id": row["Station Code"], "name": row["Station Name"], "platforms": 2}
        for _, row in stations.iterrows()
    ]

    topology = {
        "stations": station_list,
        "blocks": [
            {
                "id": "B1",
                "from": station_list[0]["id"],
                "to": station_list[-1]["id"],
                "length_km": None
            }
        ]
    }

    with open(topology_path, "w") as f:
        json.dump(topology, f, indent=2)

    print(f"✅ section_topology.json ({'sample' if subset else 'full'}) created with {len(station_list)} stations at {topology_path}")


def main():
    try:
        # ---- Load dataset ----
        if not os.path.exists(raw_file):
            print(f"❌ Error: File not found -> {raw_file}")
            sys.exit(1)

        df = pd.read_csv(raw_file)
        print(f"✅ Loaded dataset with {len(df)} rows and {len(df.columns)} columns")

        # ---- Check required columns ----
        required_cols = ["Train No", "Station Code", "Arrival time", "Departure Time", "Station Name"]
        missing_cols = [col for col in required_cols if col not in df.columns]

        if missing_cols:
            print(f"❌ Error: Missing columns in dataset -> {missing_cols}")
            sys.exit(1)

        # ---- Create full dataset files ----
        create_files(df, timetable_file, topology_file, subset=False)

        # ---- Create sample dataset files (first 100 trains) ----
        sample_df = df[df["Train No"].isin(df["Train No"].unique()[:100])]
        create_files(sample_df, timetable_sample_file, topology_sample_file, subset=True)

        print("\n🎉 Phase 1 completed: Both full and sample files are ready!")

    except Exception as e:
        print("❌ Unexpected error:", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
