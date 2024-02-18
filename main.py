from calibration.witness import read_table, write_table, run_simulation
from calibration.read_csv import read_csv_table
import win32com.client as wc
from scipy.optimize import minimize
import numpy as np

def objective_function(tbes: np.array) -> float:
    # Update the TBEs in the model
    write_table(WitObj, "Tables.it_factTBE", 3, tbes)

    # Run the simulation
    run_simulation(WitObj, run_time)

    # Get the repair time
    repair_time = read_table(WitObj, "Charts.UtilMachine01.Utilisation", 6)

    # Return the error
    error = np.sum((repair_time - historicals)**2)
    print(error)
    return error

# Create the witness object
WitObj = wc.GetObject(Class="Witness.WCL")

# Get the starting TBEs
tbes = read_table(WitObj, "Tables.it_factTBE", 3)

# Get the historical repair times
historicals = read_csv_table("historicals.csv")

# Set the simulation time
run_time = 5832

# Run the optimisation
WitObj.BeginOLE()
result = minimize(objective_function, tbes,method='Nelder-Mead')
WitObj.EndOLE()