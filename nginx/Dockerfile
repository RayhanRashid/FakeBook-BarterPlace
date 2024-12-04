# Use the official Nginx image as a parent image
FROM nginx:latest

# Create necessary directories
RUN mkdir -p /etc/letsencrypt/live/cse312barterplace.com
RUN mkdir -p /etc/ssl/certs /etc/ssl/private

# Copy custom Nginx configuration file
COPY nginx.conf /etc/nginx/nginx.conf

# Copy SSL certificate files for production
COPY fullchain.pem /etc/letsencrypt/live/cse312barterplace.com/fullchain.pem
COPY privkey.pem /etc/letsencrypt/live/cse312barterplace.com/privkey.pem

# Copy self-signed SSL certificate files for development
COPY localhost.crt /etc/ssl/certs/localhost.crt
COPY localhost.key /etc/ssl/private/localhost.key