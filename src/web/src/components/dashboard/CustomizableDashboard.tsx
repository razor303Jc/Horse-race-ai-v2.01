import React, { useState, useEffect } from 'react';
import {
    Box,
    Card,
    CardContent,
    CardHeader,
    IconButton,
    Grid,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Button,
    Checkbox,
    FormControlLabel,
    Typography,
    Switch,
    Divider,
    Chip
} from '@mui/material';
import {
    Settings,
    DragIndicator,
    Visibility,
    VisibilityOff,
    Add,
    Close,
    Dashboard as DashboardIcon,
    TrendingUp,
    AccountBalance,
    Speed,
    Assessment,
    Timeline,
    ShowChart
} from '@mui/icons-material';
import { DragDropContext, Droppable, Draggable, DropResult } from 'react-beautiful-dnd';
import { PerformanceMetricsDashboard } from './PerformanceMetricsDashboard';
import { useDailyRaces, useStage8Performance } from '../../hooks/useAPI';

interface Widget {
    id: string;
    title: string;
    component: React.ComponentType<any>;
    visible: boolean;
    size: 'small' | 'medium' | 'large';
    order: number;
    icon: React.ReactNode;
    description: string;
}

interface DashboardLayout {
    widgets: Widget[];
    gridLayout: 'compact' | 'comfortable' | 'spacious';
    theme: 'light' | 'dark';
    autoRefresh: boolean;
    refreshInterval: number;
}

// Quick Stats Widget
const QuickStatsWidget: React.FC = () => {
    const { performance } = useStage8Performance();
    
    return (
        <Grid container spacing={2}>
            <Grid item xs={6}>
                <Box sx={{ textAlign: 'center', p: 1 }}>
                    <Typography variant="h6" color="primary">£{performance.account_balance.toFixed(2)}</Typography>
                    <Typography variant="caption">Balance</Typography>
                </Box>
            </Grid>
            <Grid item xs={6}>
                <Box sx={{ textAlign: 'center', p: 1 }}>
                    <Typography variant="h6" color="success.main">{performance.win_rate.toFixed(1)}%</Typography>
                    <Typography variant="caption">Win Rate</Typography>
                </Box>
            </Grid>
            <Grid item xs={6}>
                <Box sx={{ textAlign: 'center', p: 1 }}>
                    <Typography variant="h6" color="warning.main">{performance.roi.toFixed(1)}%</Typography>
                    <Typography variant="caption">ROI</Typography>
                </Box>
            </Grid>
            <Grid item xs={6}>
                <Box sx={{ textAlign: 'center', p: 1 }}>
                    <Typography variant="h6" color="info.main">{performance.active_bets}</Typography>
                    <Typography variant="caption">Active</Typography>
                </Box>
            </Grid>
        </Grid>
    );
};

// Today's Races Widget
const TodayRacesWidget: React.FC = () => {
    const { data: racesData } = useDailyRaces();
    
    return (
        <Box>
            <Typography variant="h6" gutterBottom>
                🏇 Today's Schedule
            </Typography>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                <Chip label={`${racesData?.total_races || 0} Races`} color="primary" size="small" />
                <Chip label={`${racesData?.total_meetings || 0} Meetings`} color="secondary" size="small" />
            </Box>
            <Typography variant="body2" color="text.secondary">
                Prize money: £{racesData?.daily_stats.total_prize_money.toLocaleString() || 0}
            </Typography>
            <Typography variant="body2" color="text.secondary">
                Avg field size: {racesData?.daily_stats.average_field_size || 0}
            </Typography>
        </Box>
    );
};

// Performance Chart Widget (Mini)
const MiniPerformanceWidget: React.FC = () => {
    const { performance } = useStage8Performance();
    
    return (
        <Box>
            <Typography variant="h6" gutterBottom>
                📈 Performance Trend
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <TrendingUp color="success" sx={{ mr: 1 }} />
                <Typography variant="body2">
                    Daily P&L: £{performance.daily_pnl.toFixed(2)}
                </Typography>
            </Box>
            <Box sx={{ height: 60, backgroundColor: '#f5f5f5', borderRadius: 1, p: 1 }}>
                <Typography variant="caption" color="text.secondary">
                    Mini chart placeholder - Recharts integration
                </Typography>
            </Box>
        </Box>
    );
};

// Active Bets Widget
const ActiveBetsWidget: React.FC = () => {
    const { performance } = useStage8Performance();
    
    return (
        <Box>
            <Typography variant="h6" gutterBottom>
                🎯 Active Positions
            </Typography>
            <Typography variant="h4" color="primary" sx={{ mb: 1 }}>
                {performance.active_bets}
            </Typography>
            <Typography variant="body2" color="text.secondary">
                Total bets placed: {performance.total_bets}
            </Typography>
            <Box sx={{ mt: 2 }}>
                <Chip 
                    label="View Details" 
                    size="small" 
                    clickable 
                    color="primary" 
                    variant="outlined"
                />
            </Box>
        </Box>
    );
};

export const CustomizableDashboard: React.FC = () => {
    const [dashboardLayout, setDashboardLayout] = useState<DashboardLayout>({
        widgets: [
            {
                id: 'quick-stats',
                title: 'Quick Stats',
                component: QuickStatsWidget,
                visible: true,
                size: 'small',
                order: 0,
                icon: <Assessment />,
                description: 'Key performance metrics at a glance'
            },
            {
                id: 'today-races',
                title: "Today's Races",
                component: TodayRacesWidget,
                visible: true,
                size: 'medium',
                order: 1,
                icon: <Speed />,
                description: 'Overview of today\'s racing schedule'
            },
            {
                id: 'performance-chart',
                title: 'Performance Trend',
                component: MiniPerformanceWidget,
                visible: true,
                size: 'medium',
                order: 2,
                icon: <ShowChart />,
                description: 'Mini performance chart with trends'
            },
            {
                id: 'active-bets',
                title: 'Active Bets',
                component: ActiveBetsWidget,
                visible: true,
                size: 'small',
                order: 3,
                icon: <AccountBalance />,
                description: 'Current betting positions'
            },
            {
                id: 'performance-dashboard',
                title: 'Full Analytics',
                component: PerformanceMetricsDashboard,
                visible: false,
                size: 'large',
                order: 4,
                icon: <Timeline />,
                description: 'Comprehensive performance analytics dashboard'
            }
        ],
        gridLayout: 'comfortable',
        theme: 'light',
        autoRefresh: true,
        refreshInterval: 30
    });

    const [customizeOpen, setCustomizeOpen] = useState(false);

    // Load saved layout from localStorage
    useEffect(() => {
        const savedLayout = localStorage.getItem('dashboard-layout');
        if (savedLayout) {
            try {
                setDashboardLayout(JSON.parse(savedLayout));
            } catch (error) {
                console.error('Failed to load dashboard layout:', error);
            }
        }
    }, []);

    // Save layout to localStorage
    const saveLayout = (newLayout: DashboardLayout) => {
        setDashboardLayout(newLayout);
        localStorage.setItem('dashboard-layout', JSON.stringify(newLayout));
    };

    const handleDragEnd = (result: DropResult) => {
        if (!result.destination) return;

        const widgets = Array.from(dashboardLayout.widgets);
        const [reorderedWidget] = widgets.splice(result.source.index, 1);
        widgets.splice(result.destination.index, 0, reorderedWidget);

        // Update order
        const updatedWidgets = widgets.map((widget, index) => ({
            ...widget,
            order: index
        }));

        saveLayout({
            ...dashboardLayout,
            widgets: updatedWidgets
        });
    };

    const toggleWidgetVisibility = (widgetId: string) => {
        const updatedWidgets = dashboardLayout.widgets.map(widget =>
            widget.id === widgetId 
                ? { ...widget, visible: !widget.visible }
                : widget
        );

        saveLayout({
            ...dashboardLayout,
            widgets: updatedWidgets
        });
    };

    const getGridSize = (size: 'small' | 'medium' | 'large') => {
        switch (size) {
            case 'small': return { xs: 12, sm: 6, md: 4 };
            case 'medium': return { xs: 12, sm: 6, md: 6 };
            case 'large': return { xs: 12 };
            default: return { xs: 12, sm: 6, md: 4 };
        }
    };

    const visibleWidgets = dashboardLayout.widgets
        .filter(widget => widget.visible)
        .sort((a, b) => a.order - b.order);

    return (
        <Box sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
                <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
                    🏠 Customizable Dashboard
                </Typography>
                <Box>
                    <IconButton 
                        onClick={() => setCustomizeOpen(true)}
                        color="primary"
                        sx={{ mr: 1 }}
                    >
                        <Settings />
                    </IconButton>
                    <Chip 
                        icon={<DashboardIcon />}
                        label={`${visibleWidgets.length} widgets active`}
                        color="primary"
                        variant="outlined"
                    />
                </Box>
            </Box>

            <DragDropContext onDragEnd={handleDragEnd}>
                <Droppable droppableId="dashboard">
                    {(provided) => (
                        <Grid 
                            container 
                            spacing={dashboardLayout.gridLayout === 'compact' ? 2 : 
                                   dashboardLayout.gridLayout === 'comfortable' ? 3 : 4}
                            {...provided.droppableProps}
                            ref={provided.innerRef}
                        >
                            {visibleWidgets.map((widget, index) => (
                                <Draggable key={widget.id} draggableId={widget.id} index={index}>
                                    {(provided, snapshot) => (
                                        <Grid 
                                            item 
                                            {...getGridSize(widget.size)}
                                            ref={provided.innerRef}
                                            {...provided.draggableProps}
                                        >
                                            <Card 
                                                sx={{ 
                                                    height: '100%',
                                                    transform: snapshot.isDragging ? 'rotate(5deg)' : 'none',
                                                    boxShadow: snapshot.isDragging ? 4 : 1,
                                                    transition: 'transform 0.2s ease, box-shadow 0.2s ease'
                                                }}
                                            >
                                                <CardHeader
                                                    avatar={widget.icon}
                                                    title={widget.title}
                                                    action={
                                                        <Box {...provided.dragHandleProps}>
                                                            <DragIndicator color="action" />
                                                        </Box>
                                                    }
                                                    sx={{ 
                                                        pb: 1,
                                                        '& .MuiCardHeader-title': { fontSize: '1rem' }
                                                    }}
                                                />
                                                <CardContent sx={{ pt: 0 }}>
                                                    <widget.component />
                                                </CardContent>
                                            </Card>
                                        </Grid>
                                    )}
                                </Draggable>
                            ))}
                            {provided.placeholder}
                        </Grid>
                    )}
                </Droppable>
            </DragDropContext>

            {/* Customization Dialog */}
            <Dialog open={customizeOpen} onClose={() => setCustomizeOpen(false)} maxWidth="md" fullWidth>
                <DialogTitle>
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                        Customize Dashboard
                        <IconButton onClick={() => setCustomizeOpen(false)}>
                            <Close />
                        </IconButton>
                    </Box>
                </DialogTitle>
                <DialogContent>
                    <Typography variant="h6" gutterBottom>
                        Widget Visibility
                    </Typography>
                    <Grid container spacing={2}>
                        {dashboardLayout.widgets.map((widget) => (
                            <Grid item xs={12} sm={6} key={widget.id}>
                                <Card variant="outlined">
                                    <CardContent>
                                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                                            {widget.icon}
                                            <Typography variant="subtitle1" sx={{ ml: 1, flex: 1 }}>
                                                {widget.title}
                                            </Typography>
                                            <Switch
                                                checked={widget.visible}
                                                onChange={() => toggleWidgetVisibility(widget.id)}
                                                color="primary"
                                            />
                                        </Box>
                                        <Typography variant="body2" color="text.secondary">
                                            {widget.description}
                                        </Typography>
                                        <Chip 
                                            label={widget.size} 
                                            size="small" 
                                            color="default" 
                                            sx={{ mt: 1 }}
                                        />
                                    </CardContent>
                                </Card>
                            </Grid>
                        ))}
                    </Grid>

                    <Divider sx={{ my: 3 }} />

                    <Typography variant="h6" gutterBottom>
                        Layout Settings
                    </Typography>
                    <Grid container spacing={2}>
                        <Grid item xs={12} sm={4}>
                            <FormControlLabel
                                control={
                                    <Switch
                                        checked={dashboardLayout.autoRefresh}
                                        onChange={(e) => saveLayout({
                                            ...dashboardLayout,
                                            autoRefresh: e.target.checked
                                        })}
                                    />
                                }
                                label="Auto Refresh"
                            />
                        </Grid>
                        <Grid item xs={12} sm={8}>
                            <Typography variant="body2" color="text.secondary">
                                Automatically refresh dashboard data every {dashboardLayout.refreshInterval} seconds
                            </Typography>
                        </Grid>
                    </Grid>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setCustomizeOpen(false)}>
                        Close
                    </Button>
                    <Button 
                        variant="contained" 
                        onClick={() => {
                            // Reset to default layout
                            localStorage.removeItem('dashboard-layout');
                            window.location.reload();
                        }}
                    >
                        Reset to Default
                    </Button>
                </DialogActions>
            </Dialog>
        </Box>
    );
};
