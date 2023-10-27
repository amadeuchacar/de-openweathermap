data "aws_subnets" "vpc_subnets" {
  filter {
    name   = "vpc-id"
    values = [var.vpc_id]
  }
}

data "aws_subnet" "vpc_subnets_each" {
  for_each = toset(data.aws_subnets.vpc_subnets.ids)
  id       = each.value
}

resource "aws_redshift_subnet_group" "redshift_subnet_group" {
    name = "redshiftsubnetgroupterraform"
    subnet_ids = [ for s in data.aws_subnet.vpc_subnets_each : s.id ]

    tags = {
        Name        = "redshiftsubnetgroupterraform"
        Environment = "dev"
    }
}

resource "aws_redshift_cluster" "redshift_cluster" {
    cluster_identifier     = var.cluster_identifier
    database_name          = var.database_name
    master_username        = var.master_username
    master_password        = var.master_password
    node_type              = var.node_type
    cluster_type           = var.cluster_type
    number_of_nodes        = var.number_of_nodes
    publicly_accessible    = true
    skip_final_snapshot    = true
    vpc_security_group_ids = [aws_security_group.security_group.id]

    # Parâmetros de configuração do cluster
    cluster_parameter_group_name = "default.redshift-1.0"

    iam_roles = [aws_iam_role.s3_role.arn]

    cluster_subnet_group_name = aws_redshift_subnet_group.redshift_subnet_group.id
}