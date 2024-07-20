#!/bin/bash
set -e  # Exit immediately if a command exits with a non-zero status.

# Variables (customize these values)
RESOURCE_GROUP="ITP-MLOps-Team-Cognitive-Services-RG"
LOCATION="East US"
APP_SERVICE_PLAN="asp-intuitivescotia (B1: 1)"
WEB_APP_NAME="Datasourcing"
RUNTIME="PYTHON:3.8"

# Login to Azure (for non-interactive login, use a service principal or managed identity)
az login

# Set the subscription (optional, uncomment and set your subscription ID if needed)
# az account set --subscription "your-subscription-id"

# Create a resource group if it doesn't exist
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create an App Service plan if it doesn't exist
az appservice plan create --name $APP_SERVICE_PLAN --resource-group $RESOURCE_GROUP --sku FREE

# Create a web app if it doesn't exist
az webapp create --name $WEB_APP_NAME --resource-group $RESOURCE_GROUP --plan $APP_SERVICE_PLAN --runtime $RUNTIME

# Deploy the code to Azure App Service (assuming the code is in the current directory)
az webapp up --name $WEB_APP_NAME --resource-group $RESOURCE_GROUP --plan $APP_SERVICE_PLAN --runtime $RUNTIME
