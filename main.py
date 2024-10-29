from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from pydantic import BaseModel
from analyzer import WebsiteRater  # Changed from relative import
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Website Analyzer API",
    description="API for analyzing websites and generating performance reports",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Update this with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class WebsiteList(BaseModel):
    urls: List[str]

class AnalysisResponse(BaseModel):
    success: bool
    message: str = None
    data: dict = None
    error: str = None

@app.get("/")
async def root():
    return {"message": "Website Analyzer API is running"}

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "1.0.0"
    }

@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_websites(website_list: WebsiteList):
    try:
        if not website_list.urls:
            raise HTTPException(status_code=400, detail="No URLs provided")

        logger.info(f"Analyzing {len(website_list.urls)} websites")
        
        rater = WebsiteRater()
        
        start_time = time.time()
        results = rater.analyze_websites(website_list.urls)
        execution_time = time.time() - start_time
        
        logger.info(f"Analysis completed in {execution_time:.2f} seconds")
        
        return AnalysisResponse(
            success=True,
            data=results,
            message=f"Successfully analyzed {len(website_list.urls)} websites"
        )

    except Exception as e:
        logger.error(f"Error during analysis: {str(e)}")
        return AnalysisResponse(
            success=False,
            error=str(e)
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)