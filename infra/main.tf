# ──────────────────────────────────────────────────────────────────
# Smart Stadium Assistant – Terraform Root Module
# Target: GCP project promptwars-493516 / 139415254857
# ──────────────────────────────────────────────────────────────────

terraform {
  backend "gcs" {
    bucket = "promptwars-tf-state"
    prefix = "smart-stadium"
  }

  required_version = ">= 1.5"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# ── Enable Required APIs ─────────────────────────────────────────

resource "google_project_service" "apis" {
  for_each = toset([
    "container.googleapis.com",
    "secretmanager.googleapis.com",
    "artifactregistry.googleapis.com",
    "sqladmin.googleapis.com",
    "cloudbuild.googleapis.com",
    "compute.googleapis.com",
  ])
  project            = var.project_id
  service            = each.value
  disable_on_destroy = false
}

# ── Artifact Registry ────────────────────────────────────────────

resource "google_artifact_registry_repository" "images" {
  location      = var.region
  repository_id = "smart-stadium"
  format        = "DOCKER"
  description   = "Container images for the Smart Stadium Assistant"

  depends_on = [google_project_service.apis]
}

# ── Secret Manager ───────────────────────────────────────────────

resource "google_secret_manager_secret" "api_key" {
  secret_id = "CLONEMODEL_API_KEY"
  project   = var.project_id

  replication {
    auto {}
  }

  depends_on = [google_project_service.apis]
}

# ── GKE Autopilot Cluster ───────────────────────────────────────

resource "google_container_cluster" "primary" {
  name     = "smart-stadium-gke"
  location = var.region

  # Autopilot mode
  enable_autopilot = true

  # Network config
  network    = "default"
  subnetwork = "default"

  # Release channel
  release_channel {
    channel = "REGULAR"
  }

  # Workload identity
  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }

  deletion_protection = false

  depends_on = [google_project_service.apis]
}

# ── Service Account for Workloads ────────────────────────────────

resource "google_service_account" "workload" {
  account_id   = "ssa-workload"
  display_name = "Smart Stadium Assistant Workload"
  project      = var.project_id
}

resource "google_secret_manager_secret_iam_member" "workload_secret_access" {
  secret_id = google_secret_manager_secret.api_key.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.workload.email}"
}

resource "google_project_iam_member" "workload_log_writer" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.workload.email}"
}

resource "google_service_account_iam_member" "workload_identity" {
  service_account_id = google_service_account.workload.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "serviceAccount:${var.project_id}.svc.id.goog[default/ssa-backend]"
}

# ── CloudSQL PostgreSQL (optional – for future persistence) ──────

resource "google_sql_database_instance" "postgres" {
  count            = var.enable_cloudsql ? 1 : 0
  name             = "ssa-postgres"
  database_version = "POSTGRES_15"
  region           = var.region

  settings {
    tier              = "db-f1-micro"
    availability_type = "ZONAL"

    ip_configuration {
      ipv4_enabled = true
    }

    backup_configuration {
      enabled = true
    }
  }

  deletion_protection = false
  depends_on          = [google_project_service.apis]
}
