"""
Plotter Agent - Generates story outlines and plot structures.
"""
from typing import Dict, Any, List
from .base_agent import BaseAgent
from models.schemas import PlotRequest, PlotResponse
import json
import traceback


class PlotterAgent(BaseAgent):
    """Agent responsible for creating story outlines and plot structures."""
    
    def __init__(self):
        super().__init__(model_name="gpt-3.5-turbo")
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for the Plotter agent."""
        return """You are the Plotter, an expert story architect and narrative designer. Your role is to create compelling, well-structured story outlines that serve as blueprints for engaging narratives.

Your responsibilities include:
1. Analyzing story concepts and prompts to identify core themes and potential
2. Developing comprehensive plot structures with clear beginning, middle, and end
3. Creating memorable characters with distinct motivations and arcs
4. Establishing vivid settings that enhance the narrative
5. Identifying central conflicts and tensions that drive the story forward
6. Suggesting plot points, twists, and story beats that maintain reader engagement
7. Incorporating genre conventions while adding unique elements
8. Ensuring narrative coherence and logical story progression

When creating outlines, consider:
- Character development and growth arcs
- Pacing and story rhythm
- Thematic depth and meaning
- Conflict escalation and resolution
- Setting integration with plot
- Genre expectations and subversions
- Target audience and story length

Provide detailed, actionable outlines that writers can easily expand into full narratives. Include character descriptions, key plot points, and thematic elements. Be creative but ensure structural soundness."""
    
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process a plot generation request."""
        try:
            # Parse the request
            plot_request = PlotRequest(**request)
            
            # Build the plotting prompt
            prompt = self._build_plotting_prompt(plot_request)
            
            # Generate the outline
            response_text = await self.generate_response(prompt)
            
            # Parse and structure the response
            structured_response = self._parse_plot_response(response_text)
            
            return PlotResponse(
                success=True,
                message="Story outline generated successfully",
                session_id=plot_request.session_id,
                **structured_response
            ).dict()
            
        except Exception as e:
            print(f"❌ Error generating plot: {str(e)}")
            print("📋 Full traceback:")
            traceback.print_exc()
            return PlotResponse(
                success=False,
                message=f"Error generating plot: {str(e)}",
                session_id=request.get("session_id")
            ).dict()
    
    def _build_plotting_prompt(self, request: PlotRequest) -> str:
        """Build a comprehensive plotting prompt."""
        prompt_parts = [
            f"Create a detailed story outline for the following concept:",
            f"Prompt: {request.prompt}",
            f"Genre: {request.genre.value}",
            f"Target Length: {request.target_length.value}"
        ]
        
        if request.characters:
            prompt_parts.append(f"Characters to include: {', '.join(request.characters)}")
        
        if request.setting:
            prompt_parts.append(f"Setting: {request.setting}")
        
        if request.conflict:
            prompt_parts.append(f"Central Conflict: {request.conflict}")
        
        prompt_parts.extend([
            "",
            "Please provide:",
            "1. A compelling story summary (2-3 paragraphs)",
            "2. Detailed character profiles with motivations and arcs",
            "3. Key plot points and story beats",
            "4. Central themes and messages",
            "5. Setting details and world-building elements",
            "6. Potential subplots and character relationships",
            "",
            "Format your response as a structured outline that a writer can easily follow."
        ])
        
        return "\n".join(prompt_parts)
    
    def _parse_plot_response(self, response_text: str) -> Dict[str, Any]:
        """Parse the LLM response into structured data."""
        # This is a simplified parser - in production, you might want more sophisticated parsing
        lines = response_text.split('\n')
        
        result = {
            "outline": response_text,
            "characters": [],
            "plot_points": [],
            "themes": []
        }
        
        current_section = None
        current_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Detect sections
            if "character" in line.lower() and (":" in line or line.endswith("s")):
                if current_section and current_content:
                    self._add_to_result(result, current_section, current_content)
                current_section = "characters"
                current_content = []
            elif "plot" in line.lower() and ("point" in line.lower() or "beat" in line.lower()):
                if current_section and current_content:
                    self._add_to_result(result, current_section, current_content)
                current_section = "plot_points"
                current_content = []
            elif "theme" in line.lower():
                if current_section and current_content:
                    self._add_to_result(result, current_section, current_content)
                current_section = "themes"
                current_content = []
            else:
                if current_section:
                    current_content.append(line)
        
        # Add the last section
        if current_section and current_content:
            self._add_to_result(result, current_section, current_content)
        
        return result
    
    def _add_to_result(self, result: Dict[str, Any], section: str, content: List[str]):
        """Add parsed content to the result dictionary."""
        if section == "characters":
            # Parse character information
            char_text = " ".join(content)
            if char_text:
                result["characters"].append({"description": char_text})
        elif section == "plot_points":
            result["plot_points"].extend([line for line in content if line])
        elif section == "themes":
            result["themes"].extend([line for line in content if line])
    
    async def generate_character_details(self, character_name: str, story_context: str) -> Dict[str, Any]:
        """Generate detailed character information."""
        try:
            prompt = f"""Create a detailed character profile for '{character_name}' in the context of: {story_context}

Include:
- Physical description
- Personality traits
- Background and history
- Motivations and goals
- Character arc
- Relationships with other characters
- Unique quirks or abilities"""
            
            response = await self.generate_response(prompt)
            return {"name": character_name, "profile": response}
        except Exception as e:
            print(f"❌ Error generating character details: {str(e)}")
            print("📋 Full traceback:")
            traceback.print_exc()
            return {"name": character_name, "profile": f"Error generating character details: {str(e)}"}
    
    async def expand_plot_point(self, plot_point: str, story_context: str) -> str:
        """Expand a single plot point with more detail."""
        try:
            prompt = f"""Expand this plot point with more detail and context:
Plot Point: {plot_point}
Story Context: {story_context}

Provide a detailed expansion that includes character actions, dialogue, setting details, and emotional beats."""
            
            return await self.generate_response(prompt)
        except Exception as e:
            print(f"❌ Error expanding plot point: {str(e)}")
            print("📋 Full traceback:")
            traceback.print_exc()
            return f"Error expanding plot point: {str(e)}"