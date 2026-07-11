output "gke_cluster_name" {
  description = "Name of the GKE Autopilot cluster"
  value       = google_container_cluster.primary.name
}

output "gke_cluster_endpoint" {
  description = "GKE cluster endpoint"
  value       = google_container_cluster.primary.endpoint
  sensitive   = true
}

output "artifact_registry_url" {
  description = "Docker registry URL for container images"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.images.repository_id}"
}

output "secret_name" {
  description = "Secret Manager secret resource name"
  value       = google_secret_manager_secret.api_key.name
}

output "workload_sa_email" {
  description = "Workload service account email"
  value       = google_service_account.workload.email
}
