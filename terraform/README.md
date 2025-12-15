# AWS Lambda + RDS PostgreSQL Terraform Setup

This Terraform configuration deploys your FastAPI URL Shortener to AWS Lambda with RDS PostgreSQL.

## Architecture

- **Lambda**: Runs your FastAPI application in a container
- **API Gateway**: HTTP endpoint that triggers Lambda
- **RDS PostgreSQL**: Managed relational database
- **VPC**: Private networking for Lambda and RDS
- **ECR**: Container image repository
- **CloudWatch**: Logs for Lambda and API Gateway

## Prerequisites

1. **AWS Account** with sufficient permissions
2. **Terraform** >= 1.0 installed
3. **Docker** to build images
4. **AWS CLI** configured with credentials

```bash
aws configure
```

## Setup

### 1. Copy the variables file

```bash
cp terraform/terraform.tfvars.example terraform/terraform.tfvars
```

Edit `terraform/terraform.tfvars` and set:
- `db_password`: A strong, secure password (min 8 chars)
- `aws_region`: Your preferred AWS region
- Other variables as needed

### 2. Build and push Docker image to ECR

Get the AWS account ID:
```bash
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION="us-east-1"  # match your terraform.tfvars
```

Login to ECR:
```bash
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
```

Build and push:
```bash
docker build -f Dockerfile.lambda -t url-shortener:latest .
docker tag url-shortener:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/url-shortener:latest
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/url-shortener:latest
```

### 3. Initialize and apply Terraform

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

Confirm the plan by typing `yes`.

## Deployment

After Terraform completes, you'll get outputs including:
- `api_gateway_endpoint`: Your API URL (e.g., `https://xxx.execute-api.us-east-1.amazonaws.com`)
- `ecr_repository_url`: ECR image URL

Test the API:
```bash
curl https://xxx.execute-api.us-east-1.amazonaws.com/docs
```

## Updating the Lambda Function

After code changes:

1. Rebuild and push the Docker image (see step 2 above)
2. Update Lambda:
```bash
aws lambda update-function-code \
  --function-name url-shortener \
  --image-uri $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/url-shortener:latest
```

Or re-apply Terraform:
```bash
terraform apply
```

## Important Notes

### Security

- **Passwords**: Never commit `terraform.tfvars` to git (it's in `.gitignore`)
- **Remote State**: Use S3 backend for team collaboration (uncomment in `main.tf`)
- **Secrets Manager**: For production, use AWS Secrets Manager instead of env vars

### Lambda Configuration

- **Memory**: Default 512 MB; adjust in `terraform.tfvars`
- **Timeout**: 30 seconds; increase if needed in `main.tf`
- **Concurrency**: Set reserved concurrency if you expect high traffic

### Database

- **RDS**: Default `db.t3.micro` (free-tier eligible)
- **Multi-AZ**: Disabled by default; enable for production
- **Backups**: Enabled; set `skip_final_snapshot = false` for safety

### Costs

- Lambda: ~$0.20/million requests
- RDS: ~$10-20/month for t3.micro
- API Gateway: $3.50/million requests
- Data transfer: Variable

## Cleanup

To destroy all resources:

```bash
terraform destroy
```

Type `yes` to confirm. This will:
- Delete Lambda, API Gateway, VPC, RDS, ECR
- Remove CloudWatch logs
- Release EIPs and NAT Gateways

**Warning**: If `skip_final_snapshot = false`, Terraform will create a final RDS snapshot before deletion.

## Troubleshooting

### Lambda can't reach database

Check:
1. Security group allows inbound on port 5432 from Lambda security group
2. Lambda is in the same VPC as RDS
3. Database URL in environment variables is correct

### API Gateway returns 502

Check CloudWatch logs:
```bash
aws logs tail /aws/lambda/url-shortener --follow
```

### ECR image not found

Ensure the image is pushed to ECR and the URI matches the tag.
