"""
Workflow Orchestrator - Coordinates multiple agents for complex storytelling workflows.
"""
from typing import Dict, Any, List, Optional
from enum import Enum
import uuid
import asyncio
from datetime import datetime
import traceback

from agents import PlotterAgent, WriterAgent, EditorAgent, WorldBuilderAgent
from models.schemas import (
    OrchestrationRequest, OrchestrationResponse,
    PlotRequest, WriteRequest, EditRequest, WorldBuildRequest
)


class WorkflowType(str, Enum):
    """Available workflow types."""
    PLOT_ONLY = "plot_only"
    PLOT_TO_SCENE = "plot_to_scene"
    FULL_STORY = "full_story"  # plot -> write -> edit
    WORLD_FIRST = "world_first"  # world -> plot -> write -> edit
    COLLABORATIVE = "collaborative"
    CUSTOM = "custom"


class WorkflowStep(str, Enum):
    """Workflow step types."""
    WORLD_BUILD = "world_build"
    PLOT = "plot"
    WRITE = "write"
    EDIT = "edit"
    REVIEW = "review"
    COMPLETE = "complete"


class WorkflowState:
    """Represents the current state of a workflow."""
    
    def __init__(self, workflow_id: str, workflow_type: WorkflowType):
        self.workflow_id = workflow_id
        self.workflow_type = workflow_type
        self.current_step = WorkflowStep.PLOT
        self.steps_completed = []
        self.step_results = {}
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.user_preferences = {}
        self.session_id = None
        
    def update_step(self, step: WorkflowStep, results: Dict[str, Any]):
        """Update the current step and store results."""
        self.steps_completed.append(self.current_step)
        self.step_results[step.value] = results
        self.updated_at = datetime.now()
        
    def get_next_step(self) -> Optional[WorkflowStep]:
        """Determine the next step in the workflow."""
        workflow_sequences = {
            WorkflowType.PLOT_ONLY: [WorkflowStep.PLOT, WorkflowStep.COMPLETE],
            WorkflowType.PLOT_TO_SCENE: [WorkflowStep.PLOT, WorkflowStep.WRITE, WorkflowStep.COMPLETE],
            WorkflowType.FULL_STORY: [WorkflowStep.PLOT, WorkflowStep.WRITE, WorkflowStep.EDIT, WorkflowStep.COMPLETE],
            WorkflowType.WORLD_FIRST: [WorkflowStep.WORLD_BUILD, WorkflowStep.PLOT, WorkflowStep.WRITE, WorkflowStep.EDIT, WorkflowStep.COMPLETE],
        }
        
        sequence = workflow_sequences.get(self.workflow_type, [WorkflowStep.COMPLETE])
        
        try:
            current_index = sequence.index(self.current_step)
            if current_index + 1 < len(sequence):
                return sequence[current_index + 1]
        except ValueError:
            pass
        
        return WorkflowStep.COMPLETE


class WorkflowOrchestrator:
    """Orchestrates multi-agent workflows for storytelling."""
    
    def __init__(self):
        self.agents = {
            "plotter": PlotterAgent(),
            "writer": WriterAgent(),
            "editor": EditorAgent(),
            "world_builder": WorldBuilderAgent()
        }
        self.active_workflows: Dict[str, WorkflowState] = {}
        
    async def start_workflow(self, workflow_type: WorkflowType, initial_input: str, workflow_id: str, session_id: str) -> OrchestrationResponse:
        """Start a new multi-agent workflow."""
        try:
            # Create workflow state
            workflow_state = WorkflowState(workflow_id, workflow_type)
            workflow_state.session_id = session_id
            workflow_state.user_preferences = {}
            workflow_state.initial_input = initial_input
            
            # Determine starting step
            if workflow_type == WorkflowType.WORLD_FIRST:
                workflow_state.current_step = WorkflowStep.WORLD_BUILD
            else:
                workflow_state.current_step = WorkflowStep.PLOT
            
            self.active_workflows[workflow_id] = workflow_state
            
            # Execute the first step
            step_result = await self._execute_step(workflow_state, request.initial_prompt)
            
            # Get next actions
            next_actions = self._get_next_actions(workflow_state)
            
            return OrchestrationResponse(
                success=True,
                message=f"Workflow '{workflow_type.value}' started successfully",
                session_id=request.session_id,
                workflow_id=workflow_id,
                current_step=workflow_state.current_step.value,
                results=step_result,
                next_actions=next_actions
            )
            
        except Exception as e:
            print(f"Error starting workflow: {str(e)}")
            traceback.print_exc()
            return OrchestrationResponse(
                success=False,
                message=f"Error starting workflow: {str(e)}",
                session_id=request.session_id
            )
    
    async def continue_workflow(self, workflow_id: str, user_input: Optional[str] = None) -> OrchestrationResponse:
        """Continue an existing workflow to the next step."""
        try:
            if workflow_id not in self.active_workflows:
                return OrchestrationResponse(
                    success=False,
                    message="Workflow not found"
                )
            
            workflow_state = self.active_workflows[workflow_id]
            
            # Move to next step
            next_step = workflow_state.get_next_step()
            if next_step == WorkflowStep.COMPLETE:
                return self._complete_workflow(workflow_state)
            
            workflow_state.current_step = next_step
            
            # Execute the step
            step_result = await self._execute_step(workflow_state, user_input)
            
            # Get next actions
            next_actions = self._get_next_actions(workflow_state)
            
            return OrchestrationResponse(
                success=True,
                message=f"Step '{next_step.value}' completed successfully",
                session_id=workflow_state.session_id,
                workflow_id=workflow_id,
                current_step=workflow_state.current_step.value,
                results=step_result,
                next_actions=next_actions
            )
            
        except Exception as e:
            print(f"Error continuing workflow: {str(e)}")
            traceback.print_exc()
            return OrchestrationResponse(
                success=False,
                message=f"Error continuing workflow: {str(e)}",
                workflow_id=workflow_id
            )
    
    async def _execute_step(self, workflow_state: WorkflowState, user_input: Optional[str] = None) -> Dict[str, Any]:
        """Execute a specific workflow step."""
        try:
            step = workflow_state.current_step
            
            if step == WorkflowStep.WORLD_BUILD:
                return await self._execute_world_build_step(workflow_state, user_input)
            elif step == WorkflowStep.PLOT:
                return await self._execute_plot_step(workflow_state, user_input)
            elif step == WorkflowStep.WRITE:
                return await self._execute_write_step(workflow_state, user_input)
            elif step == WorkflowStep.EDIT:
                return await self._execute_edit_step(workflow_state, user_input)
            else:
                return {"error": f"Unknown step: {step}"}
        except Exception as e:
            print(f"Error executing step {workflow_state.current_step}: {str(e)}")
            traceback.print_exc()
            return {"error": f"Error executing step: {str(e)}"}
    
    async def _execute_world_build_step(self, workflow_state: WorkflowState, user_input: str) -> Dict[str, Any]:
        """Execute world building step."""
        try:
            world_request = WorldBuildRequest(
                world_type=user_input or "fantasy realm",
                genre=workflow_state.user_preferences.get("genre", "fantasy"),
                key_elements=workflow_state.user_preferences.get("world_elements", []),
                scope=workflow_state.user_preferences.get("world_scope", "medium"),
                session_id=workflow_state.session_id
            )
            
            result = await self.agents["world_builder"].process(world_request.dict())
            workflow_state.update_step(WorkflowStep.WORLD_BUILD, result)
            
            return result
        except Exception as e:
            print(f"Error in world build step: {str(e)}")
            traceback.print_exc()
            return {"error": f"World build step failed: {str(e)}"}
    
    async def _execute_plot_step(self, workflow_state: WorkflowState, user_input: str) -> Dict[str, Any]:
        """Execute plotting step."""
        try:
            # Use world building context if available
            world_context = ""
            if WorkflowStep.WORLD_BUILD.value in workflow_state.step_results:
                world_result = workflow_state.step_results[WorkflowStep.WORLD_BUILD.value]
                world_context = world_result.get("world_description", "")
            
            plot_request = PlotRequest(
                prompt=user_input or "Create an engaging story",
                genre=workflow_state.user_preferences.get("genre", "fantasy"),
                characters=workflow_state.user_preferences.get("characters", []),
                setting=world_context or workflow_state.user_preferences.get("setting"),
                conflict=workflow_state.user_preferences.get("conflict"),
                target_length=workflow_state.user_preferences.get("target_length", "medium"),
                session_id=workflow_state.session_id
            )
            
            result = await self.agents["plotter"].process(plot_request.dict())
            workflow_state.update_step(WorkflowStep.PLOT, result)
            
            return result
        except Exception as e:
            print(f"Error in plot step: {str(e)}")
            traceback.print_exc()
            return {"error": f"Plot step failed: {str(e)}"}
    
    async def _execute_write_step(self, workflow_state: WorkflowState, user_input: str) -> Dict[str, Any]:
        """Execute writing step."""
        try:
            # Get plot context
            plot_result = workflow_state.step_results.get(WorkflowStep.PLOT.value, {})
            outline = plot_result.get("outline", "")
            
            write_request = WriteRequest(
                outline=outline,
                scene_description=user_input,
                style=workflow_state.user_preferences.get("writing_style", "immersive"),
                length=workflow_state.user_preferences.get("scene_length", "medium"),
                session_id=workflow_state.session_id
            )
            
            result = await self.agents["writer"].process(write_request.dict())
            workflow_state.update_step(WorkflowStep.WRITE, result)
            
            return result
        except Exception as e:
            print(f"Error in write step: {str(e)}")
            traceback.print_exc()
            return {"error": f"Write step failed: {str(e)}"}
    
    async def _execute_edit_step(self, workflow_state: WorkflowState, user_input: str) -> Dict[str, Any]:
        """Execute editing step."""
        try:
            # Get written content
            write_result = workflow_state.step_results.get(WorkflowStep.WRITE.value, {})
            content = write_result.get("content", "")
            
            if not content:
                return {"error": "No content available for editing"}
            
            edit_request = EditRequest(
                content=content,
                focus_areas=workflow_state.user_preferences.get("edit_focus", []),
                preserve_style=workflow_state.user_preferences.get("preserve_style", True),
                session_id=workflow_state.session_id
            )
            
            result = await self.agents["editor"].process(edit_request.dict())
            workflow_state.update_step(WorkflowStep.EDIT, result)
            
            return result
        except Exception as e:
            print(f"Error in edit step: {str(e)}")
            traceback.print_exc()
            return {"error": f"Edit step failed: {str(e)}"}
    
    def _complete_workflow(self, workflow_state: WorkflowState) -> OrchestrationResponse:
        """Complete the workflow and return final results."""
        workflow_state.current_step = WorkflowStep.COMPLETE
        
        # Compile final results
        final_results = {
            "workflow_type": workflow_state.workflow_type.value,
            "steps_completed": [step.value for step in workflow_state.steps_completed],
            "all_results": workflow_state.step_results,
            "completion_time": datetime.now().isoformat()
        }
        
        # Clean up
        if workflow_state.workflow_id in self.active_workflows:
            del self.active_workflows[workflow_state.workflow_id]
        
        return OrchestrationResponse(
            success=True,
            message="Workflow completed successfully",
            session_id=workflow_state.session_id,
            workflow_id=workflow_state.workflow_id,
            current_step=WorkflowStep.COMPLETE.value,
            results=final_results,
            next_actions=["export", "start_new_workflow", "collaborate"]
        )
    
    def _get_next_actions(self, workflow_state: WorkflowState) -> List[str]:
        """Get available next actions for the current workflow state."""
        next_step = workflow_state.get_next_step()
        
        if next_step == WorkflowStep.COMPLETE:
            return ["complete_workflow", "export_results", "start_new_workflow"]
        
        actions = [f"continue_to_{next_step.value}"]
        
        # Add step-specific actions
        if workflow_state.current_step == WorkflowStep.PLOT:
            actions.extend(["refine_plot", "add_characters", "modify_setting"])
        elif workflow_state.current_step == WorkflowStep.WRITE:
            actions.extend(["rewrite_scene", "continue_writing", "change_style"])
        elif workflow_state.current_step == WorkflowStep.EDIT:
            actions.extend(["focus_edit", "proofread_only", "style_analysis"])
        
        actions.append("restart_workflow")
        return actions
    
    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get the current status of a workflow."""
        if workflow_id not in self.active_workflows:
            return {"error": "Workflow not found"}
        
        workflow_state = self.active_workflows[workflow_id]
        
        return {
            "workflow_id": workflow_id,
            "workflow_type": workflow_state.workflow_type.value,
            "current_step": workflow_state.current_step.value,
            "steps_completed": [step.value for step in workflow_state.steps_completed],
            "created_at": workflow_state.created_at.isoformat(),
            "updated_at": workflow_state.updated_at.isoformat(),
            "next_actions": self._get_next_actions(workflow_state)
        }
    
    def list_active_workflows(self) -> List[Dict[str, Any]]:
        """List all active workflows."""
        return [
            self.get_workflow_status(workflow_id)
            for workflow_id in self.active_workflows.keys()
        ]
    
    async def execute_parallel_agents(self, requests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute multiple agents in parallel for efficiency."""
        tasks = []
        
        for request in requests:
            agent_type = request.get("agent_type")
            if agent_type in self.agents:
                task = self.agents[agent_type].process(request)
                tasks.append(task)
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            return [result if not isinstance(result, Exception) else {"error": str(result)} for result in results]
        
        return []