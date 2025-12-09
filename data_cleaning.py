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

# same check for route codes
route_code = df.columns[8]
check_route_code = df[route_code].unique()
print(f'Possible route codes: {check_route_code}')


# define names for columns from the dataset
date_col = "Departure date"
dep_col = "Scheduled departure time"
sched_arr_col = "Scheduled arrival time"
actual_arr_col = "Actual arrival time"
ds_arr_del_col = 'Arrival delay in minutes'
route_col = "Route Code"
orig_col = "Origin airport"
dest_col = "Destination airport"

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

# 1) Make sure dataset delay column is numeric
df["delay_ds_min"] = pd.to_numeric(df[ds_arr_del_col], errors="coerce")

# 2) Convert scheduled and actual arrival times to timedeltas since midnight
df["sched_td"] = pd.to_timedelta(df[sched_arr_col].astype(str))
df["act_td"] = pd.to_timedelta(df[actual_arr_col].astype(str))

# 3) Raw delay as timedelta (can be negative or wrap around)
df["delay_td_raw"] = df["act_td"] - df["sched_td"]

# 4) Normalize delay to the range [-12h, +12h) to fix 24h wrap-around issues
df["delay_td_norm"] = (
    (df["delay_td_raw"] + pd.Timedelta(hours=12)) % pd.Timedelta(days=1)
    - pd.Timedelta(hours=12)
)

# 5) Convert normalized delay to minutes
df["delay_calc_min"] = df["delay_td_norm"].dt.total_seconds() / 60

# 6) Optional: round to integer minutes for comparison
df["delay_calc_round"] = df["delay_calc_min"].round().astype("Int64")
df["delay_ds_round"] = df["delay_ds_min"].round().astype("Int64")

# 7) Compare: where do they differ?
df["delay_diff"] = df["delay_calc_min"] - df["delay_ds_min"]

mismatches = df[df["delay_calc_round"] != df["delay_ds_round"]]

print("Number of rows:", len(df))
print("Perfect matches (rounded):", len(df) - len(mismatches))
print("Mismatches (rounded):", len(mismatches))



# print the amount of mismatches
if mismatches.empty:
    print("No mismatches. We can rely on the given delay times.")
else:
    print(f"There are {len(mismatches)} mismatches.")


# check if route code 1 is correct
# Define expected origin/destination per route code
route_rules = {
    1: ("BER", "VIE"),
    2: ("VIE", "BER"),
    3: ("VIE", "OSL"),
    4: ("OSL", "VIE"),
}

for code, (expected_orig, expected_dest) in route_rules.items():
    # Filter rows for this route code
    subset = df[df[route_col] == code]

    # If there are no rows with this route code, just report and continue
    if subset.empty:
        print(f"Route Code {code}: no rows in dataset.")
        continue

    # Build condition: origin and destination must match the expected values
    condition = (subset[orig_col] == expected_orig) & (subset[dest_col] == expected_dest)

    if condition.all():
        print(
            f"OK: For all rows with Route Code {code}, "
            f"origin={expected_orig} and destination={expected_dest}."
        )
    else:
        # Count and show violations
        n_violations = (~condition).sum()
        print(
            f"WARNING: Route Code {code} has {n_violations} violation(s) of the rule "
            f"(expected origin={expected_orig}, destination={expected_dest})."
        )

        print(
            subset.loc[~condition, [route_col, orig_col, dest_col]]
            .head()
            .to_string(index=False)
        )
        print("-" * 60)



##############################################################################
print('/n Comparison of the Airlines delay time: ')

# Filter rows for the airline FlyUIBK
flyuibk_rows = df[df["Airline"] == "FlyUIBK"]

# Compute the average delay
avg_delay_flyuibk = flyuibk_rows["delay_ds_min"].mean()

print(f"Average delay for FlyUIBK: {avg_delay_flyuibk:.2f} minutes")

# Filter rows for the airline FlyUIBK
LDA_rows = df[df["Airline"] == "LDA"]

# Compute the average delay
avg_delay_LDA = LDA_rows["delay_ds_min"].mean()

print(f"Average delay for LDA: {avg_delay_LDA:.2f} minutes")


