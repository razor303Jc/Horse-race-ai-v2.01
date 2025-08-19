// Bundle optimization configuration for Webpack
const path = require("path");
const webpack = require("webpack");
const TerserPlugin = require("terser-webpack-plugin");
const CompressionPlugin = require("compression-webpack-plugin");
const BundleAnalyzerPlugin =
  require("webpack-bundle-analyzer").BundleAnalyzerPlugin;
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const OptimizeCSSAssetsPlugin = require("optimize-css-assets-webpack-plugin");

module.exports = {
  mode: "production",

  optimization: {
    minimize: true,
    minimizer: [
      new TerserPlugin({
        terserOptions: {
          compress: {
            drop_console: true,
            drop_debugger: true,
            pure_funcs: ["console.log", "console.info", "console.debug"],
          },
          mangle: {
            safari10: true,
          },
          output: {
            comments: false,
          },
        },
        extractComments: false,
      }),
      new OptimizeCSSAssetsPlugin({
        cssProcessorOptions: {
          safe: true,
          discardComments: {
            removeAll: true,
          },
        },
      }),
    ],

    // Split chunks for better caching
    splitChunks: {
      chunks: "all",
      cacheGroups: {
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: "vendors",
          priority: 10,
          chunks: "all",
        },
        common: {
          name: "common",
          minChunks: 2,
          priority: 5,
          reuseExistingChunk: true,
        },
        material: {
          test: /[\\/]node_modules[\\/]@mui[\\/]/,
          name: "material-ui",
          priority: 15,
          chunks: "all",
        },
        charts: {
          test: /[\\/]node_modules[\\/](recharts|chart\.js|d3)[\\/]/,
          name: "charts",
          priority: 12,
          chunks: "all",
        },
        utils: {
          test: /[\\/]src[\\/]utils[\\/]/,
          name: "utils",
          priority: 8,
          chunks: "all",
        },
      },
    },

    // Runtime chunk for better caching
    runtimeChunk: {
      name: "runtime",
    },

    // Module concatenation for better tree shaking
    concatenateModules: true,

    // Remove empty chunks
    removeEmptyChunks: true,

    // Merge duplicate chunks
    mergeDuplicateChunks: true,
  },

  resolve: {
    // Resolve extensions
    extensions: [".ts", ".tsx", ".js", ".jsx", ".json"],

    // Alias for shorter imports
    alias: {
      "@": path.resolve(__dirname, "src"),
      "@components": path.resolve(__dirname, "src/components"),
      "@utils": path.resolve(__dirname, "src/utils"),
      "@hooks": path.resolve(__dirname, "src/hooks"),
      "@services": path.resolve(__dirname, "src/services"),
      "@types": path.resolve(__dirname, "src/types"),
    },

    // Fallbacks for Node.js modules
    fallback: {
      crypto: require.resolve("crypto-browserify"),
      stream: require.resolve("stream-browserify"),
      buffer: require.resolve("buffer"),
    },
  },

  module: {
    rules: [
      {
        test: /\.(ts|tsx)$/,
        exclude: /node_modules/,
        use: [
          {
            loader: "babel-loader",
            options: {
              presets: [
                [
                  "@babel/preset-env",
                  {
                    targets: {
                      browsers: ["> 1%", "last 2 versions"],
                    },
                    modules: false,
                    useBuiltIns: "usage",
                    corejs: 3,
                  },
                ],
                "@babel/preset-react",
                "@babel/preset-typescript",
              ],
              plugins: [
                "@babel/plugin-proposal-class-properties",
                "@babel/plugin-syntax-dynamic-import",
                [
                  "import",
                  {
                    libraryName: "@mui/material",
                    libraryDirectory: "",
                    camel2DashComponentName: false,
                  },
                  "core",
                ],
                [
                  "import",
                  {
                    libraryName: "@mui/icons-material",
                    libraryDirectory: "",
                    camel2DashComponentName: false,
                  },
                  "icons",
                ],
              ],
            },
          },
        ],
      },
      {
        test: /\.css$/,
        use: [
          MiniCssExtractPlugin.loader,
          {
            loader: "css-loader",
            options: {
              importLoaders: 1,
              modules: {
                auto: true,
                localIdentName: "[name]__[local]--[hash:base64:5]",
              },
            },
          },
          "postcss-loader",
        ],
      },
      {
        test: /\.(png|jpe?g|gif|svg|webp)$/i,
        type: "asset",
        parser: {
          dataUrlCondition: {
            maxSize: 8 * 1024, // 8kb
          },
        },
        generator: {
          filename: "images/[name].[hash:8][ext]",
        },
      },
      {
        test: /\.(woff|woff2|eot|ttf|otf)$/i,
        type: "asset/resource",
        generator: {
          filename: "fonts/[name].[hash:8][ext]",
        },
      },
    ],
  },

  plugins: [
    // Extract CSS
    new MiniCssExtractPlugin({
      filename: "css/[name].[contenthash:8].css",
      chunkFilename: "css/[name].[contenthash:8].css",
    }),

    // Compression
    new CompressionPlugin({
      algorithm: "gzip",
      test: /\.(js|css|html|svg)$/,
      threshold: 8192,
      minRatio: 0.8,
    }),

    // Bundle analyzer (uncomment for analysis)
    // new BundleAnalyzerPlugin({
    //   analyzerMode: 'static',
    //   openAnalyzer: false,
    // }),

    // Define environment variables
    new webpack.DefinePlugin({
      "process.env.NODE_ENV": JSON.stringify("production"),
      "process.env.BUILD_DATE": JSON.stringify(new Date().toISOString()),
    }),

    // Provide polyfills
    new webpack.ProvidePlugin({
      Buffer: ["buffer", "Buffer"],
      process: "process/browser",
    }),

    // Ignore moment locales to reduce bundle size
    new webpack.IgnorePlugin({
      resourceRegExp: /^\.\/locale$/,
      contextRegExp: /moment$/,
    }),
  ],

  // Performance hints
  performance: {
    maxAssetSize: 512000, // 500kb
    maxEntrypointSize: 512000, // 500kb
    hints: "warning",
  },

  // Source maps for production debugging
  devtool: "source-map",

  // Output configuration
  output: {
    path: path.resolve(__dirname, "dist"),
    filename: "js/[name].[contenthash:8].js",
    chunkFilename: "js/[name].[contenthash:8].chunk.js",
    publicPath: "/",
    clean: true,
  },

  // Cache configuration
  cache: {
    type: "filesystem",
    cacheDirectory: path.resolve(__dirname, ".webpack-cache"),
    buildDependencies: {
      config: [__filename],
    },
  },

  // Experiments
  experiments: {
    topLevelAwait: true,
  },
};

// Development configuration overrides
const developmentConfig = {
  mode: "development",
  devtool: "eval-source-map",

  optimization: {
    minimize: false,
    splitChunks: {
      chunks: "all",
      cacheGroups: {
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: "vendors",
          chunks: "all",
        },
      },
    },
  },

  plugins: [
    new webpack.DefinePlugin({
      "process.env.NODE_ENV": JSON.stringify("development"),
    }),

    new webpack.ProvidePlugin({
      Buffer: ["buffer", "Buffer"],
      process: "process/browser",
    }),
  ],

  devServer: {
    historyApiFallback: true,
    compress: true,
    hot: true,
    open: true,
    port: 3000,
    client: {
      overlay: {
        errors: true,
        warnings: false,
      },
    },
  },

  performance: {
    hints: false,
  },
};

// PostCSS configuration
const postcssConfig = {
  plugins: [
    require("autoprefixer"),
    require("cssnano")({
      preset: [
        "default",
        {
          discardComments: {
            removeAll: true,
          },
          minifyFontValues: {
            removeQuotes: false,
          },
        },
      ],
    }),
  ],
};

// Babel configuration for tree shaking
const babelConfig = {
  presets: [
    [
      "@babel/preset-env",
      {
        modules: false,
        useBuiltIns: "usage",
        corejs: 3,
        targets: {
          browsers: ["> 1%", "last 2 versions"],
        },
      },
    ],
    "@babel/preset-react",
    "@babel/preset-typescript",
  ],
  plugins: [
    "@babel/plugin-proposal-class-properties",
    "@babel/plugin-syntax-dynamic-import",
    // Material-UI tree shaking
    [
      "babel-plugin-import",
      {
        libraryName: "@mui/material",
        libraryDirectory: "",
        camel2DashComponentName: false,
      },
      "core",
    ],
    [
      "babel-plugin-import",
      {
        libraryName: "@mui/icons-material",
        libraryDirectory: "",
        camel2DashComponentName: false,
      },
      "icons",
    ],
    // Lodash tree shaking
    ["babel-plugin-lodash"],
    // Remove console logs in production
    process.env.NODE_ENV === "production" && [
      "babel-plugin-transform-remove-console",
    ],
  ].filter(Boolean),
};

// Package.json scripts for optimization
const packageScripts = {
  build: "webpack --config webpack.config.js",
  "build:analyze": "webpack --config webpack.config.js --env analyze",
  "build:profile":
    "webpack --config webpack.config.js --profile --json > stats.json",
  dev: "webpack serve --config webpack.config.js --env development",
  optimize: "npm run build && npm run analyze-bundle",
  "analyze-bundle": "npx webpack-bundle-analyzer dist/static/js/*.js",
  lighthouse:
    "lighthouse http://localhost:3000 --output-path=./lighthouse-report.html",
  "size-limit": "size-limit",
  "preload-routes": "node scripts/preload-routes.js",
};

// Size limit configuration
const sizeLimitConfig = [
  {
    path: "dist/js/main.*.js",
    limit: "300 KB",
  },
  {
    path: "dist/js/vendors.*.js",
    limit: "500 KB",
  },
  {
    path: "dist/css/*.css",
    limit: "50 KB",
  },
];

module.exports =
  process.env.NODE_ENV === "development"
    ? { ...module.exports, ...developmentConfig }
    : module.exports;

module.exports.postcssConfig = postcssConfig;
module.exports.babelConfig = babelConfig;
module.exports.packageScripts = packageScripts;
module.exports.sizeLimitConfig = sizeLimitConfig;
