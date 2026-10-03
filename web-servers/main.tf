terraform {
  required_providers {
    render = {
      source = "render-oss/render"
    }
  }
}



variable "render_api_key" {
  type      = string
  sensitive = true
}

variable "render_owner_id" {
  type = string
}

variable "log_level" {
  type        = string
  default     = "INFO"
  description = "Python log level for the Flask app (DEBUG, INFO, WARNING, ERROR)."
}

provider "render" {
  api_key = var.render_api_key
  owner_id = var.render_owner_id
}




resource "render_web_service" "app" {
  name   = "url-shortener"
  plan   = "free"
  region = "oregon"

  runtime_source = {
    docker = {
      repo_url        = "https://github.com/NoahFola/rate-limiter"
      branch          = "main"
      dockerfile_path = "./web-servers/Dockerfile"
      context         = "./web-servers"
      auto_deploy     = true
    }
  }

  env_vars = {
    DATABASE_URL = { value = "postgresql://postgres.jrotkyjigadwllfqugib:FOFsyTMhMoGTCeEv@aws-1-eu-central-1.pooler.supabase.com:5432/postgres" }
    REDIS_URL    = { value = "rediss://red-datid1psrm7s738r1te0:DRYKvPUQpwJX32L1XXoLYkEdok9bU5HM@oregon-keyvalue.render.com:6379" }
    LOG_LEVEL    = { value = var.log_level }
  }
}


resource "render_web_service" "app2" {
  name   = "url-shortener-2"
  plan   = "free"
  region = "oregon"

  runtime_source = {
    docker = {
      repo_url        = "https://github.com/NoahFola/rate-limiter"
      branch          = "main"
      dockerfile_path = "./web-servers/Dockerfile"
      context         = "./web-servers"
      auto_deploy     = true
    }
  }

  env_vars = {
    DATABASE_URL = { value = "postgresql://postgres.jrotkyjigadwllfqugib:FOFsyTMhMoGTCeEv@aws-1-eu-central-1.pooler.supabase.com:5432/postgres" }
    REDIS_URL    = { value = "rediss://red-datid1psrm7s738r1te0:DRYKvPUQpwJX32L1XXoLYkEdok9bU5HM@oregon-keyvalue.render.com:6379" }
    LOG_LEVEL    = { value = var.log_level }
  }
}
  
output "service_url" {
  value = render_web_service.app.url
}