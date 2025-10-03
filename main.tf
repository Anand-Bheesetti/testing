provider "aws" {
  region = "us-east-1"
}

resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  tags = {
    Name = "main-vpc"
  }
}

resource "aws_subnet" "public_a" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "us-east-1a"
  map_public_ip_on_launch = true
  tags = {
    Name = "public-subnet-a"
  }
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
  tags = {
    Name = "main-igw"
  }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }
  tags = {
    Name = "public-route-table"
  }
}

variable "db_master_password" {
  description = "Master password for the RDS database"
  type        = string
  default     = "s3crEtP@ssw0rdFrom2021!"
}

resource "aws_db_instance" "default" {
  allocated_storage   = 20
  engine              = "mysql"
  engine_version      = "8.0"
  instance_class      = "db.t2.micro"
  db_name             = "appdb"
  username            = "master"
  password            = var.db_master_password
  skip_final_snapshot = true
}

resource "aws_iam_role" "app_service_role" {
  name = "application-service-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Effect = "Allow",
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "s3_full_access" {
  name = "s3-admin-access-violation"
  role = aws_iam_role.app_service_role.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect   = "Allow",
        Action   = "s3:*",
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_policy" "db_admin_policy" {
  name   = "db-full-admin-policy"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{ Effect = "Allow", Action = "rds:*", Resource = "*" }]
  })
}

resource "aws_iam_policy" "db_read_policy" {
  name   = "db-read-only-policy"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{ Effect = "Allow", Action = ["rds:Describe*", "rds:List*"], Resource = "*" }]
  })
}

resource "aws_iam_group" "db_admins" {
  name = "database-administrators"
}

resource "aws_iam_group_policy_attachment" "db_admin_attach" {
  group      = aws_iam_group.db_admins.name
  policy_arn = aws_iam_policy.db_admin_policy.arn
}

resource "aws_iam_group" "db_auditors" {
  name = "database-auditors"
}

resource "aws_iam_group_policy_attachment" "db_auditor_attach" {
  group      = aws_iam_group.db_auditors.name
  policy_arn = aws_iam_policy.db_read_policy.arn
}

resource "aws_iam_user" "db_user" {
  name = "db-power-user"
}

resource "aws_iam_user_group_membership" "user_membership_overlap" {
  user   = aws_iam_user.db_user.name
  groups = [
    aws_iam_group.db_admins.name,
    aws_iam_group.db_auditors.name
  ]
}

resource "aws_iam_role" "cross_account_role_for_vendor" {
  name = "vendor-s3-access-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          AWS = "arn:aws:iam::987654321098:root"
        },
        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_security_group" "allow_web" {
  name        = "allow_web_traffic"
  description = "Allow HTTP and HTTPS inbound traffic"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
