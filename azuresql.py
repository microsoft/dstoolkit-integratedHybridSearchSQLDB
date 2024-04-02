# Description: This file creates a new Azure SQL database and loads data from a CSV file into the database. 
# Afterwards it connects to Azure AI Search as a data source.

import pyodbc
import pandas
#AISearch imports
import azure.core.credentials
import azure.search.documents
import azure.search.documents.indexes    
from azure.search.documents.indexes import SearchIndexerClient  
from azure.search.documents.indexes.models import (
    SearchIndexerDataContainer, SearchIndexerDataSourceConnection)


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

def create_db_and_aisearch_connection(aisearch_key, service_endpoint, sql_server, database_name, username, password, sql_driver):
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
                    INSERT INTO nobelprizewinners (Year, Discipline, Winner, Description)
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
    print("Data source connection created successfully!")