FROM nginx:1.27-alpine

# Default port; Render can override via the PORT env var.
ENV PORT=10000

# The official image runs envsubst on files in /etc/nginx/templates/ at startup
# and writes the result to /etc/nginx/conf.d/ (dropping the .template suffix).
# ${PORT}, ${APP1_HOST} and ${APP2_HOST} are filled in from environment variables.
COPY load-balancing/default.conf.template /etc/nginx/templates/default.conf.template

EXPOSE 10000