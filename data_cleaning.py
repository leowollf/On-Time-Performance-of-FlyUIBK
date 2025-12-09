# Data cleaning

import pandas as pd
import numpy as np

#import original dataset as .csv [I converted it from .xlsx to .csv beforehand]
df = pd.read_csv("original_file.csv", sep = ';') 

# check if airline names are alway correct; print all airlines
airline = df.columns[0]
check_airline = df[airline].unique()
print(f'Airlines operating: {check_airline}')

# same check for origin and destination airport
or_airport = df.columns[1]
check_or_airport = df[or_airport].unique()
print(f'Origin Airports: {check_or_airport}')

des_aiport = df.columns[2]
check_des_airport = df[des_aiport].unique()
print(f'Destination Airports: {check_des_airport}')


# define names for columns from the dataset
date_col = "Departure date"
dep_col = "Scheduled departure time"
sched_arr_col = "Scheduled arrival time"
actual_arr_col = "Actual arrival time"
ds_arr_del_col = 'Arrival delay in minutes'

# Create full datetime for departure
df["dep_dt"] = pd.to_datetime(
    df[date_col].astype(str) + " " + df[dep_col].astype(str),
    format="%Y-%m-%d %H:%M:%S",
    errors="coerce")

# Create full datetime for scheduled arrival
df["sched_arr_dt"] = pd.to_datetime(
    df[date_col].astype(str) + " " + df[sched_arr_col].astype(str),
    format="%Y-%m-%d %H:%M:%S",
    errors="coerce")

# Create full datetime for actual arrival
df["act_arr_dt"] = pd.to_datetime(
    df[date_col].astype(str) + " " + df[actual_arr_col].astype(str),
    format="%Y-%m-%d %H:%M:%S",
    errors="coerce")



#### ADDING GPT CODE ####

# 3) Make sure dataset delay column is numeric
df["delay_ds_min"] = pd.to_numeric(df[ds_arr_del_col], errors="coerce")

# 4) Recalculate delay from times (actual - scheduled)
df["delay_calc_td"] = df["act_arr_dt"] - df["sched_arr_dt"]
df["delay_calc_min"] = df["delay_calc_td"].dt.total_seconds() / 60

# 5) Optional: round to integer minutes for comparison
df["delay_calc_round"] = df["delay_calc_min"].round().astype("Int64")
df["delay_ds_round"] = df["delay_ds_min"].round().astype("Int64")

# 6) Compare: where do they differ?
df["delay_diff"] = df["delay_calc_min"] - df["delay_ds_min"]

# Rows where rounded values do not match
mismatches = df[df["delay_calc_round"] != df["delay_ds_round"]]

print("Number of rows:", len(df))
print("Perfect matches (rounded):", len(df) - len(mismatches))
print("Mismatches (rounded):", len(mismatches))

# Inspect first few mismatches
print(mismatches[[date_col,
                  sched_arr_col,
                  actual_arr_col,
                  "delay_calc_min",
                  "delay_ds_min",
                  "delay_diff"]].head().to_string(index=False))