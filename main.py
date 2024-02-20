from calibration.witness import run_simulation, get_downtime, get_tbes, write_tbes
import win32com.client as wc
from scipy.optimize import minimize
import numpy as np
import pandas as pd
from skopt import gp_minimize
from skopt.space import Real
from skopt.utils import use_named_args

runtime = 500

WitObj = wc.GetObject(Class="Witness.WCL") 

# Assuming there's a placeholder function to run the simulation
def get_sim_repair(machine_id, mtbf_values):
    # Write the MTBF values to the witness model
    write_tbes(WitObj, mtbf_values, machine_id)

    # Run the simulation
    run_simulation(WitObj, runtime)

    # Get the downtime data
    downtime = get_downtime(WitObj)
    downtime = downtime.loc[downtime['Process ID'] == machine_id,'Duration'].values

    return downtime

# Optimizes the MTBF values for a single machine
def optimize_machine(machine_id, num_categories, historical_data):
    # Create the parameter space dynamically based on the number of categories
    space = [Real(5, 100, name=f'mtbf_category_{i+1}') for i in range(num_categories)]
    
    # Define the objective function for optimization, adjusted for varying numbers of categories
    @use_named_args(space)
    def objective(**params):
        mtbf_values = np.array(list(params.values()))
        sim_repair = get_sim_repair(machine_id, mtbf_values)
        cost = np.sum((sim_repair - historical_data)**2)
        print(cost)
        return cost
    
    # Perform Bayesian Optimization
    result = gp_minimize(objective,                   # the function to minimize
                         space,                       # the bounds on each dimension of x
                         acq_func="gp_hedge",         # the acquisition function
                         n_calls=50,                  # the number of evaluations of f
                         n_random_starts=10,          # the number of random initialization points
                         noise=0.1**2,                # the noise level (optional)
                         random_state=123)            # the random seed
    
    print(f"Optimized MTBF values for Machine {machine_id}:", result.x)
    print(f"Minimum cost achieved for Machine {machine_id}:", result.fun)


# List of machines
machine_list = [1,2]

# Get historicals
# historicals = pd.read_excel('historicals.xlsx')
historicals = pd.read_excel(
    r"C:\Users\AsherKlug\OneDrive - BSC Holdings\Automated Witness Calibration\Model\historicals.xlsx"
)

# Loop over the machine list
for p in machine_list:
    historical_data = historicals.loc[historicals['Process ID'] == p, "Duration"].values
    num_categories = len(historical_data)
    print(f"Optimizing MTBF values for Machine {p} with {num_categories} categories")
    optimize_machine(p, num_categories, historical_data)