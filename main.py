# Description: This file implements a configuration for Azure AI Search hybrid search by a given Azure SQL database.
# Chunking and vectorization is done by integrated vectorization in Azure AI Search.

import openai 


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

