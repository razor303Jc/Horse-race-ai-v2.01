# Web Interface User Guide

## Overview

The Horse Racing AI v2.0 web interface provides a comprehensive, user-friendly dashboard for analyzing horse races, viewing predictions, and managing your handicapping workflow. This guide will walk you through all the features and functionality.

## Accessing the Interface

### Getting Started

1. **Start the System**: `docker-compose up -d` or `python main.py`
2. **Open Browser**: Navigate to http://localhost:8000
3. **Dashboard**: You'll see the main dashboard with recent activity

### Interface Layout

The web interface is organized into several main sections:

- **🏠 Dashboard**: Overview and recent activity
- **🏇 Race Analysis**: Core race analysis tools
- **📊 Performance**: Model performance and statistics
- **🔔 Notifications**: Alert settings and history
- **⚙️ Settings**: System configuration

## Dashboard

### Main Dashboard Features

**System Status Panel**

- **Service Health**: Shows status of all system components
- **Recent Predictions**: Latest race analyses
- **Performance Metrics**: Current model accuracy statistics
- **Quick Actions**: Fast access to common tasks

**Recent Activity**

- **Latest Races**: Recently analyzed races with results
- **Top Picks**: Highest confidence predictions
- **Performance Summary**: Win rate and accuracy trends

### Quick Start Actions

**Demo Mode**

- Click "**Try Demo**" to load sample race data
- Explore features without needing real race data
- Perfect for learning the interface

**Sample Data**

- "**Load Sample Race**" loads test race with multiple horses
- Shows all analysis features with realistic data
- Great for understanding the prediction output

## Race Analysis

### Loading Race Data

**Upload Race File**

1. Click "**Upload Race Data**"
2. Select JSON file with race information
3. System validates and processes the data
4. Results appear automatically

**Manual Entry**

1. Click "**Enter Race Manually**"
2. Fill in race details (distance, surface, class)
3. Add horses one by one with available data
4. Click "**Analyze Race**" when complete

**API Import**

1. Use "**Import from API**" for automated data
2. Connect to racing data services
3. Select race and import automatically

### Race Information Panel

**Race Details**

- **Distance**: Race distance in meters/furlongs
- **Surface**: Track surface (turf, dirt, synthetic)
- **Class**: Race class level (1-5, higher is better)
- **Conditions**: Track condition, weather
- **Prize Money**: Total purse and winner's share

**Field Information**

- **Number of Horses**: Field size
- **Favorites**: Market favorites and their odds
- **Value Opportunities**: Horses with model edge over odds

### Horse Analysis

Each horse in the race gets a comprehensive analysis:

**Basic Information**

- **Name**: Horse name and racing colors
- **Age**: Current age
- **Weight**: Assigned weight for the race
- **Jockey/Trainer**: Current connections

**Performance Scores**

- **Power Rating**: Overall strength (0-150 scale)
- **Form Score**: Recent performance quality (0-10)
- **Speed Rating**: Speed capabilities (0-100+)
- **Class Rating**: Competition level assessment

**Predictions**

- **Win Probability**: Chance of finishing first (%)
- **Place Probability**: Chance of finishing in top 3 (%)
- **Confidence**: Reliability of the prediction (%)
- **Value Assessment**: Comparison with market odds

**Detailed Analysis**

- **Key Factors**: Strengths supporting the prediction
- **Concerns**: Potential weaknesses or risks
- **Recent Form**: Last few race results with context
- **Specializations**: Distance, surface, class preferences

### Results Display

**Prediction Summary Table**

| Horse            | Win% | Place% | Confidence | Power Rating | Betting Value |
| ---------------- | ---- | ------ | ---------- | ------------ | ------------- |
| Thunder Bolt     | 34%  | 67%    | 81%        | 142          | Good Value    |
| Lightning Strike | 28%  | 61%    | 75%        | 138          | Fair Odds     |
| Storm Chaser     | 22%  | 55%    | 69%        | 134          | Overpriced    |

**Visual Indicators**

- **🟢 Green**: High confidence, good value
- **🟡 Yellow**: Moderate confidence, fair odds
- **🔴 Red**: Low confidence, poor value
- **⭐ Star**: Top pick recommendation

**Sorting and Filtering**

- Sort by any column (probability, confidence, rating)
- Filter by confidence level or value assessment
- Search for specific horses

## Advanced Features

### Monte Carlo Simulation

**Simulation Results**

- **10,000+ Simulations**: Statistical race modeling
- **Probability Ranges**: Confidence intervals for predictions
- **Race Scenarios**: Different possible outcomes
- **Risk Assessment**: Variance and uncertainty measures

**Viewing Simulation Data**

1. Click "**Show Simulation Details**"
2. View probability distributions
3. See confidence intervals
4. Understand prediction uncertainty

### Machine Learning Insights

**Model Information**

- **Active Models**: Which ML models are being used
- **Ensemble Weighting**: How models are combined
- **Feature Importance**: Which factors matter most
- **Prediction Confidence**: Model agreement levels

**Model Performance**

- **Accuracy Metrics**: Current win/place accuracy
- **Recent Performance**: Trend in model accuracy
- **Calibration**: How well probabilities match outcomes
- **Comparative Analysis**: Performance vs simple models

### Betting Integration

**Value Assessment**

- **Model vs Market**: Compare AI odds to bookmaker odds
- **Value Indicators**: Identify overpriced horses
- **Kelly Criterion**: Optimal bet sizing recommendations
- **Risk Management**: Maximum bet guidelines

**Betting Strategies**

- **Win Betting**: Straight win recommendations
- **Place Betting**: Place bet value opportunities
- **Each-Way**: Each-way value analysis
- **Exotic Bets**: Exacta, trifecta possibilities

## Performance Tracking

### Model Performance Dashboard

**Accuracy Metrics**

- **Win Prediction Accuracy**: Percentage of correct win predictions
- **Place Prediction Accuracy**: Percentage of correct place predictions
- **Calibration Score**: How well probabilities match reality
- **ROI Tracking**: Return on investment for recommendations

**Historical Performance**

- **Time Series**: Performance over time
- **Race Type Analysis**: Performance by distance, surface, class
- **Confidence Bands**: Performance by confidence level
- **Comparative Metrics**: vs random, vs favorites, vs expert picks

### Personal Statistics

**Your Performance**

- **Races Analyzed**: Total races you've analyzed
- **Predictions Made**: Number of predictions
- **Success Rate**: Your personal success rate
- **Favorite Picks**: Most successful prediction types

**Usage Statistics**

- **Sessions**: Number of analysis sessions
- **Average Session Time**: Time spent per session
- **Most Used Features**: Which tools you use most
- **Learning Progress**: Improvement over time

## Notifications

### Alert Types

**Race Alerts**

- **High Value Bets**: When model finds significant value
- **Confidence Thresholds**: Alerts for high-confidence picks
- **Class Changes**: When horses move up/down in class
- **Equipment Changes**: Notable equipment modifications

**System Alerts**

- **Model Updates**: When models are retrained
- **Performance Changes**: Significant accuracy changes
- **Data Updates**: New race data available
- **System Maintenance**: Scheduled maintenance notifications

### Notification Settings

**NTFY Integration**

1. **Install NTFY App**: Download on your phone
2. **Choose Topic**: Pick unique topic name
3. **Update Settings**: Enter topic in system settings
4. **Test Alerts**: Send test notification
5. **Customize**: Choose which alerts to receive

**Alert Preferences**

- **Frequency**: How often to receive alerts
- **Confidence Threshold**: Minimum confidence for alerts
- **Value Threshold**: Minimum value for betting alerts
- **Race Types**: Which types of races to monitor

## Settings and Configuration

### User Preferences

**Display Settings**

- **Theme**: Light or dark mode
- **Units**: Distance units (meters/furlongs)
- **Currency**: Display currency for betting
- **Time Zone**: Local time zone for race times

**Analysis Settings**

- **Default Model**: Which ML model to use by default
- **Confidence Threshold**: Minimum confidence to display
- **Value Threshold**: Minimum value to highlight
- **Simulation Count**: Number of Monte Carlo simulations

### System Configuration

**Model Settings**

- **Active Models**: Enable/disable specific models
- **Ensemble Weights**: Adjust model weightings
- **Retraining Schedule**: When to retrain models
- **Feature Selection**: Which features to include

**Data Sources**

- **Primary Sources**: Main race data feeds
- **Backup Sources**: Fallback data sources
- **Update Frequency**: How often to refresh data
- **Quality Filters**: Data quality requirements

## Mobile Interface

### Responsive Design

The web interface is fully responsive and works well on mobile devices:

**Mobile Features**

- **Touch-Friendly**: Large buttons and touch targets
- **Swipe Navigation**: Swipe between sections
- **Optimized Layout**: Content adapts to screen size
- **Fast Loading**: Optimized for mobile networks

**Mobile-Specific Functions**

- **Quick Picks**: Rapid access to top recommendations
- **Simplified View**: Streamlined interface for small screens
- **Offline Mode**: Basic functionality without internet
- **Push Notifications**: Mobile alerts through NTFY

## Troubleshooting

### Common Issues

**Page Won't Load**

- Check if services are running: `docker-compose ps`
- Verify correct URL: http://localhost:8000
- Clear browser cache and cookies
- Try a different browser

**Predictions Not Showing**

- Ensure race data is properly formatted
- Check that all required fields are present
- Verify model is loaded and trained
- Check browser console for errors

**Slow Performance**

- Reduce number of simulations in settings
- Clear browser cache
- Close other browser tabs
- Check system resources

**Notification Issues**

- Verify NTFY topic is set correctly
- Test NTFY connection in settings
- Check phone NTFY app subscription
- Ensure internet connection is stable

### Getting Help

**Built-in Help**

- **Tooltips**: Hover over any element for help
- **Help Buttons**: Click "?" icons for explanations
- **Tutorial Mode**: Guided tour of features
- **FAQ Section**: Common questions and answers

**External Resources**

- **Documentation**: Full documentation at http://localhost:8001
- **Video Tutorials**: Walkthrough videos (coming soon)
- **Community**: User forums and discussions
- **Support**: Technical support channels

## Best Practices

### Effective Analysis Workflow

1. **Load Race Data**: Start with complete, accurate data
2. **Review Context**: Understand race conditions and field
3. **Examine Predictions**: Look at top picks and confidence levels
4. **Check Value**: Compare model odds to market odds
5. **Consider Factors**: Review key factors and concerns
6. **Make Decisions**: Use information to inform betting choices
7. **Track Results**: Monitor performance and learn

### Maximizing Accuracy

- **Use High Confidence Picks**: Focus on predictions with 70%+ confidence
- **Consider Value**: Don't just pick favorites, look for value
- **Understand Context**: Consider track conditions, distances, class levels
- **Multiple Models**: Use ensemble predictions for best accuracy
- **Regular Updates**: Keep data current and models trained

### Risk Management

- **Start Small**: Begin with small stakes while learning
- **Diversify**: Don't put all money on one pick
- **Set Limits**: Establish maximum bet amounts
- **Track Performance**: Monitor your success rate and ROI
- **Stay Disciplined**: Stick to your strategy and limits

The web interface provides powerful tools for horse racing analysis. Take time to explore all features and find the workflow that works best for your needs!
