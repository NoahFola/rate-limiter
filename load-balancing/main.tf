terraform {
  required_providers {
    render = {
      source = "render-oss/render"
    }
  }
}

# Auth: set RENDER_API_KEY and RENDER_OWNER_ID as environment variables,
# or pass the variables below.
provider "render" {
  api_key  = var.render_api_key
  owner_id = var.render_owner_id
}

# ---------- Variables ----------

variable "render_api_key" {
  type      = string
  sensitive = true
  default   = null # null => provider falls back to RENDER_API_KEY env var
}

variable "render_owner_id" {
  type    = string
  default = null # null => provider falls back to RENDER_OWNER_ID env var
}

variable "repo_url" {
  type        = string
  description = "Git repo containing the nginx/ folder (Dockerfile + default.conf.template)."
}

variable "branch" {
  type    = string
  default = "main"
}

variable "dockerfile_path" {
  type        = string
  default     = "./nginx/Dockerfile"
  description = "Path to the Dockerfile from the repo root. Use ./Dockerfile if nginx is its own repo."
}

variable "app1_host" {
  type        = string
  description = "Hostname of app server 1, no https://, e.g. app1-abc.onrender.com"
}

variable "app2_host" {
  type        = string
  description = "Hostname of app server 2, no https://, e.g. app2-xyz.onrender.com"
}

variable "plan" {
  type    = string
  default = "free"
}

variable "region" {
  type    = string
  default = "oregon"
}

# ---------- Nginx service ----------

resource "render_web_service" "nginx" {
  name              = "nginx-lb"
  plan              = var.plan
  region            = var.region
  health_check_path = "/healthz"

  runtime_source = {
    docker = {
      repo_url        = var.repo_url
      branch          = var.branch
      root_dir        = "load-balancing"
      dockerfile_path = var.dockerfile_path
      auto_deploy     = true
    }
  }

  env_vars = {
    APP1_HOST = { value = var.app1_host }
    APP2_HOST = { value = var.app2_host }
    PORT      = { value = "10000" }
  }
}

# ---------- Outputs ----------

output "nginx_url" {
  value = render_web_service.nginx.url
}