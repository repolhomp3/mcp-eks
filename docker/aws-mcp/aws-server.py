#!/usr/bin/env python3
"""
AWS MCP Server - Free Tier Optimized
Focuses on free/low-cost AWS services for learning
"""

import json
import sys
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

class AWSMCP:
    def __init__(self):
        self.session = None
        self.init_aws_session()
    
    def init_aws_session(self):
        """Initialize AWS session with error handling"""
        try:
            self.session = boto3.Session()
            # Test credentials
            sts = self.session.client('sts')
            sts.get_caller_identity()
        except (NoCredentialsError, ClientError):
            self.session = None
    
    def handle_request(self, request):
        method = request.get('method')
        params = request.get('params', {})
        
        if method == 'tools/list':
            return {
                "tools": [
                    {
                        "name": "list_s3_buckets",
                        "description": "List S3 buckets (free tier friendly)",
                        "inputSchema": {"type": "object", "properties": {}}
                    },
                    {
                        "name": "get_aws_regions",
                        "description": "List available AWS regions",
                        "inputSchema": {"type": "object", "properties": {}}
                    },
                    {
                        "name": "check_free_tier_usage",
                        "description": "Check free tier usage (simulated)",
                        "inputSchema": {"type": "object", "properties": {}}
                    },
                    {
                        "name": "invoke_bedrock_model",
                        "description": "Invoke Bedrock model (cost-conscious)",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "model_id": {"type": "string", "description": "Model ID (default: amazon.titan-text-lite-v1)"},
                                "prompt": {"type": "string", "description": "Text prompt"},
                                "max_tokens": {"type": "integer", "description": "Max tokens (default: 100)", "default": 100}
                            },
                            "required": ["prompt"]
                        }
                    }
                ]
            }
        
        elif method == 'tools/call':
            if not self.session:
                return {"error": "AWS credentials not configured. Run 'aws configure' first."}
            
            tool_name = params.get('name')
            args = params.get('arguments', {})
            
            if tool_name == 'list_s3_buckets':
                return self.list_s3_buckets()
            elif tool_name == 'get_aws_regions':
                return self.get_aws_regions()
            elif tool_name == 'check_free_tier_usage':
                return self.check_free_tier_usage()
            elif tool_name == 'invoke_bedrock_model':
                return self.invoke_bedrock_model(
                    args.get('model_id', 'amazon.titan-text-lite-v1'),
                    args['prompt'],
                    args.get('max_tokens', 100)
                )
        
        return {"error": "Unknown method"}
    
    def list_s3_buckets(self):
        try:
            s3 = self.session.client('s3')
            response = s3.list_buckets()
            buckets = [bucket['Name'] for bucket in response['Buckets']]
            return {"content": [{"type": "text", "text": f"S3 Buckets: {json.dumps(buckets, indent=2)}"}]}
        except Exception as e:
            return {"error": f"S3 error: {str(e)}"}
    
    def get_aws_regions(self):
        try:
            ec2 = self.session.client('ec2', region_name='us-east-1')
            response = ec2.describe_regions()
            regions = [region['RegionName'] for region in response['Regions']]
            return {"content": [{"type": "text", "text": f"AWS Regions: {json.dumps(regions, indent=2)}"}]}
        except Exception as e:
            return {"error": f"Regions error: {str(e)}"}
    
    def check_free_tier_usage(self):
        """Simulated free tier usage check"""
        usage_info = {
            "ec2_hours_used": "0/750 hours",
            "s3_storage_used": "0/5 GB", 
            "lambda_requests": "0/1M requests",
            "dynamodb_reads": "0/25 RCU",
            "bedrock_tokens": "Varies by model",
            "note": "This is simulated data. Use AWS Billing Dashboard for real usage."
        }
        return {"content": [{"type": "text", "text": json.dumps(usage_info, indent=2)}]}
    
    def invoke_bedrock_model(self, model_id, prompt, max_tokens):
        try:
            bedrock = self.session.client('bedrock-runtime', region_name='us-west-2')
            
            # Different request formats for different models
            if 'nova' in model_id:
                # Nova models format
                body = {
                    "messages": [
                        {"role": "user", "content": [{"text": prompt}]}
                    ],
                    "inferenceConfig": {
                        "max_new_tokens": min(max_tokens, 100),
                        "temperature": 0.7
                    }
                }
            else:
                # Titan models format
                body = {
                    "inputText": prompt,
                    "textGenerationConfig": {
                        "maxTokenCount": min(max_tokens, 100),
                        "temperature": 0.7
                    }
                }
            
            response = bedrock.invoke_model(
                modelId=model_id,
                body=json.dumps(body),
                contentType='application/json'
            )
            
            result = json.loads(response['body'].read())
            
            # Extract response based on model type
            if 'nova' in model_id:
                output_text = result['output']['message']['content'][0]['text']
            else:
                output_text = result['results'][0]['outputText']
            
            return {"content": [{"type": "text", "text": f"Model: {model_id}\nResponse: {output_text}"}]}
        
        except Exception as e:
            return {"error": f"Bedrock error: {str(e)}. Note: Bedrock may not be available in all regions or require model access."}

if __name__ == "__main__":
    server = AWSMCP()
    
    for line in sys.stdin:
        try:
            request = json.loads(line.strip())
            response = server.handle_request(request)
            print(json.dumps(response))
            sys.stdout.flush()
        except Exception as e:
            print(json.dumps({"error": str(e)}))
            sys.stdout.flush()