from calibration.witness import run_simulation, get_downtime, get_tbes, write_tbes
import win32com.client as wc
import numpy as np
import pandas as pd

runtime = 5382

WitObj = wc.GetObject(Class="Witness.WCL")

historicals = pd.read_excel("historicals.xlsx")
historicals = historicals.sort_values(by=["Process ID","Maintenance ID"])

historicals = historicals.rename(columns={"Duration": "Historical Duration"})

threshold = 0.05

def get_process_list():
    """
    Optimize the simulation

    Returns:
    None
    """
    downtime = get_downtime(WitObj)

    # Merge the two dataframes
    data = pd.merge(
        downtime,
        historicals,
        on=["Process ID","Maintenance ID"],
    how = "inner"
    )

    data = data.groupby("Process ID").sum().reset_index()
    data["Variation"] = abs(1-data["Duration"]/data["Historical Duration"])
    data = data.loc[data["Variation"] >= threshold]

    return np.unique(data["Process ID"].values), data


def optimize_simulation() -> None:
    """
    Optimize the simulation

    Returns:
    None
    """
    print("Running simulation...\n")
    run_simulation(WitObj, runtime)
    process_list, data = get_process_list()

    while process_list.size > 0:
        for p in process_list:
            print(f"Optimizing Process {p}")
            print(f"Variation: {100*data.loc[data['Process ID'] == p, 'Variation'].values[0]}")

            tbes = get_tbes(WitObj, p)
            hist = historicals.loc[historicals["Process ID"] == p,"Historical Duration"].values
            sim = get_downtime(WitObj)
            sim = sim.loc[sim["Process ID"] == p,"Duration"].values 

            updated_tbes = tbes*sim/hist*1.05

            write_tbes(WitObj, updated_tbes, p)
        
        print("\n Running simulation...")
        run_simulation(WitObj, runtime)
        process_list, data = get_process_list()

optimize_simulation()