import time
import numpy as np

def read_table(WitObj, table_name: str, column_number: int) -> np.array:
    """
    Read a column from a table in a witness model

    Args:
    WitObj: object
        The witness object
    table_name: str
        The name of the table
    column_number: int
        The number of the column to read

    Returns:
    np.array
        The column of the table
    """
    t_length = int(WitObj.Expression(f"DTGetRowCount({table_name})"))

    data = np.array([])

    for index in range(t_length):
        data = np.append(
            data,
            float(WitObj.Expression(
                f"{table_name}[{index+1},{column_number}]"
            ))
        )

    return data

def write_table(WitObj, table_name: str, column_number: int, data: np.array) -> None:
    """
    Write a column to a table in a witness model

    Args:
    WitObj: object
        The witness object
    table_name: str
        The name of the table
    column_number: int
        The number of the column to write
    data: list
        The data to write
    """
    t_length = int(WitObj.Expression(f"DTGetRowCount({table_name})"))

    for index in range(t_length):
        WitObj.Action(
            f"{table_name}[{index+1},{column_number}] = {data[index]}"
        )

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
    WitObj.Run(sim_time)

    while WitObj.ModelStatus == 1:
        time.sleep(1)
    
    WitObj.Stop()