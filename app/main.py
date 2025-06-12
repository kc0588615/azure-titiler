import os
import asyncpg
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from titiler.core.factory import TilerFactory
from titiler.core.errors import DEFAULT_STATUS_CODES, add_exception_handlers
from .dependencies import ColorMapParams

# FastAPI App
app = FastAPI(
    title="TiTiler + Phaser Game Backend API",
    description="FastAPI server with TiTiler for habitat mapping and species analysis",
    version="1.0.0"
)

# CORS Configuration - Azure handles some CORS, but we add middleware for flexibility
origins = [
    "http://localhost:8080",
    "http://localhost:3000", 
    "https://your-vercel-app.vercel.app",  # Replace with your actual Vercel domain
    "*"  # Allow all origins for development
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# TiTiler factory with custom colormap
cog = TilerFactory(colormap_dependency=ColorMapParams)
app.include_router(cog.router, tags=["Cloud Optimized GeoTIFF"], prefix="/cog")
add_exception_handlers(app, DEFAULT_STATUS_CODES)

# Database connection from environment
DATABASE_URL = os.getenv("SUPABASE_DATABASE_URL", "")

@app.post("/api/habitat-analysis")
async def habitat_analysis(lat: float, lng: float):
    """
    Complex spatial query combining raster and vector data.
    Requires Supabase database with PostGIS and raster data loaded.
    """
    if not DATABASE_URL:
        return {
            "error": "Database not configured",
            "species": [],
            "message": "Set SUPABASE_DATABASE_URL environment variable"
        }
    
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        
        query = """
        WITH point AS (
            SELECT ST_SetSRID(ST_Point($1, $2), 4326) AS geom
        ),
        habitat_value AS (
            SELECT ST_Value(rast, p.geom) as habitat_type
            FROM habitat_raster_data, point p
            WHERE ST_Intersects(rast, p.geom)
            LIMIT 1
        )
        SELECT 
            s.species_name,
            s.species_id,
            h.habitat_type
        FROM species_habitat_polygons s, point p, habitat_value h
        WHERE ST_Intersects(s.geom, p.geom)
        AND s.preferred_habitat = h.habitat_type;
        """
        
        results = await conn.fetch(query, lng, lat)
        return {
            "species": [dict(r) for r in results],
            "location": {"lat": lat, "lng": lng},
            "query_type": "raster_vector_analysis"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "species": [],
            "location": {"lat": lat, "lng": lng}
        }
    finally:
        if 'conn' in locals():
            await conn.close()

@app.get("/api/simple-species")
async def simple_species_query(lat: float, lng: float):
    """
    Simple species query using only vector data (direct Supabase query alternative).
    This endpoint demonstrates the 'fast path' for simple operations.
    """
    if not DATABASE_URL:
        return {"error": "Database not configured", "species": []}
    
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        
        query = """
        SELECT species_name, species_id
        FROM species_habitat_polygons
        WHERE ST_Intersects(geom, ST_SetSRID(ST_Point($1, $2), 4326))
        LIMIT 10;
        """
        
        results = await conn.fetch(query, lng, lat)
        return {
            "species": [dict(r) for r in results],
            "location": {"lat": lat, "lng": lng},
            "query_type": "vector_only"
        }
        
    except Exception as e:
        return {"error": str(e), "species": []}
    finally:
        if 'conn' in locals():
            await conn.close()

@app.get("/")
def read_root():
    """API root endpoint with status information."""
    return {
        "message": "TiTiler + Phaser Game Backend API is running on Azure!",
        "version": "1.0.0",
        "endpoints": {
            "tiles": "/cog/tiles/{z}/{x}/{y}",
            "tilejson": "/cog/tilejson.json",
            "habitat_analysis": "/api/habitat-analysis",
            "simple_species": "/api/simple-species",
            "health": "/health",
            "docs": "/docs"
        },
        "features": [
            "TiTiler tile serving",
            "Custom habitat colormap",
            "Spatial analysis",
            "CORS enabled",
            "Azure App Service hosted"
        ]
    }

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "database_configured": bool(DATABASE_URL),
        "titiler_available": True,
        "platform": "Azure App Service"
    }