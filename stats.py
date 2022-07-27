from typing import Any, List
import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency, ttest_ind


def compare_stats(
    group1: pd.DataFrame,
    group1_label: str,
    group2: pd.DataFrame,
    group2_label: str,
    numerical_vars: List[str],
    categorical_vars: List[str],
    output_excel_filename: str,
    welchs_t_test: bool = True,
) -> pd.DataFrame:
    """Compare statistics between two groups. Will result in a table including mean(std) or mean percentage
    for each group and p-value from t-test or chi-square test depending on if the variable
    is numerical or categorical.

    Args:
        group1 (pandas.DataFrame):
            The first group to be analyzed. e.g. df[df['DIQ010'] == 1]
        group1_label (str):
            Description of the first group. e.g. "Diabetes"
        group2 (pandas.DataFrame):
            The second group to be analyzed. e.g. df[df['DIQ080'] == 1]
        group2_label (str):
            Description of the second group. e.g. "DR"
        numerical_vars (List[str]):
            list of all the numerical variables to be included in the comparison. e.g. ['RIDAGEYR', 'BMXBMI']
        categorical_vars (List[str]):
            list of all the categorical variables to be included in the comparison. e.g. ['RIDETH1', 'DMDEDUC2']
        output_excel_filename (str):
            The name of the output excel file that stores the statistics. e.g. "DRvsDiabetes.xlsx"
        welchs_t_test(bool): Default is True.
            If True, welch's t-test will be used. If False, regular student t-test will be used.

    Returns:
        pd.DataFrame: the dataframe containing the statistics.
    """

    storage = pd.DataFrame(columns=["variable", group1_label, group2_label, "p-value"])

    for num_var in numerical_vars:
        _compare_on_num_var(group1, group2, num_var, storage, welchs_t_test)

    for cat_var in categorical_vars:
        choices = set(group1[cat_var].dropna().unique()) | set(
            group2[cat_var].dropna().unique()
        )
        choices = list(choices)
        choices.sort()
        _compare_on_categorical_var(group1, group2, cat_var, choices, storage)

    storage.to_excel(output_excel_filename, index=False)
    return storage


def _compare_on_num_var(
    group1: pd.DataFrame,
    group2: pd.DataFrame,
    var: str,
    storage: pd.DataFrame,
    welchs_t_test: bool = True,
):
    group1_basic_stats = f"{group1[var].mean()} ({group1[var].std()})"
    group2_basic_stats = f"{group2[var].mean()} ({group2[var].std()})"

    t, p = ttest_ind(
        group1[var].dropna(), group2[var].dropna(), equal_var=not welchs_t_test
    )

    storage.loc[len(storage.index)] = [var, group1_basic_stats, group2_basic_stats, p]


def _compare_on_categorical_var(
    group1: pd.DataFrame,
    group2: pd.DataFrame,
    var: str,
    choices: List[Any],
    storage: pd.DataFrame,
):
    group1_vals = group1[var].value_counts()
    group2_vals = group2[var].value_counts()

    obs = np.zeros((2, len(choices)))
    index = 0
    for choice in choices:
        obs[0][index] = group1_vals[choice] if choice in group1_vals.index else 0
        obs[1][index] = group2_vals[choice] if choice in group2_vals.index else 0
        index += 1

    chi2, p, dof, ex = chi2_contingency(obs)
    storage.loc[len(storage.index)] = [var, None, None, p]

    for choice in choices:
        name = var + " = " + str(choice)
        group1_mean_percentage = (group1_vals[choice] / group1_vals.sum()) * 100
        group2_mean_percentage = (group2_vals[choice] / group2_vals.sum()) * 100
        storage.loc[len(storage.index)] = [
            name,
            group1_mean_percentage,
            group2_mean_percentage,
            None,
        ]
