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

provider "render" {
  api_key = var.render_api_key
  owner_id = var.render_owner_id
}


resource "render_keyvalue" "redis_cache" {
  name               = "redis-cache-rate-limiter"
  plan               = "free"
  region             = "oregon"
  max_memory_policy = "noeviction"
  
}

resource "render_postgres" "url_db" {
  name     = "url-shortener-db"
  plan     = "free"
  region   = "oregon"
  version  = "16"
}


