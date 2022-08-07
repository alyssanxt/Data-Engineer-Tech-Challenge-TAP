from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.dummy_operator import DummyOperator

from datetime import datetime, timedelta  
import pandas as pd

####################################################
# 1. DEFINE PYTHON FUNCTIONS
####################################################

def read_and_concat_df_function(**kwargs):
    dataset1 = pd.read_csv("dataset1.csv")
    dataset2 = pd.read_csv("dataset2.csv")

    # Concatting the dataset 
    combined_dataset = pd.concat([dataset1, dataset2])
    combined_dataset
    return combined_dataset


def preprocessing_data_function(**kwargs):
    ti = kwargs['ti']
    combined_dataset= ti.xcom_pull(task_ids='read_and_concat_df')
    # Split the name field into first_name, and last_name
    new = combined_dataset["name"].str.split(" ", n = 1, expand = True)
    # making separate first and last name column from new data frame
    combined_dataset["First Name"]= new[0]
    combined_dataset["Last Name"]= new[1]

    # Remove any zeros prepended to the price field
    combined_dataset['price'] = combined_dataset['price'].astype('str')
    combined_dataset['price'].str.lstrip('0')
    combined_dataset[["price"]] = combined_dataset[["price"]].apply(pd.to_numeric)

    # Delete any rows which do not have a name
    combined_dataset.dropna(subset=['name'], inplace=True)
    combined_dataset

    # Create a new field named above_100, which is true if the price is strictly greater than 100
    def label_price(row):
        if row['price'] > 100:
            return True
        else:
            return False
    combined_dataset['above_100'] = combined_dataset.apply(lambda row: label_price(row), axis=1)

    # Converting to CSV file
    combined_dataset.to_csv('processed_data.csv', index = False)
    return combined_dataset


############################################
#2. DEFINE AIRFLOW DAG (SETTINGS + SCHEDULE)
############################################

default_args = {
     'owner': 'airflow',
     'depends_on_past': False,
     'email': ['alyssanah@gmail.com'],
     'email_on_failure': False,
     'email_on_retry': False,
     'retries': 1
    }

dag = DAG( 'Data Processing',
            default_args=default_args,
            description='Processing data for Analysis',
            catchup=False, 
            start_date= datetime(2022, 8, 1), 
            # schedule_interval= '0 0 1 */3 *',
            schedule_interval= '@daily'  
          )  

##########################################
#3. DEFINE AIRFLOW OPERATORS
##########################################

start_pipeline = DummyOperator(
        task_id = 'start_pipeline',
        dag = dag
        )

read_and_concat_df = PythonOperator(task_id = 'read_and_concat_df', 
                                   python_callable = read_and_concat_df_function, 
                                   provide_context = True,
                                   dag= dag )
preprocessing_data = PythonOperator(task_id = 'preprocessing_data', 
                                   python_callable = preprocessing_data_function, 
                                   provide_context = True,
                                   dag= dag )



##########################################
#4. DEFINE OPERATORS HIERARCHY
##########################################

start_pipeline >> read_and_concat_df >> preprocessing_data