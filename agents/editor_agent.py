"""
Editor Agent - Refines and improves written content.
"""
from typing import Dict, Any, List
from .base_agent import BaseAgent
from models.schemas import EditRequest, EditResponse
import re
import traceback


class EditorAgent(BaseAgent):
    """Agent responsible for editing and refining written content."""
    
    def __init__(self):
        super().__init__(model_name="gpt-3.5-turbo")
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for the Editor agent."""
        return """You are the Editor, a meticulous content refiner and literary craftsperson. Your role is to enhance written content for clarity, consistency, engagement, and overall quality.

Your responsibilities include:
1. Improving grammar, syntax, and punctuation
2. Enhancing clarity and readability
3. Ensuring consistency in voice, tone, and style
4. Strengthening character development and dialogue
5. Improving pacing and narrative flow
6. Identifying and resolving plot inconsistencies
7. Enhancing descriptive language and imagery
8. Optimizing sentence structure and word choice
9. Ensuring proper story structure and organization
10. Maintaining the author's intended voice while improving quality

Editing principles:
- Preserve the author's unique voice and style unless specifically asked to change it
- Make changes that serve the story and enhance reader experience
- Focus on clarity without sacrificing literary quality
- Ensure consistency in character behavior, world-building, and timeline
- Improve flow and pacing for better reader engagement
- Enhance emotional impact and thematic resonance
- Check for overused words, phrases, or sentence structures
- Ensure proper show vs. tell balance
- Verify logical story progression and character motivations

Types of editing to perform:
- Line editing: Sentence-level improvements for clarity and flow
- Copy editing: Grammar, punctuation, and technical accuracy
- Content editing: Story structure, character development, and plot consistency
- Style editing: Voice, tone, and stylistic consistency

Always provide specific, actionable feedback and explain the reasoning behind significant changes."""
    
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process an editing request (implements abstract method from BaseAgent)."""
        return await self.process(request)
    
    async def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process an editing request."""
        try:
            # Parse the request
            edit_request = EditRequest(**request)
            
            # Perform comprehensive editing
            edited_content = await self._edit_content(
                edit_request.content,
                edit_request.focus_areas,
                edit_request.preserve_style
            )
            
            # Generate list of changes made
            changes_made = await self._identify_changes(
                edit_request.content,
                edited_content
            )
            
            # Generate additional suggestions
            suggestions = await self._generate_suggestions(edited_content)
            
            # Calculate readability score (simplified)
            readability_score = self._calculate_readability_score(edited_content)
            
            return EditResponse(
                success=True,
                message="Content edited successfully",
                session_id=edit_request.session_id,
                edited_content=edited_content,
                changes_made=changes_made,
                suggestions=suggestions,
                readability_score=readability_score
            ).dict()
            
        except Exception as e:
            print(f"❌ Error editing content: {str(e)}")
            print("📋 Full traceback:")
            traceback.print_exc()
            return EditResponse(
                success=False,
                message=f"Error editing content: {str(e)}",
                session_id=request.get("session_id")
            ).dict()
    
    async def _edit_content(self, content: str, focus_areas: List[str], preserve_style: bool) -> str:
        """Edit the content based on focus areas."""
        # Build editing prompt
        prompt_parts = [
            "Edit and improve the following content:",
            "",
            f"Original Content:\n{content}",
            ""
        ]
        
        if focus_areas:
            prompt_parts.extend([
                "Focus specifically on:",
                *[f"- {area}" for area in focus_areas],
                ""
            ])
        
        style_instruction = (
            "Preserve the original writing style and voice while making improvements."
            if preserve_style else
            "Feel free to adjust the writing style for better clarity and impact."
        )
        
        prompt_parts.extend([
            "Editing Guidelines:",
            f"- {style_instruction}",
            "- Improve clarity, flow, and readability",
            "- Fix grammar, punctuation, and syntax issues",
            "- Enhance word choice and sentence structure",
            "- Ensure consistency in tone and voice",
            "- Strengthen dialogue and character development",
            "- Improve pacing and narrative tension",
            "",
            "Provide the edited version:"
        ])
        
        return await self.generate_response("\n".join(prompt_parts))
    
    async def _identify_changes(self, original: str, edited: str) -> List[str]:
        """Identify and describe the changes made during editing."""
        prompt = f"""Compare the original and edited versions and list the key changes made:

Original:
{original[:1000]}...

Edited:
{edited[:1000]}...

Provide a concise list of the main improvements and changes made, focusing on the most significant edits."""
        
        changes_text = await self.generate_response(prompt)
        
        # Parse changes into a list
        changes = []
        for line in changes_text.split('\n'):
            line = line.strip()
            if line and (line.startswith('-') or line.startswith('•') or line[0].isdigit()):
                change = line.lstrip('-•0123456789. ')
                if change:
                    changes.append(change)
        
        return changes[:8]  # Limit to 8 changes
    
    async def _generate_suggestions(self, content: str) -> List[str]:
        """Generate additional improvement suggestions."""
        prompt = f"""Analyze this edited content and provide 3-5 additional suggestions for further improvement:

Content:
{content[:1500]}...

Focus on:
- Areas that could still be enhanced
- Opportunities for stronger impact
- Potential structural improvements
- Character or dialogue enhancements
- Ways to increase reader engagement

Provide specific, actionable suggestions."""
        
        suggestions_text = await self.generate_response(prompt)
        
        # Parse suggestions into a list
        suggestions = []
        for line in suggestions_text.split('\n'):
            line = line.strip()
            if line and (line.startswith('-') or line.startswith('•') or line[0].isdigit()):
                suggestion = line.lstrip('-•0123456789. ')
                if suggestion:
                    suggestions.append(suggestion)
        
        return suggestions[:5]  # Limit to 5 suggestions
    
    def _calculate_readability_score(self, content: str) -> float:
        """Calculate a simplified readability score."""
        # This is a simplified readability calculation
        # In production, you might use libraries like textstat
        
        sentences = len(re.findall(r'[.!?]+', content))
        words = len(content.split())
        
        if sentences == 0:
            return 0.0
        
        avg_sentence_length = words / sentences
        
        # Simple scoring: shorter sentences = higher readability
        # Scale from 0-10, where 10 is most readable
        if avg_sentence_length <= 15:
            score = 10.0
        elif avg_sentence_length <= 20:
            score = 8.0
        elif avg_sentence_length <= 25:
            score = 6.0
        elif avg_sentence_length <= 30:
            score = 4.0
        else:
            score = 2.0
        
        return round(score, 1)
    
    async def proofread(self, content: str) -> Dict[str, Any]:
        """Perform focused proofreading for grammar and mechanics."""
        try:
            prompt = f"""Proofread this content for grammar, punctuation, spelling, and mechanical errors:

{content}

Provide:
1. The corrected version
2. A list of errors found and corrected

Focus only on technical accuracy, not style or content changes."""
            
            response = await self.generate_response(prompt)
            
            # Parse the response (simplified)
            parts = response.split("Errors found:")
            corrected_text = parts[0].strip()
            errors = parts[1].strip() if len(parts) > 1 else "No errors found"
            
            return {
                "corrected_content": corrected_text,
                "errors_found": errors
            }
        except Exception as e:
            print(f"❌ Error proofreading content: {str(e)}")
            print("📋 Full traceback:")
            traceback.print_exc()
            return {
                "corrected_content": content,
                "errors_found": f"Error during proofreading: {str(e)}"
            }
    
    async def style_analysis(self, content: str) -> Dict[str, Any]:
        """Analyze the writing style and provide feedback."""
        try:
            prompt = f"""Analyze the writing style of this content:

{content[:1000]}...

Provide analysis on:
- Writing voice and tone
- Sentence structure variety
- Word choice and vocabulary level
- Pacing and rhythm
- Strengths and areas for improvement
- Overall style assessment"""
            
            analysis = await self.generate_response(prompt)
            
            return {"style_analysis": analysis}
        except Exception as e:
            print(f"❌ Error analyzing style: {str(e)}")
            print("📋 Full traceback:")
            traceback.print_exc()
            return {"style_analysis": f"Error during style analysis: {str(e)}"}
    
    async def consistency_check(self, content: str) -> List[str]:
        """Check for consistency issues in the content."""
        prompt = f"""Check this content for consistency issues:

{content}

Look for:
- Character name or description inconsistencies
- Timeline or chronology issues
- Setting or world-building contradictions
- Tone or voice inconsistencies
- Factual contradictions

List any inconsistencies found."""
        
        issues_text = await self.generate_response(prompt)
        
        # Parse issues into a list
        issues = []
        for line in issues_text.split('\n'):
            line = line.strip()
            if line and (line.startswith('-') or line.startswith('•') or line[0].isdigit()):
                issue = line.lstrip('-•0123456789. ')
                if issue:
                    issues.append(issue)
        
        return issues