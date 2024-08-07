# Eisei-ai-api-terraform

This repository contains the terraform code to deploy the Eisei AI API on AWS.

## Create aws configuration

- Install aws-vault https://github.com/99designs/aws-vault
- Set up aws account

```bash
aws-vault add <profile_name>
```
- Add mfaws to the profile. Open the file `~/.aws/config` and add the following lines to the profile.

```bash
[profile <profile_name>]
region = ap-northeast-1
mfa_serial = arn:aws:iam::<aws_account_id>:mfa/<username>
```

## Create ECR repository

- Login to the aws account
```bash
aws-vault exec <profile_name> --no-session --duration=12h -- terraform init
```

- Create ECR repository

```bash
cd terraform
terraform apply -target=aws_ecr_repository.api_ecr
docker build -t eisei-ai-api-repository .
aws ecr get-login-password --region ap-northeast-1 | docker login --username AWS --password-stdin <aws_account_id>.dkr.ecr.ap-northeast-1.amazonaws.com
docker tag eisei-ai-api-repository:latest <aws_account_id>.dkr.ecr.ap-northeast-1.amazonaws.com/eisei-ai-api-repository:latest
docker push <aws_account_id>.dkr.ecr.ap-northeast-1.amazonaws.com/eisei-ai-api-repository:latest
```

## Deploy Eisei AI API

```bash
terraform init
terraform apply
```

## Check the API

- Output the API endpoint

```bash
Outputs:

lb_dns_name = <api_endpoint>
```

## Destroy Eisei AI API

```bash
terraform destroy
```
