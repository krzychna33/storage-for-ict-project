variable "minio_server" {
  description = "MinIO server address"
  type        = string
}

variable "minio_user" {
  description = "MinIO username (root user)"
  type        = string
}

variable "minio_password" {
  description = "MinIO password"
  type        = string
}

variable "minio_ssl" {
  description = "Use SSL for MinIO connection"
  type        = bool
  default     = false
}

# User passwords
variable "administrator_password" {
  description = "Password for the administrator user"
  type        = string
  sensitive   = true
}

variable "viewer_password" {
  description = "Password for the viewer user"
  type        = string
  sensitive   = true
}

variable "uploader_password" {
  description = "Password for the uploader user"
  type        = string
  sensitive   = true
}

