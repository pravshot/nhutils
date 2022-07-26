Useful package to help download and merge data from NHANES medical database.

Example:

```python
from nhutils.generate import create_dataset

years_of_interst = ['2011-2012', '2013-2014', '2015-2016', '2017-2018']
var_names = ['SEQN', 'RIDAGEYR', 'RIAGENDR', 'DIQ010', 'DIQ080', 'HSD010']

df = create_dataset(vars=var_names, years=years_of_interest)
df.to_csv('dataset.csv', index=False)
```