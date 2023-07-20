git clone
cd fastapi-crud

# create ACR 
az acr create --name zacr1 --resource-group mygroup --sku standard --admin-enabled true
# update ACR name and build docker with image name
ACR_NAME=zacr1.azurecr.io
az acr build --registry $ACR_NAME --image zfastapi_demo1 .