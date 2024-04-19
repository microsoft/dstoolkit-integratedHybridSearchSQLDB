#!/bin/bash

# Select the resource group where all the needed services reside
RESOURCE_GROUPS=$(az group list --query "[?ends_with(name, 'aisearch-sql-rg')].name" -o tsv)
if [ -z "$RESOURCE_GROUPS" ]; then
    echo "You need to run the deploy.sh first to create the needed resources"
    exit 1
fi

if [ $(echo "$RESOURCE_GROUPS" | wc -l) -eq 1 ]; then
    RESOURCE_GROUP="$RESOURCE_GROUPS"
else
    echo "Available resource groups:"
    echo "$RESOURCE_GROUPS"
    read -p "Choose a resource group: " RG
    if ! echo "$RESOURCE_GROUPS" | grep -q "$RG"; then
        echo "Invalid resource group selected."
        exit 1
    fi

    RESOURCE_GROUP="$RG"
fi

# Export all needed variables
PREFIX=${RESOURCE_GROUP:0:8}
export AZURE_SEARCH_KEY=$(az search admin-key show --resource-group ${PREFIX}-aisearch-sql-rg --service-name ${PREFIX}-aisearch --query primaryKey -o tsv | tr -d '\r')
export AZURE_SEARCH_ENDPOINT="https://${PREFIX}-aisearch.search.windows.net"
export AZURE_SEARCH_INDEX_NAME="aiindex"
echo prefix of resource group = $PREFIX

# Move to the parent directory
cd ..

# Install Python packages
pip install -r requirements.txt

# Run Pyhon script
python main.py