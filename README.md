Useful package to help download and merge data from NHANES medical database. Can clean/filter data and do statistical comparison analysis. 

Example downloading and cleaning data:

```python
from nhutils.generate import create_dataset
from nhutils.clean import Scrubber

# define parameters of interest for new dataset
years_of_interest = ['2011-2012', '2013-2014', '2015-2016', '2017-2018']
var_names = ['SEQN', 'RIDAGEYR', 'RIAGENDR', 'DMDEDUC2', 'DIQ080', 'SMQ020']
# download and create dataset
df = create_dataset(vars=var_names, years=years_of_interest)
# clean data by using Scrubber class
scrub = Scrubber(df)
scrub.minus_one('RIAGENDR')
scrub.remove_7_and_9('DMDEDUC2')
scrub.convert_to_binary(['DIQ080', 'SMQ020'])
# save cleansed data to csv
df.to_csv('dataset.csv', index=False)
```

Example of comparison anaylsis:

```python
from nhutils.stats import compare_stats
import pandas as pd

# import data
data = pd.read_excel('final_with_new copy.xlsx')
# define groups to be compared
dr = data[data['DIQ080'] == 1]
diab = data[(data['DIQ010'] == 1) & (data['DIQ080'] == 0)]
# call compare_stats function and provide function parameters
df_stats = compare_stats(group1=dr, 
                         group1_label='DR', 
                         group2=diab, 
                         group2_label='Diabetes',
                         numerical_vars=['RIDAGEYR', 'URDACT', 'BMXBMI'],
                         categorical_vars=['RIAGENDR', 'RIDRETH1', 'DMDEDUC2'],
                         output_excel_filename='DRvsDiabetes.xlsx',
                         welchs_t_test=True,
                         decimal_places=4)
```
After running above code block, "DRvsDiabetes.xlsx" would look like this:
| variable       | DR                  | Diabetes           | p-value |
| -------------- | ------------------- | ------------------ | ------- |
| RIDAGEYR       | 62.9549 (12.424)    | 61.2482 (13.9428)  | 0.0022  |
| URDACT         | 313.9478 (969.5149) | 136.8675 (613.404) | 0       |
| BMXBMI         | 32.3415 (8.2252)    | 32.3103 (7.5454)   | 0.9321  |
| RIAGENDR       |                     |                    | 0.0823  |
| RIAGENDR = 0   | 55.3383             | 51.4528            |         |
| RIAGENDR = 1   | 44.6617             | 48.5472            |         |
| RIDRETH1       |                     |                    | 0.1905  |
| RIDRETH1 = 1   | 16.391              | 16.6667            |         |
| RIDRETH1 = 2   | 12.0301             | 9.9677             |         |
| RIDRETH1 = 3   | 28.8722             | 32.6069            |         |
| RIDRETH1 = 4   | 26.6165             | 26.7958            |         |
| RIDRETH1 = 5   | 16.0902             | 13.9629            |         |
| DMDEDUC2       |                     |                    | 0.0727  |
| DMDEDUC2 = 1.0 | 18.6747             | 15.91              |         |
| DMDEDUC2 = 2.0 | 16.5663             | 14.9284            |         |
| DMDEDUC2 = 3.0 | 23.7952             | 22.4949            |         |
| DMDEDUC2 = 4.0 | 26.3554             | 28.3436            |         |
| DMDEDUC2 = 5.0 | 14.6084             | 18.3231            |         |
