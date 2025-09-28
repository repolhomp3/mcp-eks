resource "aws_eks_addon" "vpc_cni" {
  cluster_name = module.eks.cluster_name
  addon_name   = "vpc-cni"
  addon_version = "v1.18.1-eksbuild.1"
  resolve_conflicts_on_create = "OVERWRITE"
}

resource "aws_eks_addon" "ebs_csi" {
  cluster_name = module.eks.cluster_name
  addon_name   = "aws-ebs-csi-driver"
  addon_version = "v1.30.0-eksbuild.1"
  resolve_conflicts_on_create = "OVERWRITE"
}

resource "aws_eks_addon" "kube_proxy" {
  cluster_name = module.eks.cluster_name
  addon_name   = "kube-proxy"
  addon_version = "v1.33.0-eksbuild.1"
  resolve_conflicts_on_create = "OVERWRITE"
}

resource "aws_eks_addon" "coredns" {
  cluster_name = module.eks.cluster_name
  addon_name   = "coredns"
  addon_version = "v1.11.3-eksbuild.1"
  resolve_conflicts_on_create = "OVERWRITE"
}

resource "aws_eks_addon" "pod_identity" {
  cluster_name = module.eks.cluster_name
  addon_name   = "eks-pod-identity-agent"
  addon_version = "v1.3.2-eksbuild.2"
  resolve_conflicts_on_create = "OVERWRITE"
}