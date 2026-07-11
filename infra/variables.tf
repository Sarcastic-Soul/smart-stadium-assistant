variable "project_id" {
  description = "GCP project ID"
  type        = string
  default     = "promptwars-493516"
}

variable "project_number" {
  description = "GCP project number"
  type        = string
  default     = "139415254857"
}

variable "region" {
  description = "GCP region for all resources"
  type        = string
  default     = "us-central1"
}

variable "enable_cloudsql" {
  description = "Whether to provision a CloudSQL PostgreSQL instance"
  type        = bool
  default     = false
}
