// Simplified Node-RED Function for C2 Status with Real Database Health
// This replaces hardcoded database status with real health endpoint call

const http = require("http");
const timestamp = new Date().toISOString();

// Initialize status with current hardcoded values (keeping them for now except database)
const status = {
  database: "checking...",
  redis: "healthy",
  pipeline: "healthy",
  ml_trainer: "healthy",
  web_app: "healthy",
  pipeline_progress: Math.floor(Math.random() * 100),
  pipeline_stage: "Processing Data",
  timestamp: timestamp,
  metrics: {
    selections: Math.floor(Math.random() * 20),
    success_rate: Math.floor(Math.random() * 100),
    roi: (Math.random() * 50 - 10).toFixed(1),
    profit_loss: (Math.random() * 1000 - 200).toFixed(2),
    models_trained: Math.floor(Math.random() * 10),
  },
  ai: {
    active_models: 3,
    last_prediction: "Horse #7 - Win",
    confidence: Math.floor(Math.random() * 40 + 60),
    accuracy: Math.floor(Math.random() * 20 + 75),
  },
};

// Make HTTP request to database health endpoint
const req = http.get("http://localhost:1880/database/health", (res) => {
  let data = "";

  res.on("data", (chunk) => {
    data += chunk;
  });

  res.on("end", () => {
    try {
      const healthData = JSON.parse(data);
      status.database = healthData.overall_status || "unknown";
      console.log("Database health check successful:", status.database);
    } catch (error) {
      console.error("Failed to parse health response:", error);
      status.database = "unhealthy";
    }

    // Send the response with real database status
    msg.payload = status;
    node.send(msg);
  });
});

req.on("error", (error) => {
  console.error("Database health check failed:", error.message);
  status.database = "unhealthy";
  status.pipeline_stage = "Database Health Check Failed";

  // Send response even if health check fails
  msg.payload = status;
  node.send(msg);
});

// Set timeout for health check
req.setTimeout(2000, () => {
  req.abort();
  console.error("Database health check timed out");
  status.database = "timeout";

  msg.payload = status;
  node.send(msg);
});

// Return null because we're handling the response asynchronously
return null;
