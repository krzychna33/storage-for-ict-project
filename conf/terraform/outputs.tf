output "admin_access_key" {
  value = minio_iam_user.administrator.name
}

output "admin_secret_key" {
  value     = var.administrator_password
  sensitive = true
}

output "viewer_access_key" {
  value = minio_iam_user.viewer.name
}

output "viewer_secret_key" {
  value     = var.viewer_password
  sensitive = true
}

output "uploader_access_key" {
  value = minio_iam_user.uploader.name
}

output "uploader_secret_key" {
  value     = var.uploader_password
  sensitive = true
}
