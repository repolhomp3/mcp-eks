resource "helm_release" "keda" {
  name       = "keda"
  repository = "https://kedacore.github.io/charts"
  chart      = "keda"
  version    = "2.12.1"
  namespace  = "keda-system"
  create_namespace = true

  values = [
    <<-EOT
    image:
      keda:
        tag: 2.12.1
      metricsApiServer:
        tag: 2.12.1
      webhooks:
        tag: 2.12.1
    resources:
      operator:
        limits:
          cpu: 1000m
          memory: 1000Mi
        requests:
          cpu: 100m
          memory: 100Mi
      metricServer:
        limits:
          cpu: 1000m
          memory: 1000Mi
        requests:
          cpu: 100m
          memory: 100Mi
      webhooks:
        limits:
          cpu: 50m
          memory: 100Mi
        requests:
          cpu: 10m
          memory: 10Mi
    EOT
  ]

  depends_on = [module.eks]
}