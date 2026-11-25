terraform {
  required_version = ">= 1.6, < 2.0"
  required_providers {
    kubernetes = {
      source = "hashicorp/kubernetes"
      version = "~> 2.35"
    }
  }
}
variable "kubeconfig_path" {
  type = string
  default = "~/.kube/config"
}
variable "image" {
  type = string
  default = "ecospecies:classroom"
}
variable "api_key" {
  type = string
  sensitive = true
}
provider "kubernetes" {
  config_path = pathexpand(var.kubeconfig_path)
  config_context = "kind-ecospecies"
}
resource "kubernetes_namespace_v1" "eco" {
  metadata { name = "ecospecies" }
}
resource "kubernetes_secret_v1" "auth" {
  metadata {
    name = "eco-auth"
    namespace = kubernetes_namespace_v1.eco.metadata[0].name
  }
  data = { API_KEY = var.api_key }
}
resource "kubernetes_deployment_v1" "api" {
  metadata {
    name = "ecospecies"
    namespace = kubernetes_namespace_v1.eco.metadata[0].name
  }
  spec {
    replicas = 1
    selector { match_labels = { app = "ecospecies" } }
    template {
      metadata { labels = { app = "ecospecies" } }
      spec {
        security_context {
          run_as_non_root = true
          run_as_user = 10001
          fs_group = 10001
        }
        container {
          name = "api"
          image = var.image
          image_pull_policy = "IfNotPresent"
          port { container_port = 8000 }
          env {
            name = "API_KEY"
            value_from {
              secret_key_ref {
                name = kubernetes_secret_v1.auth.metadata[0].name
                key = "API_KEY"
              }
            }
          }
          resources {
            requests = { cpu = "100m", memory = "256Mi" }
            limits = { cpu = "1", memory = "1Gi" }
          }
          readiness_probe {
            http_get {
              path = "/ready"
              port = 8000
            }
            initial_delay_seconds = 15
          }
          liveness_probe {
            http_get {
              path = "/health"
              port = 8000
            }
            initial_delay_seconds = 30
          }
        }
      }
    }
  }
}
resource "kubernetes_service_v1" "api" {
  metadata {
    name = "ecospecies"
    namespace = kubernetes_namespace_v1.eco.metadata[0].name
  }
  spec {
    selector = { app = "ecospecies" }
    port {
      port = 8000
      target_port = 8000
    }
  }
}
