import openai 
import azure.core.credentials
import azure.search.documents
import azure.search.documents.indexes    
from azure.search.documents.indexes.models import (
    SearchField, SearchFieldDataType, 
    VectorSearch, HnswAlgorithmConfiguration, VectorSearchProfile, AzureOpenAIVectorizer, 
    AzureOpenAIParameters, SearchIndex, HnswParameters, VectorSearchAlgorithmMetric, SemanticConfiguration, SemanticPrioritizedFields, 
    SemanticField, SemanticSearch)
from azure.search.documents.indexes import SearchIndexClient

# #AI Search vars
# aisearch_key = os.environ.get("AZURE_SEARCH_KEY")
# service_endpoint = os.environ.get("AZURE_SEARCH_ENDPOINT")
# index_name = os.environ.get("AZURE_SEARCH_INDEX_NAME")
# embedding_length = 1536

# #OpenAI vars
# openai.api_key = os.environ.get("OPENAI_API_KEY")
# openai.api_type = os.environ.get("OPENAI_API_TYPE")
# openai_uri = os.environ.get("OPENAI_URI")
# openai_deployment = os.environ.get("OPENAI_DEPLOYMENT")

#create indexer with vector search configuration
#1. create fiels
#2. create indexer

#indexerfields
#id, chunk, vector 
#parameters of chunks
#db_table_id, db_table_year, db_table_discipline, db_table_winner, db_table_description 
#parameters of Azure SQL DB table
#latest implementation reference: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/samples/sample_vector_search.py
def create_index(aisearch_key, service_endpoint, index_name, embedding_length, openai_key, openai_type, openai_uri, openai_deployment):
    openai.api_key =  openai_key
    openai.api_type = openai_type
    
    fields = [
    SearchField(name="Id", type=SearchFieldDataType.String, key=True, analyzer_name="keyword"),
    SearchField(name="chunk", type=SearchFieldDataType.String, sortable=False, filterable=False, facetable=False),
    SearchField(name="vector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single), vector_search_dimensions=embedding_length, vector_search_profile_name="vectorsearch-profile"),
    SearchField(name="db_table_id", type=SearchFieldDataType.String, sortable=True, filterable=True, facetable=True),
    SearchField(name="db_table_year", type=SearchFieldDataType.String, sortable=True, filterable=True, facetable=True),
    SearchField(name="db_table_discipline", type=SearchFieldDataType.String, sortable=True, filterable=True, facetable=True),
    SearchField(name="db_table_winner", type=SearchFieldDataType.String, sortable=True, filterable=True, facetable=True),
    SearchField(name="db_table_description", type=SearchFieldDataType.String, sortable=True, filterable=True, facetable=True)
    ]

    vector_search_config = VectorSearch(
    
    profiles=[ 
        VectorSearchProfile(
            name="vectorsearch-profile",
            algorithm_configuration_name="hnsw-config",
            vectorizer="openai-ada" 
        )
    ], #at least azure-search-documents 11.6.0b1 (preview in March 26, 2024). See https://pypi.org/project/azure-search-documents/#history
    algorithms=[
        HnswAlgorithmConfiguration(
            name="hnsw-config",
            parameters=HnswParameters(  
                m=4,  
                ef_construction=400,  
                ef_search=500,  
                metric=VectorSearchAlgorithmMetric.COSINE,  
            ),  
        )

    ],
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
    
    #add semantic configuration
    semantic_search_config = SemanticConfiguration(
        name=f"{index_name}-semantic",
        prioritized_fields=SemanticPrioritizedFields(
            content_fields=[SemanticField(field_name="chunk")]
        )
    )
    
    semantic_search = SemanticSearch(configurations=[semantic_search_config]) 
    
    aisearch_client = SearchIndexClient(service_endpoint, azure.core.credentials.AzureKeyCredential(aisearch_key))
    #Create search index with vector search configuration
    try:
        search_index = SearchIndex(name=index_name, fields=fields, vector_search=vector_search_config, semantic_search=semantic_search)
        search_index_response = aisearch_client.create_or_update_index(search_index)
        print("indexer created successfully!") 
    except Exception as e:
        print(e)