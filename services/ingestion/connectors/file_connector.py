"""
File connector: reads content from local text files.
"""
import uuid
from pathlib import Path
from typing import Iterator
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'schemas')))
from models import ContentEvent
from connector import Connector, ConnectorRegistry


class FileConnector(Connector):
    """Reads text files from a local directory."""
    
    @property
    def source_name(self) -> str:
        return "file"
    
    def fetch(self) -> Iterator[ContentEvent]:
        """
        Scan configured directory and yield one event per file.
        
        Config keys:
            - path: Directory path to scan
            - pattern: File glob pattern (default: *.txt)
        """
        directory = Path(self.config.get("path", "."))
        pattern = self.config.get("pattern", "*.txt")
        
        for file_path in directory.glob(pattern):
            if file_path.is_file():
                try:
                    text = file_path.read_text(encoding="utf-8")
                    yield ContentEvent(
                        id=str(uuid.uuid4()),
                        source=self.source_name,
                        content_type="text",
                        text=text,
                        metadata={
                            "file_name": file_path.name,
                            "file_path": str(file_path.absolute()),
                            "file_size": file_path.stat().st_size
                        }
                    )
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")


# Register this connector
ConnectorRegistry.register("file", FileConnector)
