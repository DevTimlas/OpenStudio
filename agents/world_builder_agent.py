"""
World Builder Agent - Creates detailed settings and environments.
"""
from typing import Dict, Any, List
from .base_agent import BaseAgent
from models.schemas import WorldBuildRequest, WorldBuildResponse, StoryGenre, ContentLength
import traceback
import uuid


class WorldBuilderAgent(BaseAgent):
    """Agent responsible for creating detailed worlds and settings."""
    
    def __init__(self):
        super().__init__(model_name="gpt-3.5-turbo")
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for the World Builder agent."""
        return """You are the World Builder, a master architect of fictional realms and settings. Your role is to create rich, immersive worlds that serve as compelling backdrops for stories.

Your responsibilities include:
1. Designing comprehensive fictional worlds with internal consistency
2. Creating detailed geographical layouts and environmental features
3. Developing cultural systems, societies, and civilizations
4. Establishing historical backgrounds and timelines
5. Creating political systems, governments, and power structures
6. Designing economic systems and trade relationships
7. Developing religions, mythologies, and belief systems
8. Creating languages, customs, and social norms
9. Establishing natural laws, magic systems, or technological frameworks
10. Ensuring all elements work together cohesively

World-building principles:
- Internal consistency: All elements should logically fit together
- Cultural authenticity: Societies should feel real and lived-in
- Environmental logic: Geography should influence culture and history
- Historical depth: Events should have causes and consequences
- Conflict potential: Include sources of tension and story opportunities
- Sensory richness: Worlds should engage all the senses
- Accessibility: Complex worlds should be understandable to readers
- Genre appropriateness: Match the world to the story's genre and tone

Consider these elements when building worlds:
- Physical geography (climate, terrain, natural resources)
- Political structures (governments, laws, conflicts)
- Social systems (classes, customs, relationships)
- Economic systems (currency, trade, resources)
- Cultural elements (art, music, literature, traditions)
- Religious/spiritual systems (beliefs, practices, institutions)
- Historical events (wars, discoveries, catastrophes)
- Technology/magic levels (capabilities, limitations, costs)
- Languages and communication
- Daily life and social norms

Adapt complexity and focus based on the story's needs and scope."""
    
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process a world building request (implements abstract method from BaseAgent)."""
        return await self.process(request)
    
    async def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process a world building request."""
        try:
            # Ensure session_id is present in request
            if "session_id" not in request or request["session_id"] is None:
                request["session_id"] = str(uuid.uuid4())
    
            # Parse the request
            world_request = WorldBuildRequest(**request)
            
            # Build the world creation prompt
            prompt = self._build_world_prompt(world_request)
            
            # Generate the world description
            world_content = await self.generate_response(prompt)
            
            # Parse and structure the response
            structured_world = self._parse_world_response(world_content, world_request)
            
            return WorldBuildResponse(
                success=True,
                message="World created successfully",
                session_id=world_request.session_id,
                **structured_world
            ).dict()
            
        except Exception as e:
            print(f"❌ Error creating world: {str(e)}")
            print("📋 Full traceback:")
            traceback.print_exc()
            return WorldBuildResponse(
                success=False,
                message=f"Error creating world: {str(e)}",
                session_id=request.get("session_id")
            ).dict()
    
    def _build_world_prompt(self, request: WorldBuildRequest) -> str:
        """Build a comprehensive world building prompt."""
        prompt_parts = [
            f"Create a detailed fictional world with the following specifications:",
            f"World Type: {request.world_type}",
            f"Genre: {request.genre.value}",
            f"Detail Scope: {request.scope.value}"
        ]
        
        if request.key_elements:
            prompt_parts.append(f"Key Elements to Include: {', '.join(request.key_elements)}")
        
        # Add genre-specific requirements
        genre_requirements = self._get_genre_requirements(request.genre)
        prompt_parts.extend(["", "Genre Requirements:", genre_requirements, ""])
        
        # Add scope-specific instructions
        scope_instructions = self._get_scope_instructions(request.scope)
        prompt_parts.extend(["Detail Level:", scope_instructions, ""])
        
        prompt_parts.extend([
            "Please provide a comprehensive world description including:",
            "1. **Overview**: General description and unique features",
            "2. **Geography**: Physical layout, climate, and notable locations",
            "3. **History**: Key historical events and timeline",
            "4. **Culture & Society**: Social structures, customs, and daily life",
            "5. **Politics & Government**: Power structures and governance",
            "6. **Economy & Trade**: Economic systems and resources",
            "7. **Religion & Beliefs**: Spiritual systems and mythologies",
            "8. **Technology/Magic**: Capabilities and limitations",
            "9. **Notable Locations**: Important places with descriptions",
            "10. **Conflicts & Tensions**: Sources of drama and story potential",
            "",
            "Format your response with clear sections and rich, immersive details."
        ])
        
        return "\n".join(prompt_parts)
    
    def _get_genre_requirements(self, genre: StoryGenre) -> str:
        """Get specific requirements based on the genre."""
        genre_map = {
            StoryGenre.FANTASY: "Include magic systems, mythical creatures, and fantastical elements. Consider different races or species.",
            StoryGenre.SCIFI: "Include advanced technology, space travel, or futuristic elements. Consider scientific principles and their implications.",
            StoryGenre.MYSTERY: "Create locations that support investigation and intrigue. Include hidden secrets and complex social dynamics.",
            StoryGenre.HORROR: "Design atmospheric, unsettling environments. Include sources of fear and supernatural or psychological threats.",
            StoryGenre.ROMANCE: "Create settings that facilitate romantic encounters and emotional connections. Consider social customs around relationships.",
            StoryGenre.THRILLER: "Design high-stakes environments with potential for danger and tension. Include complex political or social structures.",
            StoryGenre.ADVENTURE: "Create diverse, explorable locations with hidden treasures, dangers, and opportunities for discovery.",
            StoryGenre.DRAMA: "Focus on realistic social structures and relationships. Emphasize cultural depth and human complexity."
        }
        return genre_map.get(genre, "Create a world appropriate for the story's themes and tone.")
    
    def _get_scope_instructions(self, scope: ContentLength) -> str:
        """Get instructions based on the detail scope."""
        scope_map = {
            ContentLength.SHORT: "Provide essential details for immediate story needs. Focus on 2-3 key locations and basic cultural elements.",
            ContentLength.MEDIUM: "Develop a well-rounded world with multiple locations, detailed culture, and rich history. Include 5-7 major locations.",
            ContentLength.LONG: "Create an extensive world with deep lore, complex societies, and intricate relationships between elements.",
            ContentLength.EXTENDED: "Build a comprehensive world suitable for multiple stories, with extensive detail in all areas."
        }
        return scope_map.get(scope, "Provide appropriate detail for the world's intended use.")
    
    def _parse_world_response(self, response_text: str, request: WorldBuildRequest) -> Dict[str, Any]:
        """Parse the world building response into structured data."""
        result = {
            "world_description": response_text,
            "locations": [],
            "rules": [],
            "history": ""
        }
        
        # Extract locations (simplified parsing)
        location_section = self._extract_section(response_text, ["location", "places", "geography"])
        if location_section:
            locations = self._parse_locations(location_section)
            result["locations"] = locations
        
        # Extract rules/laws
        rules_section = self._extract_section(response_text, ["rules", "laws", "technology", "magic"])
        if rules_section:
            rules = self._parse_rules(rules_section)
            result["rules"] = rules
        
        # Extract history
        history_section = self._extract_section(response_text, ["history", "timeline", "past"])
        if history_section:
            result["history"] = history_section
        
        return result
    
    def _extract_section(self, text: str, keywords: List[str]) -> str:
        """Extract a section from the text based on keywords."""
        lines = text.split('\n')
        section_lines = []
        in_section = False
        
        for line in lines:
            line_lower = line.lower()
            
            # Check if this line starts a relevant section
            if any(keyword in line_lower for keyword in keywords) and ('**' in line or '#' in line or ':' in line):
                in_section = True
                section_lines.append(line)
                continue
            
            # Check if we've moved to a new section
            if in_section and ('**' in line or line.startswith('#')) and not any(keyword in line_lower for keyword in keywords):
                break
            
            if in_section:
                section_lines.append(line)
        
        return '\n'.join(section_lines)
    
    def _parse_locations(self, location_text: str) -> List[Dict[str, Any]]:
        """Parse location information from text."""
        locations = []
        current_location = None
        
        for line in location_text.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            # Check if this is a location name (starts with -, *, or number)
            if line.startswith(('-', '*', '•')) or (line[0].isdigit() and '.' in line[:3]):
                if current_location:
                    locations.append(current_location)
                
                # Extract location name
                name = line.lstrip('-*•0123456789. ').split(':')[0].strip()
                description = line.split(':', 1)[1].strip() if ':' in line else ""
                
                current_location = {
                    "name": name,
                    "description": description,
                    "type": "location"
                }
            elif current_location and line:
                # Add to current location description
                current_location["description"] += " " + line
        
        if current_location:
            locations.append(current_location)
        
        return locations[:10]  # Limit to 10 locations
    
    def _parse_rules(self, rules_text: str) -> List[str]:
        """Parse rules and laws from text."""
        rules = []
        
        for line in rules_text.split('\n'):
            line = line.strip()
            if line and (line.startswith(('-', '*', '•')) or (line[0].isdigit() and '.' in line[:3])):
                rule = line.lstrip('-*•0123456789. ')
                if rule:
                    rules.append(rule)
        
        return rules[:15]  # Limit to 15 rules
    
    async def expand_location(self, location_name: str, world_context: str) -> Dict[str, Any]:
        """Expand details for a specific location."""
        try:
            prompt = f"""Provide detailed information about this location:

Location: {location_name}
World Context: {world_context}

Include:
- Physical description and layout
- Notable features and landmarks
- Inhabitants and their culture
- History and significance
- Current events or conflicts
- Atmosphere and mood
- Opportunities for story events"""
            
            description = await self.generate_response(prompt)
            
            return {
                "name": location_name,
                "detailed_description": description,
                "type": "expanded_location"
            }
        except Exception as e:
            print(f"❌ Error expanding location: {str(e)}")
            print("📋 Full traceback:")
            traceback.print_exc()
            return {
                "name": location_name,
                "detailed_description": f"Error expanding location: {str(e)}",
                "type": "expanded_location"
            }
    
    async def create_culture(self, culture_name: str, world_context: str) -> Dict[str, Any]:
        """Create detailed cultural information."""
        try:
            prompt = f"""Create a detailed culture for this world:

Culture Name: {culture_name}
World Context: {world_context}

Include:
- Social structure and hierarchy
- Customs and traditions
- Values and beliefs
- Daily life and routines
- Art, music, and literature
- Language characteristics
- Relationships with other cultures
- Unique practices or ceremonies"""
            
            culture_details = await self.generate_response(prompt)
            
            return {
                "name": culture_name,
                "details": culture_details
            }
        except Exception as e:
            print(f"❌ Error creating culture: {str(e)}")
            print("📋 Full traceback:")
            traceback.print_exc()
            return {
                "name": culture_name,
                "details": f"Error creating culture: {str(e)}"
            }
    
    async def generate_conflict(self, world_description: str) -> List[str]:
        """Generate potential conflicts for the world."""
        prompt = f"""Based on this world description, suggest 5-7 potential conflicts or tensions that could drive stories:

World: {world_description}

Consider:
- Political tensions and power struggles
- Resource conflicts and economic disputes
- Cultural clashes and social issues
- Historical grievances and unresolved conflicts
- Environmental or supernatural threats
- Personal conflicts arising from the world's nature

Provide specific, story-ready conflict ideas."""
        
        conflicts_text = await self.generate_response(prompt)
        
        conflicts = []
        for line in conflicts_text.split('\n'):
            line = line.strip()
            if line and (line.startswith(('-', '*', '•')) or (line[0].isdigit() and '.' in line[:3])):
                conflict = line.lstrip('-*•0123456789. ')
                if conflict:
                    conflicts.append(conflict)
        
        return conflicts[:7]