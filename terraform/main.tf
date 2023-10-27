terraform {
    required_providers {
      aws = {
        source = "hashicorp/aws"
        version = "~> 4.0"
      }
    }
}

# Configure AWS provider
provider "aws" {
    region = var.region
}