"""
Enhanced Bridge API Integration
Connects the enhanced generator with ModelForge bridge service
"""

from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import asyncio
import json
import logging
from pathlib import Path
import uuid
from datetime import datetime

# Import enhanced generator
from instance.ai_modules.enhanced_generator import (
    EnhancedModelGenerator,
    GenerationConfig,
    AssetType,
    StyleFilter,
    PerformancePreset
)

logger = logging.getLogger(__name__)

class GenerationRequest(BaseModel):
    """API request model for generation"""
    prompt: str
    youtube_urls: Optional[List[str]] = None
    reference_images: Optional[List[str]] = None
    asset_type: str = "single_object"
    style: str = "roblox_cartoony"
    performance: str = "balanced"
    generate_lods: bool = True
    lod_levels: int = 3
    generate_variations: bool = False
    variation_count: int = 5
    auto_rig: bool = False
    auto_texture: bool = True
    texture_resolution: int = 1024
    use_roblox_materials: bool = True
    poly_budget: Optional[int] = None

class GenerationJob:
    """Track generation jobs"""
    def __init__(self, job_id: str, request: GenerationRequest):
        self.id = job_id
        self.request = request
        self.status = "pending"
        self.progress = 0.0
        self.result = None
        self.error = None
        self.created_at = datetime.now()
        self.completed_at = None
        self.messages = []
        
    def to_dict(self):
        return {
            "id": self.id,
            "status": self.status,
            "progress": self.progress,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "messages": self.messages,
            "error": self.error,
            "result": self.result
        }

# Global job storage (use Redis in production)
jobs: Dict[str, GenerationJob] = {}

# Generator instance
generator = None

def init_generator():
    """Initialize the enhanced generator"""
    global generator
    generator = EnhancedModelGenerator()
    logger.info("Enhanced generator initialized")

async def process_generation(job_id: str):
    """Process generation job asynchronously"""
    job = jobs.get(job_id)
    if not job:
        return
        
    try:
        job.status = "processing"
        job.progress = 0.1
        job.messages.append("Starting generation...")
        
        # Convert request to config
        config = GenerationConfig(
            prompt=job.request.prompt,
            youtube_urls=job.request.youtube_urls,
            reference_images=job.request.reference_images,
            asset_type=AssetType[job.request.asset_type.upper()],
            style=StyleFilter[job.request.style.upper()],
            performance=PerformancePreset[job.request.performance.upper()],
            generate_lods=job.request.generate_lods,
            lod_levels=job.request.lod_levels,
            generate_variations=job.request.generate_variations,
            variation_count=job.request.variation_count,
            auto_rig=job.request.auto_rig,
            auto_texture=job.request.auto_texture,
            texture_resolution=job.request.texture_resolution,
            use_roblox_materials=job.request.use_roblox_materials,
            poly_budget=job.request.poly_budget
        )
        
        # Update progress
        job.progress = 0.3
        job.messages.append("Configuration prepared")
        
        # Generate
        result = generator.generate(config)
        
        job.progress = 0.9
        job.messages.append("Generation complete")
        
        # Store result
        job.result = result
        job.status = "completed"
        job.progress = 1.0
        job.completed_at = datetime.now()
        job.messages.append("Job completed successfully")
        
    except Exception as e:
        logger.error(f"Generation failed for job {job_id}: {e}")
        job.status = "failed"
        job.error = str(e)
        job.messages.append(f"Error: {e}")
        job.completed_at = datetime.now()

def create_enhanced_routes(app: FastAPI):
    """Add enhanced generation routes to existing app"""
    
    @app.post("/api/v2/generate")
    async def generate_model(request: GenerationRequest, background_tasks: BackgroundTasks):
        """Submit a new generation job"""
        job_id = str(uuid.uuid4())
        job = GenerationJob(job_id, request)
        jobs[job_id] = job
        
        # Start processing in background
        background_tasks.add_task(process_generation, job_id)
        
        return JSONResponse({
            "job_id": job_id,
            "status": "accepted",
            "message": "Generation job submitted"
        })
    
    @app.get("/api/v2/job/{job_id}")
    async def get_job_status(job_id: str):
        """Get job status and progress"""
        job = jobs.get(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return JSONResponse(job.to_dict())
    
    @app.get("/api/v2/jobs")
    async def list_jobs(
        status: Optional[str] = Query(None),
        limit: int = Query(50, le=200)
    ):
        """List all jobs with optional filtering"""
        job_list = list(jobs.values())
        
        if status:
            job_list = [j for j in job_list if j.status == status]
            
        # Sort by creation time
        job_list.sort(key=lambda x: x.created_at, reverse=True)
        
        # Limit results
        job_list = job_list[:limit]
        
        return JSONResponse({
            "jobs": [j.to_dict() for j in job_list],
            "total": len(jobs)
        })
    
    @app.delete("/api/v2/job/{job_id}")
    async def cancel_job(job_id: str):
        """Cancel a pending or processing job"""
        job = jobs.get(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
            
        if job.status in ["completed", "failed"]:
            raise HTTPException(status_code=400, detail="Cannot cancel completed job")
            
        job.status = "cancelled"
        job.completed_at = datetime.now()
        job.messages.append("Job cancelled by user")
        
        return JSONResponse({"message": "Job cancelled"})
    
    @app.get("/api/v2/styles")
    async def list_styles():
        """List available style filters"""
        return JSONResponse({
            "styles": [
                {"id": "realistic", "name": "Realistic", "description": "Photorealistic with PBR materials"},
                {"id": "roblox_cartoony", "name": "Roblox Cartoony", "description": "Stylized cartoon, bright colors"},
                {"id": "voxel", "name": "Voxel", "description": "Cubic shapes, minecraft style"},
                {"id": "anime", "name": "Anime", "description": "Anime style with cel shading"},
                {"id": "low_poly", "name": "Low Poly", "description": "Flat shaded geometric style"}
            ]
        })
    
    @app.get("/api/v2/presets")
    async def list_presets():
        """List performance presets"""
        return JSONResponse({
            "presets": [
                {"id": "mobile", "name": "Mobile Friendly", "poly_budget": 3000},
                {"id": "balanced", "name": "Balanced", "poly_budget": 10000},
                {"id": "high", "name": "High Detail", "poly_budget": 50000},
                {"id": "cinematic", "name": "Cinematic", "poly_budget": 150000}
            ]
        })
    
    @app.get("/api/v2/asset-types")
    async def list_asset_types():
        """List available asset types"""
        return JSONResponse({
            "types": [
                {"id": "single_object", "name": "Single Object", "description": "Individual prop or item"},
                {"id": "prop_pack", "name": "Prop Pack", "description": "Collection of related props"},
                {"id": "environment", "name": "Environment", "description": "Complete room or scene"},
                {"id": "character", "name": "Character", "description": "Riggable character model"},
                {"id": "vehicle", "name": "Vehicle", "description": "Vehicle with functional parts"},
                {"id": "world", "name": "World", "description": "Large scale world or terrain"}
            ]
        })
    
    @app.post("/api/v2/enhance-prompt")
    async def enhance_prompt(prompt: str = Query(...)):
        """Enhance a prompt with AI suggestions"""
        from instance.ai_modules.enhanced_generator import PromptEnhancer
        
        enhancer = PromptEnhancer()
        config = GenerationConfig(
            prompt=prompt,
            style=StyleFilter.ROBLOX_CARTOONY,
            performance=PerformancePreset.BALANCED
        )
        
        enhanced = enhancer.enhance(prompt, config)
        
        return JSONResponse({
            "original": prompt,
            "enhanced": enhanced,
            "suggestions": [
                "Add 'exterior only' for simpler geometry",
                "Specify poly count for optimization",
                "Include style keywords for consistency"
            ]
        })

# Example integration with existing bridge
if __name__ == "__main__":
    import uvicorn
    from bridge_service import app  # Import existing app
    
    # Initialize enhanced generator
    init_generator()
    
    # Add enhanced routes
    create_enhanced_routes(app)
    
    # Run server
    uvicorn.run(app, host="127.0.0.1", port=8765)
