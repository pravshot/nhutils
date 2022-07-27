from typing import Any, List
import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency, ttest_ind
import statsmodels.api as sm


def log_reg(
    data: pd.DataFrame,
    dependent_var: str,
    independent_numerical_vars: List[str],
    independent_categorical_vars: List[str],
    output_excel_filename: str = None,
) -> pd.DataFrame:
    """Perform logistic regression anaylsis on data. Will print out results and return
    pandas dataframe containing odds ratio, p-value, and conf-int.

    Args:
        data (pd.DataFrame): data that logistic regression model will be applied on
        dependent_var (str): outcome/dependent variable(values should be 0 or 1)
        independent_numerical_vars (List[str]): all independent variables that are numerical
        independent_categorical_vars (List[str]): all independent variables that are categorical
        output_excel_filename (str, optional): Defaults to None.
            if given, will create an excel file holding stats results

    Returns:
        pd.DataFrame: holds the results of the logistic regression analysis
    """
    # subset data to only include variables of interest and do listwise deletion
    x_vars = independent_numerical_vars + independent_categorical_vars
    subset = data[x_vars + [dependent_var]]
    subset.dropna(inplace=True)
    # create x and y variables
    x = pd.get_dummies(
        subset[x_vars],
        columns=independent_categorical_vars,
        drop_first=True,
        prefix_sep="=",
    )
    x_full = sm.add_constant(x, has_constant="skip")
    y = subset[dependent_var]
    # perform logistic regression
    logit = sm.Logit(y, x_full)
    result = logit.fit()
    print(result.summary())
    model_odds = pd.DataFrame(np.exp(result.params), columns=["OR"])
    model_odds["p-value"] = result.pvalues
    model_odds[["2.5%", "97.5%"]] = np.exp(result.conf_int())
    print(model_odds)

    if output_excel_filename:
        model_odds.to_excel(output_excel_filename, index=True)

    return model_odds


def compare_stats(
    group1: pd.DataFrame,
    group1_label: str,
    group2: pd.DataFrame,
    group2_label: str,
    numerical_vars: List[str],
    categorical_vars: List[str],
    output_excel_filename: str = None,
    welchs_t_test: bool = True,
    decimal_places: int = 3,
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
            list of all the categorical variables to be included in the comparison. e.g. ['RIDRETH1', 'DMDEDUC2']
        output_excel_filename (str, optional): Defaults to None.
            if given, will create excel file that stores the statistics. e.g. "DRvsDiabetes.xlsx"
        welchs_t_test(bool): Default is True.
            If True, welch's t-test will be used. If False, regular student t-test will be used.
        decimal_places (int): Default is 3.
            The number of decimal places to round the results to.

    Returns:
        pd.DataFrame: the dataframe containing the statistics.
    """

    storage = pd.DataFrame(columns=["variable", group1_label, group2_label, "p-value"])

    for num_var in numerical_vars:
        _compare_on_num_var(
            group1, group2, num_var, storage, welchs_t_test, decimal_places
        )

    for cat_var in categorical_vars:
        choices = set(group1[cat_var].dropna().unique()) | set(
            group2[cat_var].dropna().unique()
        )
        choices = list(choices)
        choices.sort()
        _compare_on_categorical_var(
            group1, group2, cat_var, choices, storage, decimal_places
        )

    if output_excel_filename:
        storage.to_excel(output_excel_filename, index=False)

    return storage


def _compare_on_num_var(
    group1: pd.DataFrame,
    group2: pd.DataFrame,
    var: str,
    storage: pd.DataFrame,
    welchs_t_test: bool,
    decimal_places: int,
):
    group1_basic_stats = f"{round(group1[var].mean(), decimal_places)} ({round(group1[var].std(), decimal_places)})"
    group2_basic_stats = f"{round(group2[var].mean(), decimal_places)} ({round(group2[var].std(), decimal_places)})"

    t, p = ttest_ind(
        group1[var].dropna(), group2[var].dropna(), equal_var=not welchs_t_test
    )

    storage.loc[len(storage.index)] = [
        var,
        group1_basic_stats,
        group2_basic_stats,
        round(p, decimal_places),
    ]


def _compare_on_categorical_var(
    group1: pd.DataFrame,
    group2: pd.DataFrame,
    var: str,
    choices: List[Any],
    storage: pd.DataFrame,
    decimal_places: int,
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
    storage.loc[len(storage.index)] = [var, None, None, round(p, decimal_places)]

    for choice in choices:
        name = var + " = " + str(choice)
        group1_mean_percentage = (group1_vals[choice] / group1_vals.sum()) * 100
        group2_mean_percentage = (group2_vals[choice] / group2_vals.sum()) * 100
        storage.loc[len(storage.index)] = [
            name,
            round(group1_mean_percentage, decimal_places),
            round(group2_mean_percentage, decimal_places),
            None,
        ]
