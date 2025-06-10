terraform {
  backend "s3" {
    bucket         = "kafka-kubernetes-project" # To be created
    key            = "staging/terraform.tfstate"
    region         = "eu-north-1"
    encrypt        = true
  }
}