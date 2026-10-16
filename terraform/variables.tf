variable "aws_region" {
  description = "AWS region for all resources."
  type        = string
  default     = "ap-south-1"
}

variable "project" {
  description = "Project name used for resource names and tags."
  type        = string
  default     = "pantrypal"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)."
  type        = string
  default     = "dev"
}

variable "vpc_cidr" {
  description = "CIDR block of the VPC."
  type        = string
  default     = "10.30.0.0/16"
}

variable "public_subnets" {
  description = "Public subnet CIDRs, one per availability zone (load balancers, NAT gateway)."
  type        = list(string)
  default     = ["10.30.0.0/20", "10.30.16.0/20"]
}

variable "private_subnets" {
  description = "Private subnet CIDRs, one per availability zone (EKS worker nodes)."
  type        = list(string)
  default     = ["10.30.128.0/20", "10.30.144.0/20"]
}

variable "kubernetes_version" {
  description = "EKS control plane version."
  type        = string
  default     = "1.31"
}

variable "node_instance_types" {
  description = "Instance types for the managed node group."
  type        = list(string)
  default     = ["t3.medium"]
}

variable "node_min_size" {
  type    = number
  default = 1
}

variable "node_desired_size" {
  type    = number
  default = 2
}

variable "node_max_size" {
  type    = number
  default = 3
}

variable "enable_cluster_creator_admin_permissions" {
  description = "Grant the identity running Terraform cluster-admin through an EKS access entry. Set to false for the local AWS emulator, which has no EKS access-entry API."
  type        = bool
  default     = true
}
