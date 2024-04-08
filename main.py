# This file imports all necessary environment variables and runs the main functions to create a new Azure SQL database,
# load data from a CSV file into the database,
# create an Azure AI Search index with vector search configuration,
# create a skillset for Azure AI Search with Azure OpenAi Embedding and TextSplit,
# and create an indexer with index, data source, and skillset.


import os
import time
import logging
import azuresql
import openai 
import index
import skillset
import indexer
from azure.search.documents import SearchClient  
from azure.core.credentials import AzureKeyCredential 
from azure.search.documents.models import VectorizableTextQuery 
from azure.search.documents.models import (
    QueryType,QueryAnswerType
)

#Debug mode
#set stderr_logs to True if you want to see logs in the console
stderr_logs = True

#enables the vector search sample request below
vectorsearchsample = True

#enables the hybrid search sample request below
hyrbidsearchsample = False

#enables the hybrid search with semantic reranking sample request below
vectorsemanticsearchsample = False

#specifies if the user wants (or needs) to create the AI Search configuration for Azure SQL integrated vectorization.
enroll = True


if stderr_logs:
    logging_handlers = [
        logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ]
else:
    logging_handlers = [
        logging.FileHandler("debug.log")
    ]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=logging_handlers
)

logging.info("Starting the main script")
start_time = time.time()

# #OpenAI vars
openai.api_key = os.environ.get("OPENAI_API_KEY")
openai.api_type = os.environ.get("OPENAI_API_TYPE")
openai_uri = os.environ.get("OPENAI_URI")
openai_deployment = os.environ.get("OPENAI_DEPLOYMENT")

# #AI Search vars
aisearch_key = os.environ.get("AZURE_SEARCH_KEY")
service_endpoint = os.environ.get("AZURE_SEARCH_ENDPOINT")
index_name = os.environ.get("AZURE_SEARCH_INDEX_NAME")
embedding_length = 1536

# #Azure SQL vars
sql_server = os.environ.get("SQL_SERVER_NAME")
database_name = os.environ.get("SQL_DATABASE_NAME")
username = os.environ.get("SQL_USERNAME")
password = os.environ.get("SQL_PASSWORD")
sql_driver = os.environ.get("SQL_DRIVER")

#search input defines the term that should be searched in the index
search_input = "Einstein"

if enroll:
    logging.info("Enroll mode: Enrolling Azure AI Search with Azure SQL integrated vectorization")
    
    #create a new Azure SQL database and loads data from a CSV file into the database. 
    azuresql.create_db_and_aisearch_connection(aisearch_key, service_endpoint, sql_server, database_name, username, password, sql_driver)

    #create indexer with vector search configuration
    index.create_index(aisearch_key, service_endpoint, index_name, embedding_length, openai.api_key, openai.api_type, openai_uri, openai_deployment)

    #create a skillset for Azure AI Search with Azure OpenAi Embedding and TextSplit
    skillset.createSkillset(openai_uri, openai_deployment, openai.api_key, index_name, service_endpoint, aisearch_key)

    #create indexer with index, data source and skillset
    indexer.create_indexer(service_endpoint, index_name, aisearch_key)

#vector search
#This is a sample request for a vector search. It takes a text input and returns the most similar vector from the index.
#
if vectorsearchsample:
    
    logging.info(f"Vector search enabled. Running vector search sample request with search input {search_input}")

    search_client = SearchClient(service_endpoint, index_name, credential=AzureKeyCredential(aisearch_key))
    vector_query = VectorizableTextQuery(text=search_input, k_nearest_neighbors=2, fields="vector", exhaustive=True)

    results = search_client.search(
        search_text=None,
        vector_queries=[vector_query],
        select=["Id", "chunk", "db_table_id", "db_table_year", "db_table_discipline", "db_table_winner", "db_table_description"],
        top=2
    )

    for result in results:
        print(f"Nobel price result: {result['db_table_year']} {result['db_table_winner']} description: {result['db_table_description']}")
        

#hybrid search
#This is a sample request for a hybrid search. Additionally to the vector search, it also searches for the text input in the index.
if hyrbidsearchsample:
    
    logging.info(f"Hybrid search enabled. Running hybrid search sample request with search input {search_input}")
    
    search_client = SearchClient(service_endpoint, index_name, credential=AzureKeyCredential(aisearch_key))
    vector_query = VectorizableTextQuery(text=search_input, k_nearest_neighbors=2, fields="vector", exhaustive=True)

    results = search_client.search(
        search_text=search_input,
        vector_queries=[vector_query],
        select=["Id", "chunk", "db_table_id", "db_table_year", "db_table_discipline", "db_table_winner", "db_table_description"],
        top=2
    )

    for result in results:
        print(f"Nobel price result: {result['db_table_year']} {result['db_table_winner']} description: {result['db_table_description']}")

#hybrid search with semantic reranking
#This is a sample request for a hybrid search with semantic reranking.
if vectorsemanticsearchsample:
    logging.info(f"Hybrid semantic search enabled. Running hybrid search in combination with semantic search with sample request with search input {search_input}")
    
    search_client = SearchClient(service_endpoint, index_name, credential=AzureKeyCredential(aisearch_key))
    vector_query = VectorizableTextQuery(text=search_input, k_nearest_neighbors=2, fields="vector", exhaustive=True)

    results = search_client.search(
        search_text=search_input,
        vector_queries=[vector_query],
        select=["Id", "chunk", "db_table_id", "db_table_year", "db_table_discipline", "db_table_winner", "db_table_description"],
        query_type=QueryType.SEMANTIC,
        semantic_configuration_name=f"{index_name}-semantic",
        query_caption=QueryAnswerType.EXTRACTIVE,
        query_answer=QueryAnswerType.EXTRACTIVE,
        top=2
    )

    semantic_results = results.get_answers()
    if semantic_results:
        for result in semantic_results:
            if result.highlights:
                print(f"Semantic search result (highlight): {result.highlights}")
            else:
                print(f"Semantic search result: {result.text}")
            
            print(f"Semantic results score:  {result.score}")
            

    for result in results:
        print(f"Nobel price result: {result['db_table_year']} {result['db_table_winner']} description: {result['db_table_description']}")
        captions = result["@search.captions"]
        if captions:
            caption = captions[0]
            if caption.highlights:
                print(f"Caption: {caption.highlights}")
            else:
                print(f"Caption: {caption.text}")
                
logging.info(f"Finished execution in {time.time() - start_time} seconds")