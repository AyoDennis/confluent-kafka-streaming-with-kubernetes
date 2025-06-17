output "app_producer_api_key" {
  value     = confluent_api_key.app-producer-kafka-api-key.id
  sensitive = true
}

output "app_producer_api_secret" {
  value     = confluent_api_key.app-producer-kafka-api-key.secret
  sensitive = true
}

output "app_producer_schema_registry_key" {
  value     = confluent_api_key.schema_registry_key.id
  sensitive = true
}

output "app_producer_schema_registry_secret" {
  value     = confluent_api_key.schema_registry_key.secret
  sensitive = true
}


output "app_consumer_api_key" {
  value     = confluent_api_key.app-consumer-kafka-api-key.id
  sensitive = true
}

output "app_consumer_api_secret" {
  value     = confluent_api_key.app-consumer-kafka-api-key.secret
  sensitive = true
}