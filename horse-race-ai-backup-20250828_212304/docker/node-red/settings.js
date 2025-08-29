module.exports = {
  // Node-RED runtime settings
  uiPort: process.env.PORT || 1880,
  mqttReconnectTime: 15000,
  serialReconnectTime: 15000,
  debugMaxLength: 1000,
  debugUseColors: true,

  // Flow settings
  flowFile: "flows.json",
  flowFilePretty: true,
  userDir: "/data",
  nodesDir: "/data/nodes",

  // Security
  credentialSecret: process.env.NODE_RED_CREDENTIAL_SECRET || false,

  // Web interface settings
  httpAdminRoot: "/",
  httpNodeRoot: "/",
  ui: {
    path: "ui",
    middleware: function (req, res, next) {
      // Add any custom middleware here
      next();
    },
  },

  // Global context for Horse Racing AI
  functionGlobalContext: {
    horse_racing: {
      database_url:
        process.env.DATABASE_URL ||
        "postgresql://horse_racing:secure_password_123@localhost:5432/postgres",
      cards_database_url:
        process.env.CARDS_DATABASE_URL ||
        "postgresql://horse_racing:secure_password_123@localhost:5432/cards_horse_racing_db",
      results_database_url:
        process.env.RESULTS_DATABASE_URL ||
        "postgresql://horse_racing:secure_password_123@localhost:5432/results_horse_racing_db",
      advanced_database_url:
        process.env.ADVANCED_DATABASE_URL ||
        "postgresql://horse_racing:secure_password_123@localhost:5432/advanced_racing_metrics_db",
      workspace_path: "/workspace",
      data_path: "/workspace/data",
      tools_path: "/workspace/tools",
      logs_path: "/workspace/logs",
      smtp_host: "smtp.gmail.com",
      smtp_port: 465,
      smtp_user: process.env.SMTP_USER || "your-email@gmail.com",
      smtp_password: process.env.APP_PASSWORD || "awmf ulio rtjv qybx",
    },
  },

  // Context storage
  exportGlobalContextKeys: false,
  contextStorage: {
    default: "memoryOnly",
    memoryOnly: { module: "memory" },
    file: { module: "localfilesystem" },
  },

  // Logging
  logging: {
    console: {
      level: process.env.NODE_RED_LOG_LEVEL || "info",
      metrics: false,
      audit: false,
    },
    file: {
      level: "info",
      filename: "/data/node-red.log",
      maxFiles: 5,
      maxSize: "10MB",
    },
  },

  // Editor settings
  editorTheme: {
    projects: {
      enabled: false,
    },
    palette: {
      editable: true,
    },
    codeEditor: {
      lib: "monaco",
      options: {
        theme: "vs-dark",
      },
    },
  },

  // Function node settings
  functionExternalModules: true,
  functionGlobalContext: {
    // Add global modules here if needed
  },
};
