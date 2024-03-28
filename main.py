# Description: This file implements a configuration for Azure AI Search hybrid search by a given Azure SQL database.
# Chunking and vectorization is done by integrated vectorization in Azure AI Search.

# import openai 
# import os

import azuresql
import index
import skillset
import indexer
from azure.search.documents import SearchClient  
import os
from azure.core.credentials import AzureKeyCredential 
from azure.search.documents.models import VectorizableTextQuery 
from azure.search.documents.models import (
    QueryType)
# #OpenAI vars
# openai.api_key = os.environ.get("OPENAI_API_KEY")
# openai.api_type = os.environ.get("OPENAI_API_TYPE")
# openai_uri = os.environ.get("OPENAI_URI")
# openai_deployment = os.environ.get("OPENAI_DEPLOYMENT")

# #AI Search vars
aisearch_key = os.environ.get("AZURE_SEARCH_KEY")
service_endpoint = os.environ.get("AZURE_SEARCH_ENDPOINT")
index_name = os.environ.get("AZURE_SEARCH_INDEX_NAME")
# embedding_length = 1536

# #Azure SQL vars
# sql_server = os.environ.get("SQL_SERVER_NAME")
# database_name = os.environ.get("SQL_DATABASE_NAME")
# username = os.environ.get("SQL_USERNAME")
# password = os.environ.get("SQL_PASSWORD")
# sql_driver = os.environ.get("SQL_DRIVER")

#create a new Azure SQL database and loads data from a CSV file into the database.
azuresql.create_db_and_aisearch_connection()

#create indexer with vector search configuration
index.create_index()

#create a skillset for Azure AI Search with Azure OpenAi Embedding and TextSplit
skillset.createSkillset()

#create indexer with index, data source and skillset
indexer.create_indexer()

#DNS issues? https://moonape1226.medium.com/domain-resolve-error-name-or-service-not-known-forazure-openai-service-domain-c32607357e57
#vector search
search_input = "time is relative"

search_client = SearchClient(service_endpoint, index_name, credential=AzureKeyCredential(aisearch_key))
vector_query = VectorizableTextQuery(text=search_input, k_nearest_neighbors=2, fields="vector", exhaustive=True)

results = search_client.search(
    search_text=None,
    vector_queries=[vector_query],
    select=["Id", "chunk", "db_table_id", "db_table_year", "db_table_discipline", "db_table_winner", "db_table_description"],
    top=2
)

for results in results:
    print(f"Nobel price result: {'db_table_year'} {'db_table_winner'}")
    
#hybrid search
# search_input = "time is relative"

# search_client = SearchClient(service_endpoint, index_name, credential=AzureKeyCredential(aisearch_key))
# vector_query = VectorizableTextQuery(text=search_input, k_nearest_neighbors=2, fields="vector", exhaustive=True)

# results = search_client.search(
#     search_text=search_input,
#     vector_queries=[vector_query],
#     select=["Id", "chunk", "db_table_id", "db_table_year", "db_table_discipline", "db_table_winner", "db_table_description"],
#     top=2
# )

# for results in results:
#     print(f"Nobel price result: {'db_table_year'} {'db_table_winner'}")