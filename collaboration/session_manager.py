"""Session management for collaborative storytelling."""

import uuid
import asyncio
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

class SessionStatus(Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    EXPIRED = "expired"

class ParticipantRole(Enum):
    OWNER = "owner"
    COLLABORATOR = "collaborator"
    VIEWER = "viewer"

@dataclass
class Participant:
    """Represents a session participant."""
    id: str
    name: str
    role: ParticipantRole
    joined_at: datetime
    last_activity: datetime
    contributions: List[str] = field(default_factory=list)

@dataclass
class SessionContent:
    """Represents session content and progress."""
    world_building: Dict[str, Any] = field(default_factory=dict)
    plot_outline: Dict[str, Any] = field(default_factory=dict)
    written_content: Dict[str, Any] = field(default_factory=dict)
    edited_content: Dict[str, Any] = field(default_factory=dict)
    shared_notes: List[str] = field(default_factory=list)
    version_history: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class CollaborationSession:
    """Represents a collaborative storytelling session."""
    id: str
    name: str
    description: str
    owner_id: str
    participants: Dict[str, Participant]
    status: SessionStatus
    created_at: datetime
    last_activity: datetime
    expires_at: Optional[datetime]
    content: SessionContent
    settings: Dict[str, Any] = field(default_factory=dict)
    workflow_state: Optional[str] = None

class SessionManager:
    """Manages collaborative storytelling sessions."""
    
    def __init__(self):
        self.sessions: Dict[str, CollaborationSession] = {}
        self.cleanup_interval = 3600  # 1 hour in seconds
        
    async def create_session(
        self,
        name: str,
        description: str,
        owner_id: str,
        owner_name: str,
        expires_in_hours: int = 24
    ) -> CollaborationSession:
        """Create a new collaboration session."""
        try:
            session_id = str(uuid.uuid4())
            now = datetime.utcnow()
            expires_at = now + timedelta(hours=expires_in_hours)
            
            owner = Participant(
                id=owner_id,
                name=owner_name,
                role=ParticipantRole.OWNER,
                joined_at=now,
                last_activity=now
            )
            
            session = CollaborationSession(
                id=session_id,
                name=name,
                description=description,
                owner_id=owner_id,
                participants={owner_id: owner},
                status=SessionStatus.ACTIVE,
                created_at=now,
                last_activity=now,
                expires_at=expires_at,
                content=SessionContent(),
                settings={
                    "max_participants": 10,
                    "allow_anonymous": False,
                    "auto_save": True,
                    "version_control": True
                }
            )
            
            self.sessions[session_id] = session
            return session
        except Exception as e:
            print(f"Error creating session: {str(e)}")
            traceback.print_exc()
            raise
    
    async def join_session(
        self,
        session_id: str,
        participant_id: str,
        participant_name: str,
        role: ParticipantRole = ParticipantRole.COLLABORATOR
    ) -> bool:
        """Add a participant to an existing session."""
        try:
            if session_id not in self.sessions:
                return False
                
            session = self.sessions[session_id]
            
            if session.status != SessionStatus.ACTIVE:
                return False
                
            if len(session.participants) >= session.settings.get("max_participants", 10):
                return False
                
            participant = Participant(
                id=participant_id,
                name=participant_name,
                role=role,
                joined_at=datetime.utcnow(),
                last_activity=datetime.utcnow()
            )
            
            session.participants[participant_id] = participant
            session.last_activity = datetime.utcnow()
            
            return True
        except Exception as e:
            print(f"Error joining session: {str(e)}")
            traceback.print_exc()
            return False
    
    async def leave_session(self, session_id: str, participant_id: str) -> bool:
        """Remove a participant from a session."""
        if session_id not in self.sessions:
            return False
            
        session = self.sessions[session_id]
        
        if participant_id not in session.participants:
            return False
            
        # Don't allow owner to leave unless transferring ownership
        if participant_id == session.owner_id and len(session.participants) > 1:
            return False
            
        del session.participants[participant_id]
        session.last_activity = datetime.utcnow()
        
        # If owner leaves and no other participants, mark session as completed
        if participant_id == session.owner_id and len(session.participants) == 0:
            session.status = SessionStatus.COMPLETED
            
        return True
    
    async def update_content(
        self,
        session_id: str,
        participant_id: str,
        content_type: str,
        content_data: Dict[str, Any]
    ) -> bool:
        """Update session content."""
        try:
            if session_id not in self.sessions:
                return False
                
            session = self.sessions[session_id]
            
            if participant_id not in session.participants:
                return False
                
            if session.status != SessionStatus.ACTIVE:
                return False
                
            # Update content based on type
            if content_type == "world_building":
                session.content.world_building.update(content_data)
            elif content_type == "plot_outline":
                session.content.plot_outline.update(content_data)
            elif content_type == "written_content":
                session.content.written_content.update(content_data)
            elif content_type == "edited_content":
                session.content.edited_content.update(content_data)
            elif content_type == "shared_notes":
                if isinstance(content_data.get("note"), str):
                    session.content.shared_notes.append(content_data["note"])
            
            # Add to version history if enabled
            if session.settings.get("version_control", True):
                version_entry = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "participant_id": participant_id,
                    "content_type": content_type,
                    "changes": content_data
                }
                session.content.version_history.append(version_entry)
            
            # Update participant activity
            session.participants[participant_id].last_activity = datetime.utcnow()
            session.participants[participant_id].contributions.append(content_type)
            session.last_activity = datetime.utcnow()
            
            return True
        except Exception as e:
            print(f"Error updating content for session {session_id}: {str(e)}")
            traceback.print_exc()
            return False
    
    async def get_session(self, session_id: str) -> Optional[CollaborationSession]:
        """Get session by ID."""
        try:
            return self.sessions.get(session_id)
        except Exception as e:
            print(f"Error getting session {session_id}: {str(e)}")
            traceback.print_exc()
            return None
    
    async def list_sessions(
        self,
        participant_id: Optional[str] = None,
        status: Optional[SessionStatus] = None
    ) -> List[CollaborationSession]:
        """List sessions with optional filtering."""
        sessions = list(self.sessions.values())
        
        if participant_id:
            sessions = [s for s in sessions if participant_id in s.participants]
            
        if status:
            sessions = [s for s in sessions if s.status == status]
            
        return sessions
    
    async def update_participant_activity(self, session_id: str, participant_id: str):
        """Update participant's last activity timestamp."""
        if session_id in self.sessions and participant_id in self.sessions[session_id].participants:
            self.sessions[session_id].participants[participant_id].last_activity = datetime.utcnow()
            self.sessions[session_id].last_activity = datetime.utcnow()
    
    async def change_session_status(
        self,
        session_id: str,
        new_status: SessionStatus,
        participant_id: str
    ) -> bool:
        """Change session status (owner only)."""
        if session_id not in self.sessions:
            return False
            
        session = self.sessions[session_id]
        
        # Only owner can change status
        if participant_id != session.owner_id:
            return False
            
        session.status = new_status
        session.last_activity = datetime.utcnow()
        
        return True
    
    async def transfer_ownership(
        self,
        session_id: str,
        current_owner_id: str,
        new_owner_id: str
    ) -> bool:
        """Transfer session ownership."""
        if session_id not in self.sessions:
            return False
            
        session = self.sessions[session_id]
        
        if session.owner_id != current_owner_id:
            return False
            
        if new_owner_id not in session.participants:
            return False
            
        # Update ownership
        session.owner_id = new_owner_id
        session.participants[new_owner_id].role = ParticipantRole.OWNER
        
        # Demote previous owner to collaborator
        if current_owner_id in session.participants:
            session.participants[current_owner_id].role = ParticipantRole.COLLABORATOR
            
        session.last_activity = datetime.utcnow()
        
        return True
    
    async def cleanup_expired_sessions(self):
        """Remove expired sessions."""
        now = datetime.utcnow()
        expired_sessions = []
        
        for session_id, session in self.sessions.items():
            if session.expires_at and session.expires_at < now:
                expired_sessions.append(session_id)
            elif session.status == SessionStatus.COMPLETED:
                # Remove completed sessions after 7 days
                if (now - session.last_activity).days > 7:
                    expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.sessions[session_id]
        
        return len(expired_sessions)
    
    async def get_session_statistics(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session statistics and analytics."""
        if session_id not in self.sessions:
            return None
            
        session = self.sessions[session_id]
        
        stats = {
            "session_id": session_id,
            "duration_hours": (datetime.utcnow() - session.created_at).total_seconds() / 3600,
            "participant_count": len(session.participants),
            "total_contributions": sum(len(p.contributions) for p in session.participants.values()),
            "content_sections": {
                "world_building": len(session.content.world_building),
                "plot_outline": len(session.content.plot_outline),
                "written_content": len(session.content.written_content),
                "edited_content": len(session.content.edited_content),
                "shared_notes": len(session.content.shared_notes)
            },
            "version_history_count": len(session.content.version_history),
            "most_active_participant": max(
                session.participants.values(),
                key=lambda p: len(p.contributions),
                default=None
            ).name if session.participants else None
        }
        
        return stats

# Global session manager instance
session_manager = SessionManager()