resource "aws_iam_role" "mcp_pod_role" {
  name = "mcp-pod-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "pods.eks.amazonaws.com"
        }
        Action = [
          "sts:AssumeRole",
          "sts:TagSession"
        ]
      }
    ]
  })
}

resource "aws_iam_policy" "mcp_policy" {
  name = "mcp-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel",
          "bedrock:ListFoundationModels",
          "s3:ListAllMyBuckets",
          "s3:GetBucketLocation",
          "s3:ListBucket",
          "s3:GetObject",
          "ec2:DescribeRegions",
          "sts:GetCallerIdentity"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "mcp_policy_attachment" {
  role       = aws_iam_role.mcp_pod_role.name
  policy_arn = aws_iam_policy.mcp_policy.arn
}

resource "aws_eks_pod_identity_association" "mcp_pod_identity" {
  cluster_name    = module.eks.cluster_name
  namespace       = "default"
  service_account = "mcp-service-account"
  role_arn        = aws_iam_role.mcp_pod_role.arn
}