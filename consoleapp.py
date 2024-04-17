from azure.search.documents import SearchClient  
from azure.core.credentials import AzureKeyCredential 
from azure.search.documents.models import VectorizableTextQuery 
from azure.search.documents.models import (
    QueryType,QueryAnswerType
)

# ... (your existing code to set up the connection)
def vectorsearch(service_endpoint, index_name, aisearch_key):
    search_client = SearchClient(service_endpoint, index_name, credential=AzureKeyCredential(aisearch_key))
    
    while True:
        search_input = input("Enter your search command: ")
        if search_input.lower() == 'quit':
            break

        vector_query = VectorizableTextQuery(text=search_input, k_nearest_neighbors=2, fields="vector", exhaustive=True)
        
        results = search_client.search(
            search_text=None,
            vector_queries=[vector_query],
            select=["Id", "chunk", "db_table_id", "db_table_year", "db_table_discipline", "db_table_winner", "db_table_description"],
            top=2
        )

        for result in results:
            print(f"Nobel price result: {result['db_table_year']} {result['db_table_winner']} description: {result['db_table_description']}")

    print("Exiting the application.")

def hybridsearch(service_endpoint, index_name, aisearch_key):
    search_client = SearchClient(service_endpoint, index_name, credential=AzureKeyCredential(aisearch_key))

    while True:
        search_input = input("Enter your search command: ")
        if search_input.lower() == 'quit':
            break

        vector_query = VectorizableTextQuery(text=search_input, k_nearest_neighbors=2, fields="vector", exhaustive=True)

        results = search_client.search(
            search_text=search_input,
            vector_queries=[vector_query],
            select=["Id", "chunk", "db_table_id", "db_table_year", "db_table_discipline", "db_table_winner", "db_table_description"],
            top=2
        )

        for result in results:
            print(f"Nobel price result: {result['db_table_year']} {result['db_table_winner']} description: {result['db_table_description']}")

        print("Exiting the application.")

def vectorsemanticsearch(service_endpoint, index_name, aisearch_key):
    search_client = SearchClient(service_endpoint, index_name, credential=AzureKeyCredential(aisearch_key))
    while True:
        search_input = input("Enter your search command: ")
        if search_input.lower() == 'quit':
            break    

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

        print("Exiting the application.")
