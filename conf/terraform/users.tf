# --- Administrator (pełny dostęp) ---
resource "minio_iam_user" "administrator" {
  name   = "administrator"
  secret = var.administrator_password
}

resource "minio_iam_policy" "AdministratorPolicy" {
  name   = "AdministratorPolicy"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect   = "Allow",
      Action   = ["s3:*"],
      Resource = ["arn:aws:s3:::*"]
    }]
  })
}

resource "minio_iam_user_policy_attachment" "admin_attach" {
  user_name   = minio_iam_user.administrator.name
  policy_name = minio_iam_policy.AdministratorPolicy.name
}

# --- Viewer ---
resource "minio_iam_user" "viewer" {
  name   = "viewer"
  secret = var.viewer_password
}

resource "minio_iam_policy" "ViewerPolicy" {
  name   = "ViewerPolicy"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect   = "Allow",
        Action   = ["s3:ListBucket"],
        Resource = ["arn:aws:s3:::raw-data"]
      },
      {
        Effect   = "Allow",
        Action   = ["s3:GetObject"],
        Resource = ["arn:aws:s3:::raw-data/*"]
      }
    ]
  })
}

resource "minio_iam_user_policy_attachment" "viewer_attach" {
  user_name   = minio_iam_user.viewer.name
  policy_name = minio_iam_policy.ViewerPolicy.name
}

# --- Uploader ---
resource "minio_iam_user" "uploader" {
  name   = "uploader"
  secret = var.uploader_password
}

resource "minio_iam_policy" "UploaderPolicy" {
  name   = "UploaderPolicy"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect   = "Allow",
        Action   = ["s3:ListBucket"],
        Resource = ["arn:aws:s3:::raw-data"]
      },
      {
        Effect   = "Allow",
        Action   = [
          "s3:PutObject",
          "s3:ListMultipartUploadParts",
          "s3:AbortMultipartUpload"
        ],
        Resource = ["arn:aws:s3:::raw-data/*"]
      }
    ]
  })
}

resource "minio_iam_user_policy_attachment" "uploader_attach" {
  user_name   = minio_iam_user.uploader.name
  policy_name = minio_iam_policy.UploaderPolicy.name
}
