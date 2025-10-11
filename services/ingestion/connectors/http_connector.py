"""
HTTP connector: fetches content from HTTP endpoints.
"""
import uuid
from typing import Iterator
import requests
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data', 'schemas')))
from models import ContentEvent
from connector import Connector, ConnectorRegistry


class HTTPConnector(Connector):
    """Fetches content from HTTP URLs."""
    
    @property
    def source_name(self) -> str:
        return "http"
    
    def fetch(self) -> Iterator[ContentEvent]:
        """
        Fetch content from URLs specified in config.
        
        Config keys:
            - urls: List of URLs to fetch
        """
        urls = self.config.get("urls", [])
        
        for url in urls:
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                
                yield ContentEvent(
                    id=str(uuid.uuid4()),
                    source=self.source_name,
                    content_type="text",
                    text=response.text,
                    metadata={
                        "url": url,
                        "status_code": response.status_code,
                        "content_length": len(response.text)
                    }
                )
            except Exception as e:
                print(f"Error fetching {url}: {e}")


# Register this connector
ConnectorRegistry.register("http", HTTPConnector)
