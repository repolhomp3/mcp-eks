#!/usr/bin/env python3
"""
Custom MCP Server Template
Use this as a starting point for building your own MCP servers
"""

import json
import sys
import requests
from datetime import datetime

class CustomMCP:
    def __init__(self):
        self.data_store = {}  # Simple in-memory storage
    
    def handle_request(self, request):
        method = request.get('method')
        params = request.get('params', {})
        
        if method == 'tools/list':
            return {
                "tools": [
                    {
                        "name": "store_data",
                        "description": "Store key-value data",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "key": {"type": "string", "description": "Data key"},
                                "value": {"type": "string", "description": "Data value"}
                            },
                            "required": ["key", "value"]
                        }
                    },
                    {
                        "name": "get_data",
                        "description": "Retrieve stored data",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "key": {"type": "string", "description": "Data key"}
                            },
                            "required": ["key"]
                        }
                    },
                    {
                        "name": "get_weather",
                        "description": "Get weather info (demo API call)",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "city": {"type": "string", "description": "City name"}
                            },
                            "required": ["city"]
                        }
                    },
                    {
                        "name": "generate_timestamp",
                        "description": "Generate current timestamp",
                        "inputSchema": {"type": "object", "properties": {}}
                    }
                ]
            }
        
        elif method == 'tools/call':
            tool_name = params.get('name')
            args = params.get('arguments', {})
            
            if tool_name == 'store_data':
                return self.store_data(args['key'], args['value'])
            elif tool_name == 'get_data':
                return self.get_data(args['key'])
            elif tool_name == 'get_weather':
                return self.get_weather(args['city'])
            elif tool_name == 'generate_timestamp':
                return self.generate_timestamp()
        
        return {"error": "Unknown method"}
    
    def store_data(self, key, value):
        self.data_store[key] = {
            "value": value,
            "timestamp": datetime.now().isoformat()
        }
        return {"content": [{"type": "text", "text": f"Stored '{key}' = '{value}'"}]}
    
    def get_data(self, key):
        if key in self.data_store:
            data = self.data_store[key]
            return {"content": [{"type": "text", "text": json.dumps(data, indent=2)}]}
        else:
            return {"error": f"Key '{key}' not found"}
    
    def get_weather(self, city):
        """Demo API call - uses free weather service"""
        try:
            # Using a free weather API (no key required)
            url = f"https://wttr.in/{city}?format=j1"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                current = data['current_condition'][0]
                weather_info = {
                    "city": city,
                    "temperature": f"{current['temp_C']}°C",
                    "description": current['weatherDesc'][0]['value'],
                    "humidity": f"{current['humidity']}%"
                }
                return {"content": [{"type": "text", "text": json.dumps(weather_info, indent=2)}]}
            else:
                return {"error": f"Weather API error: {response.status_code}"}
        
        except Exception as e:
            return {"error": f"Weather request failed: {str(e)}"}
    
    def generate_timestamp(self):
        timestamp = {
            "iso": datetime.now().isoformat(),
            "unix": int(datetime.now().timestamp()),
            "readable": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        return {"content": [{"type": "text", "text": json.dumps(timestamp, indent=2)}]}

if __name__ == "__main__":
    server = CustomMCP()
    
    for line in sys.stdin:
        try:
            request = json.loads(line.strip())
            response = server.handle_request(request)
            print(json.dumps(response))
            sys.stdout.flush()
        except Exception as e:
            print(json.dumps({"error": str(e)}))
            sys.stdout.flush()