from calibration.witness import run_simulation, get_downtime, get_tbes, write_tbes
import win32com.client as wc
from scipy.optimize import minimize
import numpy as np
import pandas as pd

class OptimizationStopException(Exception):
    pass

############################################
###### Fill in your parameters here ########
############################################

# the file which contains the historical repair times
historical_file = "historicals.xlsx"

# the runtime of the simulation
simulation_runtime = 1000

############################################

# connect to witness
WitObj = wc.GetObject(Class="Witness.WCL")

# get unique list of processes in the simulation
processes = set()
t_length = int(WitObj.Expression("DTGetRowCount(Tables.it_factTBE)"))
for id in range(t_length):
    processes.add(int(WitObj.Expression(f"Tables.it_factTBE[{id+1},7]")))

# read the historical repair times
historical = pd.read_excel(historical_file)

# We need to work systematically over the processes
# For each process, we will:
# 1. Get the expected duration of maintenance for the maintenance ID
# 2. Get the simulated duration of maintenance for the same maintenance ID
# 3. Compare the two using a cost function
# 4. Minimise the cost function to find the best fit parameters

def objective_function(tbes: np.array) -> float:
    # Write the tbes to the witness model
    write_tbes(WitObj, tbes, p)

    # Run the simulation
    run_simulation(WitObj, simulation_runtime)

    # Get the simulated downtime
    sim_downtime = get_downtime(WitObj)
    sim_downtime = sim_downtime.loc[sim_downtime["Process ID"] == p,'Duration'].values

    # Calculate the cost function
    cost = np.sum((hist_downtime - sim_downtime)**2)

    print(cost)
    return cost

def callback_function(tbes):
    if objective_function(tbes) < 0.5:
        raise OptimizationStopException

for p in processes:
    # get the historical downtime for the process
    hist_downtime = historical.loc[historical["Process ID"] == p,'Duration'].values

    # initial guess
    initial_tbes = get_tbes(WitObj, p)

    print("Optimising for process", p)
    # minimise the cost function
    try:
        result = minimize(objective_function, initial_tbes, method="Nelder-Mead", callback=callback_function)
    except OptimizationStopException:
        print("Optimization stopped as the objective function returned a value smaller than 0.5.")