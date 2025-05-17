# Storage for ICT proj

## About setup
This repository contains a setup for a storage system using MinIO, which is an open-source object storage server compatible with Amazon S3.
We are using docker to run MinIO locally and terraform to configure it.

## Running MinIO locally using docker

in `conf` dir:

```shell
docker compose up
```

You can adjust docker-compose.yml file to change the number of minio instances, load balancer settings, etc.

It will spin up few minio containers and a load balancer.
It's because we deploy it in topology with multiple minio instances.

When it's running you can also access the minio console at `http://localhost:9001` and the load balancer at `http://localhost:9000`.

## Configuring MinIO using Terraform

### Prerequisites

In order to configure minio (buckets, policies, users) we use terraform.
To run it you need to have `terraform` installed (check `https://developer.hashicorp.com/terraform/install` for guidance).

There is one more step to do before running terraform. You need to set up tferraform variables.
In the `terraform` directory, create a file called `terraform.tfvars` and copy the content from `terraform.tfvars.example` into it. 
Then, fill in the values for the variables.

The `terraform.tfvars` file should look like this:
```hcl
# MinIO connection details
minio_server = "localhost:9000"
minio_user = "minioadmin"
minio_password = "minioadmin"  # Replace with your actual secure password
minio_ssl = false

# User passwords
administrator_password = "admin_secure_password123"  # Replace with a secure password
viewer_password = "viewer_secure_password123"        # Replace with a secure password
uploader_password = "uploader_secure_password123"    # Replace with a secure password
```

### Running Terraform

To plan and apply the terraform configuration, run the following commands in the `terraform` directory:

```shell
terraform init
```
It will download the necessary providers.

```shell
terraform plan
```
It will show you what will be created. 

```shell
terraform apply
```
It will create the resources.

### Output

In the end you will see an output like this:
```shell
admin_access_key = "administrator"
admin_secret_key = <sensitive>
uploader_access_key = "uploader"
uploader_secret_key = <sensitive>
viewer_access_key = "viewer"
viewer_secret_key = <sensitive>
```

You can use this output (and values like passwords from tfvars file) to access the minio instance from web console or using the minio client.



