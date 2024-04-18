# Hybrid Azure AI Search with Azure SQL DB

## Scenario
This repo shows how to make an Azure SQL DB searchable through Azure AI Search. In general it allows you to vectorize the data within the Azure SQL DB using an OpenAI embedding model and make ist searchable through requests that are also being vectorized. The hybrid part allows you to use classic search methods in combination with vector search an get the best result between both worlds.
We use Python and Python SDKs to implement this scenario while the resources are created using terraform.

![High Level Architecture of the Scenario showing Azure AI Search in the middle connected to Azure SQL DB, Azure OpenAI and the Python app.](/data/Architecture.png)

## Prerequisites 
- Since we are working with bash please work on a Linux machine, WSL2 or the Azure Cloud shell
- Install Python
    3.11
- Install the following System packages:
    - Pip (`apt install python3-pip`)
    - SQL Driver (`sudo apt-get install -y msodbcsql18`)
    - SQL Connection (`sudo apt install unixodbc-dev`)
    - Terraform (`sudo apt install terraform=1.4.4-*`)
- Azure Subscription with OpenAI and Ada Model enabled

## Repository

### Terraform
- Azure resource group
- Azure SQL server
    - Firewall Rule
        allow current IP address
        allow other Azure services
- Azure SQL DB
- Azure OpenAI
    - text-embedding-ada-002 model deployment
- Azure AI Search with Semantic Ranker enabled

### Python
- Create a new table in the Azure SQL DB and upload the CSV Data
    <details>
    <summary>
        Understand the data
    </summary>
    We are using the list of all nobelprize winners since 1901 containing the year they received the price, the discipline they work in, their name and a description of why they won the price.

    | year  | discipline | winner | description |
    | ----- | ---------- | ------ | ----------- | 
    | 1901  | chemistry  | Jacobus van Hoff | in recognition of the extraordinary services he has rendered by the discovery of the laws of chemical dynamics and osmotic pressure in solutions |
    | 1901  | literature | Sully Prudhomme | in special recognition of his poetic composition, which gives evidence of lofty idealism, artistic perfection and a rare combination of the qualities of both heart and intellect |

    </details>
- Create a Data source within the Azure AI Search service that links to the table previously created in the Azure SQL DB
    <details>
    <summary>
        Understand Data sources
    </summary>
        The Data sources that can be defined in the Azure AI Search service provide connection information for on demand or scheduled data refresh of a target index, pulling data from supported Azure data sources.
     
     ```json
        {
        "name": "nobelprizewinners-azuresqlcon", #Name of the data source
        "description": null, #Anything you want, or nothing at all
        "type": "azuresql", #Must be a supported data source
        "subtype": null,
        "credentials": { #Connection string for your data source
            "connectionString": "..."
        },
        "container": {
            "name": "[nobelprizewinners]", #Name of the table, view, collection, or blob container you wish to index
            "query": null
        },
        "dataChangeDetectionPolicy": null,
        "dataDeletionDetectionPolicy": null,
        "encryptionKey": null,
        "identity": null
        }
    ```


    </details>
- Create an Index within the Azure AI Search service that mapps the data from the datasource to the index, defines what data can be searched and what kind of index should be created - in this case vector search and bm25 search with a semantic ranker. The vectorizer will than vectorize the users search text to be able to apply it to the vectorized index.
    <details>
    <summary>
        Understand the Index
    </summary>

    ```json
        {  
        "name": "aiindex", #Name of the index
        "fields": [ #Fields to be created in the index that will be filled by the data from the DB
            {  
                "name": "db_table_description", #Name of the field
                "type": "SearchFieldDataType.String", #Type of the field being indexed
                "searchable": true (default where applicable) | false (only Edm.String and Collection(Edm.String) fields can be searchable),  
                "filterable": true (default) | false,  
                "sortable": true (default where applicable) | false (Collection(Edm.String) fields cannot be sortable),  
                "facetable": true (default where applicable) | false (Edm.GeographyPoint fields cannot be facetable),
            },
            {
                "name": "vector", #Needed to write the vector received from OpenAI into
                "type": "Collection(Edm.Single)",
                "dimensions": 1536, #
                "vectorSearchProfile": "hnsw-profile",
                "searchable": true,
                "retrievable": true
            },
            { ... 
            }
        ],
        "vectorizers": [ #This is where the user request will be sent
            {
                "name": "openai-ada", #Name of the vectorizer
                "kind": "azureOpenAI", #Value of predefinded kinds that sets the expectations against the following parameters
                "azureOpenAIParameters": { #Predefined key following kind
                    "resourceUri": "https://region.openai.azure.com/", #address of the OpenAI Service that will be used for vestorization
                    "deploymentId": "adadeployment", #Name you gave the text embedding model deployment
                    "apiKey": "xxx", #Key of your Azure OpenAI Service
                }
            }
        ],
        "vectorSearch": {
            "algorithms": [
                {
                    "name": "hnsw-config",
                    "kind": "hnsw",
                    "hnswParameters": {
                        "metric": "cosine",
                        "m": 4,
                        "efConstruction": 400,
                        "efSearch": 500
                    },
                    "exhaustiveKnnParameters": null
                },
                {
                    "name": "exhaustiveknn-config",
                    "kind": "exhaustiveKnn",
                    "hnswParameters": null,
                    "exhaustiveKnnParameters": {
                        "metric": "cosine"
                    }
                }
            ],
        },
        "profiles": [
            {
                "name": "hnsw-profile", #Name of the profile
                "algorithm": "hnsw-config", #There are two algorithms in Azure AI Search for vector search: KNN and HNSW, see below for more details,
                "vectorizer": "openai-ada" #Name of the vectorizer you chose
            },
            {
                "name": "knn-profile",
                "algorithm": "exhaustiveknn-config",
                "vectorizer": "openai-ada"
            }
        ],
        "similarity": (optional) {
            "@odata.type": "#Microsoft.Azure.Search.BM25Similarity",
            "k1": null,
            "b": null
        },
        "semantic": {
            "defaultConfiguration": null,
            "configurations": [
                {
                    "name": "aiindex-semantic",
                    "prioritizedFields": {
                        "titleField": null,
                        "prioritizedContentFields": [
                            {
                                "fieldName": "chunk"
                            }
                        ],
                        "prioritizedKeywordsFields": []
                    }
                }
            ]
        }
        }        
    ```
    </details>

    <details>
    <summary>
        Understand the vector search
    </summary>

    </details>
    <details>
    <summary>
        Understand the bm25
    </summary>

    </details>
    <details>
    <summary>
        Understand the semantic ranker
    </summary>

    </details>
- Create a Skillset within the Azure AI Search service that links to the Ada embedding model deployment in the Azure OpenAI service
    <details>
    <summary>
        Understand the Skillsets
    </summary>

    ```json
        {
            "skills": [
                {
                    "@odata.type": "#Microsoft.Skills.Text.SplitSkill",
                    "name": "#1", #Name of the Skill
                    "description": null,
                    "context": "/document/reviews_text", #Scope of the operation, which could be once per document or once for each item in a collection
                    "defaultLanguageCode": "en",
                    "textSplitMode": "pages",
                    "maximumPageLength": 5000,
                    "inputs": [ #Originate from nodes in an enriched document
                        {
                            "name": "text",
                            "source": "/document/reviews_text" #Identify a given node
                        }
                    ],
                    "outputs": [ #send back to the enriched document as a new node
                        {
                            "name": "textItems",
                            "targetName": "pages"
                        }
                    ]
                },
                {
                    "@odata.type": "#Microsoft.Skills.Text.SentimentSkill",
                    "name": "#2",
                    "description": null,
                    "context": "/document/reviews_text/pages/*",
                    "defaultLanguageCode": "en",
                    "inputs": [
                        {
                            "name": "text",
                            "source": "/document/reviews_text/pages/*",
                        }
                    ],
                    "outputs": [
                        {
                            "name": "sentiment",
                            "targetName": "sentiment"
                        },
                        {
                            "name": "confidenceScores",
                            "targetName": "confidenceScores"
                        },
                        {
                            "name": "sentences",
                            "targetName": "sentences"
                        }
                    ]
                }
            . . .
        ]
        }
    ```

    </details>
    <details>
    <summary>
        Understand the Ada embedding model
    </summary>

    </details>
- Create an Indexer within the Azure AI Search service that links to the Skillset and the Data source
    <details>
    <summary>
        Understand the Indexer
    </summary>

    </details>
![More detailed Architecture of the Scenario showing Azure AI Search in the middle connected to Azure SQL DB, Azure OpenAI and the Python app.](/data/Architecture_Detail.png)

## 1. Create Resources
1. To create all the resources mentioned in the Terraform section and the settings in the Python section of this repo we created a Bash script for you.
Clone this repo either to a Linux machine, WSL2 or to the Azure Cloud shell.
```git clone repolink```
1. Potentially change the region where the resources will be created in `/deployment/deploy.sh` line 4. Be aware that the services are not available in all regions.
1. Execute the Bash script that applies the terraform template, stores the environment variables and executes the python code. To do so navigate to the repo you cloned and type
```bash /deployment/deploy.sh```
1. Go to `portal.azure.com`, find your resource group and look at the different resources created. Specifically Azure AI Search, the Index, Indexer, Datasource and Skillset are important. Look at the JSON definitions created here.

## 2. Test Resources
The first run of this repo will search for "Einstein" in the data and return the result in the console. If you want to test more options you can run the ```logic.sh``` script. You can change the search options in ```main.py``` by setting them True. The options are:
- **Hybrid Search**
- **Semantic Search**
- **Vector Search**
- **App** - this runs a console app so you can continuously create querries and receive responses

## 3. Adapt Repository

### Different Search functionalities
If you have already deployed all the resources and only wish to run a different scenario - eg. use hybrid search instead of only vector search - you have to enter your current PREFIX in the deploy.sh. Additionally you need to navigate to main.py and change the value of enroll to == False and the other variabled accordingly.

### Different Database

### Retrain when new Data arrives

### ...

## Potential Errors

- For some reason Windows added \r to some variables in the bash script. If you get an error like this, tun the following to fix the error: ```sed -i 's/\r//g' deploy.sh```