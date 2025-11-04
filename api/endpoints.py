"""FastAPI endpoints for OpenStudio multi-agent storytelling platform."""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from typing import Dict, Any
import uuid
import asyncio
import traceback
from datetime import datetime
import os

from models.schemas import (
    PlotRequest, PlotResponse,
    WriteRequest, WriteResponse,
    EditRequest, EditResponse,
    WorldBuildRequest, WorldBuildResponse,
    CollaborationRequest, CollaborationResponse,
    OrchestrationRequest, OrchestrationResponse,
    ContentLength, StoryGenre, WritingStyle
)
import time
import logging

logging.basicConfig(level=logging.INFO)
from agents import PlotterAgent, WriterAgent, EditorAgent, WorldBuilderAgent
from orchestrator import WorkflowOrchestrator, WorkflowType
from config import settings

app = FastAPI(
    title="OpenStudio API",
    description="Multi-agent storytelling platform with AI-powered creative agents",
    version="1.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agents
plotter_agent = PlotterAgent()
writer_agent = WriterAgent()
editor_agent = EditorAgent()
world_builder_agent = WorldBuilderAgent()
orchestrator = WorkflowOrchestrator()

# Session storage (in production, use Redis or database)
sessions: Dict[str, Dict[str, Any]] = {}

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Serve the main frontend application."""
    try:
        return templates.TemplateResponse("index.html", {"request": request, "cache_id": int(time.time())})
    except Exception as e:
        print(f"❌ Error serving root page: {str(e)}")
        print("📋 Full traceback:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to serve frontend: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        return {"status": "healthy", "timestamp": datetime.now().isoformat()}
    except Exception as e:
        print(f"❌ Error in health check: {str(e)}")
        print("📋 Full traceback:")
        traceback.print_exc()
        return {"status": "error", "error": str(e), "timestamp": datetime.now().isoformat()}

# Simplified API endpoints for frontend
import uuid

@app.post("/api/plot")
async def api_plot(request: Request):
    """Simplified plot generation endpoint for frontend."""
    try:
        # Get JSON data from request body
        data = await request.json()

        # Ensure session_id is present in data
        if "session_id" not in data or data["session_id"] is None:
            data["session_id"] = str(uuid.uuid4())
        
        # Map frontend genre values to enum values
        genre_mapping = {
            "Fantasy": "fantasy",
            "Science Fiction": "sci-fi", 
            "Mystery": "mystery",
            "Romance": "romance",
            "Thriller": "thriller",
            "Historical Fiction": "horror",  # Map to closest available
            "Contemporary Fiction": "drama"  # Map to closest available
        }
        
        # Map frontend length values to enum values
        length_mapping = {
            "Short Story": "short",
            "Novella": "medium", 
            "Novel": "long",
            "Series": "extended"
        }
        
        genre = data.get("genre", "fantasy")
        if genre in genre_mapping:
            genre = genre_mapping[genre]
        
        length = data.get("length", "medium")
        if length in length_mapping:
            length = length_mapping[length]
        
        # Create a PlotRequest from the simplified request
        plot_request = PlotRequest(
            session_id=data.get("session_id"),
            prompt=data.get("content", ""),  # Map content to prompt
            genre=genre,
            target_length=length,
            characters=data.get("characters", []),
            setting=data.get("setting", ""),
            conflict=data.get("conflict", "")
        )
        
        result = await plotter_agent.process_request(plot_request.dict())
        return {
            "success": True,
            "result": result,
            "agent": "plotter"
        }
    except Exception as e:
        print(f"❌ Error in api_plot: {str(e)}")
        print("📋 Full traceback:")
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
            "agent": "plotter"
        }

@app.post("/api/write")
async def api_write(request: Request):
    """Simplified writing endpoint for frontend."""
    try:
        # Get JSON data from request body
        data = await request.json()
        session_id = data.get("session_id")
        if not session_id:
            session_id = str(uuid.uuid4())
            data["session_id"] = session_id
        
        # Map frontend genre values to enum values
        genre_mapping = {
            "Fantasy": "fantasy",
            "Science Fiction": "sci-fi", 
            "Mystery": "mystery",
            "Romance": "romance",
            "Thriller": "thriller",
            "Historical Fiction": "horror",  # Map to closest available
            "Contemporary Fiction": "drama"  # Map to closest available
        }
        
        # Map frontend length values to enum values
        length_mapping = {
            "Short Story": "short",
            "Novella": "medium", 
            "Novel": "long",
            "Series": "extended"
        }

        # Map frontend style values to enum values
        style_mapping = {
            "Concise": WritingStyle.CONCISE,
            "Poetic": WritingStyle.POETIC,
            "Immersive": WritingStyle.IMMERSIVE,
            "Dialogue-heavy": WritingStyle.DIALOGUE_HEAVY,
            "Descriptive": WritingStyle.DESCRIPTIVE
        }
        
        genre = data.get("genre", "fantasy")
        if genre in genre_mapping:
            genre = genre_mapping[genre]
        
        length = data.get("length", "medium")
        if length in length_mapping:
            length = length_mapping[length]

        style = data.get("style", "descriptive")
        if style in style_mapping:
            style = style_mapping[style]
        else:
            style = WritingStyle.DESCRIPTIVE # Default to descriptive if invalid
        
        # Create a WriteRequest from the simplified request
        write_request = WriteRequest(
            scene_description=data.get("content", ""),  # Map content to scene_description
            style=style,
            length=length,
            previous_context=data.get("previous_context")
        )
        
        result = await writer_agent.process_request(write_request.dict())
        logging.info(f"Result from writer_agent.process_request: {result}")
        return {
            "success": True,
            "result": result,
            "agent": "writer"
        }
    except Exception as e:
        print(f"❌ Error in api_write: {str(e)}")
        print("📋 Full traceback:")
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
            "agent": "writer"
        }

@app.post("/api/edit")
async def api_edit(request: Request):
    """Simplified editing endpoint for frontend."""
    try:
        # Get JSON data from request body
        data = await request.json()
        session_id = data.get("session_id")
        if not session_id:
            session_id = str(uuid.uuid4())
            data["session_id"] = session_id
        
        # Create an EditRequest from the simplified request
        edit_request = EditRequest(
            content=data.get("content", ""),  # Keep as content for EditRequest
            focus_areas=data.get("focus_areas", []),
            preserve_style=data.get("preserve_style", True),
            target_audience=data.get("target_audience", "general")
        )
        
        result = await editor_agent.process_request(edit_request.content)
        return {
            "success": True,
            "result": result,
            "agent": "editor"
        }
    except Exception as e:
        print(f"❌ Error in api_edit: {str(e)}")
        print("📋 Full traceback:")
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
            "agent": "editor"
        }

@app.post("/api/worldbuild")
async def api_worldbuild(request: Request):
    """Simplified world building endpoint for frontend."""
    try:
        # Get JSON data from request body
        data = await request.json()

        # Ensure session_id is present in data
        if "session_id" not in data or data["session_id"] is None:
            data["session_id"] = str(uuid.uuid4())
        
        # Map frontend genre values to enum values
        genre_mapping = {
            "Fantasy": "fantasy",
            "Science Fiction": "sci-fi", 
            "Mystery": "mystery",
            "Romance": "romance",
            "Thriller": "thriller",
            "Historical Fiction": "horror",  # Map to closest available
            "Contemporary Fiction": "drama"  # Map to closest available
        }
        
        genre = data.get("genre", "fantasy")
        if genre in genre_mapping:
            genre = genre_mapping[genre]
        
        # Map frontend scope values to enum values
        scope_mapping = {
            "Region": ContentLength.MEDIUM,
            "Continent": ContentLength.LONG,
            "Planet": ContentLength.EXTENDED,
            "Local": ContentLength.SHORT
        }

        scope = data.get("scope", "Region")
        if scope in scope_mapping:
            scope = scope_mapping[scope]
        else:
            scope = ContentLength.MEDIUM # Default to medium if invalid

        # Create a WorldBuildRequest from the simplified request
        worldbuild_request = WorldBuildRequest(
            session_id=data.get("session_id"),
            world_type=data.get("content", ""),  # Map content to world_type
            genre=genre,
            scope=scope,
            elements=data.get("elements", []),
            complexity=data.get("complexity", "medium"),
            cultural_depth=data.get("cultural_depth", "medium")
        )
        
        result = await world_builder_agent.process_request(worldbuild_request.dict())
        return {
            "success": True,
            "result": result,
            "agent": "worldbuilder"
        }
    except Exception as e:
        print(f"❌ Error in api_worldbuild: {str(e)}")
        print("📋 Full traceback:")
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
            "agent": "worldbuilder"
        }

# Plotter endpoints
@app.post("/plotter/generate", response_model=PlotResponse)
async def generate_plot(request: PlotRequest):
    """Generate story plot and outline."""
    try:
        response = await plotter_agent.process_request(request.dict())
        return PlotResponse(
            success=True,
            message="Plot generated successfully",
            outline=response.get("plot_outline", ""),
            characters=response.get("characters", []),
            themes=response.get("themes", []),
            plot_points=response.get("story_arc", [])
        )
    except Exception as e:
        print(f"❌ Error in generate_plot: {str(e)}")
        print("📋 Full traceback:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Plot generation failed: {str(e)}")

@app.post("/plotter/expand-character")
async def expand_character(character_name: str, context: str = ""):
    """Expand character details."""
    try:
        response = await plotter_agent.expand_character(character_name, context)
        return {"success": True, "character_details": response}
    except Exception as e:
        print(f"❌ Error in expand_character: {str(e)}")
        print("📋 Full traceback:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Character expansion failed: {str(e)}")

# Writer endpoints
@app.post("/writer/generate", response_model=WriteResponse)
async def generate_content(request: WriteRequest):
    """Generate written content from plot outline."""
    try:
        response = await writer_agent.process_request(request.dict())
        return WriteResponse(
            success=True,
            message="Content generated successfully",
            content=response.get("content", ""),
            word_count=response.get("word_count", 0),
            suggestions=response.get("suggestions", [])
        )
    except Exception as e:
        print(f"❌ Error in generate_content: {str(e)}")
        print("📋 Full traceback:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Content generation failed: {str(e)}")

@app.post("/writer/continue")
async def continue_scene(scene_context: str, target_length: int = 500):
    """Continue writing from existing scene."""
    try:
        response = await writer_agent.continue_scene(scene_context, target_length)
        return {"success": True, "continued_content": response}
    except Exception as e:
        print(f"❌ Error in continue_scene: {str(e)}")
        print("📋 Full traceback:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Scene continuation failed: {str(e)}")

@app.post("/writer/rewrite")
async def rewrite_section(content: str, style_instructions: str = ""):
    """Rewrite content section with style instructions."""
    try:
        response = await writer_agent.rewrite_section(content, style_instructions)
        return {"success": True, "rewritten_content": response}
    except Exception as e:
        print(f"❌ Error in rewrite_section: {str(e)}")
        print("📋 Full traceback:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Content rewriting failed: {str(e)}")

# Editor endpoints
@app.post("/editor/refine", response_model=EditResponse)
async def refine_content(request: EditRequest):
    """Refine and edit written content."""
    try:
        response = await editor_agent.process_request(request.dict())
        return EditResponse(
            success=True,
            message="Content refined successfully",
            edited_content=response.get("refined_content", ""),
            changes_made=response.get("changes_made", []),
            suggestions=response.get("suggestions", []),
            readability_score=response.get("readability_score", 0.0)
        )
    except Exception as e:
        print(f"❌ Error in refine_content: {str(e)}")
        print("📋 Full traceback:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Content refinement failed: {str(e)}")

@app.post("/editor/proofread")
async def proofread_content(content: str):
    """Proofread content for grammar and spelling."""
    try:
        response = await editor_agent.proofread(content)
        return {"success": True, "proofread_result": response}
    except Exception as e:
        print(f"❌ Error in proofread_content: {str(e)}")
        print("📋 Full traceback:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Proofreading failed: {str(e)}")

@app.post("/editor/style-analysis")
async def analyze_style(content: str):
    """Analyze writing style and provide feedback."""
    try:
        response = await editor_agent.analyze_style(content)
        return {"success": True, "style_analysis": response}
    except Exception as e:
        print(f"❌ Error in analyze_style: {str(e)}")
        print("📋 Full traceback:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Style analysis failed: {str(e)}")

# World Builder endpoints
@app.post("/world-builder/create", response_model=WorldBuildResponse)
async def create_world(request: WorldBuildRequest):
    """Create detailed world and setting."""
    try:
        response = await world_builder_agent.process_request(request.dict())
        return WorldBuildResponse(
            success=True,
            message="World created successfully",
            world_description=response.get("world_description", ""),
            locations=response.get("locations", []),
            rules=response.get("rules", []),
            history=response.get("history", "")
        )
    except Exception as e:
        print(f"❌ Error in create_world: {str(e)}")
        print("📋 Full traceback:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"World creation failed: {str(e)}")

@app.post("/world-builder/expand-location")
async def expand_location(location_name: str, context: str = ""):
    """Expand details for a specific location."""
    try:
        response = await world_builder_agent.expand_location(location_name, context)
        return {"success": True, "location_details": response}
    except Exception as e:
        print(f"❌ Error in expand_location: {str(e)}")
        print("📋 Full traceback:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Location expansion failed: {str(e)}")

@app.post("/world-builder/create-culture")
async def create_culture(culture_name: str, world_context: str = ""):
    """Create detailed culture within the world."""
    try:
        response = await world_builder_agent.create_culture(culture_name, world_context)
        return {"success": True, "culture_details": response}
    except Exception as e:
        print(f"❌ Error in create_culture: {str(e)}")
        print("📋 Full traceback:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Culture creation failed: {str(e)}")

# Orchestrator endpoints
@app.post("/orchestrator/workflow", response_model=OrchestrationResponse)
async def start_workflow(request: OrchestrationRequest):
    """Start a multi-agent workflow."""
    try:
        if not request.session_id:
            request.session_id = str(uuid.uuid4())
        workflow_id = str(uuid.uuid4())
        workflow_state = await orchestrator.start_workflow(
            workflow_type=WorkflowType(request.workflow_type),
            initial_input=request.initial_input,
            workflow_id=workflow_id,
            session_id=request.session_id
        )
        
        return OrchestrationResponse(
            success=True,
            message="Workflow started successfully",
            workflow_id=workflow_id,
            current_step=workflow_state.current_step.value,
            status=workflow_state.status,
            results=workflow_state.results,
            next_actions=workflow_state.next_actions
        )
    except Exception as e:
        print(f"❌ Error in start_workflow: {str(e)}")
        print("📋 Full traceback:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Workflow start failed: {str(e)}")

@app.post("/orchestrator/continue/{workflow_id}")
async def continue_workflow(workflow_id: str, user_input: str = ""):
    """Continue an existing workflow."""
    try:
        workflow_state = await orchestrator.continue_workflow(workflow_id, user_input)
        return {
            "success": True,
            "workflow_id": workflow_id,
            "current_step": workflow_state.current_step.value,
            "status": workflow_state.status,
            "results": workflow_state.results,
            "next_actions": workflow_state.next_actions
        }
    except Exception as e:
        print(f"❌ Error in continue_workflow: {str(e)}")
        print("📋 Full traceback:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Workflow continuation failed: {str(e)}")

@app.get("/orchestrator/status/{workflow_id}")
async def get_workflow_status(workflow_id: str):
    """Get current workflow status."""
    try:
        workflow_state = orchestrator.get_workflow_status(workflow_id)
        if not workflow_state:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        return {
            "workflow_id": workflow_id,
            "current_step": workflow_state.current_step.value,
            "status": workflow_state.status,
            "results": workflow_state.results,
            "next_actions": workflow_state.next_actions
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status retrieval failed: {str(e)}")

# Collaboration endpoints
@app.post("/collaboration/create-session", response_model=CollaborationResponse)
async def create_collaboration_session(request: CollaborationRequest):
    """Create a new collaboration session."""
    try:
        session_id = str(uuid.uuid4())
        sessions[session_id] = {
            "id": session_id,
            "participants": request.participants,
            "project_type": request.project_type,
            "shared_context": request.shared_context,
            "created_at": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat(),
            "content": {},
            "workflow_history": []
        }
        
        return CollaborationResponse(
            success=True,
            message="Collaboration session created successfully",
            session_id=session_id,
            participants=request.participants,
            shared_context=request.shared_context,
            session_status="active"
        )
    except Exception as e:
        print(f"❌ Error in create_collaboration_session: {str(e)}")
        print("📋 Full traceback:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Session creation failed: {str(e)}")

@app.get("/collaboration/session/{session_id}")
async def get_collaboration_session(session_id: str):
    """Get collaboration session details."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    return {
        "success": True,
        "session": session
    }

@app.post("/collaboration/session/{session_id}/update")
async def update_collaboration_session(session_id: str, content: Dict[str, Any]):
    """Update collaboration session content."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        sessions[session_id]["content"].update(content)
        sessions[session_id]["last_activity"] = datetime.utcnow().isoformat()
        
        return {
            "success": True,
            "message": "Session updated successfully",
            "session_id": session_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Session update failed: {str(e)}")

@app.delete("/collaboration/session/{session_id}")
async def delete_collaboration_session(session_id: str):
    """Delete a collaboration session."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    del sessions[session_id]
    return {
        "success": True,
        "message": "Session deleted successfully"
    }

# Utility endpoints
@app.get("/sessions")
async def list_sessions():
    """List all active collaboration sessions."""
    return {
        "success": True,
        "sessions": list(sessions.keys()),
        "total_sessions": len(sessions)
    }

@app.get("/agents/status")
async def get_agents_status():
    """Get status of all agents."""
    return {
        "success": True,
        "agents": {
            "plotter": "active",
            "writer": "active", 
            "editor": "active",
            "world_builder": "active"
        },
        "orchestrator": "active"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.endpoints:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )