# Create all needed resources in azure
$env:TF_VAR_region = "West US"
$env:TF_VAR_sqlpassword = ConvertTo-SecureString -String (New-Guid).Guid -AsPlainText -Force
$env:TF_VAR_sqlusername = ConvertTo-SecureString -String (New-Guid).Guid -AsPlainText -Force
$env:TF_VAR_start_ip_address = Invoke-RestMethod -Uri 'https://api.ipify.org'
$env:TF_VAR_end_ip_address = Invoke-RestMethod -Uri 'https://api.ipify.org'
terraform init
terraform plan -out "main.tfplan"
terraform apply "main.tfplan"
terraform apply "main.tfplan"

# Export all needed variables
$PREFIX = terraform state show random_string.random | Select-String -Pattern "id" | ForEach-Object { $_ -replace '.*= ', '' } | ForEach-Object { $_ -replace '"', '' }
Write-Host "prefix=$PREFIX"
Write-Host "sqladmin=$env:TF_VAR_sqlusername"
Write-Host "sqlpassword=$env:TF_VAR_sqlpassword"
$env:AZURE_SEARCH_KEY = az search admin-key show --resource-group ${PREFIX}-aisearch-sql-rg --service-name ${PREFIX}-aisearch --query primaryKey -o tsv
$env:AZURE_SEARCH_ENDPOINT = "https://${PREFIX}-aisearch.search.windows.net"
$env:AZURE_SEARCH_INDEX_NAME = "aiindex"
$env:SQL_SERVER_NAME = "${PREFIX}-sqlserver-hybrid.database.windows.net"
$env:SQL_DATABASE_NAME = "sqldb-hybrid"
$env:SQL_USERNAME = $env:TF_VAR_sqlusername
$env:SQL_PASSWORD = $env:TF_VAR_sqlpassword
$env:SQL_DRIVER = "{ODBC Driver 18 for SQL Server}"
$env:OPENAI_API_KEY = az cognitiveservices account keys list --name ${PREFIX}-openaiaccount --resource-group ${PREFIX}-aisearch-sql-rg | ConvertFrom-Json | Select-Object -ExpandProperty key1
$env:OPENAI_API_TYPE = "azure"
$env:OPENAI_URI = "https://$(echo $env:TF_VAR_region | tr '[:upper:]' '[:lower:]' | tr -d ' ').openai.azure.com/"
$env:OPENAI_DEPLOYMENT = "adadeployment"

# Move to the parent directory
cd ..

# Install Python packages
pip install -r requirements.txt

# Run Pyhon script
python3 main.py
