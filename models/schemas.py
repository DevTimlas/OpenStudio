"""
Pydantic models for OpenStudio API requests and responses.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum
import traceback


class StoryGenre(str, Enum):
    """Available story genres."""
    FANTASY = "fantasy"
    SCIFI = "sci-fi"
    MYSTERY = "mystery"
    ROMANCE = "romance"
    THRILLER = "thriller"
    HORROR = "horror"
    DRAMA = "drama"
    COMEDY = "comedy"
    ADVENTURE = "adventure"


class WritingStyle(str, Enum):
    """Available writing styles."""
    CONCISE = "concise"
    POETIC = "poetic"
    IMMERSIVE = "immersive"
    DIALOGUE_HEAVY = "dialogue-heavy"
    DESCRIPTIVE = "descriptive"


class ContentLength(str, Enum):
    """Content length options."""
    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"
    EXTENDED = "extended"


# Base Models
class BaseRequest(BaseModel):
    """Base request model."""
    session_id: Optional[str] = Field(None, description="Session ID for tracking")
    user_id: Optional[str] = Field(None, description="User ID for collaboration")


class BaseResponse(BaseModel):
    """Base response model."""
    success: bool = Field(True, description="Whether the request was successful")
    message: Optional[str] = Field(None, description="Response message")
    session_id: Optional[str] = Field(None, description="Session ID")


# Plotter Models
class PlotRequest(BaseRequest):
    """Request model for story plotting."""
    prompt: str = Field(..., description="Story concept or prompt")
    genre: StoryGenre = Field(StoryGenre.FANTASY, description="Story genre")
    characters: Optional[List[str]] = Field(None, description="Character names or descriptions")
    setting: Optional[str] = Field(None, description="Story setting")
    conflict: Optional[str] = Field(None, description="Main conflict")
    target_length: ContentLength = Field(ContentLength.MEDIUM, description="Target story length")


class PlotResponse(BaseResponse):
    """Response model for story plotting."""
    outline: Optional[str] = Field(None, description="Generated story outline")
    characters: Optional[List[Dict[str, Any]]] = Field(None, description="Character details")
    plot_points: Optional[List[str]] = Field(None, description="Key plot points")
    themes: Optional[List[str]] = Field(None, description="Story themes")


# Writer Models
class WriteRequest(BaseRequest):
    """Request model for scene writing."""
    outline: Optional[str] = Field(None, description="Story outline to expand")
    scene_description: Optional[str] = Field(None, description="Specific scene to write")
    style: WritingStyle = Field(WritingStyle.IMMERSIVE, description="Writing style")
    length: ContentLength = Field(ContentLength.MEDIUM, description="Scene length")
    previous_context: Optional[str] = Field(None, description="Previous story context")


class WriteResponse(BaseResponse):
    """Response model for scene writing."""
    content: Optional[str] = Field(None, description="Generated scene content")
    word_count: Optional[int] = Field(None, description="Word count of generated content")
    suggestions: Optional[List[str]] = Field(None, description="Writing suggestions")


# Editor Models
class EditRequest(BaseRequest):
    """Request model for content editing."""
    content: str = Field(..., description="Content to edit")
    focus_areas: Optional[List[str]] = Field(None, description="Specific areas to focus on")
    preserve_style: bool = Field(True, description="Whether to preserve original style")


class EditResponse(BaseResponse):
    """Response model for content editing."""
    edited_content: Optional[str] = Field(None, description="Edited content")
    changes_made: Optional[List[str]] = Field(None, description="List of changes made")
    suggestions: Optional[List[str]] = Field(None, description="Additional suggestions")
    readability_score: Optional[float] = Field(None, description="Readability score")


# World Builder Models
class WorldBuildRequest(BaseRequest):
    """Request model for world building."""
    world_type: str = Field(..., description="Type of world to build")
    genre: StoryGenre = Field(StoryGenre.FANTASY, description="World genre")
    key_elements: Optional[List[str]] = Field(None, description="Key world elements")
    scope: ContentLength = Field(ContentLength.MEDIUM, description="World detail scope")


class WorldBuildResponse(BaseResponse):
    """Response model for world building."""
    world_description: Optional[str] = Field(None, description="World description")
    locations: Optional[List[Dict[str, Any]]] = Field(None, description="Key locations")
    rules: Optional[List[str]] = Field(None, description="World rules and laws")
    history: Optional[str] = Field(None, description="World history")


# Collaboration Models
class CollaborationRequest(BaseRequest):
    """Request model for collaboration features."""
    project_id: str = Field(..., description="Project ID")
    action: str = Field(..., description="Collaboration action")
    content: Optional[str] = Field(None, description="Content to share")


class CollaborationResponse(BaseResponse):
    """Response model for collaboration features."""
    project_url: Optional[str] = Field(None, description="Shareable project URL")
    collaborators: Optional[List[str]] = Field(None, description="List of collaborators")
    updates: Optional[List[Dict[str, Any]]] = Field(None, description="Recent updates")


# Multi-Agent Orchestration Models
class OrchestrationRequest(BaseRequest):
    """Request model for multi-agent orchestration."""
    workflow: str = Field(..., description="Workflow type (plot->write->edit)")
    initial_prompt: str = Field(..., description="Initial story prompt")
    preferences: Optional[Dict[str, Any]] = Field(None, description="User preferences")


class OrchestrationResponse(BaseResponse):
    """Response model for multi-agent orchestration."""
    workflow_id: Optional[str] = Field(None, description="Workflow tracking ID")
    current_step: Optional[str] = Field(None, description="Current workflow step")
    results: Optional[Dict[str, Any]] = Field(None, description="Step results")
    next_actions: Optional[List[str]] = Field(None, description="Available next actions")