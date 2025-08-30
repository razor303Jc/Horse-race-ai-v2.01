// Pipeline Health Check Function for Node-RED
// Tests the health of the horse_racing_data_pipeline_clean container

const timestamp = new Date().toISOString();

// Pipeline health check function
async function checkPipelineHealth() {
  try {
    // Method 1: Check if container is running via Docker API simulation
    // In a real implementation, this could use Docker API or container inspection

    // Method 2: Check if pipeline endpoints are responding
    // Test the pipeline's internal health endpoint if available

    // Method 3: Check container logs for recent activity
    // Look for recent successful operations

    // For now, we'll simulate a container health check
    // This can be enhanced to actually check the Docker container status

    const containerName = "horse_racing_data_pipeline_clean";

    // Simulate container health check
    // In production, this would exec: docker inspect horse_racing_data_pipeline_clean
    const healthStatus = await simulateContainerHealthCheck(containerName);

    return {
      timestamp: timestamp,
      container: containerName,
      status: healthStatus.running ? "healthy" : "unhealthy",
      container_state: healthStatus.state,
      last_started: healthStatus.started_at,
      uptime: healthStatus.uptime,
      response_time_ms: healthStatus.response_time,
    };
  } catch (error) {
    return {
      timestamp: timestamp,
      container: "horse_racing_data_pipeline_clean",
      status: "unhealthy",
      error: error.message,
      response_time_ms: "error",
    };
  }
}

// Simulate container health check
// This would be replaced with actual Docker API calls in production
async function simulateContainerHealthCheck(containerName) {
  const startTime = Date.now();

  try {
    // Simulate checking container status
    // In production: docker inspect <container_name> --format '{{.State.Health.Status}}'

    // For demonstration, we'll randomly simulate healthy/unhealthy states
    // In real implementation, this would check actual container state
    const isRunning = Math.random() > 0.3; // 70% chance of healthy
    const responseTime = Date.now() - startTime;

    return {
      running: isRunning,
      state: isRunning ? "running" : "exited",
      started_at: new Date(Date.now() - Math.random() * 3600000).toISOString(),
      uptime: Math.floor(Math.random() * 7200) + "seconds",
      response_time: responseTime,
    };
  } catch (error) {
    throw new Error(`Container health check failed: ${error.message}`);
  }
}

// Node-RED function implementation
const pipelineHealthResult = await checkPipelineHealth();

msg.payload = pipelineHealthResult;
msg.statusCode = pipelineHealthResult.status === "healthy" ? 200 : 503;

return msg;
