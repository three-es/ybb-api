import os
import tempfile
import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

class TempFileStorage:
    def __init__(self):
        self._temp_dir = tempfile.mkdtemp()
        self._files: Dict[str, Dict] = {}
    
    def store_file(self, file_data: bytes, original_filename: str) -> Tuple[str, str]:
        """Store a file in temporary storage and return its unique ID and path."""
        # Generate unique ID for this file
        file_id = str(uuid.uuid4())
        
        # Create temporary file
        _, ext = os.path.splitext(original_filename)
        temp_path = os.path.join(self._temp_dir, f"{file_id}{ext}")
        
        # Write file data
        with open(temp_path, 'wb') as f:
            f.write(file_data)
        
        # Store file info
        self._files[file_id] = {
            'path': temp_path,
            'downloaded': False,
            'created_at': datetime.now(),
            'original_name': original_filename
        }
        
        return file_id, temp_path

    def get_file(self, file_id: str) -> Optional[Tuple[str, str]]:
        """Get file path if it exists and hasn't been downloaded."""
        file_info = self._files.get(file_id)
        if not file_info or file_info['downloaded']:
            return None
            
        # Mark as downloaded
        file_info['downloaded'] = True
        return file_info['path'], file_info['original_name']

    def cleanup_old_files(self, max_age_hours: int = 24):
        """Remove files older than specified hours."""
        now = datetime.now()
        for file_id, info in list(self._files.items()):
            if now - info['created_at'] > timedelta(hours=max_age_hours):
                try:
                    os.remove(info['path'])
                    del self._files[file_id]
                except OSError:
                    pass

# Global instance
storage = TempFileStorage()
