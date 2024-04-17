#Description: Create an indexer to index data from Azure SQL DB, skillset and index.
#Afterwards it runs the indexer.
import logging
from azure.search.documents.indexes.models import SearchIndexer
from azure.search.documents.indexes import SearchIndexerClient
from azure.core.credentials import AzureKeyCredential

#to run this code indipendently, uncomment the following lines and make sure to set your environment variables
#
# service_endpoint = os.environ.get("AZURE_SEARCH_ENDPOINT")
# index_name = os.environ.get("AZURE_SEARCH_INDEX_NAME")
# aisearch_key = os.environ.get("AZURE_SEARCH_KEY")

def create_indexer(service_endpoint, index_name, aisearch_key):
    indexer_name = f"{index_name}-indexer"
    logging.info(f"Start creating indexer {indexer_name}")
    indexer = SearchIndexer(
        name=indexer_name,
        description="Indexer to index data from Azure SQL DB, chunk text and vectorize it",
        skillset_name=index_name + "-skillset",
        target_index_name=index_name,
        data_source_name="nobelprizewinners-azuresqlcon" #TODO make it smarter
    )
    logging.info(f"created indexer configuration for {indexer_name}. Skillset: {indexer.skillset_name}, Target Index: {indexer.target_index_name}, Data Source: {indexer.data_source_name}")
    
    indexer_c = SearchIndexerClient(service_endpoint, AzureKeyCredential(aisearch_key))
    indexer_result = indexer_c.create_or_update_indexer(indexer)

    logging.info(f"Indexer {indexer_result.name} created")
    
    logging.info(f"Start running indexer {indexer_name}")
    
    indexer_c.run_indexer(indexer_name) #add waiting time for bigger dbs, insert status check
    logging.info(f"Running indexer {indexer_name} is finished")