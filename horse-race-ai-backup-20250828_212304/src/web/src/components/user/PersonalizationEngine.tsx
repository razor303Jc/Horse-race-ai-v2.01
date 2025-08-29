import React, { useState, useEffect, useCallback, useMemo } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Grid,
  Box,
  Tabs,
  Tab,
  Button,
  Switch,
  FormControlLabel,
  Slider,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  Alert,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction,
  IconButton,
  Paper,
  Avatar,
  Rating,
  Divider,
  LinearProgress,
  Tooltip,
  Badge
} from '@mui/material';
import {
  Psychology,
  Favorite,
  TrendingUp,
  Star,
  Schedule,
  LocationOn,
  MonetizationOn,
  Assessment,
  Notifications,
  Settings,
  AutoAwesome,
  Tune,
  Refresh,
  Save,
  RestoreFromTrash,
  Timeline,
  ShowChart,
  BarChart,
  Speed,
  Edit,
  Delete,
  Add
} from '@mui/icons-material';

interface UserPreference {
  id: string;
  category: string;
  name: string;
  description: string;
  value: any;
  type: 'boolean' | 'slider' | 'select' | 'multi-select';
  options?: string[];
  min?: number;
  max?: number;
  step?: number;
  impact: 'high' | 'medium' | 'low';
}

interface PersonalizedRecommendation {
  id: string;
  type: 'race' | 'horse' | 'strategy' | 'market';
  title: string;
  description: string;
  confidence: number;
  value_rating: number;
  reason: string;
  data: any;
  priority: 'high' | 'medium' | 'low';
  expires_at: string;
}

interface BehaviorPattern {
  pattern_type: string;
  description: string;
  frequency: number;
  success_rate: number;
  recommendation: string;
  action_suggestions: string[];
}

interface AIInsight {
  id: string;
  title: string;
  insight: string;
  confidence: number;
  category: 'performance' | 'strategy' | 'market' | 'risk';
  actionable: boolean;
  potential_impact: number;
}

export const PersonalizationEngine: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [aiEnabled, setAiEnabled] = useState(true);
  const [learningMode, setLearningMode] = useState('active');
  const [saving, setSaving] = useState(false);

  // User preferences state
  const [preferences, setPreferences] = useState<UserPreference[]>([
    {
      id: 'pref_1',
      category: 'Betting',
      name: 'Risk Tolerance',
      description: 'How much risk you\'re comfortable with in your betting strategy',
      value: 7,
      type: 'slider',
      min: 1,
      max: 10,
      step: 1,
      impact: 'high'
    },
    {
      id: 'pref_2',
      category: 'Betting',
      name: 'Preferred Bet Types',
      description: 'Types of bets you prefer to place',
      value: ['win', 'place', 'each_way'],
      type: 'multi-select',
      options: ['win', 'place', 'each_way', 'lay', 'accumulator', 'trixie', 'yankee'],
      impact: 'high'
    },
    {
      id: 'pref_3',
      category: 'Racing',
      name: 'Favorite Courses',
      description: 'Racing courses you prefer to bet on',
      value: ['newmarket', 'ascot', 'cheltenham'],
      type: 'multi-select',
      options: ['newmarket', 'ascot', 'cheltenham', 'york', 'doncaster', 'epsom', 'goodwood'],
      impact: 'medium'
    },
    {
      id: 'pref_4',
      category: 'Racing',
      name: 'Distance Preference',
      description: 'Preferred race distances for betting',
      value: 'medium',
      type: 'select',
      options: ['sprint', 'medium', 'staying', 'all'],
      impact: 'medium'
    },
    {
      id: 'pref_5',
      category: 'Strategy',
      name: 'Auto-Betting',
      description: 'Allow AI to place bets automatically based on your criteria',
      value: false,
      type: 'boolean',
      impact: 'high'
    },
    {
      id: 'pref_6',
      category: 'Strategy',
      name: 'Value Betting Focus',
      description: 'How much to prioritize value bets over favorites',
      value: 8,
      type: 'slider',
      min: 1,
      max: 10,
      step: 1,
      impact: 'high'
    },
    {
      id: 'pref_7',
      category: 'Notifications',
      name: 'Opportunity Alerts',
      description: 'Get notified about high-value betting opportunities',
      value: true,
      type: 'boolean',
      impact: 'medium'
    },
    {
      id: 'pref_8',
      category: 'Interface',
      name: 'Dashboard Complexity',
      description: 'Level of detail shown in your dashboard',
      value: 'advanced',
      type: 'select',
      options: ['simple', 'standard', 'advanced', 'expert'],
      impact: 'low'
    }
  ]);

  // Mock personalized recommendations
  const [recommendations] = useState<PersonalizedRecommendation[]>([
    {
      id: 'rec_1',
      type: 'race',
      title: 'High-Value Race at Newmarket',
      description: 'Race 4 at 15:30 shows strong value opportunities based on your preferences',
      confidence: 0.87,
      value_rating: 9.2,
      reason: 'Matches your preference for medium-distance races at Newmarket with high value potential',
      data: { race_id: 'NM_001', race_time: '15:30', course: 'Newmarket' },
      priority: 'high',
      expires_at: '2024-01-15T15:30:00Z'
    },
    {
      id: 'rec_2',
      type: 'horse',
      title: 'Thunder Bay - Each Way Value',
      description: 'Strong each-way value in upcoming race based on your betting patterns',
      confidence: 0.74,
      value_rating: 8.1,
      reason: 'You have 73% success rate with similar odds range and each-way bets',
      data: { horse_name: 'Thunder Bay', odds: 4.5, bet_type: 'each_way' },
      priority: 'medium',
      expires_at: '2024-01-15T16:00:00Z'
    },
    {
      id: 'rec_3',
      type: 'strategy',
      title: 'Adjust Risk Level',
      description: 'Consider reducing stake sizes for today based on recent performance',
      confidence: 0.91,
      value_rating: 7.8,
      reason: 'Your recent losing streak suggests a more conservative approach',
      data: { suggested_stake_reduction: 0.3, period: '3 days' },
      priority: 'high',
      expires_at: '2024-01-16T00:00:00Z'
    }
  ]);

  // Mock behavior patterns
  const [behaviorPatterns] = useState<BehaviorPattern[]>([
    {
      pattern_type: 'Weekend Heavy Betting',
      description: 'You tend to bet 2.5x more on weekends',
      frequency: 0.85,
      success_rate: 0.42,
      recommendation: 'Consider maintaining weekday discipline on weekends',
      action_suggestions: [
        'Set weekend-specific betting limits',
        'Use smaller stakes for weekend bets',
        'Focus on quality over quantity'
      ]
    },
    {
      pattern_type: 'Favorite Bias',
      description: 'You bet on favorites 68% of the time',
      frequency: 0.68,
      success_rate: 0.51,
      recommendation: 'Explore more value in outsiders',
      action_suggestions: [
        'Allocate 30% of bankroll to longshots',
        'Use each-way betting for higher odds',
        'Research form more thoroughly for outsiders'
      ]
    },
    {
      pattern_type: 'Course Specialization',
      description: 'You perform 23% better at Newmarket and Ascot',
      frequency: 0.45,
      success_rate: 0.71,
      recommendation: 'Continue focusing on these courses',
      action_suggestions: [
        'Increase stake sizes at preferred courses',
        'Study track conditions more carefully',
        'Build expertise in course-specific factors'
      ]
    }
  ]);

  // Mock AI insights
  const [aiInsights] = useState<AIInsight[]>([
    {
      id: 'insight_1',
      title: 'Optimal Staking Strategy',
      insight: 'Your kelly criterion adherence could improve by 15% with automated staking',
      confidence: 0.89,
      category: 'strategy',
      actionable: true,
      potential_impact: 8.5
    },
    {
      id: 'insight_2',
      title: 'Market Timing Opportunity',
      insight: 'You consistently get better odds when betting 2-3 hours before race time',
      confidence: 0.76,
      category: 'market',
      actionable: true,
      potential_impact: 6.2
    },
    {
      id: 'insight_3',
      title: 'Risk Management Alert',
      insight: 'Your current drawdown period suggests reducing position sizes by 25%',
      confidence: 0.94,
      category: 'risk',
      actionable: true,
      potential_impact: 9.1
    }
  ]);

  const updatePreference = useCallback((prefId: string, newValue: any) => {
    setPreferences(prev => prev.map(pref => 
      pref.id === prefId ? { ...pref, value: newValue } : pref
    ));
  }, []);

  const savePreferences = useCallback(async () => {
    setSaving(true);
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1500));
    setSaving(false);
    // Show success notification
  }, [preferences]);

  const resetPreferences = useCallback(() => {
    // Reset to default values
    console.log('Resetting preferences to defaults');
  }, []);

  const getImpactColor = (impact: string): 'success' | 'warning' | 'error' => {
    switch (impact) {
      case 'high': return 'error';
      case 'medium': return 'warning';
      case 'low': return 'success';
      default: return 'warning';
    }
  };

  const getPriorityColor = (priority: string): 'error' | 'warning' | 'info' => {
    switch (priority) {
      case 'high': return 'error';
      case 'medium': return 'warning';
      case 'low': return 'info';
      default: return 'info';
    }
  };

  const renderPreferenceControl = (pref: UserPreference) => {
    switch (pref.type) {
      case 'boolean':
        return (
          <Switch
            checked={pref.value}
            onChange={(e) => updatePreference(pref.id, e.target.checked)}
          />
        );
      
      case 'slider':
        return (
          <Box sx={{ px: 2 }}>
            <Slider
              value={pref.value}
              onChange={(_, value) => updatePreference(pref.id, value)}
              min={pref.min}
              max={pref.max}
              step={pref.step}
              marks
              valueLabelDisplay="auto"
            />
          </Box>
        );
      
      case 'select':
        return (
          <Select
            value={pref.value}
            onChange={(e) => updatePreference(pref.id, e.target.value)}
            size="small"
            sx={{ minWidth: 120 }}
          >
            {pref.options?.map(option => (
              <MenuItem key={option} value={option}>
                {option.charAt(0).toUpperCase() + option.slice(1)}
              </MenuItem>
            ))}
          </Select>
        );
      
      case 'multi-select':
        return (
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
            {pref.options?.map(option => (
              <Chip
                key={option}
                label={option.charAt(0).toUpperCase() + option.slice(1)}
                clickable
                color={pref.value.includes(option) ? 'primary' : 'default'}
                onClick={() => {
                  const newValue = pref.value.includes(option)
                    ? pref.value.filter((v: string) => v !== option)
                    : [...pref.value, option];
                  updatePreference(pref.id, newValue);
                }}
              />
            ))}
          </Box>
        );
      
      default:
        return null;
    }
  };

  const categorizedPreferences = useMemo(() => {
    return preferences.reduce((acc, pref) => {
      if (!acc[pref.category]) {
        acc[pref.category] = [];
      }
      acc[pref.category].push(pref);
      return acc;
    }, {} as Record<string, UserPreference[]>);
  }, [preferences]);

  return (
    <Box sx={{ width: '100%' }}>
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h4" component="h1">
              🧠 AI Personalization Engine
            </Typography>
            <Box display="flex" gap={2} alignItems="center">
              <FormControlLabel
                control={
                  <Switch
                    checked={aiEnabled}
                    onChange={(e) => setAiEnabled(e.target.checked)}
                    color="primary"
                  />
                }
                label="AI Learning"
              />
              <Button
                startIcon={<Save />}
                onClick={savePreferences}
                variant="contained"
                disabled={saving}
              >
                {saving ? 'Saving...' : 'Save Preferences'}
              </Button>
            </Box>
          </Box>

          <Alert severity="info" sx={{ mb: 2 }}>
            <Typography variant="subtitle1">
              🎯 Intelligent Personalization Active
            </Typography>
            <Typography variant="body2">
              Your AI learns from your betting patterns and preferences to provide personalized 
              recommendations, insights, and optimizations. All data is processed securely and privately.
            </Typography>
          </Alert>
        </CardContent>
      </Card>

      <Tabs 
        value={activeTab} 
        onChange={(_, newValue) => setActiveTab(newValue)} 
        sx={{ mb: 3 }}
        variant="scrollable"
        scrollButtons="auto"
      >
        <Tab label="🎯 Recommendations" />
        <Tab label="⚙️ Preferences" />
        <Tab label="📊 Behavior Analysis" />
        <Tab label="🤖 AI Insights" />
      </Tabs>

      {/* Recommendations Tab */}
      {activeTab === 0 && (
        <Grid container spacing={3}>
          {recommendations.map((rec) => (
            <Grid item xs={12} md={6} lg={4} key={rec.id}>
              <Card sx={{ height: '100%' }}>
                <CardContent>
                  <Box display="flex" justifyContent="between" alignItems="center" mb={2}>
                    <Typography variant="h6" gutterBottom>
                      {rec.title}
                    </Typography>
                    <Chip
                      label={rec.priority}
                      color={getPriorityColor(rec.priority)}
                      size="small"
                    />
                  </Box>
                  
                  <Typography variant="body2" color="text.secondary" paragraph>
                    {rec.description}
                  </Typography>
                  
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" gutterBottom>
                      Confidence: {(rec.confidence * 100).toFixed(1)}%
                    </Typography>
                    <LinearProgress
                      variant="determinate"
                      value={rec.confidence * 100}
                      color={rec.confidence > 0.8 ? 'success' : rec.confidence > 0.6 ? 'warning' : 'error'}
                      sx={{ height: 8, borderRadius: 4 }}
                    />
                  </Box>
                  
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" gutterBottom>
                      Value Rating:
                    </Typography>
                    <Rating
                      value={rec.value_rating / 2}
                      max={5}
                      precision={0.1}
                      readOnly
                      size="small"
                    />
                  </Box>
                  
                  <Typography variant="body2" sx={{ fontStyle: 'italic', mb: 2 }}>
                    "{rec.reason}"
                  </Typography>
                  
                  <Button fullWidth variant="outlined" size="small">
                    Act on Recommendation
                  </Button>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Preferences Tab */}
      {activeTab === 1 && (
        <Box>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
            <Typography variant="h6">
              Personalization Preferences
            </Typography>
            <Button
              startIcon={<RestoreFromTrash />}
              onClick={resetPreferences}
              variant="outlined"
              size="small"
            >
              Reset to Defaults
            </Button>
          </Box>

          {Object.entries(categorizedPreferences).map(([category, prefs]) => (
            <Card key={category} sx={{ mb: 3 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  {category} Preferences
                </Typography>
                
                <List>
                  {prefs.map((pref, index) => (
                    <Box key={pref.id}>
                      <ListItem>
                        <ListItemIcon>
                          <Chip
                            label={pref.impact}
                            color={getImpactColor(pref.impact)}
                            size="small"
                          />
                        </ListItemIcon>
                        <ListItemText
                          primary={pref.name}
                          secondary={pref.description}
                          sx={{ flexGrow: 1, mr: 2 }}
                        />
                        <ListItemSecondaryAction>
                          {renderPreferenceControl(pref)}
                        </ListItemSecondaryAction>
                      </ListItem>
                      {index < prefs.length - 1 && <Divider />}
                    </Box>
                  ))}
                </List>
              </CardContent>
            </Card>
          ))}
        </Box>
      )}

      {/* Behavior Analysis Tab */}
      {activeTab === 2 && (
        <Grid container spacing={3}>
          {behaviorPatterns.map((pattern, index) => (
            <Grid item xs={12} md={6} key={index}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    {pattern.pattern_type}
                  </Typography>
                  
                  <Typography variant="body2" color="text.secondary" paragraph>
                    {pattern.description}
                  </Typography>
                  
                  <Grid container spacing={2} sx={{ mb: 2 }}>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">
                        Frequency
                      </Typography>
                      <Typography variant="h6">
                        {(pattern.frequency * 100).toFixed(1)}%
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">
                        Success Rate
                      </Typography>
                      <Typography 
                        variant="h6"
                        color={pattern.success_rate > 0.5 ? 'success.main' : 'error.main'}
                      >
                        {(pattern.success_rate * 100).toFixed(1)}%
                      </Typography>
                    </Grid>
                  </Grid>
                  
                  <Alert 
                    severity={pattern.success_rate > 0.5 ? 'success' : 'warning'} 
                    sx={{ mb: 2 }}
                  >
                    <Typography variant="subtitle2">
                      Recommendation
                    </Typography>
                    <Typography variant="body2">
                      {pattern.recommendation}
                    </Typography>
                  </Alert>
                  
                  <Typography variant="subtitle2" gutterBottom>
                    Action Suggestions:
                  </Typography>
                  <List dense>
                    {pattern.action_suggestions.map((suggestion, i) => (
                      <ListItem key={i} disablePadding>
                        <ListItemIcon>
                          <AutoAwesome fontSize="small" />
                        </ListItemIcon>
                        <ListItemText 
                          primary={suggestion}
                          primaryTypographyProps={{ variant: 'body2' }}
                        />
                      </ListItem>
                    ))}
                  </List>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* AI Insights Tab */}
      {activeTab === 3 && (
        <Grid container spacing={3}>
          {aiInsights.map((insight) => (
            <Grid item xs={12} md={6} lg={4} key={insight.id}>
              <Card sx={{ height: '100%' }}>
                <CardContent>
                  <Box display="flex" justifyContent="between" alignItems="center" mb={2}>
                    <Typography variant="h6" gutterBottom>
                      {insight.title}
                    </Typography>
                    <Chip
                      label={insight.category}
                      variant="outlined"
                      size="small"
                    />
                  </Box>
                  
                  <Typography variant="body2" paragraph>
                    {insight.insight}
                  </Typography>
                  
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" gutterBottom>
                      AI Confidence: {(insight.confidence * 100).toFixed(1)}%
                    </Typography>
                    <LinearProgress
                      variant="determinate"
                      value={insight.confidence * 100}
                      color={insight.confidence > 0.8 ? 'success' : 'warning'}
                      sx={{ height: 6, borderRadius: 3 }}
                    />
                  </Box>
                  
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" gutterBottom>
                      Potential Impact: {insight.potential_impact.toFixed(1)}/10
                    </Typography>
                    <LinearProgress
                      variant="determinate"
                      value={insight.potential_impact * 10}
                      color={insight.potential_impact > 7 ? 'success' : 'primary'}
                      sx={{ height: 6, borderRadius: 3 }}
                    />
                  </Box>
                  
                  {insight.actionable && (
                    <Button fullWidth variant="contained" size="small">
                      Apply Insight
                    </Button>
                  )}
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
    </Box>
  );
};

export default PersonalizationEngine;
