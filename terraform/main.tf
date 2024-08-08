terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.0"
    }
  }
}

provider "aws" {
  region = "ap-northeast-1"
}

# Create a VPC
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
}

# Create public subnets
resource "aws_subnet" "public" {
  count                   = 2
  vpc_id                  = aws_vpc.main.id
  cidr_block              = cidrsubnet(aws_vpc.main.cidr_block, 8, count.index)
  map_public_ip_on_launch = true
  availability_zone       = element(["ap-northeast-1a", "ap-northeast-1c"], count.index)
}

# Create an Internet Gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
}

# Create a route table
resource "aws_route_table" "main" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }
}

# Associate the route table with the public subnets
resource "aws_route_table_association" "public" {
  count          = length(aws_subnet.public[*].id)
  subnet_id      = element(aws_subnet.public[*].id, count.index)
  route_table_id = aws_route_table.main.id
}

# Create a Security Group
resource "aws_security_group" "main" {
  vpc_id = aws_vpc.main.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 22
    to_port     = 22
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

# Create an EC2 instance
resource "aws_instance" "app_instance" {
  ami                         = "ami-0e35aea09ae54a6db" # Replace with a valid Amazon Linux 2 AMI ID
  instance_type               = "t2.medium"
  subnet_id                   = element(aws_subnet.public[*].id, 0)
  vpc_security_group_ids      = [aws_security_group.main.id]
  associate_public_ip_address = true

  root_block_device {
    volume_size = 30
  }

  user_data = <<-EOF
              #!/bin/bash
              set -e  # Exit immediately if a command exits with a non-zero status

              # Activate the virtual environment
              source /home/ec2-user/venv/bin/activate

              # Change to the app directory
              cd /app/app

              # Start FastAPI app on port 8080
              nohup uvicorn main:app --host 0.0.0.0 --port 8080 &
              EOF

  tags = {
    Name = "FastAPIAppInstance"
  }

  depends_on = [
    aws_security_group.main
  ]
}

# Output the public IP of the EC2 instance
output "instance_public_ip" {
  value = aws_instance.app_instance.public_ip
}
