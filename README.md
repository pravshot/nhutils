Useful package to help download and merge data from NHANES medical database.

Example:

```python
from nhutils.generate import create_dataset
from nhutils.clean import Scrubber

# define dataset parameters
years_of_interest = ['2011-2012', '2013-2014', '2015-2016', '2017-2018']
var_names = ['SEQN', 'RIDAGEYR', 'RIAGENDR', 'DMDEDUC2', 'DIQ080', 'SMQ020']
# create dataset
df = create_dataset(vars=var_names, years=years_of_interest)
# clean data by using Scrubber class
scrub = Scrubber(df)
scrub.minus_one('RIAGENDR')
scrub.remove_7_and_9('DMDEDUC2')
scrub.convert_to_binary(['DIQ080', 'SMQ020'])
# save cleaned data to csv
df.to_csv('dataset.csv', index=False)
```