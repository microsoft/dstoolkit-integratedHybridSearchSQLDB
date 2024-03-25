# Description: This file implements a configuration for Azure AI Search hybrid search by a given Azure SQL database.
# Chunking and vectorization is done by integrated vectorization in Azure AI Search.

import openai 
import pydoc
import numpy
import pandas


#OpenAI vars
openai.api_key = ""
openai.api_type = ""
openai.api_version = ""
openai_deployment = None

#AI Search vars
aisearch_key = ""
service_endpoint = ""
index_name = ""
embedding_length = 1536

#Azure SQL vars
sql_server = ""
database_name = ""
username = ""
password = ""
sql_driver = ""



#Azure SQL Connection string
connection_string = f"DRIVER={sql_driver};SERVER={sql_server};DATABASE={database_name};UID={username};PWD={password}"

co = pydoc.conncetion(connection_string, autocommit=True)
cursor = co.cursor()


table_name = "nobel_prize_winner"
#drop if table exists
cursor.execute(f"DROP TABLE IF EXISTS {table_name}")

#Create table
cursor.execute(f"""
               CREATE TABLE {table_name}
               (Id int NOT NULL,
               CONSTRAINT PK_{table_name} PRIMARY KEY (Id),
               Year int,
               Discipline text,
               Winner text,
               Description text);
               """)

print("Created new table nobel_prize_winner")

cursor.execute(f"CREATE INDEX idx ON {table_name} (Id)")
print("Created SQL index")

#Load data into the table
csv_file  = pandas.read_csv("./data/nobel_prize_winner.csv")

