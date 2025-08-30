// Redis Health Check Function for Node-RED
// This will be added to the database-health-tab as a new endpoint

function createRedisHealthFlow() {
  return [
    {
      id: "http-redis-health",
      type: "http in",
      z: "database-health-tab",
      name: "Redis Health API",
      url: "/redis/health",
      method: "get",
      upload: false,
      swaggerDoc: "",
      x: 140,
      y: 160,
      wires: [["function-redis-health"]],
    },
    {
      id: "function-redis-health",
      type: "function",
      z: "database-health-tab",
      name: "Redis Health Check",
      func: `// Redis health check using net module for basic connectivity
const net = require('net');
const timestamp = new Date().toISOString();

// Redis connection details
const redisHost = 'horse_racing_redis_clean';
const redisPort = 6379;

// Create a simple TCP connection test to Redis
const startTime = Date.now();
const client = new net.Socket();

// Set timeout for connection
const connectionTimeout = setTimeout(() => {
    client.destroy();
    msg.payload = {
        timestamp: timestamp,
        overall_status: 'timeout',
        redis_info: {
            host: redisHost,
            port: redisPort,
            error: 'Connection timeout'
        },
        connection_test: 'failed',
        response_time: 'timeout'
    };
    msg.statusCode = 503;
    node.send(msg);
}, 2000);

client.connect(redisPort, redisHost, () => {
    clearTimeout(connectionTimeout);
    const responseTime = Date.now() - startTime;
    
    // Send Redis PING command
    client.write('PING\\r\\n');
    
    client.on('data', (data) => {
        client.destroy();
        
        const response = data.toString();
        const isPong = response.includes('PONG');
        
        const healthReport = {
            timestamp: timestamp,
            overall_status: isPong ? 'healthy' : 'degraded',
            redis_info: {
                host: redisHost,
                port: redisPort,
                ping_response: response.trim(),
                version: 'Redis 7.x'
            },
            connection_test: isPong ? 'successful' : 'ping_failed',
            response_time: responseTime + 'ms'
        };
        
        msg.payload = healthReport;
        msg.statusCode = isPong ? 200 : 503;
        node.send(msg);
    });
});

client.on('error', (error) => {
    clearTimeout(connectionTimeout);
    msg.payload = {
        timestamp: timestamp,
        overall_status: 'unhealthy',
        redis_info: {
            host: redisHost,
            port: redisPort,
            error: error.message
        },
        connection_test: 'failed',
        response_time: 'error'
    };
    msg.statusCode = 503;
    node.send(msg);
});

return null; // Async response handling`,
      outputs: 1,
      noerr: 0,
      initialize: "",
      finalize: "",
      libs: [],
      x: 380,
      y: 160,
      wires: [["debug-redis-health", "http-response-redis-health"]],
    },
    {
      id: "debug-redis-health",
      type: "debug",
      z: "database-health-tab",
      name: "Redis Health Debug",
      active: true,
      tosidebar: true,
      console: false,
      tostatus: false,
      complete: "payload",
      targetType: "msg",
      x: 600,
      y: 140,
      wires: [],
    },
    {
      id: "http-response-redis-health",
      type: "http response",
      z: "database-health-tab",
      name: "Redis Health Response",
      statusCode: "",
      headers: { "Content-Type": "application/json" },
      x: 620,
      y: 180,
      wires: [],
    },
    {
      id: "inject-test-redis-health",
      type: "inject",
      z: "database-health-tab",
      name: "Test Redis Health",
      topic: "",
      payload: "",
      payloadType: "date",
      repeat: "",
      crontab: "",
      once: false,
      onceDelay: 0.1,
      x: 140,
      y: 220,
      wires: [["function-redis-health"]],
    },
  ];
}

module.exports = { createRedisHealthFlow };
