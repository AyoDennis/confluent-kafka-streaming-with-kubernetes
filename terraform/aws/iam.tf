resource "aws_iam_user" "k8_kafka" {
  name = "k8_kafka"

  tags = {
    service     = "ESO"
    environment = "dev"
  }
}

resource "aws_iam_access_key" "ESO_credentials" {
  user = aws_iam_user.k8_kafka.name
}

resource "aws_ssm_parameter" "k8_kafka_access_key" {
  name  = "/dev/ESO/k8_kafka_access_key"
  type  = "String"
  value = aws_iam_access_key.ESO_credentials.id
}

resource "aws_ssm_parameter" "k8_kafka_secret_key" {
  name  = "/dev/ESO/k8_kafka_secret_key"
  type  = "String"
  value = aws_iam_access_key.ESO_credentials.secret
}

resource "aws_iam_policy" "ESO_policy" {
  name        = "ESO_policy"
  description = "Dedicated policy for external secret operator "

    policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "s3:*",
          "ecr-public:*",
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret"
        ]
        Resource = [
          "*",
        ]
      },
    ]
  })
}

resource "aws_iam_user_policy_attachment" "test-ESO" {
  user       = aws_iam_user.k8_kafka.name
  policy_arn = aws_iam_policy.ESO_policy.arn
}

