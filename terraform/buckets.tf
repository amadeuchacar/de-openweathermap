data "aws_caller_identity" "current" {}

resource "aws_s3_bucket" "tf-buckets" {
    count = length(var.bucket_names)
    bucket = "${var.bucket_names[count.index]}"
    force_destroy = true

    tags = {
        Bucket_Name = "${var.bucket_names[count.index]}"
        environment = var.environment
        Project_Name = var.project_name
    }
}

resource "aws_s3_bucket_ownership_controls" "s3_bucket_acl_ownership" {
    count = length(var.bucket_names)
    bucket = "${var.bucket_names[count.index]}"

    rule {
        object_ownership = "ObjectWriter"
    }

    depends_on = [aws_s3_bucket.tf-buckets]
}

resource "aws_s3_bucket_public_access_block" "public_access_block" {
    count = length(var.bucket_names)
    bucket = "${var.bucket_names[count.index]}"

    block_public_acls = true
    block_public_policy = true
    ignore_public_acls = true
    restrict_public_buckets = true

    depends_on = [ aws_s3_bucket.tf-buckets ]
}