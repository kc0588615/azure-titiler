# Azure TiTiler Deployment

This repository contains the TiTiler application configured for deployment on Azure App Service.

## Features

- **TiTiler**: FastAPI-based dynamic tile server for Cloud Optimized GeoTIFFs (COGs)
- **Custom Colormap**: Habitat-specific colormap for visualization
- **Supabase Integration**: PostGIS spatial queries for species analysis
- **Azure Optimized**: Configured for Azure App Service with GitHub Actions CI/CD

## Local Development

1. Clone the repository:
```bash
git clone https://github.com/yourusername/azure-titiler.git
cd azure-titiler
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set environment variables:
```bash
export SUPABASE_DATABASE_URL="postgresql://postgres:password@db.project.supabase.co:5432/postgres"
export AZURE_BLOB_BASE_URL="https://phasertitiler.blob.core.windows.net/geotiff"
```

5. Run the application:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

6. Access the API docs at: http://localhost:8000/docs

## Azure Deployment

This repository is configured for automatic deployment to Azure App Service using GitHub Actions.

### Initial Setup

1. Create Azure resources (see AZURE_CLOUD_MIGRATION_GUIDE.md)
2. Configure GitHub repository secrets in Settings > Secrets:
   - `AZUREAPPSERVICE_CLIENTID`
   - `AZUREAPPSERVICE_TENANTID`
   - `AZUREAPPSERVICE_SUBSCRIPTIONID`

3. Push to main branch to trigger deployment

### Manual Deployment

```bash
# Using Azure CLI
az webapp deploy \
  --resource-group titiler-rg \
  --name my-titiler \
  --src-path . \
  --type zip
```

## API Endpoints

- `/` - API root with status information
- `/health` - Health check endpoint
- `/docs` - Interactive API documentation
- `/cog/tiles/{z}/{x}/{y}` - Tile endpoint for COGs
- `/cog/tilejson.json` - TileJSON metadata
- `/api/habitat-analysis` - Complex spatial query with raster/vector data
- `/api/simple-species` - Simple species query using vector data

## Example Usage

### Get tile from Azure Blob COG:
```bash
curl "https://my-titiler.azurewebsites.net/cog/tiles/10/512/512?url=https://phasertitiler.blob.core.windows.net/geotiff/habitat_data.tif&colormap_name=habitat_custom"
```

### Query species at location:
```bash
curl -X POST "https://my-titiler.azurewebsites.net/api/habitat-analysis?lat=40.7128&lng=-74.0060"
```

## Environment Variables

- `SUPABASE_DATABASE_URL` - PostgreSQL connection string for Supabase
- `AZURE_BLOB_BASE_URL` - Base URL for Azure Blob Storage container
- `WEBSITES_PORT` - Port for Azure App Service (default: 8000)

## Monitoring

View logs in Azure Portal:
- App Service > Monitoring > Log stream
- Application Insights (if configured)

Or using Azure CLI:
```bash
az webapp log tail --resource-group titiler-rg --name my-titiler
```

## License

MIT