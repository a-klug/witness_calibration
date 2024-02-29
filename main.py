from calibration.witness import run_simulation, get_downtime, get_tbes, write_tbes
import win32com.client as wc
import numpy as np
import pandas as pd
import math

# Initialize Witness Object
WitObj = wc.GetObject(Class="Witness.WCL")

# Load historical data
historicals = pd.read_excel("historicals.xlsx")
historicals = historicals.sort_values(by=["Process ID","Maintenance ID"])
historicals = historicals.rename(columns={"Duration": "Historical Duration"})

runtime = 5382

def objective_function(WitObj, historicals):
    """
    Define the objective function for optimization.
    """
    sim_downtime = get_downtime(WitObj)
    merged = pd.merge(sim_downtime, historicals, on=["Process ID","Maintenance ID"], how="inner")
    squared_diffs = (merged["Duration"] - merged["Historical Duration"])**2
    return squared_diffs.sum()

def tweak_tbes(tbes):
    """
    Slightly varies the TBEs to generate a new state.
    """
    factor = np.random.normal(loc=1.0, scale=0.05, size=tbes.shape)  # Small random changes
    new_tbes = tbes * factor
    return new_tbes.clip(min=0)  # Ensure no negative times

def simulated_annealing(WitObj, historicals, runtime):
    """
    Perform optimization using simulated annealing.
    """
    initial_temp = 100.0
    final_temp = 1.0
    alpha = 0.95  # Cooling rate
    current_temp = initial_temp
    
    process_list = np.unique(historicals["Process ID"].values)
    best_cost = float('inf')
    run_simulation(WitObj, runtime)
    
    for process in process_list:
        tbes = get_tbes(WitObj, process)
        while current_temp > final_temp:
            new_tbes = tweak_tbes(tbes)
            write_tbes(WitObj, new_tbes, process)
            run_simulation(WitObj, runtime)
            cost = objective_function(WitObj, historicals)
            print(cost)

            if cost < best_cost:
                best_cost = cost
                tbes = new_tbes
            else:
                delta = cost - best_cost
                if np.random.rand() < math.exp(-delta / current_temp):
                    best_cost = cost  # Accept worse state with certain probability
                    tbes = new_tbes
            
            current_temp *= alpha  # Cool down
            
        write_tbes(WitObj, tbes, process)  # Save the best state at the end
        print(f"Process {process}: Optimization complete")

simulated_annealing(WitObj, historicals, runtime)