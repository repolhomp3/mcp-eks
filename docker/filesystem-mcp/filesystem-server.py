#!/usr/bin/env python3
"""
Simple File System MCP Server
Provides read/write access to local files with safety constraints
"""

import json
import sys
import os
from pathlib import Path

class FileSystemMCP:
    def __init__(self, allowed_paths=None):
        self.allowed_paths = allowed_paths or [str(Path.home())]
    
    def is_path_allowed(self, path):
        """Check if path is within allowed directories"""
        abs_path = os.path.abspath(path)
        return any(abs_path.startswith(allowed) for allowed in self.allowed_paths)
    
    def handle_request(self, request):
        method = request.get('method')
        params = request.get('params', {})
        
        if method == 'tools/list':
            return {
                "tools": [
                    {
                        "name": "read_file",
                        "description": "Read contents of a file",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "path": {"type": "string", "description": "File path to read"}
                            },
                            "required": ["path"]
                        }
                    },
                    {
                        "name": "write_file", 
                        "description": "Write content to a file",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "path": {"type": "string", "description": "File path to write"},
                                "content": {"type": "string", "description": "Content to write"}
                            },
                            "required": ["path", "content"]
                        }
                    },
                    {
                        "name": "list_directory",
                        "description": "List files in a directory", 
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "path": {"type": "string", "description": "Directory path"}
                            },
                            "required": ["path"]
                        }
                    }
                ]
            }
        
        elif method == 'tools/call':
            tool_name = params.get('name')
            args = params.get('arguments', {})
            
            if tool_name == 'read_file':
                return self.read_file(args['path'])
            elif tool_name == 'write_file':
                return self.write_file(args['path'], args['content'])
            elif tool_name == 'list_directory':
                return self.list_directory(args['path'])
        
        return {"error": "Unknown method"}
    
    def read_file(self, path):
        if not self.is_path_allowed(path):
            return {"error": "Path not allowed"}
        try:
            with open(path, 'r') as f:
                return {"content": [{"type": "text", "text": f.read()}]}
        except Exception as e:
            return {"error": str(e)}
    
    def write_file(self, path, content):
        if not self.is_path_allowed(path):
            return {"error": "Path not allowed"}
        try:
            with open(path, 'w') as f:
                f.write(content)
            return {"content": [{"type": "text", "text": f"File written successfully to {path}"}]}
        except Exception as e:
            return {"error": str(e)}
    
    def list_directory(self, path):
        if not self.is_path_allowed(path):
            return {"error": "Path not allowed"}
        try:
            files = os.listdir(path)
            return {"content": [{"type": "text", "text": "\n".join(files)}]}
        except Exception as e:
            return {"error": str(e)}

if __name__ == "__main__":
    import os
    project_dir = os.path.dirname(os.path.abspath(__file__))
    server = FileSystemMCP([os.path.dirname(project_dir)])  # Restrict to project directory
    
    for line in sys.stdin:
        try:
            request = json.loads(line.strip())
            response = server.handle_request(request)
            print(json.dumps(response))
            sys.stdout.flush()
        except Exception as e:
            print(json.dumps({"error": str(e)}))
            sys.stdout.flush()