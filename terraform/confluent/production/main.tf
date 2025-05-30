terraform {
  required_providers {
    confluent = {
      source  = "confluentinc/confluent"
      version = "2.28.0"
    }
  }
}

provider "confluent" {
  cloud_api_key    = var.confluent_cloud_api_key
  cloud_api_secret = var.confluent_cloud_api_secret
}

resource "confluent_environment" "production" {
  display_name = "Staging"

  stream_governance {
    package = "ESSENTIALS"
  }
}

resource "confluent_kafka_cluster" "basic" {
  display_name = "Primary Cluster"
  availability = "SINGLE_ZONE"
  cloud        = "AWS"
  region       = "us-east-2"
  basic {}
  environment {
    id = confluent_environment.production.id
  }
}

data "confluent_schema_registry_cluster" "essentials" {
  environment {
    id = confluent_environment.production.id
  }

  depends_on = [
    confluent_kafka_cluster.basic
  ]
}