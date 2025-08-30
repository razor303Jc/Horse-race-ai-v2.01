module.exports = {
  // Node-RED settings for Horse Racing AI C2 Command Center

  // HTTP settings
  uiPort: process.env.PORT || 1880,
  uiHost: "0.0.0.0",

  // Security settings
  httpAdminRoot: "/admin",
  httpNodeRoot: "/api",

  // User directory
  userDir: "/data",

  // Flow file
  flowFile: "flows.json",

  // Enable projects
  editorTheme: {
    projects: {
      enabled: false,
    },
    page: {
      title: "Horse Racing AI - C2 Command Center",
      favicon: "/absolute/path/to/theme/icon",
    },
    header: {
      title: "🏇 Horse Racing AI C2",
      url: "https://github.com/razor303Jc/Horse-race-ai-v2.01",
    },
    menu: {
      "menu-item-keyboard-shortcuts": false,
      "menu-item-help": {
        label: "Help & Documentation",
        url: "http://localhost:8000/docs",
      },
    },
  },

  // Runtime settings
  runtimeState: {
    enabled: false,
    ui: false,
  },

  // Logging
  logging: {
    console: {
      level: "info",
      metrics: false,
      audit: false,
    },
  },

  // Function timeout
  functionGlobalContext: {
    // Database connections
    postgres: {
      host: process.env.POSTGRES_HOST || "172.20.0.10",
      port: process.env.POSTGRES_PORT || 5432,
      database: "cards_horse_racing_db",
      user: process.env.POSTGRES_USER || "horse_racing",
      password: process.env.POSTGRES_PASSWORD || "secure_password_123",
    },
    redis: {
      host: process.env.REDIS_HOST || "172.20.0.11",
      port: process.env.REDIS_PORT || 6379,
      password: process.env.REDIS_PASSWORD || "redis_password_123",
    },
    // API endpoints
    api: {
      webApp: "http://172.20.0.12:8000",
      pipeline: "http://172.20.0.13:8000",
      mlTrainer: "http://172.20.0.14:8000",
    },
  },

  // Export settings
  exportGlobalContextKeys: false,

  // Context storage
  contextStorage: {
    default: "memoryOnly",
    memoryOnly: { module: "memory" },
    file: { module: "localfilesystem" },
  },
};
