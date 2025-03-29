from abc import ABC, abstractmethod
from typing import Dict, Any
import requests
import os
from dotenv import load_dotenv

load_dotenv()

PRODUCTION_SERVER_IP = os.getenv("PRODUCTION_SERVER_IP")
PRODUCTION_SERVER_PORT = "8000"
PRODUCTION_SERVER_ENDPOINT = f"http://{PRODUCTION_SERVER_IP}:{PRODUCTION_SERVER_PORT}/api/odds"

class BaseParser(ABC):
    """Base class for all traffic parsers"""
    
    @abstractmethod
    def can_handle_url(self, url: str) -> bool:
        """Check if this parser can handle the given URL"""
        pass
        
    @abstractmethod
    def process_traffic(self, traffic_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process the traffic data and return processed results"""
        pass
        
    def send_to_endpoint(self, processed_data: Dict[str, Any]) -> None:
        """Send processed data to the configured endpoint"""
        try:
            response = requests.post(PRODUCTION_SERVER_ENDPOINT, json=processed_data)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to send data to endpoint: {str(e)}")

class ParserFactory:
    """Factory class for creating and managing parsers"""
    
    def __init__(self):
        self.parsers: list[BaseParser] = []
        
    def register_parser(self, parser: BaseParser) -> None:
        """Register a new parser"""
        self.parsers.append(parser)
        
    def get_parser_for_url(self, url: str) -> BaseParser:
        """Get the appropriate parser for the given URL"""
        for parser in self.parsers:
            if parser.can_handle_url(url):
                return parser
        raise ValueError(f"No parser found for URL: {url}")

# Global parser factory instance
parser_factory = ParserFactory() 