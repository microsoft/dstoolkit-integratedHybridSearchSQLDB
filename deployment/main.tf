
# Configure the Azure provider
terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "3.97.1"
    }
  }

  required_version = ">= 1.1.0"
}

provider "azurerm" {
  features {}
}
#random string generation
resource "random_string" "random" {
  length  = 8
  special = false
  lower   = true
  upper   = false
}

#get the environment variables
variable "region" {}
variable "sqlpassword" {}
variable "sqlusername" {}
variable "start_ip_address" {}
variable "end_ip_address" {}

#resource group. 
#Location is important since everyone else will inherit from here
resource "azurerm_resource_group" "rg" {
  name     = "${random_string.random.result}-aisearch-sql-rg"
  location = var.region
}
#Action needed: add sql credentials
resource "azurerm_mssql_server" "server" {
  name                         = "${random_string.random.result}-sqlserver-hybrid"
  resource_group_name          = azurerm_resource_group.rg.name
  location                     = azurerm_resource_group.rg.location
  administrator_login          = var.sqlusername
  administrator_login_password = var.sqlpassword
  version                      = "12.0"
}
#Azure SQL Database deployment
resource "azurerm_mssql_database" "db" {
  name      = "sqldb-hybrid"
  server_id = azurerm_mssql_server.server.id
}
#Action needed: add your local client ip address
resource "azurerm_mssql_firewall_rule" "firewallrule" {
  name             = "AllowIpRangeFromTF"
  server_id        = azurerm_mssql_server.server.id
  start_ip_address = var.start_ip_address
  end_ip_address   = var.end_ip_address

}
#allow all azure services to access the sql server
resource "azurerm_mssql_firewall_rule" "allow_azure_services" {
  name             = "AllowAzureServices"
  server_id        = azurerm_mssql_server.server.id
  start_ip_address = "0.0.0.0"
  end_ip_address   = "0.0.0.0"

}

#Azure OpenAI
resource "azurerm_cognitive_account" "openai" {
  name                = "${random_string.random.result}-openaiaccount"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  kind                = "OpenAI"
  sku_name            = "S0"
}
#OpenAI ada version 2 embedding 
resource "azurerm_cognitive_deployment" "deployment" {
  name                 = "adadeployment"
  cognitive_account_id = azurerm_cognitive_account.openai.id
  model {
    format  = "OpenAI"
    name    = "text-embedding-ada-002"
    version = "2"
  }

  scale {
    type = "Standard"
  }
}

#Azure AI Search with semantic ranker enabled
resource "azurerm_search_service" "search" {
  name                = "${random_string.random.result}-aisearch"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = "basic"
  semantic_search_sku = "free"
  replica_count       = 1
  partition_count     = 1
}
