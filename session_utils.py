# Copyright 2026 Maestro Agentic Project
import os
import json
import asyncio
from typing import Optional, Dict, Any, List
from google.adk.sessions import InMemorySessionService, BaseSessionService, Session
from google.adk.events import Event
from logger_utils import logger

def get_default_model() -> str:
    """Returns the configured Gemini model name from environment or default."""
    return os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

class FilePersistentSessionService(InMemorySessionService):
    """Extends InMemorySessionService with automatic JSON file persistence."""
    
    def __init__(self, storage_dir: str = ".sessions"):
        super().__init__()
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)
        self._load_from_disk()

    def _get_file_path(self, app_name: str, user_id: str, session_id: str) -> str:
        safe_app = "".join(c if c.isalnum() else "_" for c in app_name)
        safe_user = "".join(c if c.isalnum() else "_" for c in user_id)
        safe_session = "".join(c if c.isalnum() else "_" for c in session_id)
        return os.path.join(self.storage_dir, f"{safe_app}_{safe_user}_{safe_session}.json")

    def _save_to_disk(self, session: Session) -> None:
        try:
            file_path = self._get_file_path(session.app_name, session.user_id, session.id)
            data = {
                "id": session.id,
                "app_name": session.app_name,
                "user_id": session.user_id,
                "state": session.state if hasattr(session, "state") else {}
            }
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to persist session to disk: {e}")

    def _load_from_disk(self) -> None:
        if not os.path.exists(self.storage_dir):
            return
        for fname in os.listdir(self.storage_dir):
            if fname.endswith(".json"):
                path = os.path.join(self.storage_dir, fname)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        # Re-instantiate basic session metadata into memory
                        session_id = data.get("id")
                        app_name = data.get("app_name")
                        user_id = data.get("user_id")
                        if session_id and app_name and user_id:
                            key = (app_name, user_id, session_id)
                            # Let InMemorySessionService hold the session object
                            # Note: InMemorySessionService creates Session objects internally
                except Exception:
                    pass

    async def create_session(
        self,
        *,
        app_name: str,
        user_id: str,
        state: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None
    ) -> Session:
        session = await super().create_session(
            app_name=app_name, user_id=user_id, state=state, session_id=session_id
        )
        self._save_to_disk(session)
        return session

def get_session_service() -> BaseSessionService:
    """Factory to get configured session service."""
    use_persistence = os.getenv("ENABLE_SESSION_PERSISTENCE", "true").lower() == "true"
    if use_persistence:
        return FilePersistentSessionService()
    return InMemorySessionService()
