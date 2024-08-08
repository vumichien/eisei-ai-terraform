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

## Deploy Eisei AI API

- Login to the aws account
```bash
aws-vault exec <profile_name> --no-session --duration=12h
```

- Apply plan

```bash
cd terraform
terraform init
terraform apply -auto-approve
```

Outputs:
```bash
instance_public_ip = <instance_public_ip>
```
## Check the API

browser : http://<instance_public_ip>:8080

## Destroy Eisei AI API

```bash
terraform destroy -auto-approve
```

## Create AMI for Eisei AI API (Optional)
- Start the the large instance (t2.xlarge) with the latest Amazon Linux 2023 AMI
- Run the following commands in `create_ami.sh` to create the AMI
