# Hybrid Azure AI Search with Azure SQL DB

## Scenario



## Prerequisites 
- Python
    3.11
- System packages:
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
- Create new table in the Azure SQL DB and upload the CSV Data
    <details>
        <summary>
            Understand the data
        </summary>

            | First Header  | Second Header |
            | ------------- | ------------- |
            | Content Cell  | Content Cell  |
            | Content Cell  | Content Cell  |

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
- Create an Index within the Azure AI Search service that mapps the data from the datasource to the index, defines what data can be searched and defines what kind of index should be created - in this case vector search and bm25 search with a semantic ranker??
++ VECTORIZER
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
            }
        ],
        "similarity": (optional) { },
        "suggesters": (optional) [ ... ],  
        "scoringProfiles": (optional) [ ... ],  
        "analyzers":(optional) [ ... ],
        "charFilters":(optional) [ ... ],
        "tokenizers":(optional) [ ... ],
        "tokenFilters":(optional) [ ... ],
        "defaultScoringProfile": (optional) "Name of a custom scoring profile to use as the default",  
        "corsOptions": (optional) { },
        "encryptionKey":(optional) { }  
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
- 

## 1. Create Resources
1. To create all the resources mentioned in the Terraform section and the settings in the Python section of this repo we created a Bash script for you.
Clone this repo either to a Linux machine, WSL2 or to the Azure Cloud shell.
```git clone repolink```
1. Potentially change region in `/deployment/deploy.sh` line 4
1. Execute the Bash script that executes the terraform template, stores the environment variables and executes the python code. Navigate to the repo you cloned.
```bash /deployment/deploy.sh```
1. 


## 2. Test Resources


## 3. Adapt Repository

### Different Database

### Retrain when new Data arrives

### ...

## Potential Errors

```sed -i 's/\r//g' script.sh```