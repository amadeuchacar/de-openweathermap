# OpenWeatherMap Data Engineering Project

## Objetivo

*Realizar um processo de ETL para visualizar dados de previsão do tempo para os próximos 7 dias de todas as cidades do estado do Rio de Janeiro (BRA).*

## Diagrama do projeto:
![Diagram](/pics/OpenweatherProject.png)

## Tecnologias e linguagens utilizadas
- Python
- SQL
- Spark
- Docker
- Airflow
- Amazon Web Services (S3, EC2, Security Groups, IAM, Redshift)
- Terraform

## Realização do projeto

### 1 - Infraestrutura na AWS utilizando Terraform
#### 1.1. Backend do Terraform
É necessário criar um Bucket S3 para armazenar o estado do Terraform, com versionamento de código ativado.
![Bucket Backend](/pics/terraform-backend-bucket.png)
Também é necessário ter configurado na sua máquina o Terraform e a AWS CLI.

#### 1.2. Iniciar o Terraform -> `terraform init`
#### 1.3. Validar códigos do Terraform -> `terraform validate`
#### 1.4. Planejar a execução do Terraform -> `terraform plan`
#### 1.5. Aplicar as configurações do Terraform -> `terraform apply`

Após o término da aplicação, será possível visualizar as estruturas na AWS:
![Buckets After Terraform Apply](/pics/buckets-after-terraform-apply.png)
![IAM After Terraform Apply](/pics/iam-after-terraform-apply.png)
![Redshift Cluster After Terraform Apply](/pics/redshift-after-terraform-apply.png)
![Security Group After Terraform Apply](/pics/security-group-after-terraform.png)
![EC2 After Terraform Apply](/pics/ec2-after-terraform-apply.png)

### 2 - Airflow e orquestração dos pipelines
Após a EC2 executar seu script de inicialização, será possível acessar a UI do Airflow pelo IP da instância na porta 8080.

#### 2.1. Criar conexão com Redshift
É necessário criar uma conexão com o Redshift na UI do Airflow (Admin -> Connections -> +)
![Redshift Connection](/pics/redshift_connection.png)

#### 2.2. Execução da primeira DAG (ETL DATA LAKE)
Nesta primeira DAG será feito todo o processo de ETL do Data Lake (ingestão -> raw -> bronze -> silver -> gold)
![Dag 01 Run](/pics/dag-01-run.png)

Após a execução da DAG é possível verificar o Data Lake:
![Data Lake](/pics/bucket-data-lake.png)

E cada etapa de ETL que utiliza o GlueJobOperator criou um Job no Glue como este:
![Job Glue](/pics/etl-step-1-gluejob.png)

#### 2.3. Execução da segunda DAG (Criar tabelas no Data Warehouse Redshift)
Nesta segunda DAG é criada a estrutura do Data Warehouse no cluster Redshift, deletando tabelas possivelmente existentes.
![Dag 02 Run](/pics/dag-02-run.png)

É possível verificar a estrutura criada:
![Redshift Tables Empty](/pics/redshift-tables.png)

#### 2.4. Execução da terceira DAG (Carregar dados no Data Warehouse Redshift)
Nesta terceira DAG é feito o carregamento dos dados da camada Gold do Data Lake no Data Warehouse
![Dag 03 Run](/pics/dag-03-run.png)

É possível verificar o resultado do carregamento:
![DW 01](/pics/redshift-tables-after-dag.png)
![DW 02](/pics/redshift-tables-after-dag-02.png)

### 3 - Visualização dos dados no Quicksight

#### 3.1. Configurar fonte de dados

É necessário configurar a fonte de dados no Quicksight para o Data Warehouse Redshift criado
![Quicksight Configuration](/pics/quicksight-data-source.png)

Depois, pela modelagem de dados realizada no DW, para juntar todos os dados é necessário utilizar uma fonte de dados com SQL personalizado, utilizando o script `scripts/sql/quicksight.sql` e visualizar.

#### 3.2 Visualizações

Algumas visualizações podem ser montadas no Quicksight, como por exemplo:

##### Média da probabilidade de chuva por dia (próximos 7 dias) e por cidade
![Quicksight Viz 01](/pics/quicksightviz01.png)

#### Mapa de média de probabilidade de chuva em cada cidade pela média de temperatura
![Quicksight Viz 02](/pics/quicksightviz02.png)