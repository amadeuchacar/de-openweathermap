# AWS REGION
variable "region" {
    description = "AWS region to deploy resources"
    type = string
}

# BUCKETS
variable "bucket_names" {
    type = list(string)
}

# PROJECT
variable "project_name" {
    description = "name of the project"
    type = string
}

variable "environment" {
    description = "environment"
    type = string
}

# EC2
variable "ami_id" {
    description = "The AMI to use"
    default = "ami-0dbc3d7bc646e8516"
}

variable "number_of_instances" {
    description = "number of instances to be created"
    default = 1
}

variable "instance_type" {
    description = "instance type"
    default = "t2.small"
}

variable "ami_key_pair_name" {
    description = "key pair to access ec2 instance"
}

# IAM / ACCESS
variable "role_name" {
    description = "role name for ec2"
    type = string
}

variable "access_key" {
    description = "Access key to AWS console"
}

variable "secret_key" {
    description = "Secret key to AWS console"
}

variable "aws_iam_instance_profile_name" {
    description = "instance profile name to attach iam into ec2"
    type = string
}

# SECURITY GROUP / VPC / CONNECTION
variable "security_group_name" {
    description = "security group with rules for ec2 and redshift"
    type = string
}

variable "vpc_id" {
    description = "vpc default id"
    type = string
}

# REDSHIFT
variable "cluster_identifier" {
    description = "redshitf cluster identifier"
    type = string
}

variable "database_name" {
    description = "redshift database name"
    type = string
    default = "dev"
}

variable "master_username" {
    description = "username to redshift"
    type = string
    default = "admin"
}

variable "master_password" {
    description = "password to redshift"
    type = string
    default = "admin"
}

variable "node_type" {
    description = "redshift node type"
    type = string
}

variable "cluster_type" {
    description = "cluster type - single node or multi node"
    type = string
}

variable "number_of_nodes" {
    description = "number of nodes"
    default = 1
}

variable "redshiftsubnetgroupname" {
    description = "redshift subnet group name"
    type = string
}