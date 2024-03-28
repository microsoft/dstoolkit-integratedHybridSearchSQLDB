#!/bin/bash

# Create all needed resources in azure
export TF_VAR_region="us-west-2"
export TF_VAR_sqlpassword=""
terraform init
terraform plan -out "main.tfplan"
terraform apply "main.tfplan"
PREFIX = terraform state show random_string.random | grep "id"
AZURE_SEARCH_KEY = $(az search admin-key show --resource-group aisearch-sql-integrated --service-name ${PREFIX}-aisearch --query primaryKey -o tsv)
AZURE_SEARCH_ENDPOINT = "https://${PREFIX}-aisearch.search.windows.net"
AZURE_SEARCH_INDEX_NAME = "aiindex"
SQL_SERVER_NAME = "${PREFIX}-sqlserver-hybrid"
SQL_DATABASE_NAME = "sqldb-hybrid"
SQL_USERNAME = $(az sql server show --name ${PREFIX}-sqlserver-hybrid --resource-group aisearch-sql-integrated --query administratorLogin -o tsv)
SQL_PASSWORD = ""
SQL_DRIVER = ""
OPENAI_API_KEY = $(az cognitiveservices account keys list --name ${PREFIX}-openaiaccount --resource-group aisearch-sql-integrated --query primaryKey -o tsv)
OPENAI_API_TYPE = "azure"
OPENAI_URI = "https://${PREFIX}-openaiaccount.openai.azure.com/"
OPENAI_DEPLOYMENT = "text-embedding-ada-002"
cd ..



