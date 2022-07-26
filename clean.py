import pandas as pd
from typing import List
import numpy as np

class Scrubber:
    def __init__(self, df: pd.DataFrame):
        self.df = df
    
    def get_data(self):
        return self.df
    
    def convert_to_binary(self, vars: str or List[str]):
        """Useful for yes/no questions. Removes 7 and 9 and replaces 1(yes), 2(no) with 1(yes), 0(no).

        Args:
            var (str or List[str]): the variable or list of variables that will be changed.
        """
        if isinstance(vars, str):
            vars = [vars]
        for var in vars:
            self.df[var] = self.df[var].map(Scrubber.__convert_to_binary)
    
    
    def remove_7_and_9(self, vars: str or List[str]):
        """Removes 7 and 9 and replaces with NaN.

        Args:
            var (str or List[str]): the variable or list of variables that will be changed.
        """
        if isinstance(vars, str):
            vars = [vars]
        for var in vars:
            self.df[var] = self.df[var].map(Scrubber.__remove_7_and_9)
    
    def remove_77_and_99(self, vars: str or List[str]):
        """Removes 77 and 99 and replaces with NaN.

        Args:
            var (str or List[str]): the variable or list of variables that will be changed.
        """
        if isinstance(vars, str):
            vars = [vars]
        for var in vars:
            self.df[var] = self.df[var].map(Scrubber.__remove_77_and_99)
    
    def remove_777_and_999(self, vars: str or List[str]):
        """Removes 777 and 999 and replaces with NaN.

        Args:
            var (str or List[str]): the variable or list of variables that will be changed.
        """
        if isinstance(vars, str):
            vars = [vars]
        for var in vars:
            self.df[var] = self.df[var].map(Scrubber.__remove_777_and_999)
    
    def minus_one(self, vars: str or List[str]):
        """Subtracts 1 from variable. Useful for RIAGENDR, since 1(Male), 2(Female) will become 0(Male), 1(Female).

        Args:
            var (str or List[str]): the variable or list of variables that will be changed.
        """
        if isinstance(vars, str):
            vars = [vars]
        for var in vars:
            self.df[var] = self.df[var].map(Scrubber.__minus_one)
    
    def __convert_to_binary(x):
        if x == 7 or x == 9:
            return np.nan
        elif x == 2:
            return 0
        else: 
            return x
    
    def __minus_one(x):
        return x - 1
    
    def __remove_7_and_9(x):
        if x == 7 or x == 9:
            return np.nan
        else:
            return x
    
    def __remove_77_and_99(x):
        if x == 77 or x == 99:
            return np.nan
        else:
            return x
    
    def __remove_777_and_999(x):
        if x == 777 or x == 999:
            return np.nan
        else:
            return x
    