#!/bin/bash

# Create all needed resources in azure
export TF_VAR_region="East US"
export TF_VAR_sqlpassword=$(openssl rand -base64 12)
export TF_VAR_sqlusername=$(openssl rand -base64 6)
export TF_VAR_start_ip_address=$(curl -s ifconfig.me/ip)
export TF_VAR_end_ip_address=$(curl -s ifconfig.me/ip)
terraform init
terraform plan -out "main.tfplan"
terraform apply "main.tfplan"
terraform apply "main.tfplan"

# Export all needed variables
PREFIX=$(terraform state show random_string.random | grep "id" | awk -F' = ' '{print $2}' | tr -d '"')
echo sqladmin=${TF_VAR_sqlusername}
echo sqlpassword=${TF_VAR_sqlpassword}
export AZURE_SEARCH_KEY=$(az search admin-key show --resource-group ${PREFIX}-aisearch-sql-rg --service-name ${PREFIX}-aisearch --query primaryKey -o tsv | rev | cut -c 2- | rev)
export AZURE_SEARCH_ENDPOINT="https://${PREFIX}-aisearch.search.windows.net"
export AZURE_SEARCH_INDEX_NAME="aiindex"
export SQL_SERVER_NAME="${PREFIX}-sqlserver-hybrid.database.windows.net"
export SQL_DATABASE_NAME="sqldb-hybrid"
export SQL_USERNAME=${TF_VAR_sqlusername}
export SQL_PASSWORD=${TF_VAR_sqlpassword}
export SQL_DRIVER="{ODBC Driver 18 for SQL Server}"
export OPENAI_API_KEY=$(az cognitiveservices account keys list --name ${PREFIX}-openaiaccount --resource-group ${PREFIX}-aisearch-sql-rg | jq -r .key1)
export OPENAI_API_TYPE="azure"
export OPENAI_URI="https://$(echo $TF_VAR_region | tr '[:upper:]' '[:lower:]' | tr -d ' ').openai.azure.com/"
export OPENAI_DEPLOYMENT="adadeployment"

# Move to the parent directory
cd ..

# Install Python packages
pip install -r requirements.txt

# Run Pyhon script
python3 main.py



