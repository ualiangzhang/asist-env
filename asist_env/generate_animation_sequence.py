import pandas as pd
from pathlib import Path

pd.set_option("display.max_rows", None, "display.max_columns", None)

data_folder = Path("data")
processed_csv = data_folder / "processed_03.csv"

raw_sequence = pd.read_csv(processed_csv)
state_sequence = pd.DataFrame(columns=['timestamp', 'state'])

last_state = None
for index, row in raw_sequence.iterrows():
    if row["Room_in"] != "None":
        if row["triage_result"] == "SUCCESSFUL":
            curr_state = "v" + row["event_triage_victim_id"]
        else:
            curr_state = row["Room_in"]
    # elif row["Portal_in"] != "None":
    #     curr_state = row["Portal_in"]
    else:
        continue

    if curr_state != last_state:
        last_state = curr_state

        state_sequence = state_sequence.append({
            'timestamp': row["@timestamp"],
            'state': curr_state
        }, ignore_index=True)

print(state_sequence)
