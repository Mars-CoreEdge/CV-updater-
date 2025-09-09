import os
import requests
from typing import Any, Dict, List, Optional


class SupabaseClient:
    def __init__(self) -> None:
        self.url = os.getenv("SUPABASE_URL", "").rstrip("/")
        self.service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
        if not self.url or not self.service_role_key:
            raise RuntimeError("Supabase URL or SERVICE ROLE key not configured")
        self.rest_url = f"{self.url}/rest/v1"
        self.headers = {
            "apikey": self.service_role_key,
            "Authorization": f"Bearer {self.service_role_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }

    # --------------- CVs table helpers ---------------
    def list_cvs(self) -> List[Dict[str, Any]]:
        params = {
            "select": "id,title,filename,created_at,updated_at,is_active",
            "order": "updated_at.desc",
        }
        r = requests.get(f"{self.rest_url}/cvs", headers=self.headers, params=params)
        r.raise_for_status()
        return r.json() or []

    def get_cv(self, cv_id: int) -> Optional[Dict[str, Any]]:
        params = {
            "id": f"eq.{cv_id}",
            "select": "id,title,filename,current_content,created_at,updated_at,is_active",
        }
        r = requests.get(f"{self.rest_url}/cvs", headers=self.headers, params=params)
        r.raise_for_status()
        data = r.json()
        return data[0] if data else None

    def get_active_cv_content(self) -> Optional[str]:
        params = {
            "is_active": "eq.true",
            "select": "current_content",
            "limit": 1
        }
        r = requests.get(f"{self.rest_url}/cvs", headers=self.headers, params=params)
        r.raise_for_status()
        data = r.json()
        return (data[0] or {}).get("current_content") if data else None

    # --------------- Manual projects (optional mirror) ---------------
    def clear_manual_projects(self) -> None:
        # If you create a supabase table 'manual_projects' with 'project_data' jsonb
        try:
            requests.delete(f"{self.rest_url}/manual_projects", headers=self.headers)
        except Exception:
            pass

    def insert_manual_projects(self, projects: List[Dict[str, Any]]) -> None:
        try:
            body = [{"project_data": p} for p in projects]
            if body:
                requests.post(f"{self.rest_url}/manual_projects", headers=self.headers, json=body)
        except Exception:
            pass

    def list_manual_projects(self) -> List[Dict[str, Any]]:
        try:
            params = {"select": "id,project_data,created_at", "order": "created_at.desc"}
            r = requests.get(f"{self.rest_url}/manual_projects", headers=self.headers, params=params)
            r.raise_for_status()
            return r.json() or []
        except Exception:
            return []

    def insert_cv(self, title: str, filename: str, content: str) -> Dict[str, Any]:
        # Set all others inactive first
        requests.patch(f"{self.rest_url}/cvs", headers=self.headers, json={"is_active": False})

        body = [{
            "title": title,
            "filename": filename,
            "original_content": content,
            "current_content": content,
            "is_active": True,
        }]
        r = requests.post(f"{self.rest_url}/cvs", headers=self.headers, json=body)
        r.raise_for_status()
        data = r.json()
        return data[0] if isinstance(data, list) and data else data

    def update_cv(self, cv_id: int, fields: Dict[str, Any]) -> None:
        params = {"id": f"eq.{cv_id}"}
        # prefer not returning full representation here
        headers = {**self.headers, "Prefer": "return=minimal"}
        r = requests.patch(f"{self.rest_url}/cvs", headers=headers, params=params, json=fields)
        r.raise_for_status()

    def delete_cv(self, cv_id: int) -> Dict[str, Any]:
        # Find if it was active
        cv = self.get_cv(cv_id)
        was_active = bool(cv.get("is_active")) if cv else False

        params = {"id": f"eq.{cv_id}"}
        r = requests.delete(f"{self.rest_url}/cvs", headers=self.headers, params=params)
        r.raise_for_status()

        if was_active:
            # Promote latest as active if any remains
            latest = self.list_cvs()
            if latest:
                latest_id = latest[0]["id"]
                self.update_cv(latest_id, {"is_active": True})

        return {"deleted": True}

    def activate_cv(self, cv_id: int) -> None:
        # deactivate all, then activate one
        requests.patch(f"{self.rest_url}/cvs", headers=self.headers, json={"is_active": False})
        self.update_cv(cv_id, {"is_active": True})

    def get_cv_content_for_download(self, cv_id: int) -> Optional[Dict[str, Any]]:
        params = {
            "id": f"eq.{cv_id}",
            "select": "title,current_content",
            "limit": 1
        }
        r = requests.get(f"{self.rest_url}/cvs", headers=self.headers, params=params)
        r.raise_for_status()
        data = r.json()
        return data[0] if data else None


def get_supabase_client() -> SupabaseClient:
    return SupabaseClient()


