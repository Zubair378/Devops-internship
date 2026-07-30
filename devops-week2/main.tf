terraform {
  required_providers {
    minikube = {
      source  = "scott-the-programmer/minikube"
      version = "0.6.0"
    }
  }
}

provider "minikube" {}

resource "minikube_cluster" "my-cluster" {
  driver       = "docker"
  cluster_name = "devops-week2"
  memory       = "2200mb"
  cpus         = 2
}
