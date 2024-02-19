import pandas as pd

def read_excel_file(file_name: str) -> pd.DataFrame:
    """
    Read an excel file into a pandas dataframe

    Args:
    file_name: str
        The name of the file to read

    Returns:
    pd.DataFrame
        The data from the file
    """
    return pd.read_excel(file_name)