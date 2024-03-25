# Configure the Azure provider
terraform {
  required_providers {
    azurerm = {
      source = "hashicorp/azurerm"
      version = "3.97.1"
    }
  }

  required_version = ">= 1.1.0"
}

provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "rg"{
  name  = "aisearch-sql-integrated"
  location = "East US"
}

resource "azurerm_mssql_server" "server"{
  name                       = "sqlserver-hybrid"
  resource_group_name        = azurerm_resource_group.rg.name
  location                   = azurerm_resource_group.rg.location
  administrator_login        = ""
  administrator_login_password = ""
  version                    = "12.0"
}

resource "azurerm_mssql_database" "db" {
  name = "sqldb-hybrid"
  server_id = azurerm_mssql_server.server.id
}

resource "azurerm_mssql_firewall_rule" "firewallrule" {
  name                = "AllowIpRangeFromTF"
  server_id           = azurerm_mssql_server.server.id
  start_ip_address = "0.0.0.0"
  end_ip_address   = "0.0.0.0" #replace the IP addresses with your own (range)
  
  }

  #Azure OpenAI
  resource "azurerm_cognitive_account" "openai" {
    name                = "openaiaccount"
    resource_group_name = azurerm_resource_group.rg.name
    location            = azurerm_resource_group.rg.location
    kind                = "OpenAI"
    sku_name            = "S0"
  }

  resource "azurerm_cognitive_deployment" "deployment" {
    name                = "adadeployment"
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
  
  #Azure AI Search
  resource "azurerm_search_service" "search" {
    name                = "aisearch"
    resource_group_name = azurerm_resource_group.rg.name
    location            = azurerm_resource_group.rg.location
    sku                 = "basic"
    replica_count       = 1
    partition_count     = 1
  }