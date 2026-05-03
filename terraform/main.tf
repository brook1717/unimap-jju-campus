# ──────────────────────────────────────────────────────────────────────────────
# main.tf — UniMap Backend on AWS (EC2 + Elastic IP)
# ──────────────────────────────────────────────────────────────────────────────
# Deploys:
#   • Ubuntu 22.04 LTS t3.micro (Free Tier)
#   • 30 GB gp3 root volume
#   • Security Group: SSH (your IP only), HTTP (80), HTTPS (443)
#   • Elastic IP associated with the instance
#   • SSH key pair from your public key
#   • user_data bootstrap script (placeholder for software install)
# ──────────────────────────────────────────────────────────────────────────────

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# ── Data: Latest Ubuntu 22.04 LTS AMI ────────────────────────────────────────

data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# ── SSH Key Pair ──────────────────────────────────────────────────────────────

resource "aws_key_pair" "deployer" {
  key_name   = "${var.project_name}-deployer-key"
  public_key = var.public_key

  tags = {
    Name    = "${var.project_name}-deployer-key"
    Project = var.project_name
  }
}

# ── Security Group ────────────────────────────────────────────────────────────

resource "aws_security_group" "web" {
  name        = "${var.project_name}-web-sg"
  description = "UniMap backend — SSH (restricted), HTTP, HTTPS"

  # SSH — restricted to operator IP only
  ingress {
    description = "SSH from my IP"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.my_ip]
  }

  # HTTP — public
  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # HTTPS — public
  ingress {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # All outbound traffic
  egress {
    description = "Allow all outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name    = "${var.project_name}-web-sg"
    Project = var.project_name
  }
}

# ── EC2 Instance ──────────────────────────────────────────────────────────────

resource "aws_instance" "backend" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.instance_type
  key_name               = aws_key_pair.deployer.key_name
  vpc_security_group_ids = [aws_security_group.web.id]

  root_block_device {
    volume_size           = var.volume_size
    volume_type           = var.volume_type
    delete_on_termination = true
    encrypted             = true
  }

  user_data = file("${path.module}/scripts/user_data.sh")

  tags = {
    Name    = "${var.project_name}-backend"
    Project = var.project_name
  }
}

# ── Elastic IP ────────────────────────────────────────────────────────────────

resource "aws_eip" "backend" {
  domain = "vpc"

  tags = {
    Name    = "${var.project_name}-backend-eip"
    Project = var.project_name
  }
}

resource "aws_eip_association" "backend" {
  instance_id   = aws_instance.backend.id
  allocation_id = aws_eip.backend.id
}
