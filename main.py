# Description: This file implements a configuration for Azure AI Search hybrid search by a given Azure SQL database.
# Chunking and vectorization is done by integrated vectorization in Azure AI Search.

import openai 
import pyodbc
import pandas
import os

#AISearch imports
import azure.core.credentials
import azure.search.documents
import azure.search.documents.indexes    
from azure.search.documents.indexes import SearchIndexerClient  
from azure.search.documents.indexes.models import (
    SearchIndexerDataContainer, SearchIndexerDataSourceConnection, SearchField, SearchFieldDataType, 
    VectorSearch, HnswAlgorithmConfiguration, VectorSearchAlgorithmKind, VectorSearchProfile, AzureOpenAIVectorizer, 
    AzureOpenAIParameters, SearchIndex, HnswParameters, SearchableField)
from azure.search.documents.indexes import SearchIndexClient

#OpenAI vars
openai.api_key = os.environ.get("OPENAI_API_KEY")
openai.api_type = os.environ.get("OPENAI_API_TYPE")
openai_uri = os.environ.get("OPENAI_URI")
openai_deployment = os.environ.get("OPENAI_DEPLOYMENT")

#AI Search vars
aisearch_key = os.environ.get("AZURE_SEARCH_KEY")
service_endpoint = os.environ.get("AZURE_SEARCH_ENDPOINT")
index_name = os.environ.get("AZURE_SEARCH_INDEX_NAME")
embedding_length = 1536

#Azure SQL vars
sql_server = os.environ.get("SQL_SERVER_NAME")
database_name = os.environ.get("SQL_DATABASE_NAME")
username = os.environ.get("SQL_USERNAME")
password = os.environ.get("SQL_PASSWORD")
sql_driver = os.environ.get("SQL_DRIVER")



#Azure SQL Connection string
connection_string = f"DRIVER={sql_driver};SERVER={sql_server};DATABASE={database_name};UID={username};PWD={password}"
print(connection_string)
co = pyodbc.connect(connection_string)
cursor = co.cursor()


table_name = "nobelprizewinners"
#drop if table exists
cursor.execute(f"DROP TABLE IF EXISTS {table_name}")

#Create table
cursor.execute(f"""
               CREATE TABLE {table_name}
               (ID INT IDENTITY(1,1) NOT NULL PRIMARY KEY, 
               Year int,
               Discipline text,
               Winner text,
               Description text);
               """)

print("Created new table "+ table_name) 

#create a sql index?

#Load data into the table

data  = pandas.read_csv("./data/nobel-prize-winners.csv")
df = pandas.DataFrame(data)

for row in df.itertuples():
    yearentry = row.year
    disciplineentry = row.discipline
    winnerentry = row.winner
    descentry = str(row.desc)
        
    cursor.execute("""
                   INSERT INTO nobel_prize_winner (Year, Discipline, Winner, Description)
                   VALUES (?,?,?,?)
                   """,
                   yearentry,
                   disciplineentry,
                   winnerentry,
                   descentry
                   )
co.commit()
    
print("Data loaded into SQL table")

#Azure SQL TCP connection string for Azure AI Search integration
#create connection between Azure SQL and Azure AI Search
sqltcpcon = f'Encrypt=True;TrustServerCertificate=False;Connection Timeout=30;Server=tcp:{sql_server};Database={database_name};User ID={username};Password={password};'

aisearch = SearchIndexerClient(service_endpoint, azure.core.credentials.AzureKeyCredential(aisearch_key))
search_container = SearchIndexerDataContainer(name=table_name)

data_source_connection = SearchIndexerDataSourceConnection(
    name=f"{table_name}-azuresqlcon",
    type="azuresql",
    connection_string=sqltcpcon,
    container=search_container
)

datacon = aisearch.create_or_update_data_source_connection(data_source_connection)

#create indexer with vector search configuration
#1. create fiels
#2. create indexer

#indexerfields
#id, chunk, vector 
#parameters of chunks
#db_table_id, db_table_year, db_table_discipline, db_table_winner, db_table_description 
#parameters of Azure SQL DB table
#latest implementation reference: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_vector_search.py
fields = [
    SearchField(name="Id", type=SearchFieldDataType.String, key=True),
    SearchField(name="chunk", type=SearchFieldDataType.String, sortable=False, filterable=False, facetable=False),
    SearchField(name="vector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single), vector_search_dimensions=embedding_length, vector_search_profile_name="vectorsearch-profile"),
    SearchField(name="db_table_id", type=SearchFieldDataType.String, sortable=False, filterable=False, facetable=False),
    SearchField(name="db_table_year", type=SearchFieldDataType.String, sortable=True, filterable=True, facetable=True),
    SearchField(name="db_table_discipline", type=SearchFieldDataType.String, sortable=True, filterable=True, facetable=True),
    SearchField(name="db_table_winner", type=SearchFieldDataType.String, sortable=True, filterable=True, facetable=True),
    SearchField(name="db_table_description", type=SearchFieldDataType.String, sortable=False, filterable=False, facetable=False)
]

vector_search_config = VectorSearch(
    
    profiles=[ 
        VectorSearchProfile(
            name="vectorsearch-profile",
            algorithm_configuration_name="hnsw-config",
            vectorizer="openai-ada" #can not find vectorizer?
        )
    ], #at least azure-search-documents 11.6.0b1 (preview in March 26, 2024). See https://pypi.org/project/azure-search-documents/#history
    algorithms=[
        HnswAlgorithmConfiguration(
            name="hnsw-config"
        )

    ],#there is no vectorizer in this version...
    vectorizers=[
        AzureOpenAIVectorizer(
            name="openai-ada",
            kind="azureOpenAI",
            azure_open_ai_parameters=AzureOpenAIParameters(
                resource_uri=openai_uri,
                deployment_id=openai_deployment,
                api_key=openai.api_key,
            )

        )
    ]
)
    
#TODO semantic configuration?
aisearch_client = SearchIndexClient(service_endpoint, azure.core.credentials.AzureKeyCredential(aisearch_key))
#Create search index with vector search configuration
try:
    search_index = SearchIndex(name=index_name, fields=fields, vector_search=vector_search_config)
    search_index_response = aisearch_client.create_or_update_index(search_index)
    print("indexer created successfully!") 
except Exception as e:
    print(e)

    


