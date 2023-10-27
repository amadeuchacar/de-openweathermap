# ROLES AWS
resource "aws_iam_role" "s3_role" {
    name = var.role_name

    assume_role_policy = jsonencode({
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "ec2.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            },
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "glue.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    })
}

# PASS ROLE 
resource "aws_iam_policy" "iamPassRole" {
    name = "iamPassRole"

    policy = jsonencode({
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": "iam:PassRole",
                "Resource": aws_iam_role.s3_role.arn
            }
        ]
    })
}

# IAM Instance Profile
resource "aws_iam_instance_profile" "s3_role_instance_profile" {
    name = var.aws_iam_instance_profile_name
    role = aws_iam_role.s3_role.name
    depends_on = [ aws_iam_role.s3_role ]
}

# Attach IAM policy to IAM role
locals {
  iam_pass_role_policy_arn = aws_iam_policy.iamPassRole.arn
}

resource "aws_iam_policy_attachment" "s3_role_policy_attachment_redshiftfull" {
    name = "Policy Attachment - Redshift Full Access"
    policy_arn = "arn:aws:iam::aws:policy/AmazonRedshiftFullAccess"
    roles = [aws_iam_role.s3_role.name]
    depends_on = [ aws_iam_role.s3_role ]
}

resource "aws_iam_policy_attachment" "s3_role_policy_attachment_s3full" {
    name = "Policy Attachment - AmazonS3FullAccess"
    policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
    roles = [aws_iam_role.s3_role.name]
    depends_on = [ aws_iam_role.s3_role ]
}

resource "aws_iam_policy_attachment" "s3_role_policy_attachment_glueconsolefull" {
    name = "Policy Attachment - AWSGlueConsoleFullAccess"
    policy_arn = "arn:aws:iam::aws:policy/AWSGlueConsoleFullAccess"
    roles = [aws_iam_role.s3_role.name]
    depends_on = [ aws_iam_role.s3_role ]
}

resource "aws_iam_policy_attachment" "s3_role_policy_attachment_glueservicerole" {
    name = "Policy Attachment - AWSGlueServiceRole"
    policy_arn = "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
    roles = [aws_iam_role.s3_role.name]
    depends_on = [ aws_iam_role.s3_role ]
}

resource "aws_iam_policy_attachment" "s3_role_policy_attachment_passrole" {
    name = "Policy Attachment - Pass Role"
    policy_arn = local.iam_pass_role_policy_arn
    roles = [aws_iam_role.s3_role.name]
    depends_on = [ aws_iam_role.s3_role ]
}