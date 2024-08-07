#!/bin/bash

# Initialize Terraform (if not already initialized)
terraform init

# List all resources managed by Terraform
all_resources=$(terraform state list)

# Define the resource to exclude
exclude_resource="aws_ecr_repository.api_ecr"

# Create a variable to hold the -target arguments for terraform destroy
targets=""

# Loop through all resources and add them to the targets variable if they are not the excluded resource
for resource in $all_resources; do
  if [[ $resource != $exclude_resource ]]; then
    targets="$targets -target=$resource"
  fi
done

# Run terraform destroy with all targets except the excluded resource
terraform destroy $targets -auto-approve