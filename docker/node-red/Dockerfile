# Fresh Node-RED C2 Command Center Docker Image
FROM nodered/node-red:latest

USER root

# Install system dependencies
RUN apk add --no-cache \
    python3 \
    py3-pip \
    curl \
    git \
    docker-cli \
    bash

# Setup Docker group for container management
ARG DOCKER_GID=999
RUN addgroup -g ${DOCKER_GID} docker 2>/dev/null || true
RUN adduser node-red docker 2>/dev/null || true

# Switch to node-red user
USER node-red

# Copy package.json to data directory (following Node-RED best practices)
COPY --chown=node-red:node-red package.json /data/package.json

# Copy Node-RED configuration files
COPY --chown=node-red:node-red settings.js /data/settings.js
COPY --chown=node-red:node-red flows.json /data/flows.json

# Set working directory to data (where Node-RED expects user files)
WORKDIR /data

# Install additional packages using npm (packages will be installed to /data/node_modules)
RUN npm install

# Return to default working directory
WORKDIR /usr/src/node-red

# Use standard Node-RED startup
CMD ["npm", "start", "--cache", "/data/.npm", "--", "--userDir", "/data"]
