terraform {
  backend "s3" {
    bucket         = "kafka-kubernetes-Project" # To be created
    key            = "dev/dev.tfstate"
    region         = "eu-north-1"
    encrypt        = true
  }
}