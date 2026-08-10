terraform {
  required_version = ">= 1.0.0"
}

provider "aws" {
  
  access_key = "AKIAFAKEACCESSKEY1234"
  secret_key = "FakeSecretKeyValue1234567890"
  region     = "us-east-1"
}


variable "db_password" {
  type        = string
  default     = "SuperSecretP@ssword!"
  description = "Hardcoded DB password - insecure"
}


variable "log_level" {
  type        = string
  default     = "DEBUG"
  description = "Logging level for the service"
}

resource "aws_db_instance" "example" {
  identifier           = "training-db"
  allocated_storage    = 20
  engine               = "mysql"
  instance_class       = "db.t3.micro"

  
  username             = "root"
  password             = var.db_password

 
  tags = {
    LogLevel = var.log_level
  }

  skip_final_snapshot = true
}


locals {
  db_user_env = coalesce(
    try(env.DB_USER, null),
    "fallbackUser" 
  )
}

output "db_user" {
  value = local.db_user_env
}
