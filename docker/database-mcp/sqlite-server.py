#!/usr/bin/env python3
"""
SQLite MCP Server
Provides database operations for learning SQL and data management
"""

import json
import sys
import sqlite3
import os

class SQLiteMCP:
    def __init__(self, db_path="learning.db"):
        self.db_path = db_path
        self.init_sample_data()
    
    def init_sample_data(self):
        """Create sample tables and data for learning"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create sample tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                user_id INTEGER,
                status TEXT DEFAULT 'active',
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Insert sample data if tables are empty
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            sample_users = [
                ("Alice Johnson", "alice@example.com"),
                ("Bob Smith", "bob@example.com"),
                ("Carol Davis", "carol@example.com")
            ]
            cursor.executemany("INSERT INTO users (name, email) VALUES (?, ?)", sample_users)
            
            sample_projects = [
                ("MCP Learning", "Learning Model Context Protocol", 1, "active"),
                ("AWS Integration", "Exploring AWS services", 1, "planning"),
                ("Database Design", "SQL and NoSQL patterns", 2, "active")
            ]
            cursor.executemany("INSERT INTO projects (name, description, user_id, status) VALUES (?, ?, ?, ?)", sample_projects)
        
        conn.commit()
        conn.close()
    
    def handle_request(self, request):
        method = request.get('method')
        params = request.get('params', {})
        
        if method == 'tools/list':
            return {
                "tools": [
                    {
                        "name": "execute_query",
                        "description": "Execute a SQL query",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "query": {"type": "string", "description": "SQL query to execute"},
                                "params": {"type": "array", "description": "Query parameters", "default": []}
                            },
                            "required": ["query"]
                        }
                    },
                    {
                        "name": "get_schema",
                        "description": "Get database schema information",
                        "inputSchema": {"type": "object", "properties": {}}
                    }
                ]
            }
        
        elif method == 'tools/call':
            tool_name = params.get('name')
            args = params.get('arguments', {})
            
            if tool_name == 'execute_query':
                return self.execute_query(args['query'], args.get('params', []))
            elif tool_name == 'get_schema':
                return self.get_schema()
        
        return {"error": "Unknown method"}
    
    def execute_query(self, query, params):
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Enable column access by name
            cursor = conn.cursor()
            
            cursor.execute(query, params)
            
            if query.strip().upper().startswith('SELECT'):
                results = [dict(row) for row in cursor.fetchall()]
                return {"content": [{"type": "text", "text": json.dumps(results, indent=2)}]}
            else:
                conn.commit()
                return {"content": [{"type": "text", "text": f"Query executed successfully. Rows affected: {cursor.rowcount}"}]}
        
        except Exception as e:
            return {"error": str(e)}
        finally:
            conn.close()
    
    def get_schema(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            schema_info = {}
            for table in tables:
                table_name = table[0]
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                schema_info[table_name] = [
                    {"name": col[1], "type": col[2], "nullable": not col[3], "primary_key": bool(col[5])}
                    for col in columns
                ]
            
            return {"content": [{"type": "text", "text": json.dumps(schema_info, indent=2)}]}
        
        except Exception as e:
            return {"error": str(e)}
        finally:
            conn.close()

if __name__ == "__main__":
    server = SQLiteMCP("database-mcp/learning.db")
    
    for line in sys.stdin:
        try:
            request = json.loads(line.strip())
            response = server.handle_request(request)
            print(json.dumps(response))
            sys.stdout.flush()
        except Exception as e:
            print(json.dumps({"error": str(e)}))
            sys.stdout.flush()