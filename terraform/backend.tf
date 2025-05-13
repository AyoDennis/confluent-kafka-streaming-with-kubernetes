terraform {
  backend "s3" {
    bucket         = "Kafka-Kubernetes-Project" # To be created
    key            = "dev/dev.tfstate"
    region         = "eu-north-1"
    encrypt        = true
  }
}