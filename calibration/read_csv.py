import csv
import numpy as np

def read_csv_table(file_name: str) -> np.array:
    """
    Reads a csv file consisting of a single column of data

    Args:
    file_name: str
        The name of the file to read

    Returns:
    np.array
        The data from the file
    """
    with open(file_name, "r") as file:
        reader = csv.reader(file)
        data = np.array([float(row[0]) for row in reader])

    return data