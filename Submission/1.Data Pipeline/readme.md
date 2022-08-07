# Documentation 
The airflow scheduler will run on a daily basis, where it takes in local CSV files to run the processing work. 

The start date to run this date is tagged 7th August 2022. 

## Code explanation
`read_and_concat_df_function`: This function reads in the csv files and concatenates the files together before processing the data. 

`preprocessing_data_function`: This function has 4 processing work applied to it, following a chronological order. xcom.pull is used to pull data from Airflow's temporary store. 
1. The data is first split into respective first and last names
2. the "Price" column is first converted to a string, where `lstrip()` is used to remove any prepended 0s. Afterwards, the series column is converted back to a float. 
3. Rows which do not have any values in "Name" column is removed
4. A function is written to see if the price is > 100, where it return True or False accordingly in a new column added named "above_100"

