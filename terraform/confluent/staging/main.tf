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

resource "confluent_environment" "staging" {
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
    id = confluent_environment.staging.id
  }
}


data "confluent_schema_registry_cluster" "essentials" {
  environment {
    id = confluent_environment.staging.id
  }

  depends_on = [
    confluent_kafka_cluster.basic
  ]
}

resource "confluent_service_account" "app-manager" {
  display_name = "app-manager"
  description  = "Service account to manage the Kafka cluster"
}

resource "confluent_role_binding" "app-manager-kafka-cluster-admin" {
  principal   = "User:${confluent_service_account.app-manager.id}"
  role_name   = "CloudClusterAdmin"
  crn_pattern = confluent_kafka_cluster.basic.rbac_crn
}

resource "confluent_api_key" "app-manager-kafka-api-key" {
  display_name = "app-manager-kafka-api-key"
  description  = "Kafka API Key that is owned by 'app-manager' service account"
  owner {
    id          = confluent_service_account.app-manager.id
    api_version = confluent_service_account.app-manager.api_version
    kind        = confluent_service_account.app-manager.kind
  }

  managed_resource {
    id          = confluent_kafka_cluster.basic.id
    api_version = confluent_kafka_cluster.basic.api_version
    kind        = confluent_kafka_cluster.basic.kind

    environment {
      id = confluent_environment.staging.id
    }
  }

  depends_on = [
    confluent_role_binding.app-manager-kafka-cluster-admin
  ]
}

resource "confluent_kafka_topic" "customer-information" {
  kafka_cluster {
    id = confluent_kafka_cluster.basic.id
  }
  topic_name    = "customer-information"
  rest_endpoint = confluent_kafka_cluster.basic.rest_endpoint
  partitions_count = 3
  credentials {
    key    = confluent_api_key.app-manager-kafka-api-key.id
    secret = confluent_api_key.app-manager-kafka-api-key.secret
  }
}


resource "confluent_role_binding" "schema_registry_write_all_subjects" {
  principal   = "User:${confluent_service_account.app-manager.id}"
  role_name   = "ResourceOwner"
  crn_pattern = "${data.confluent_schema_registry_cluster.essentials.resource_name}/subject=customer-information-value"

  depends_on = [
    confluent_service_account.app-manager,
    data.confluent_schema_registry_cluster.essentials
  ]
}


resource "confluent_api_key" "schema_registry_key" {
  display_name = "Schema Registry API Key for app-manager"
  description  = "API key for Schema Registry access"

  owner {
    id          = confluent_service_account.app-manager.id
    api_version = confluent_service_account.app-manager.api_version
    kind        = confluent_service_account.app-manager.kind
  }

  managed_resource {
    id          = data.confluent_schema_registry_cluster.essentials.id
    api_version = data.confluent_schema_registry_cluster.essentials.api_version
    kind        = data.confluent_schema_registry_cluster.essentials.kind

    environment {
      id = confluent_environment.staging.id
    }
  }

  depends_on = [
    data.confluent_schema_registry_cluster.essentials,
    confluent_role_binding.schema_registry_write_all_subjects
  ]
}


## create contract
resource "confluent_schema" "my_data_contract" {
  subject_name = "${confluent_kafka_topic.customer-information.topic_name}-value"
  format       = "JSON"
  schema       = file("${path.module}/project_schema.json")

  schema_registry_cluster {
    id = data.confluent_schema_registry_cluster.essentials.id
  }

  rest_endpoint = data.confluent_schema_registry_cluster.essentials.rest_endpoint

  depends_on = [
    confluent_api_key.schema_registry_key
  ]

  credentials {
    key    = confluent_api_key.schema_registry_key.id
    secret = confluent_api_key.schema_registry_key.secret
  }
}



resource "confluent_service_account" "app-producer" {
  display_name = "app-producer"
  description  = "Service account to produce to 'customer-information' topic of 'staging' Kafka cluster"
}


resource "confluent_kafka_acl" "app-producer-write-on-topic" {
  kafka_cluster {
    id = confluent_kafka_cluster.basic.id
  }
  resource_type = "TOPIC"
  resource_name = confluent_kafka_topic.customer-information.topic_name
  pattern_type  = "LITERAL"
  principal     = "User:${confluent_service_account.app-producer.id}"
  host          = "*"
  operation     = "WRITE"
  permission    = "ALLOW"
  rest_endpoint = confluent_kafka_cluster.basic.rest_endpoint
  credentials {
    key    = confluent_api_key.app-manager-kafka-api-key.id
    secret = confluent_api_key.app-manager-kafka-api-key.secret
  }
}


resource "confluent_api_key" "app-producer-kafka-api-key" {
  display_name = "app-producer-kafka-api-key"
  description  = "Kafka API Key that is owned by 'app-producer' service account"
  owner {
    id          = confluent_service_account.app-producer.id
    api_version = confluent_service_account.app-producer.api_version
    kind        = confluent_service_account.app-producer.kind
  }

  managed_resource {
    id          = confluent_kafka_cluster.basic.id
    api_version = confluent_kafka_cluster.basic.api_version
    kind        = confluent_kafka_cluster.basic.kind

    environment {
      id = confluent_environment.staging.id
    }
  }

  depends_on = [
    confluent_service_account.app-producer
  ]
}




resource "confluent_service_account" "app-consumer" {
  display_name = "app-consumer"
  description  = "Service account to read from 'customer-information' topic of 'staging' Kafka cluster"
}


resource "confluent_kafka_acl" "app-consumer-read-on-topic" {
  kafka_cluster {
    id = confluent_kafka_cluster.basic.id
  }
  resource_type = "TOPIC"
  resource_name = confluent_kafka_topic.customer-information.topic_name
  pattern_type  = "LITERAL"
  principal     = "User:${confluent_service_account.app-consumer.id}"
  host          = "*"
  operation     = "READ"
  permission    = "ALLOW"
  rest_endpoint = confluent_kafka_cluster.basic.rest_endpoint
  credentials {
    key    = confluent_api_key.app-manager-kafka-api-key.id
    secret = confluent_api_key.app-manager-kafka-api-key.secret
  }
  depends_on = [
    confluent_service_account.app-consumer
  ]
}

resource "confluent_kafka_acl" "app-consumer-read-on-topic-consumer-group" {
  kafka_cluster {
    id = confluent_kafka_cluster.basic.id
  }
  resource_type = "GROUP"
  resource_name = "DLA-"
  pattern_type  = "PREFIXED"
  principal     = "User:${confluent_service_account.app-consumer.id}"
  host          = "*"
  operation     = "READ"
  permission    = "ALLOW"
  rest_endpoint = confluent_kafka_cluster.basic.rest_endpoint
  credentials {
    key    = confluent_api_key.app-manager-kafka-api-key.id
    secret = confluent_api_key.app-manager-kafka-api-key.secret
  }
  depends_on = [
    confluent_service_account.app-consumer
  ]
}


resource "confluent_api_key" "app-consumer-kafka-api-key" {
  display_name = "app-consumer-kafka-api-key"
  description  = "Kafka API Key that is owned by 'app-consumer' service account"
  owner {
    id          = confluent_service_account.app-consumer.id
    api_version = confluent_service_account.app-consumer.api_version
    kind        = confluent_service_account.app-consumer.kind
  }

  managed_resource {
    id          = confluent_kafka_cluster.basic.id
    api_version = confluent_kafka_cluster.basic.api_version
    kind        = confluent_kafka_cluster.basic.kind

    environment {
      id = confluent_environment.staging.id
    }
  }

  depends_on = [
    confluent_service_account.app-consumer,
    confluent_kafka_acl.app-consumer-read-on-topic
  ]
}