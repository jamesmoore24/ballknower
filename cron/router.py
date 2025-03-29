import json
import os
import logging
from typing import Optional, List, Dict, Any
from mitmproxy import io
from parsers.base import parser_factory
from parsers.bet365 import Bet365Parser  # This will register the parser

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def process_traffic_file(file_path: str) -> List[Dict[str, Any]]:
    """
    Process a traffic.mitm file and route requests to appropriate parsers based on URL
    
    Args:
        file_path (str): Path to the traffic.mitm file
        
    Returns:
        List[Dict[str, Any]]: List of processed odds data from all parsers
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Traffic file not found at {file_path}")
    
    all_odds = []  # Store all processed odds data
        
    try:
        with open(file_path, "rb") as f:
            flow_reader = io.FlowReader(f)
            for flow in flow_reader.stream():
                try:
                    # Extract URL from the flow
                    url = flow.request.url
                    
                    try:
                        # Get appropriate parser for the URL
                        parser = parser_factory.get_parser_for_url(url)
                        
                        # Prepare traffic data in the format expected by parsers
                        traffic_data = {
                            'request': {
                                'url': url,
                                'method': flow.request.method,
                                'headers': dict(flow.request.headers),
                                'content': flow.request.content.decode('utf-8') if flow.request.content else ''
                            },
                            'response': {
                                'status_code': flow.response.status_code,
                                'headers': dict(flow.response.headers),
                                'content': flow.response.content.decode('utf-8') if flow.response.content else ''
                            },
                            'timestamp': flow.timestamp_start
                        }
                        
                        # Process the traffic data
                        processed_data = parser.process_traffic(traffic_data)
                        
                        # Send to endpoint
                        parser.send_to_endpoint(processed_data)
                        
                        # Store the processed data
                        all_odds.append(processed_data)
                        
                        logger.info(f"Successfully processed and sent data for URL: {url}")
                        
                    except ValueError as e:
                        # No parser found for URL - log and continue
                        logger.debug(f"No parser found for URL: {url}")
                        continue
                        
                except Exception as e:
                    logger.error(f"Error processing flow in {file_path}: {str(e)}")
                    continue
                    
    except Exception as e:
        logger.error(f"Error reading MITM file {file_path}: {str(e)}")
        raise
        
    return all_odds

def process_directory(directory: str = "scrape-data") -> List[Dict[str, Any]]:
    """
    Process all traffic.mitm files in the specified directory
    
    Args:
        directory (str): Directory containing traffic.mitm files
        
    Returns:
        List[Dict[str, Any]]: Combined list of processed odds data from all files
    """
    if not os.path.exists(directory):
        raise FileNotFoundError(f"Directory not found: {directory}")
    
    all_processed_data = []
        
    for filename in os.listdir(directory):
        if filename.endswith('.mitm'):
            file_path = os.path.join(directory, filename)
            logger.info(f"Processing {file_path}...")
            try:
                file_data = process_traffic_file(file_path)
                all_processed_data.extend(file_data)
            except Exception as e:
                logger.error(f"Failed to process {file_path}: {str(e)}")
                
    return all_processed_data

if __name__ == "__main__":
    process_directory()

