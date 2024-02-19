from calibration.witness import run_simulation, get_downtime, get_tbes, write_tbes
import win32com.client as wc

wo = wc.GetObject(Class="Witness.WCL")

run_simulation(wo, 1000)

print(get_downtime(wo))