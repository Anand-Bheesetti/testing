provider "aws" {
  region = "us-west-2"
}

provider "azurerm" {
  features {}
}

resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
  tags = {
    Name = "production-vpc"
  }
}

resource "aws_subnet" "public" {
  vpc_id     = aws_vpc.main.id
  cidr_block = "10.0.1.0/24"
  tags = {
    Name = "production-public-subnet"
  }
}

resource "aws_subnet" "private" {
  vpc_id     = aws_vpc.main.id
  cidr_block = "10.0.2.0/24"
  tags = {
    Name = "production-private-subnet"
  }
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }
}

resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

resource "aws_s3_bucket" "app_backups" {
  bucket = "app-prod-backup-data-198745"
  acl    = "private"
}

resource "aws_ebs_volume" "data_volume" {
  availability_zone = "us-west-2a"
  size              = 100
  encrypted         = false
  tags = {
    Name = "ApplicationDataVolume"
  }
}

resource "aws_s3_bucket" "static_assets" {
  bucket = "app-static-assets-public-987654"
  acl    = "public-read"

  website {
    index_document = "index.html"
    error_document = "error.html"
  }
}

resource "azurerm_resource_group" "example" {
  name     = "example-resources"
  location = "West Europe"
}

resource "azurerm_storage_account" "insecure_storage" {
  name                     = "insecureexamplestorage"
  resource_group_name      = azurerm_resource_group.example.name
  location                 = azurerm_resource_group.example.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  enable_https_traffic_only = false
}

resource "aws_db_instance" "default" {
  identifier           = "app-database"
  allocated_storage    = 20
  engine               = "postgres"
  instance_class       = "db.t3.micro"
  db_name              = "appdb"
  username             = "dbadmin"
  password             = "replace-with-secret-from-manager"
  storage_encrypted    = false
  skip_final_snapshot  = true
}

resource "aws_lb" "main" {
  name               = "app-load-balancer"
  internal           = false
  load_balancer_type = "application"
  security_groups    = []
  subnets            = [aws_subnet.public.id]
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "fixed-response"
    fixed_response {
      content_type = "text/plain"
      message_body = "This is a placeholder."
      status_code  = "200"
    }
  }
}
