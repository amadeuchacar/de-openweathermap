resource "aws_instance" "ec2_instance" {
  ami = var.ami_id
  count = var.number_of_instances
  instance_type = var.instance_type
  key_name = var.ami_key_pair_name
  iam_instance_profile = var.aws_iam_instance_profile_name
  vpc_security_group_ids = [aws_security_group.security_group.id]
  depends_on = [ aws_s3_bucket.tf-buckets ]

  user_data = <<-EOF
              #!/bin/bash
              # Variáveis
              DOCKER_COMPOSE_URL="https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)"
              GITHUB_REPO="https://github.com/amadeuchacar/de-openweather-test.git"
              PROJECT_DIR="/opt/project"
              S3_BUCKET="s3://openweather-amadeu/scripts"
              
              # Atualiza o sistema e instala o Docker
              sudo yum update -y
              sudo yum install docker -y
              sudo service docker start
              sudo usermod -a -G docker ec2-user
              newgrp docker

              # Instala o Docker Compose
              sudo wget "$DOCKER_COMPOSE_URL" -O /usr/libexec/docker/cli-plugins/docker-compose
              sudo chmod +x /usr/libexec/docker/cli-plugins/docker-compose

              # Habilita e inicia o serviço Docker
              sudo systemctl enable docker.service --now

              # Instala o Git
              sudo yum install git -y

              # Clone o repositório do GitHub
              sudo git clone "$GITHUB_REPO" "$PROJECT_DIR"
              cd "$PROJECT_DIR"

              # Sincroniza o diretório de scripts com o bucket S3
              aws s3 sync ./scripts "$S3_BUCKET"

              # Inicializa e inicia o Airflow
              docker compose up airflow-init
              docker compose up airflow-webserver airflow-scheduler -d
              EOF
}