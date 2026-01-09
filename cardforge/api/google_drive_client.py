"""
CardForge Google Drive Client
Async Google Drive API for backup/sync
"""

from typing import Optional, List, Dict, Any, BinaryIO
from datetime import timedelta
import json
import io

from .base_client import BaseAPIClient


class GoogleDriveClient(BaseAPIClient):
    """
    Async Google Drive API client for collection backup.
    
    Requires OAuth2 credentials.
    """
    
    base_url = "https://www.googleapis.com/drive/v3"
    upload_url = "https://www.googleapis.com/upload/drive/v3"
    rate_limit = 10.0
    cache_ttl = timedelta(minutes=5)
    
    CARDFORGE_FOLDER = "CardForge Backups"
    
    def __init__(
        self,
        credentials_json: Optional[str] = None,
        access_token: Optional[str] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self._credentials = credentials_json
        if access_token:
            self._headers["Authorization"] = f"Bearer {access_token}"
    
    async def set_access_token(self, token: str):
        """Set or update the access token."""
        self._headers["Authorization"] = f"Bearer {token}"
    
    async def health_check(self) -> bool:
        """Check if Google Drive API is accessible."""
        try:
            await self.get("/about", params={"fields": "user"})
            return True
        except Exception:
            return False
    
    # =====================
    # Folder Methods
    # =====================
    
    async def get_or_create_backup_folder(self) -> str:
        """Get or create the CardForge backup folder."""
        # Search for existing folder
        query = f"name='{self.CARDFORGE_FOLDER}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        result = await self.get("/files", params={
            "q": query,
            "fields": "files(id, name)"
        })
        
        files = result.get("files", [])
        if files:
            return files[0]["id"]
        
        # Create new folder
        return await self.create_folder(self.CARDFORGE_FOLDER)
    
    async def create_folder(
        self, 
        name: str, 
        parent_id: Optional[str] = None
    ) -> str:
        """Create a folder and return its ID."""
        metadata = {
            "name": name,
            "mimeType": "application/vnd.google-apps.folder"
        }
        
        if parent_id:
            metadata["parents"] = [parent_id]
        
        result = await self.post("/files", data=metadata)
        return result["id"]
    
    # =====================
    # File Methods
    # =====================
    
    async def list_files(
        self,
        folder_id: Optional[str] = None,
        query: Optional[str] = None,
        page_size: int = 100,
    ) -> List[Dict[str, Any]]:
        """List files, optionally in a specific folder."""
        params = {
            "pageSize": page_size,
            "fields": "files(id, name, mimeType, modifiedTime, size)"
        }
        
        q_parts = ["trashed=false"]
        if folder_id:
            q_parts.append(f"'{folder_id}' in parents")
        if query:
            q_parts.append(query)
        
        params["q"] = " and ".join(q_parts)
        
        result = await self.get("/files", params=params)
        return result.get("files", [])
    
    async def get_file_metadata(self, file_id: str) -> Dict[str, Any]:
        """Get file metadata."""
        return await self.get(
            f"/files/{file_id}",
            params={"fields": "id, name, mimeType, modifiedTime, size"}
        )
    
    async def download_file(self, file_id: str) -> bytes:
        """Download file content."""
        url = f"{self.base_url}/files/{file_id}"
        params = {"alt": "media"}
        
        await self._rate_limiter.acquire()
        
        async with self.session.get(url, params=params) as response:
            response.raise_for_status()
            return await response.read()
    
    async def download_json(self, file_id: str) -> Dict[str, Any]:
        """Download and parse JSON file."""
        content = await self.download_file(file_id)
        return json.loads(content.decode('utf-8'))
    
    async def upload_file(
        self,
        name: str,
        content: bytes,
        mime_type: str = "application/json",
        folder_id: Optional[str] = None,
    ) -> str:
        """Upload a file and return its ID."""
        # Metadata part
        metadata = {"name": name}
        if folder_id:
            metadata["parents"] = [folder_id]
        
        url = f"{self.upload_url}/files"
        params = {"uploadType": "multipart"}
        
        # Build multipart body
        import aiohttp
        
        form = aiohttp.FormData()
        form.add_field(
            'metadata',
            json.dumps(metadata),
            content_type='application/json'
        )
        form.add_field(
            'file',
            content,
            content_type=mime_type,
            filename=name
        )
        
        await self._rate_limiter.acquire()
        
        async with self.session.post(url, params=params, data=form) as response:
            response.raise_for_status()
            result = await response.json()
            return result["id"]
    
    async def upload_json(
        self,
        name: str,
        data: Dict[str, Any],
        folder_id: Optional[str] = None,
    ) -> str:
        """Upload JSON data as a file."""
        content = json.dumps(data, indent=2).encode('utf-8')
        return await self.upload_file(
            name=name,
            content=content,
            mime_type="application/json",
            folder_id=folder_id
        )
    
    async def update_file(
        self,
        file_id: str,
        content: bytes,
        mime_type: str = "application/json",
    ) -> str:
        """Update an existing file's content."""
        url = f"{self.upload_url}/files/{file_id}"
        params = {"uploadType": "media"}
        
        await self._rate_limiter.acquire()
        
        async with self.session.patch(
            url, 
            params=params, 
            data=content,
            headers={"Content-Type": mime_type}
        ) as response:
            response.raise_for_status()
            result = await response.json()
            return result["id"]
    
    async def delete_file(self, file_id: str) -> bool:
        """Delete a file."""
        await self._rate_limiter.acquire()
        
        async with self.session.delete(f"{self.base_url}/files/{file_id}") as response:
            return response.status == 204
    
    # =====================
    # Backup Methods
    # =====================
    
    async def backup_collection(
        self,
        collection_data: Dict[str, Any],
        backup_name: Optional[str] = None,
    ) -> str:
        """
        Backup collection to Google Drive.
        
        Returns file ID of backup.
        """
        from datetime import datetime
        
        folder_id = await self.get_or_create_backup_folder()
        
        if not backup_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"collection_backup_{timestamp}.json"
        
        return await self.upload_json(
            name=backup_name,
            data=collection_data,
            folder_id=folder_id
        )
    
    async def get_latest_backup(self) -> Optional[Dict[str, Any]]:
        """Get the most recent backup file."""
        folder_id = await self.get_or_create_backup_folder()
        files = await self.list_files(folder_id=folder_id)
        
        # Sort by modified time
        backups = sorted(
            files,
            key=lambda f: f.get("modifiedTime", ""),
            reverse=True
        )
        
        if not backups:
            return None
        
        return await self.download_json(backups[0]["id"])
    
    async def list_backups(self) -> List[Dict[str, Any]]:
        """List all backup files."""
        folder_id = await self.get_or_create_backup_folder()
        files = await self.list_files(folder_id=folder_id)
        
        return sorted(
            files,
            key=lambda f: f.get("modifiedTime", ""),
            reverse=True
        )
