import os
from database import Base, engine
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
from routers import categories, expenses, merchant_rules

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Expense Tracker API",
    description=(
        "Personal expense tracking and categorization system with API key "
        "authentication"
    ),
    version="1.0.0",
)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    openapi_schema["components"]["securitySchemes"] = {
        "ApiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "x-api-key",
            "description": "API key for authentication"
        }
    }
    
    for path in openapi_schema["paths"]:
        if path not in ["/docs", "/redoc", "/openapi.json", "/"]:
            for method in ["get", "post", "put", "delete"]:
                if method in openapi_schema["paths"][path]:
                    openapi_schema["paths"][path][method]["security"] = [
                        {"ApiKeyAuth": []}
                    ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

# Get API key from environment variable
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise ValueError("API_KEY environment variable is required")


@app.middleware("http")
async def api_key_middleware(request: Request, call_next):
    """Middleware to validate API key for all requests."""
    if request.url.path in ["/docs", "/redoc", "/openapi.json", "/health"]:
        return await call_next(request)
    
    api_key = request.headers.get("x-api-key")
    if not api_key:
        return JSONResponse(
            status_code=401,
            content={
                "detail": (
                    "API key is required. Please provide 'x-api-key' header."
                )
            }
        )

    if api_key != API_KEY:
        return JSONResponse(
            status_code=403,
            content={"detail": "Invalid API key."}
        )
    
    response = await call_next(request)
    return response

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(expenses.router)
app.include_router(categories.router)
app.include_router(merchant_rules.router)


@app.get("/")
def read_root():
    """Root endpoint with API information."""
    return {
        "message": "Expense Tracker API",
        "version": "1.0.0",
        "description": "Personal expense tracking and categorization system",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    # Get configuration from environment variables
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("ENVIRONMENT") != "production"

    uvicorn.run("main:app", host=host, port=port, reload=reload)
