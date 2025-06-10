# Define MinIO buckets

resource "minio_s3_bucket" "raw" {
  bucket     = "raw-data"
  acl        = "private"
}

resource "minio_s3_bucket_versioning" "raw_versioning" {
  bucket     = minio_s3_bucket.raw.id

  versioning_configuration {
    status = "Enabled"
  }
  depends_on = [minio_s3_bucket.raw]
}
