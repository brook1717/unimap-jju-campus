# ──────────────────────────────────────────────────────────────────────────────
# variables.tf — Input variables for the UniMap AWS deployment
# ──────────────────────────────────────────────────────────────────────────────

variable "aws_region" {
  description = "AWS region to deploy into"
  type        = string
  default     = "eu-west-1"
}

variable "project_name" {
  description = "Name prefix for all resources"
  type        = string
  default     = "unimap"
}

variable "my_ip" {
  description = "Your public IP in CIDR notation for SSH access (e.g. 203.0.113.5/32)"
  type        = string
  # No default — must be supplied at plan/apply time
}

variable "public_key" {
  description = "SSH public key material (contents of ~/.ssh/id_rsa.pub or id_ed25519.pub)"
  type        = string
  sensitive   = true
}

variable "instance_type" {
  description = "EC2 instance type (Free Tier eligible)"
  type        = string
  default     = "t3.micro"
}

variable "volume_size" {
  description = "Root EBS volume size in GB"
  type        = number
  default     = 30
}

variable "volume_type" {
  description = "EBS volume type"
  type        = string
  default     = "gp3"
}
