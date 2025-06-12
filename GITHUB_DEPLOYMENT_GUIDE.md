# GitHub Deployment Guide for Azure TiTiler

This guide walks you through setting up GitHub repository and connecting it to Azure App Service for automatic deployments.

## Prerequisites

- Azure CLI installed and logged in
- GitHub account
- Azure subscription with resource group created

## Step 1: Create GitHub Repository

1. Go to GitHub and create a new repository named `azure-titiler`
2. Don't initialize with README (we already have one)

## Step 2: Push Code to GitHub

```bash
# Navigate to the project directory
cd /home/danby/phaser-june/azure-titiler

# Initialize git repository
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: TiTiler Azure deployment"

# Add your GitHub repository as origin
git remote add origin https://github.com/YOUR_USERNAME/azure-titiler.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## Step 3: Create Azure Resources

If you haven't already, create the Azure resources:

```bash
# Create resource group
az group create --name titiler-rg --location eastus

# Create storage account for COGs
az storage account create \
  --name phasertitiler \
  --resource-group titiler-rg \
  --location eastus \
  --sku Standard_LRS \
  --kind StorageV2 \
  --allow-blob-public-access true

# Create App Service plan
az appservice plan create \
  --name titiler-plan \
  --resource-group titiler-rg \
  --sku B1 \
  --is-linux

# Create Web App
az webapp create \
  --name my-titiler \
  --resource-group titiler-rg \
  --plan titiler-plan \
  --runtime "PYTHON|3.11"
```

## Step 4: Configure Azure App Service for GitHub Deployment

### Option A: Using Azure Portal (Recommended for first-time setup)

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to your App Service: `my-titiler`
3. In the left menu, select **Deployment Center**
4. Choose **GitHub** as the source
5. Click **Authorize** and sign in to GitHub
6. Select:
   - Organization: Your GitHub username
   - Repository: `azure-titiler`
   - Branch: `main`
7. For **Authentication type**, select **User-assigned identity**
8. Click **Save**

Azure will automatically:
- Create a workflow file in your repository
- Set up the necessary secrets
- Configure the deployment pipeline

### Option B: Using Azure CLI

```bash
# Create a service principal for GitHub Actions
az ad sp create-for-rbac \
  --name "github-actions-titiler" \
  --role contributor \
  --scopes /subscriptions/{subscription-id}/resourceGroups/titiler-rg \
  --json-auth > azure-credentials.json

# The output contains the credentials needed for GitHub secrets
```

## Step 5: Configure GitHub Secrets

If you used Option B or need to manually configure:

1. Go to your GitHub repository
2. Navigate to **Settings** > **Secrets and variables** > **Actions**
3. Add these secrets:
   - `AZUREAPPSERVICE_CLIENTID`: From azure-credentials.json
   - `AZUREAPPSERVICE_TENANTID`: From azure-credentials.json
   - `AZUREAPPSERVICE_SUBSCRIPTIONID`: Your Azure subscription ID

## Step 6: Configure App Settings

Set the environment variables for your App Service:

```bash
# Set Supabase database URL
az webapp config appsettings set \
  --resource-group titiler-rg \
  --name my-titiler \
  --settings SUPABASE_DATABASE_URL="postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres"

# Set Azure Blob Storage URL
az webapp config appsettings set \
  --resource-group titiler-rg \
  --name my-titiler \
  --settings AZURE_BLOB_BASE_URL="https://phasertitiler.blob.core.windows.net/geotiff"

# Set port
az webapp config appsettings set \
  --resource-group titiler-rg \
  --name my-titiler \
  --settings WEBSITES_PORT=8000

# Set startup command
az webapp config set \
  --resource-group titiler-rg \
  --name my-titiler \
  --startup-file "pip install -r requirements.txt && uvicorn app.main:app --host 0.0.0.0 --port 8000"
```

## Step 7: Upload COG Files to Azure Blob Storage

```bash
# Get storage account key
STORAGE_KEY=$(az storage account keys list \
  --resource-group titiler-rg \
  --account-name phasertitiler \
  --query '[0].value' -o tsv)

# Create container
az storage container create \
  --name geotiff \
  --account-name phasertitiler \
  --account-key $STORAGE_KEY \
  --public-access blob

# Upload your COG files
az storage blob upload \
  --account-name phasertitiler \
  --account-key $STORAGE_KEY \
  --container-name geotiff \
  --file /path/to/your/habitat_data.tif \
  --name habitat_data.tif
```

## Step 8: Trigger First Deployment

The deployment will trigger automatically when you push to the main branch. You can also:

1. Make a small change (e.g., update README)
2. Commit and push:
```bash
git add README.md
git commit -m "Trigger deployment"
git push
```

3. Watch the deployment in GitHub Actions tab

## Step 9: Verify Deployment

```bash
# Check deployment status
az webapp show \
  --resource-group titiler-rg \
  --name my-titiler \
  --query state -o tsv

# Test the API
curl https://my-titiler.azurewebsites.net/health

# View logs
az webapp log tail \
  --resource-group titiler-rg \
  --name my-titiler
```

## Monitoring Deployments

### GitHub Actions
- Go to your repository's **Actions** tab
- View deployment runs and logs
- Re-run failed deployments if needed

### Azure Portal
- Navigate to your App Service
- Go to **Deployment Center** > **Logs**
- View deployment history and status

## Troubleshooting

### Deployment Fails
1. Check GitHub Actions logs for errors
2. Verify all secrets are correctly set
3. Ensure Python version matches (3.11)

### App Not Starting
1. Check Azure App Service logs:
```bash
az webapp log tail --resource-group titiler-rg --name my-titiler
```
2. Verify environment variables are set
3. Check startup command is correct

### CORS Issues
```bash
# Add allowed origins
az webapp cors add \
  --resource-group titiler-rg \
  --name my-titiler \
  --allowed-origins "https://your-frontend-domain.com"
```

## Next Steps

1. **Custom Domain**: Add your domain to the App Service
2. **SSL Certificate**: Configure HTTPS with managed certificate
3. **Monitoring**: Set up Application Insights
4. **Scaling**: Configure auto-scaling rules
5. **Staging Slots**: Create staging environment for testing

## Continuous Deployment Workflow

After initial setup, your workflow is simple:

1. Make changes locally
2. Test locally: `uvicorn app.main:app --reload`
3. Commit changes: `git commit -am "Update feature"`
4. Push to GitHub: `git push`
5. GitHub Actions automatically deploys to Azure

The deployment typically takes 2-5 minutes. Monitor progress in GitHub Actions tab.