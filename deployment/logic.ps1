# Get the list of resource groups ending with the specified suffix using Azure CLI
$RESOURCE_GROUPS = az group list --query "[?ends_with(name, 'aisearch-sql-rg')].name" --output tsv

# Check if any matching resource groups were found
if (-not $RESOURCE_GROUPS) {
    Write-Host "You need to run the deploy.sh first to create the needed resources"
    exit
} else {
    # Display the list of matching resource groups
    Write-Host "Available resource groups:"
    $RESOURCE_GROUPS | ForEach-Object {
        Write-Host "- $_"
    }

    # Prompt the user to enter the name of the resource group
    $RESOURCE_GROUP = Read-Host "Choose a resource group"

    # Check if the entered name is in the list of resource groups
    if ($RESOURCE_GROUPS -contains $RESOURCE_GROUP) {
        Write-Host "Selected resource group: $RESOURCE_GROUP"
    } else {
        Write-Host "Invalid resource group selected."
        exit
    }
}

# Export all needed variables
$PREFIX = $RESOURCE_GROUP.Substring(0, 8)
$env:AZURE_SEARCH_KEY = az search admin-key show --resource-group ${PREFIX}-aisearch-sql-rg --service-name ${PREFIX}-aisearch --query primaryKey -o tsv
$env:AZURE_SEARCH_ENDPOINT = "https://${PREFIX}-aisearch.search.windows.net"
$env:AZURE_SEARCH_INDEX_NAME = "aiindex"
Write-Host $env:AZURE_SEARCH_KEY
Write-Host "prefix  = $PREFIX"

# Move to the parent directory
cd ..

# Install Python packages
pip install -r requirements.txt

# Run Python script
python main.py