# scripts/load_data.py
import pandas as pd
import json
import os
import sys

# Define base path safely
base_path = r"C:\Users\ASUS\OneDrive\Pictures\IntelliBlock\data"

# Switch between full or sample data here
timetable_file = os.path.join(base_path, "timetable_sample.csv")   # use timetable.csv for full
topology_file = os.path.join(base_path, "section_topology_sample.json")  # use section_topology.json for full

try:
    # ---- Load timetable ----
    if not os.path.exists(timetable_file):
        print(f"❌ Error: File not found -> {timetable_file}")
        sys.exit(1)

    timetable = pd.read_csv(timetable_file)

    if timetable.empty:
        print("❌ Error: timetable.csv is empty")
        sys.exit(1)

    print(f"✅ Timetable loaded: {len(timetable)} rows, {len(timetable.columns)} columns")
    print("\nSample rows:")
    print(timetable.head())

    # ---- Load topology ----
    if not os.path.exists(topology_file):
        print(f"❌ Error: File not found -> {topology_file}")
        sys.exit(1)

    with open(topology_file, "r") as f:
        topology = json.load(f)

    if "stations" not in topology or not topology["stations"]:
        print("❌ Error: Topology file missing 'stations' or empty")
        sys.exit(1)

    print(f"\n✅ Topology loaded: {len(topology['stations'])} stations")
    print("First 3 stations:")
    for s in topology["stations"][:3]:
        print(f"- {s['id']} ({s['name']})")

except Exception as e:
    print("❌ Unexpected error:", str(e))
    sys.exit(1)
