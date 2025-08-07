# 🏇 Horse Racing AI v2.0 Documentation

<div align="center">

![Horse Racing AI v2.0](https://img.shields.io/badge/Horse%20Racing%20AI-v2.0-blue?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEyIDJMMTMuMDkgOC4yNkwyMCA5TDEzLjA5IDE1Ljc0TDEyIDIyTDEwLjkxIDE1Ljc0TDQgOUwxMC45MSA4LjI2TDEyIDJaIiBmaWxsPSJ3aGl0ZSIvPgo8L3N2Zz4K)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![ML](https://img.shields.io/badge/Machine%20Learning-61.9%25%20Accuracy-FF6B6B?style=for-the-badge)

**Advanced AI-Powered Horse Racing Handicapping System**

_Combining machine learning, statistical analysis, and real-time data processing for superior racing predictions_

</div>

---

## � What is Horse Racing AI v2.0?

Horse Racing AI v2.0 is a **state-of-the-art handicapping system** that revolutionizes horse racing analysis through:

- **🧠 Advanced Machine Learning**: Multi-model ensemble with 61.9% win accuracy
- **📊 Real-time Analytics**: Live data processing and statistical modeling
- **🌐 Modern Web Interface**: Intuitive dashboard for analysis and insights
- **⚡ Automated Processing**: Browser automation with Playwright for data collection
- **🔔 Smart Notifications**: Real-time alerts via NTFY integration

## ⭐ Key Features & Performance

<div class="grid cards" markdown>

- :material-brain: **AI-Powered Predictions**

  ***

  Advanced machine learning models delivering **61.9% win accuracy** and **76.6% place accuracy** with ensemble methods and confidence scoring.

- :material-web: **Modern Web Dashboard**

  ***

  Responsive Flask-based interface with real-time analytics, race cards, betting insights, and performance tracking.

- :material-database: **Automated Data Collection**

  ***

  Browser automation with Playwright for real-time data scraping, validation, and processing from multiple sources.

- :material-chart-line: **Advanced Analytics**

  ***

  Statistical analysis with pandas, numpy, scikit-learn, and Monte Carlo simulation for comprehensive insights.

- :material-docker: **Production Ready**

  ***

  Complete Docker containerization with PostgreSQL, Redis, health checks, and microservices architecture.

- :material-bell: **Smart Notifications**

  ***

  Real-time alerts via NTFY integration for race results, betting opportunities, and system updates.

</div>

## � Documentation Navigation

<div class="grid cards" markdown>

- :material-rocket-launch: **Getting Started**

  ***

  Perfect for new users who want to get up and running quickly.

  [:octicons-arrow-right-24: Overview](getting-started/overview.md)

  [:octicons-arrow-right-24: Installation](getting-started/installation.md)

  [:octicons-arrow-right-24: Quick Start](getting-started/quickstart.md)

- :material-account: **User Guide**

  ***

  Comprehensive guides for using the system effectively.

  [:octicons-arrow-right-24: Web Interface](user-guide/web-interface.md)

  [:octicons-arrow-right-24: API Reference](user-guide/api-reference.md)

- :material-code-braces: **Developer Docs**

  ***

  Technical documentation for developers and contributors.

  [:octicons-arrow-right-24: Development Setup](development/setup.md)

  [:octicons-arrow-right-24: Testing Guide](development/testing.md)

- :material-file-document: **Project Info**

  ***

  Detailed project information and implementation status.

  [:octicons-arrow-right-24: Implementation Status](documentation/IMPLEMENTATION_COMPLETE.md)

  [:octicons-arrow-right-24: Development Journey](documentation/COMPLETE_DEVELOPMENT_JOURNEY.md)

</div>

## 🎯 Choose Your Path

!!! example "I'm New Here"

    **👋 Welcome!** Start with the basics and get familiar with the system.

    1. [:material-information: **Overview**](getting-started/overview.md) - Learn what Horse Racing AI v2.0 can do
    2. [:material-download: **Installation**](getting-started/installation.md) - Set up your environment
    3. [:material-play: **Quick Start**](getting-started/quickstart.md) - Try it out in 5 minutes

!!! tip "I Want to Use It"

    **🎯 Ready to analyze races?** Jump straight to the user guides.

    1. [:material-web: **Web Dashboard**](user-guide/web-interface.md) - Complete interface guide
    2. [:material-api: **API Reference**](user-guide/api-reference.md) - Programmatic access
    3. [:material-chart-line: **Best Practices**](user-guide/best-practices.md) - Pro tips and strategies

!!! warning "I Want to Develop"

    **💻 Building something?** Get the technical details you need.

    1. [:material-cog: **Setup Guide**](development/setup.md) - Development environment
    2. [:material-test-tube: **Testing**](development/testing.md) - Quality assurance
    3. [:material-docker: **Docker Dev**](development/docker-dev.md) - Container development

## 🔗 Service Access Points

When running the complete system locally:

| Service                 | URL                                     | Description                         |
| ----------------------- | --------------------------------------- | ----------------------------------- |
| 🏇 **Main Application** | [localhost:8000](http://localhost:8000) | Horse racing analysis dashboard     |
| 📚 **Documentation**    | [localhost:8001](http://localhost:8001) | This documentation site             |
| 🗄️ **Database Admin**   | [localhost:8083](http://localhost:8083) | PostgreSQL administration (pgAdmin) |
| 📢 **Notifications**    | [localhost:8081](http://localhost:8081) | NTFY notification server            |
| 🔍 **Redis Insights**   | [localhost:6380](http://localhost:6380) | Redis cache monitoring              |

## 🏆 System Achievements

### Performance Metrics

- **🎯 Prediction Accuracy**: 69.2% combined win/place accuracy
- **📊 Confidence Calibration**: 72.4% average confidence scores
- **⚡ Processing Speed**: Real-time analysis capability
- **📈 Data Scale**: 8,900+ training records with comprehensive validation

### Technical Excellence

- **💻 Code Quality**: 3,000+ lines with comprehensive error handling
- **🧪 Testing**: Extensive pytest suite with high coverage
- **🐳 Production Ready**: Docker deployment with health checks
- **📈 Scalable**: Efficient batch processing and microservices architecture

## 🚀 Quick Start Guide

!!! tip "Get Running in 5 Minutes"

    ```bash
    # 1. Clone the repository
    git clone https://github.com/Horse-race-handicaping-ai/Horse-race-ai-v2.0.git
    cd Horse-race-ai-v2.0

    # 2. Start all services with Docker
    docker-compose --profile docs up -d

    # 3. Access the applications
    open http://localhost:8000  # 🏇 Main Application
    open http://localhost:8001  # 📚 Documentation
    open http://localhost:8083  # 🗄️ Database Admin
    ```

=== "🏆 Performance Metrics"

    | Metric | Value | Description |
    |--------|-------|-------------|
    | **Win Accuracy** | 61.9% | Model accuracy for predicting race winners |
    | **Place Accuracy** | 76.6% | Model accuracy for top-3 finishes |
    | **Confidence Score** | 72.4% | Average prediction confidence |
    | **Training Data** | 8,900+ | Comprehensive race records |
    | **Processing Speed** | Real-time | Live analysis capability |

=== "🔧 Tech Stack"

    | Component | Technology | Purpose |
    |-----------|------------|---------|
    | **Backend** | Python 3.11+ | Core application logic |
    | **Web Framework** | Flask | REST API and web interface |
    | **ML Libraries** | scikit-learn, XGBoost | Machine learning models |
    | **Database** | PostgreSQL | Data persistence |
    | **Cache** | Redis | Session and data caching |
    | **Frontend** | HTML5/CSS3/JS | Modern responsive UI |
    | **Automation** | Playwright | Browser automation |
    | **Containers** | Docker | Deployment and scaling |

=== "🎯 Use Cases"

    **For Handicappers**

    - Analyze race cards with AI predictions
    - Track horse performance trends
    - Get confidence-scored betting insights
    - Monitor real-time race results

    **For Developers**

    - Extend ML models and algorithms
    - Integrate with external APIs
    - Customize data sources
    - Build additional features

    **For Researchers**

    - Study betting market efficiency
    - Analyze racing patterns
    - Test prediction algorithms
    - Export data for analysis

## 🔗 Access Points

When running locally:

- **🏇 Main Application**: http://localhost:8000 - Horse racing analysis dashboard
- **📚 Documentation**: http://localhost:8001 - This documentation site
- **🗄️ Database Admin**: http://localhost:8083 - PostgreSQL administration
- **📢 Notifications**: http://localhost:8081 - NTFY notification server

## 📞 Support & Community

!!! question "Need Help?"

    **� Found a Bug?** Report issues on our GitHub repository
    **� Have an Idea?** Suggest features and improvements
    **🤝 Want to Contribute?** Check the development documentation
    **❓ General Questions?** Join our community discussions

## � Recent Updates

!!! success "v2.0 Features"

    - ✅ **Enhanced ML Models** - Improved prediction accuracy to 61.9%
    - ✅ **Docker Deployment** - Complete containerization with health checks
    - ✅ **Web Dashboard** - Modern responsive interface with real-time updates
    - ✅ **Automated Testing** - Comprehensive pytest suite with 85%+ coverage
    - ✅ **Documentation** - Complete user and developer guides

---

<div align="center">

**🏇 Ready to revolutionize your horse racing analysis?**

[Get Started Now](getting-started/installation.md){ .md-button .md-button--primary }
[View on GitHub](https://github.com/Horse-race-handicaping-ai/Horse-race-ai-v2.0){ .md-button }

_Built with ❤️ for the racing community_

</div>
