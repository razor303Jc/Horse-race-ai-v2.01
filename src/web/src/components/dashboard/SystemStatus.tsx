// components/dashboard/SystemStatus.tsx
import { Speed } from '@mui/icons-material'
import {
    Box,
    Chip,
    Grid,
    Paper,
    Typography,
    useTheme
} from '@mui/material'
import React from 'react'
import { useSystemStatus } from '../../contexts/DashboardContext'

interface StatusIndicatorProps {
  label: string
  status: string
}

const StatusIndicator: React.FC<StatusIndicatorProps> = ({ label, status }) => {
  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'operational':
      case 'excellent':
      case 'connected':
      case 'active':
        return 'success'
      case 'warning':
        return 'warning'
      case 'error':
        return 'error'
      default:
        return 'info'
    }
  }

  return (
    <Chip
      label={`${label}: ${status || 'UNKNOWN'}`}
      color={getStatusColor(status || '')}
      variant="outlined"
      sx={{ width: '100%' }}
    />
  )
}

const SystemStatus: React.FC = () => {
  const systemStatus = useSystemStatus()
  const theme = useTheme()

  if (!systemStatus) {
    return null
  }

  const statusItems = [
    { label: 'Overall', status: systemStatus.overall_status },
    { label: 'ML Models', status: systemStatus.ml_models },
    { label: 'Betting', status: systemStatus.betting_integration },
    { label: 'AI', status: systemStatus.contextual_ai },
    { label: 'Notifications', status: systemStatus.notifications },
    { label: 'Performance', status: systemStatus.performance_tracker },
  ]

  return (
    <Paper 
      sx={{ 
        p: 3, 
        mb: 4, 
        background: 'rgba(255, 255, 255, 0.05)', 
        backdropFilter: 'blur(10px)' 
      }}
    >
      <Typography 
        variant="h5" 
        gutterBottom 
        sx={{ 
          color: 'white', 
          display: 'flex', 
          alignItems: 'center', 
          gap: 2 
        }}
      >
        <Speed /> System Status Overview
      </Typography>
      
      <Grid container spacing={2}>
        {statusItems.map((item, index) => (
          <Grid item xs={12} sm={6} md={2} key={index}>
            <StatusIndicator label={item.label} status={item.status} />
          </Grid>
        ))}
      </Grid>

      <Box mt={2}>
        <Typography variant="caption" color="text.secondary">
          Last updated: {new Date(systemStatus.timestamp).toLocaleString()}
        </Typography>
      </Box>
    </Paper>
  )
}

export default SystemStatus
