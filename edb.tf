terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

# IAM Users
resource "aws_iam_user" "app_user" {
  name = "app-user"
}

resource "aws_iam_user" "dev_user" {
  name = "dev-user"
}

# IAM Policies
resource "aws_iam_policy" "s3_rw" {
  name        = "s3-readwrite"
  description = "Read/Write access to app bucket"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["s3:GetObject", "s3:PutObject"]
        Resource = ["arn:aws:s3:::app-bucket/*"]
      }
    ]
  })
}

# Hidden privilege escalation policy (violation)
resource "aws_iam_policy" "hidden_escalation" {
  name        = "hidden-escalation"
  description = "Hidden privilege escalation policy"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["iam:AttachUserPolicy", "iam:PutUserPolicy"]
        Resource = "*"
      }
    ]
  })
}

# Attach policies
resource "aws_iam_user_policy_attachment" "attach_s3_user" {
  user       = aws_iam_user.app_user.name
  policy_arn = aws_iam_policy.s3_rw.arn
}

resource "aws_iam_user_policy_attachment" "attach_escalation_dev" {
  user       = aws_iam_user.dev_user.name
  policy_arn = aws_iam_policy.hidden_escalation.arn
}

# S3 Bucket
resource "aws_s3_bucket" "app_bucket" {
  bucket = "app-bucket"
  acl    = "private"
}

# Dummy resources to inflate length
resource "aws_security_group" "dummy_sg" {
  name        = "dummy-sg"
  description = "Dummy SG to increase lines"
  vpc_id      = "vpc-123456"
}

resource "aws_instance" "dummy_instance" {
  ami           = "ami-12345678"
  instance_type = "t3.micro"
  count         = 50
  tags = {
    Name = "dummy-instance-${count.index}"
  }
}
