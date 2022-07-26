from pickle import FALSE
from typing import List
import pandas as pd
import wget
import os
import xport.v56
from time import time
from nhutils.constants import *

# main driver function for generating dataset
def create_dataset(
    vars: List[str], years: List[str], by: str = "SEQN", join_method: str = "outer"
) -> pd.DataFrame:
    """The main function to download data from Nhanes and merge together into single pandas dataframe.
    All you have to pass is the variable names and years.
    You can also specify the 'by' and 'join_method' parameters but default values are most likely what you want.

    Args:
        vars (List[str]): 
            list of all the variable names you want in the dataset (e.g. ['SEQN', 'DIQ010', 'RIDAGEYR'])
        years (List[str]): 
            list of all the years you want to include in the dataset. Has to be in the format of 'YYYY-YYYY' 
            (e.g. ['2015-2016', '2017-2018'])
        by (str, optional): Defaults to "SEQN".
            the variable that is used to do the merging of data. 
        join_method (str, optional): Defaults to "outer".
            the method used to merge data.

    Returns:
        pd.DataFrame: the created dataset
    """
    
    start = time()
    
    vars = _preproccess_vars(vars)
    years = _preproccess_years(years)

    dataset = None
    
    for year in years:
        files_to_download = _get_filenames_to_download(vars, year)
        _download_files(files_to_download, year)
        print("merging files...")
        year_dataset = None
        for file in files_to_download:
            vars_in_file = _find_all_vars_in_file(file, vars, year) + ["SEQN"]
            df = pd.read_csv(DOWNLOADED_DIR + file.replace(".XPT", ".csv"))
            df = df[vars_in_file]
            if file == files_to_download[0]:
                year_dataset = df
            else:
                year_dataset = year_dataset.merge(df, on=by, how=join_method, suffixes=(False, False))
        if year == years[0]:
            dataset = year_dataset
        else:
            dataset = pd.concat([dataset, year_dataset], axis=0)
        print("done")
    end = time()
    print(f"finished creating dataset in {end - start} seconds")
    # move SEQN to the front
    col = dataset.pop('SEQN')
    dataset.insert(0, col.name, col)
    return dataset


# validate/preproccess years input
def _preproccess_years(years: List[str]) -> List[str]:
    print("preproccessing years input...")
    for year in years:
        if year not in ALL_YEARS:
            raise ValueError(f"{year} is not a valid year. Valid years are {ALL_YEARS}")
    print("done")
    return years


# validate/preproccess vars input
def _preproccess_vars(vars: List[str]) -> List[str]:
    print("preproccessing vars input...")
    vars = set(vars)
    vars.add("SEQN")
    vars = list(vars)
    for var in vars:
        if var not in ALL_VARS:
            raise ValueError(f"{var} is not a valid variable. I could not find it.")
    print("done")
    return vars

# get list of filenames to download for a given year
def _get_filenames_to_download(vars: List[str], year: str) -> List[str]:
    print(f"figuring out which files to download for {year}...")
    var_file_map = globals()['VAR_TO_FILENAME_' + year.replace('-', '_')]
    files_to_download = set()
    for var in vars:
        if not var == "SEQN":
            files_to_download.add(var_file_map[var])
    print("done")
    return list(files_to_download)

# downloads files and saves them as .csv to downloaded directory
def _download_files(files_to_download: List[str], year: str) -> None:
    print("downloading files...")
    BASE_URL = "https://wwwn.cdc.gov/Nchs/Nhanes/"
    # make sure downloaded directory exists
    if not os.path.exists(DOWNLOADED_DIR):
        os.makedirs(DOWNLOADED_DIR)
    
    for file in files_to_download:
        # check to see if file is already downloaded
        if os.path.exists(DOWNLOADED_DIR + file.replace('.XPT', '.csv')):
            continue
        # download the file
        url = BASE_URL + year + '/' + file
        filename = wget.download(url, out=DOWNLOADED_DIR)
        # convert to csv
        with open(DOWNLOADED_DIR + file, 'rb') as f:
            library = xport.v56.load(f)
            ds = next(iter(library.values()))
            output_filename = DOWNLOADED_DIR + file.replace(".XPT", ".csv")
            ds.to_csv(output_filename, index=False)
    print("\ndone")
    
# find all vars that are in given file
def _find_all_vars_in_file(file: str, vars: List[str], year: str) -> List[str]:
    var_file_map = globals()['VAR_TO_FILENAME_' + year.replace('-', '_')]
    vars_in_file = []
    for var in vars: 
        if var_file_map[var] == file:
            vars_in_file.append(var)
    return vars_in_file
    