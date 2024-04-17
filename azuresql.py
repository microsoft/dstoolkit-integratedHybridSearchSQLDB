# Description: This file creates a new Azure SQL database and loads data from a CSV file into the database. 
# Afterwards it connects to Azure AI Search as a data source.
import logging
import pyodbc
import pandas
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexerClient
from azure.search.documents.indexes.models import (
    SearchIndexerDataContainer, SearchIndexerDataSourceConnection)

#to run this code indipendently, uncomment the following lines and make sure to set your environment variables
#
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
    logging.info("Creating a Azure SQL DB Table and importing data from CSV file")
    #Azure SQL Connection string
    connection_string = f"DRIVER={sql_driver};SERVER=tcp:{sql_server};DATABASE={database_name};UID={username};PWD={password}"
    logging.info(f"Connection String for Azuer SQL DB: {connection_string}")
    #TODO: add error handling
    co = pyodbc.connect(connection_string)
    cursor = co.cursor()


    table_name = "nobelprizewinners"
    logging.info(f"Creating table {table_name}")
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

    logging.info(f"Finished creating new table {table_name}") 


    #Load data into the Azure SQL Database table
    csv_file_path = "./data/nobel-prize-winners.csv"
    logging.info(f"Loading data from {csv_file_path} into {table_name}")
    data  = pandas.read_csv(csv_file_path)
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
        
    logging.info(f"Data loaded into {table_name} successfully")

    #Azure SQL TCP connection string for Azure AI Search integration
    #creates a connection between Azure SQL and Azure AI Search
    sqltcpcon = f'Encrypt=True;TrustServerCertificate=False;Connection Timeout=30;Server=tcp:{sql_server};Database={database_name};User ID={username};Password={password};'
    logging.info(f"SQL TCP Connection String for Azure AI Search: {sqltcpcon}")
    
    logging.info("Creating a data source connection for Azure AI Search")
    aisearch = SearchIndexerClient(service_endpoint, AzureKeyCredential(aisearch_key))
    search_container = SearchIndexerDataContainer(name=table_name)

    data_source_connection = SearchIndexerDataSourceConnection(
        name=f"{table_name}-azuresqlcon",
        type="azuresql",
        connection_string=sqltcpcon,
        container=search_container
    )

    datacon = aisearch.create_or_update_data_source_connection(data_source_connection)
    logging.info(f"Data source connection {datacon.name} created")