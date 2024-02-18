from calibration.witness import read_table, write_table, run_simulation
from calibration.read_csv import read_csv_table
import win32com.client as wc
from scipy.optimize import minimize
import numpy as np

############################################
###### Fill in your parameters here ########
############################################

# input table in Witness which contains the TBEs for all machines
input_tbe_table = "Tables.it_factTBE"

# the column in the input table which contains mean time between failures, assuming a negative exponential distribution
input_tbe_column = 3

# the chart in Witness which contains the repair time
utilisation_chart = "Charts.UtilMachine01.Utilisation"

# the column in the chart which contains the repair time
utilisation_chart_column = 6

# the file which contains the historical repair times
historical_file = "historicals.csv"

# the runtime of the simulation
simulation_runtime = 5832

############################################


def objective_function(tbes: np.array) -> float:
    # Update the TBEs in the model
    write_table(WitObj, input_tbe_table, input_tbe_column, tbes)

    # Run the simulation
    run_simulation(WitObj, simulation_runtime)

    # Get the repair time
    repair_time = read_table(WitObj, utilisation_chart, utilisation_chart_column)

    # Return the error
    error = np.sum((repair_time - historicals)**2)
    print(error)
    return error

# Create the witness object
WitObj = wc.GetObject(Class="Witness.WCL")

# Get the starting TBEs
tbes = read_table(WitObj, input_tbe_table, input_tbe_column)

# Get the historical repair times
historicals = read_csv_table(historical_file)

# Run the optimisation
WitObj.BeginOLE()
result = minimize(objective_function, tbes,method='BFGS')
WitObj.EndOLE()

# Save the TBEs
with open("tbes.txt", "w") as file:
    for tbe in result.x:
        file.write(str(tbe) + "\n")