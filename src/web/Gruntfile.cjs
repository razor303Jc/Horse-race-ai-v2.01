module.exports = function(grunt) {
  // Project configuration
  grunt.initConfig({
    pkg: grunt.file.readJSON('package.json'),

    // Watch for file changes
    watch: {
      // Watch TypeScript React files
      react: {
        files: ['src/**/*.{ts,tsx}', 'src/**/*.css', 'public/**/*'],
        tasks: ['shell:buildReact'],
        options: {
          livereload: true,
          spawn: false,
          interrupt: true
        }
      },
      
      // Watch Python API files  
      api: {
        files: ['../../src/web/api_server*.py', '../../*.py'],
        tasks: ['shell:restartAPI'],
        options: {
          spawn: false,
          interrupt: true
        }
      },

      // Watch database files
      database: {
        files: ['../../*.sql', '../../database/**/*.sql'],
        tasks: ['shell:checkDatabase'],
        options: {
          spawn: false
        }
      }
    },

    // Shell commands
    shell: {
      // Build React application
      buildReact: {
        command: 'npm run build',
        options: {
          stdout: true,
          stderr: true
        }
      },

      // Start development server
      startDev: {
        command: 'npm run dev',
        options: {
          stdout: true,
          stderr: true,
          async: true
        }
      },

      // Restart API server
      restartAPI: {
        command: [
          'echo "🔄 Restarting API server..."',
          'pkill -f "api_server" || true',
          'sleep 2',
          'cd ../.. && python src/web/api_server_enhanced.py &'
        ].join(' && '),
        options: {
          stdout: true,
          stderr: true,
          async: true
        }
      },

      // Check database connection
      checkDatabase: {
        command: 'cd ../.. && python -c "from src.web.api_server_enhanced import get_db_connection; print(\\"✅ Database connection OK\\" if get_db_connection() else \\"❌ Database connection failed\\")"',
        options: {
          stdout: true,
          stderr: true
        }
      },

      // Install dependencies
      install: {
        command: 'npm install',
        options: {
          stdout: true,
          stderr: true
        }
      },

      // Clean build artifacts
      clean: {
        command: 'rm -rf dist/ node_modules/.vite/ && echo "🧹 Cleaned build artifacts"',
        options: {
          stdout: true
        }
      },

      // Docker commands
      dockerBuild: {
        command: 'cd ../.. && docker-compose build horse-racing-ai',
        options: {
          stdout: true,
          stderr: true
        }
      },

      dockerUp: {
        command: 'cd ../.. && docker-compose up -d horse-racing-ai',
        options: {
          stdout: true,
          stderr: true
        }
      },

      dockerDown: {
        command: 'cd ../.. && docker-compose down',
        options: {
          stdout: true,
          stderr: true
        }
      },

      // Open browser
      openBrowser: {
        command: 'open http://localhost:5003 || xdg-open http://localhost:5003 || start http://localhost:5003',
        options: {
          stdout: true
        }
      }
    },

    // Run tasks concurrently
    concurrent: {
      // Development mode: run both React dev server and API server
      dev: {
        tasks: ['shell:startDev', 'shell:restartAPI'],
        options: {
          logConcurrentOutput: true,
          limit: 2
        }
      },

      // Watch mode: watch files and run browser sync
      watch: {
        tasks: ['watch:react', 'watch:api', 'watch:database'],
        options: {
          logConcurrentOutput: true,
          limit: 3
        }
      }
    }
  });

  // Load plugins
  grunt.loadNpmTasks('grunt-contrib-watch');
  grunt.loadNpmTasks('grunt-shell');
  grunt.loadNpmTasks('grunt-concurrent');

  // Register tasks
  grunt.registerTask('default', ['shell:checkDatabase', 'shell:install', 'shell:buildReact']);
  grunt.registerTask('dev', ['shell:checkDatabase', 'concurrent:dev', 'shell:openBrowser']);
  grunt.registerTask('build', ['shell:clean', 'shell:install', 'shell:buildReact']);
  grunt.registerTask('docker:build', ['build', 'shell:dockerBuild']);
  grunt.registerTask('docker:up', ['shell:dockerUp']);
  grunt.registerTask('docker:down', ['shell:dockerDown']);
  grunt.registerTask('start', ['dev']);
  grunt.registerTask('clean', ['shell:clean']);
  
  // Auto-reload task
  grunt.registerTask('auto', 'Start auto-reload development environment', function() {
    grunt.log.writeln('🚀 Starting auto-reload development environment...');
    grunt.log.writeln('📱 React dev server: http://localhost:5003');
    grunt.log.writeln('🔧 API server: http://localhost:8001');
    grunt.log.writeln('🔍 Watch mode activated - files will auto-reload');
    grunt.task.run(['shell:checkDatabase', 'concurrent:watch']);
  });

  // Custom task to check environment
  grunt.registerTask('env', 'Check development environment', function() {
    grunt.log.writeln('🔍 Checking development environment...');
    
    // Check Node.js version
    var nodeVersion = process.version;
    grunt.log.writeln('Node.js version: ' + nodeVersion);
    
    // Check if Docker is running
    grunt.log.writeln('Use `docker ps` to check Docker containers');
    grunt.log.writeln('Use `grunt docker:up` to start Docker services');
    
    grunt.log.writeln('✅ Environment check complete');
  });
};
