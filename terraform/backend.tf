terraform {
    backend "s3" {
        bucket = "terraform-backend-openweather"
        key = "global/s3/terraform.tfstate"
        region = "us-east-1"
    }
}