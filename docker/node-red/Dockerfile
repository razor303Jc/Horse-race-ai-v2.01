# Custom Node-RED Docker Image for Horse Racing AI
FROM nodered/node-red:latest

USER root

# Install additional system dependencies if needed
RUN apk add --no-cache \
    python3 \
    py3-pip \
    curl \
    git

# Install required Node-RED nodes globally
RUN npm install -g \
    node-red-dashboard \
    node-red-contrib-cron-plus \
    node-red-node-email \
    node-red-contrib-postgresql \
    node-red-contrib-fs-ops \
    node-red-contrib-moment \
    node-red-contrib-ui-led \
    @flowfuse/node-red-dashboard

# Copy custom settings
COPY --chown=node-red:node-red settings.js /usr/src/node-red/custom-settings.js
COPY --chown=node-red:node-red package.json /usr/src/node-red/package.json

# Switch back to node-red user
USER node-red

# Use default entrypoint
ENTRYPOINT ["./entrypoint.sh"]
