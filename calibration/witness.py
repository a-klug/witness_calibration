import time
import numpy as np
import pandas as pd

def get_tbes(WitObj, ProcessID: int) -> np.array:
    """
    Read a column from a table in a witness model

    Args:
    WitObj: object
        The witness object
    ProcessID: int
        The process ID to get the data for

    Returns:
    np.array
        The data from the table
    """
    table_name = "Tables.it_factTBE" # Assuming that this is the name of the table

    t_length = int(WitObj.Expression(f"DTGetRowCount({table_name})"))

    data = np.array([])

    query = f"DTFindNum({table_name}(1), 1, 7, {ProcessID})"

    row = int(WitObj.Expression(query))

    while int(WitObj.Expression(f"{table_name}[{row},7]")) == ProcessID:
        data = np.append(data, float(WitObj.Expression(f"{table_name}[{row},3]")))
        row += 1
        if row > t_length:
            break

    return data

def write_tbes(WitObj, tbes: np.array, ProcessID: int) -> None:
    """
    Write a column to a table in a witness model

    Args:
    WitObj: object
        The witness object
    tbes: np.array
        The data to write to the table
    ProcessID: int
        The process ID to write the data for
    
    Returns:
        None
    """
    
    table_name = "Tables.it_factTBE" # Assuming that this is the name of the table

    row = int(WitObj.Expression(f"DTFindNum({table_name}(1), 1, 7, {ProcessID})"))

    for id, tbe in enumerate(tbes):
        WitObj.Action(f"{table_name}[{row+id},3] = {tbe}")

def run_simulation(WitObj, sim_time: int) -> None:
    """
    Run a witness simulation

    Args:
    WitObj: object
        The witness object
    sim_time: int
        The time to run the simulation
    """
    WitObj.Stop()
    WitObj.Begin()

    WitObj.Batch(sim_time)

    time.sleep(1)
    while WitObj.ModelStatus == 1:
        time.sleep(1)
    
    WitObj.Stop()
    time.sleep(1)

def get_downtime(WitObj) -> pd.DataFrame:
    """
    Get the downtime of a machine from a witness table. 
    This method assumes that the downtimes are recorded in the table Tables.ot_DowntimeEvents.

    Args:
    WitObj: object
        The witness object

    Returns:
    pd.DataFrame
        The downtime of the machine
    """
    
    table_name = "Tables.ot_DowntimeEvents"

    t_length = int(WitObj.Expression(f"DTGetRowCount({table_name})"))

    # data = {
    #     "Process ID" : [],
    #     "Maintenance ID" : [],
    #     "Downtime ID" : [],
    #     "Duration": []
    # }

    # for index in range(t_length):
    #     data["Process ID"].append(
    #         WitObj.Expression(f"{table_name}[{index+1},1]")
    #     )
    #     data["Maintenance ID"].append(
    #         WitObj.Expression(f"{table_name}[{index+1},2]")
    #     )
    #     data["Downtime ID"].append(
    #         WitObj.Expression(f"{table_name}[{index+1},3]")
    #     )
    #     data["Duration"].append(
    #         WitObj.Expression(f"{table_name}[{index+1},4]")
    #     )

    # data = pd.DataFrame(data)

    save = int(WitObj.Expression(f"DTSave({table_name})"))

    data = pd.read_csv(
        r"C:\Users\AsherKlug\OneDrive - BSC Holdings\Automated Witness Calibration\Model\downtime.csv",
        header=None,
        names="Process ID, Maintenance ID, Downtime ID, Timestamp".split(", ")
    )

    data = data.sort_values(by="Process ID, Maintenance ID, Timestamp".split(", "))

    data['Duration'] = data['Timestamp'].diff().fillna(0)

    durations = data.loc[data["Downtime ID"] == 1].groupby("Process ID, Maintenance ID".split(", ")).sum().reset_index()

    return durations.drop(columns=["Downtime ID", "Timestamp"])

    # durations = {
    #     "Process ID" : [],
    #     "Maintenance ID" : [],
    #     "Downtime ID" : [],
    #     "Duration": []
    # }

    # for index, row in data.iterrows():
    #     if index == 0:
    #         continue

    #     if row["Process ID"] == data.loc[index-1, "Process ID"] and row["Maintenance ID"] == data.loc[index-1, "Maintenance ID"]:
    #         durations["Process ID"].append(row["Process ID"])
    #         durations["Maintenance ID"].append(row["Maintenance ID"])
    #         durations["Downtime ID"].append(row["Downtime ID"])
    #         durations["Duration"].append(row["Duration"] - data.loc[index-1, "Duration"])
    
    # durations = pd.DataFrame(durations)

    # durations = durations.loc[durations["Downtime ID"] == 1] # Remove the downtime events

    # durations =  durations.groupby("Process ID, Maintenance ID".split(", ")).sum().reset_index()

    # return durations.drop(columns="Downtime ID")