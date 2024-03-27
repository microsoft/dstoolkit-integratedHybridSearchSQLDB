#file to create an indexer with index, data source and skillset.

from azure.search.documents.indexes.models import SearchIndexer
import os
from azure.search.documents.indexes import SearchIndexerClient
from azure.core.credentials import AzureKeyCredential

service_endpoint = os.environ.get("AZURE_SEARCH_ENDPOINT")
index_name = os.environ.get("AZURE_SEARCH_INDEX_NAME")
aisearch_key = os.environ.get("AZURE_SEARCH_KEY")

def create_indexer():
    indexer_name = f"{index_name}-indexer"

    indexer = SearchIndexer(
        name=indexer_name,
        description="Indexer to index data from Azure SQL DB, chunk text and vectorize it",
        skillset_name=index_name + "-skillset",
        target_index_name=index_name,
        data_source_name="nobelprizewinners-azuresqlcon" #TODO make it smarter
    )
    #TODO: need firewall rule for Azure SQL DB 
    indexer_c = SearchIndexerClient(service_endpoint, AzureKeyCredential(aisearch_key))
    indexer_result = indexer_c.create_or_update_indexer(indexer)

    indexer_c.run_indexer(indexer_name) #add waiting time for bigger dbs, insert status check
    print(f"{indexer_name} created")