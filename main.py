# Description: This file implements a configuration for Azure AI Search hybrid search by a given Azure SQL database.
# Chunking and vectorization is done by integrated vectorization in Azure AI Search.

# import openai 
# import os

import azuresql
import index
import skillset

# #OpenAI vars
# openai.api_key = os.environ.get("OPENAI_API_KEY")
# openai.api_type = os.environ.get("OPENAI_API_TYPE")
# openai_uri = os.environ.get("OPENAI_URI")
# openai_deployment = os.environ.get("OPENAI_DEPLOYMENT")

# #AI Search vars
# aisearch_key = os.environ.get("AZURE_SEARCH_KEY")
# service_endpoint = os.environ.get("AZURE_SEARCH_ENDPOINT")
# index_name = os.environ.get("AZURE_SEARCH_INDEX_NAME")
# embedding_length = 1536

# #Azure SQL vars
# sql_server = os.environ.get("SQL_SERVER_NAME")
# database_name = os.environ.get("SQL_DATABASE_NAME")
# username = os.environ.get("SQL_USERNAME")
# password = os.environ.get("SQL_PASSWORD")
# sql_driver = os.environ.get("SQL_DRIVER")

#create a new Azure SQL database and loads data from a CSV file into the database.
#azuresql.create_db_and_aisearch_connection()

#create indexer with vector search configuration
index.create_index()

skillset.createSkillset()