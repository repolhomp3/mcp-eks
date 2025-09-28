#!/bin/bash

# Build and push Docker images
# Update these with your actual registry

REGISTRY="your-registry"
TAG="latest"

# Copy MCP server files from source directory
# Update MCP_SOURCE_DIR to point to your MCP source directory
MCP_SOURCE_DIR="../MCP"
cp $MCP_SOURCE_DIR/aws-mcp/aws-server.py docker/aws-mcp/
cp $MCP_SOURCE_DIR/database-mcp/sqlite-server.py docker/database-mcp/
cp $MCP_SOURCE_DIR/database-mcp/learning.db docker/database-mcp/
cp $MCP_SOURCE_DIR/custom-mcp/template-server.py docker/custom-mcp/
cp $MCP_SOURCE_DIR/local-mcp/filesystem-server.py docker/filesystem-mcp/

# Build images
docker build -t $REGISTRY/aws-mcp:$TAG docker/aws-mcp/
docker build -t $REGISTRY/database-mcp:$TAG docker/database-mcp/
docker build -t $REGISTRY/custom-mcp:$TAG docker/custom-mcp/
docker build -t $REGISTRY/filesystem-mcp:$TAG docker/filesystem-mcp/
docker build -t $REGISTRY/mcp-frontend:$TAG frontend/

# Push images (uncomment when ready)
# docker push $REGISTRY/aws-mcp:$TAG
# docker push $REGISTRY/database-mcp:$TAG
# docker push $REGISTRY/custom-mcp:$TAG
# docker push $REGISTRY/filesystem-mcp:$TAG
# docker push $REGISTRY/mcp-frontend:$TAG

echo "Images built successfully!"
echo "Update helm/mcp-servers/values.yaml with your registry URL"