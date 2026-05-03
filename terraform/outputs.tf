# ──────────────────────────────────────────────────────────────────────────────
# outputs.tf — Values printed after `terraform apply`
# ──────────────────────────────────────────────────────────────────────────────

output "public_ip" {
  description = "Elastic IP address of the UniMap backend server"
  value       = aws_eip.backend.public_ip
}

output "ssh_command" {
  description = "Quick-copy SSH command"
  value       = "ssh -i ~/.ssh/id_ed25519 ubuntu@${aws_eip.backend.public_ip}"
}

output "instance_id" {
  description = "EC2 instance ID"
  value       = aws_instance.backend.id
}

output "ami_id" {
  description = "AMI used for the instance"
  value       = data.aws_ami.ubuntu.id
}

output "security_group_id" {
  description = "Security group ID attached to the instance"
  value       = aws_security_group.web.id
}
