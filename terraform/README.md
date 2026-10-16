# PantryPal infrastructure (AWS)

Provisions the cluster PantryPal runs on:

- **VPC** `10.30.0.0/16` across 2 availability zones: 2 public subnets (load balancers, NAT gateway), 2 private subnets (worker nodes), one NAT gateway.
- **EKS** cluster `pantrypal-dev-eks` (Kubernetes 1.31) with a managed node group (`t3.medium`, 1–3 nodes, 2 desired) in the private subnets.

Modules: [`terraform-aws-modules/vpc`](https://registry.terraform.io/modules/terraform-aws-modules/vpc/aws/5.8.1) 5.8.1 and [`terraform-aws-modules/eks`](https://registry.terraform.io/modules/terraform-aws-modules/eks/aws/20.37.1) 20.37.1.

```bash
cp terraform.tfvars.example terraform.tfvars   # optional overrides; git-ignored
terraform init
terraform plan -out=tfplan
terraform apply tfplan
aws eks update-kubeconfig --region ap-south-1 --name pantrypal-dev-eks
terraform destroy                               # always tear down after the demo
```

Cost warning: EKS control plane (~$0.10/h), the NAT gateway and the EC2 nodes are billed while they exist.

Credentials come from `aws configure` / `AWS_PROFILE` / SSO, never from files in this repo.

## Running against a local AWS emulator

Without an AWS account the same code can be applied to [Moto](https://github.com/getmoto/moto):

```bash
docker run -d --name moto -p 4566:5000 -e MOTO_IAM_LOAD_MANAGED_POLICIES=true motoserver/moto
export AWS_ENDPOINT_URL=http://localhost:4566 AWS_ACCESS_KEY_ID=test AWS_SECRET_ACCESS_KEY=test AWS_REGION=ap-south-1
terraform apply -var enable_cluster_creator_admin_permissions=false   # Moto has no EKS access-entry API
```
