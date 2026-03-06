# CloudComputing-Phase1

## Overview
This project implements the **Phase 1 modular monolithic system** for the SOFE 4630U Cloud Computing group project.

The system processes a selected **NGSIM US-101** trajectory dataset, detects driving scenarios, and generates **labeled 5-second scenario windows**.

The main scenario types currently detected are:

- Car-following
- Lane change
- Sudden braking
- Near collision

Each output scenario window contains:

- the **ego vehicle**
- **surrounding vehicles**
- a **scenario label**
- computed safety metrics such as gap distance, relative velocity, time headway, and TTC

---

## Project Structure

```text
CloudComputing-Phase1/
│
├── src/
│   ├── preprocess.py
│   ├── neighbors.py
│   ├── metrics.py
│   ├── scenarios.py
│   ├── windowing.py
│   └── main.py
│
├── requirements.txt
├── README.md
└── .gitignore

File Descriptions

preprocess.py
Loads and cleans the NGSIM dataset.

neighbors.py
Identifies the leader vehicle for each vehicle in the same lane.

metrics.py
Computes safety metrics such as gap distance, leader velocity, relative velocity, time headway, and time-to-collision.

scenarios.py
Applies rule-based logic to detect scenario events.

windowing.py
Extracts labeled 5-second scenario windows containing the ego vehicle and surrounding vehicles.

main.py
Runs the full Phase 1 pipeline.

How the Pipeline Works

The system runs in this order:

Load the NGSIM dataset

Clean and preprocess the data

Detect leader vehicles

Compute safety metrics

Detect scenario events

Extract 5-second labeled windows

Save outputs as CSV files

Requirements

Install the required Python packages:

pip install -r requirements.txt

Typical dependencies include:

pandas

numpy

Input Dataset

The system expects the selected NGSIM CSV file to be available in the project root directory.

Example:

us101_1118847220800_1118847821000.csv

Make sure the file_path in src/main.py matches the CSV location.

Example:

file_path = "us101_1118847220800_1118847821000.csv"
How to Run the Project

From the project root folder, run:

python3 src/main.py

or on Windows:

python src/main.py
Expected Output

After the script finishes, it will create an output folder like this:

outputs_windows/
├── car_following/
├── lane_change/
├── near_collision/
├── sudden_braking/
└── windows_summary.csv
Output meaning

Each folder contains extracted scenario windows

Each CSV file represents one detected event

Each file includes:

ego vehicle rows

surrounding vehicles

safety metrics

scenario label

The windows_summary.csv file contains a summary of all generated windows.

Example Console Output

When the pipeline runs successfully, it prints something like:

near_collision 40
sudden_braking 15895
lane_change 361
car_following 1693

It will also print a small preview of the generated window summary.

Cloud Execution

For Phase 1, the system was executed in the cloud using:

Google Cloud Storage for dataset storage

Google Compute Engine VM for processing

Python modular monolithic application for scenario extraction

The pipeline can also be run locally for testing, as long as the input dataset is available.

Notes

The current implementation is a modular monolithic system, meaning it runs as one application but is separated internally into multiple modules.

Some extracted windows may contain fewer than 50 unique frames if the event occurs near the start or end of a vehicle trajectory.

This is expected because the NGSIM dataset only tracks each vehicle while it is visible in the selected segment.

Summary

This project satisfies the main goals of Phase 1 by:

running as a single deployable application
being internally modular
executing in the cloud
detecting driving scenarios
generating labeled 5-second scenario samples
