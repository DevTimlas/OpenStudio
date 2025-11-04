"""
Writer Agent - Expands outlines into detailed prose and scenes.
"""
from typing import Dict, Any
from .base_agent import BaseAgent
from models.schemas import WriteRequest, WriteResponse, WritingStyle, ContentLength
import traceback


class WriterAgent(BaseAgent):
    """Agent responsible for expanding outlines into detailed prose."""
    
    def __init__(self):
        super().__init__(model_name="gpt-3.5-turbo")
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for the Writer agent."""
        return """You are the Writer, a master storyteller and prose craftsman. Your role is to transform story outlines and scene descriptions into engaging, well-written narrative content.

Your responsibilities include:
1. Expanding plot outlines into detailed scenes with rich descriptions
2. Creating compelling dialogue that reveals character and advances plot
3. Developing atmospheric and immersive scene settings
4. Maintaining consistent voice and tone throughout the narrative
5. Balancing action, dialogue, and description for optimal pacing
6. Incorporating sensory details to bring scenes to life
7. Ensuring smooth transitions between scenes and chapters
8. Adapting writing style to match specified preferences and genres

Writing principles to follow:
- Show, don't tell - use action and dialogue to reveal information
- Create vivid, specific imagery that engages the senses
- Vary sentence structure and length for rhythm and flow
- Use active voice and strong verbs
- Develop authentic character voices in dialogue
- Maintain narrative tension and forward momentum
- Respect genre conventions while adding unique elements
- Consider the target audience and adjust complexity accordingly

Adapt your writing style based on user preferences:
- Concise: Clear, direct prose with minimal embellishment
- Poetic: Lyrical language with metaphors and beautiful imagery
- Immersive: Rich descriptions that fully engage the reader's senses
- Dialogue-heavy: Focus on character interactions and conversations
- Descriptive: Detailed scene-setting and atmospheric writing

Always maintain high literary quality while serving the story's needs."""
    
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process a writing request."""
        try:
            # Parse the request
            write_request = WriteRequest(**request)
            
            # Build the writing prompt
            prompt = self._build_writing_prompt(write_request)
            
            # Generate the content
            content = await self.generate_response(
                prompt
            )
            
            # Calculate word count
            word_count = len(content.split())
            
            # Generate writing suggestions
            suggestions = await self._generate_suggestions(content, write_request.style)
            
            return WriteResponse(
                success=True,
                message="Scene content generated successfully",
                session_id=write_request.session_id,
                content=content,
                word_count=word_count,
                suggestions=suggestions
            ).dict()
            
        except Exception as e:
            print(f"❌ Error generating content: {str(e)}")
            print("📋 Full traceback:")
            traceback.print_exc()
            return WriteResponse(
                success=False,
                message=f"Error generating content: {str(e)}",
                session_id=request.get("session_id")
            ).dict()
    
    def _build_writing_prompt(self, request: WriteRequest) -> str:
        """Build a comprehensive writing prompt."""
        prompt_parts = []
        
        if request.outline:
            prompt_parts.extend([
                "Expand the following story outline into detailed prose:",
                f"Outline: {request.outline}",
                ""
            ])
        
        if request.scene_description:
            prompt_parts.extend([
                "Write a detailed scene based on this description:",
                f"Scene: {request.scene_description}",
                ""
            ])
        
        if request.previous_context:
            prompt_parts.extend([
                "Previous Context:",
                f"{request.previous_context}",
                ""
            ])
        
        # Add style instructions
        style_instructions = self._get_style_instructions(request.style)
        prompt_parts.extend([
            f"Writing Style: {request.style.value}",
            style_instructions,
            ""
        ])
        
        # Add length instructions
        length_instructions = self._get_length_instructions(request.length)
        prompt_parts.extend([
            f"Target Length: {request.length.value}",
            length_instructions,
            ""
        ])
        
        prompt_parts.extend([
            "Requirements:",
            "- Create engaging, well-paced prose",
            "- Include vivid descriptions and sensory details",
            "- Develop authentic dialogue if characters interact",
            "- Maintain narrative tension and reader interest",
            "- Ensure smooth flow and readability",
            "",
            "Write the scene now:"
        ])
        
        return "\n".join(prompt_parts)
    
    def _get_style_instructions(self, style: WritingStyle) -> str:
        """Get specific instructions for the writing style."""
        style_map = {
            WritingStyle.CONCISE: "Use clear, direct language. Avoid unnecessary words. Focus on action and essential details. Keep sentences crisp and impactful.",
            WritingStyle.POETIC: "Lyrical language with metaphors, imagery, and rhythm. Create an artistic, flowing prose style.",
            WritingStyle.IMMERSIVE: "Rich, detailed descriptions that fully engage all senses. Build a vivid world the reader can step into.",
            WritingStyle.DIALOGUE_HEAVY: "Focus primarily on character conversations. Use dialogue to reveal character, advance plot, and create tension.",
            WritingStyle.DESCRIPTIVE: "Emphasize detailed scene-setting and atmospheric descriptions. Paint a complete picture of the environment and mood."
        }
        return style_map.get(style, "Use a balanced, engaging writing style.")
    
    def _get_length_instructions(self, length: ContentLength) -> str:
        """Get specific instructions for content length."""
        length_map = {
            ContentLength.SHORT: "Write 200-500 words. Focus on key moments and essential details.",
            ContentLength.MEDIUM: "Write 500-1000 words. Develop the scene with good detail and pacing.",
            ContentLength.LONG: "Write 1000-2000 words. Create a fully developed scene with rich detail.",
            ContentLength.EXTENDED: "Write 2000+ words. Develop multiple scenes or a complete chapter."
        }
        return length_map.get(length, "Write an appropriately sized scene.")
    
    async def _generate_suggestions(self, content: str, style: WritingStyle) -> list:
        """Generate writing improvement suggestions."""
        suggestion_prompt = f"""Analyze this written content and provide 3-5 specific suggestions for improvement:

Content: {content}

Style Focus: {style.value}

Provide suggestions for:
- Pacing and flow
- Character development
- Dialogue improvement
- Descriptive enhancement
- Plot advancement

Format as a simple list of actionable suggestions."""
        
        suggestions_text = await self.generate_response(suggestion_prompt)
        
        # Parse suggestions into a list
        suggestions = []
        for line in suggestions_text.split('\n'):
            line = line.strip()
            if line and (line.startswith('-') or line.startswith('•') or line[0].isdigit()):
                # Clean up list markers
                suggestion = line.lstrip('-•0123456789. ')
                if suggestion:
                    suggestions.append(suggestion)
        
        return suggestions[:5]  # Limit to 5 suggestions
    
    async def continue_scene(self, existing_content: str, direction: str) -> str:
        """Continue writing from existing content in a specific direction."""
        try:
            prompt = f"""Continue this scene in the following direction:

Existing Content:
{existing_content}

Direction: {direction}

Continue the scene naturally, maintaining the established tone, style, and character voices. Write 300-800 words."""
            
            return await self.generate_response(prompt)
        except Exception as e:
            print(f"❌ Error continuing scene: {str(e)}")
            print("📋 Full traceback:")
            traceback.print_exc()
            return f"Error continuing scene: {str(e)}"
    
    async def rewrite_section(self, content: str, focus: str, style: WritingStyle) -> str:
        """Rewrite a specific section with a particular focus."""
        try:
            style_instruction = self._get_style_instructions(style)
            
            prompt = f"""Rewrite this section with the following focus:

Original Content:
{content}

Focus: {focus}
Style: {style.value} - {style_instruction}

Maintain the core narrative while improving the specified aspect."""
            
            return await self.generate_response(prompt)
        except Exception as e:
            print(f"❌ Error rewriting section: {str(e)}")
            print("📋 Full traceback:")
            traceback.print_exc()
            return f"Error rewriting section: {str(e)}"