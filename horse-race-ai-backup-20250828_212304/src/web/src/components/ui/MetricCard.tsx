// components/ui/MetricCard.tsx
import { TrendingDown, TrendingFlat, TrendingUp } from '@mui/icons-material'
import {
    Box,
    Card,
    CardContent,
    CircularProgress,
    Typography,
    useTheme
} from '@mui/material'
import React from 'react'

interface MetricCardProps {
  title: string
  value: string | number
  subtitle?: string
  icon?: React.ReactNode
  color?: 'primary' | 'secondary' | 'success' | 'warning' | 'error'
  trend?: 'up' | 'down' | 'neutral'
  trendValue?: number
  loading?: boolean
  onClick?: () => void
}

const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  subtitle,
  icon,
  color = 'primary',
  trend,
  trendValue,
  loading = false,
  onClick
}) => {
  const theme = useTheme()

  const getTrendIcon = () => {
    switch (trend) {
      case 'up':
        return <TrendingUp color="success" />
      case 'down':
        return <TrendingDown color="error" />
      case 'neutral':
        return <TrendingFlat color="disabled" />
      default:
        return null
    }
  }

  const getTrendColor = () => {
    switch (trend) {
      case 'up':
        return theme.palette.success.main
      case 'down':
        return theme.palette.error.main
      default:
        return theme.palette.text.secondary
    }
  }

  return (
    <Card
      onClick={onClick}
      sx={{
        cursor: onClick ? 'pointer' : 'default',
        '&:hover': onClick ? {
          transform: 'translateY(-2px)',
          boxShadow: theme.shadows[8],
        } : {},
        transition: 'all 0.3s ease'
      }}
    >
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between" mb={1}>
          <Box display="flex" alignItems="center" gap={1}>
            {icon && (
              <Box color={`${color}.main`} display="flex" alignItems="center">
                {icon}
              </Box>
            )}
            <Typography variant="body2" color="text.secondary" fontWeight={500}>
              {title}
            </Typography>
          </Box>
          {trend && getTrendIcon()}
        </Box>

        {loading ? (
          <Box display="flex" alignItems="center" justifyContent="center" py={2}>
            <CircularProgress size={32} color={color} />
          </Box>
        ) : (
          <>
            <Typography 
              variant="h4" 
              color={`${color}.main`}
              fontWeight={700}
              mb={1}
            >
              {value}
            </Typography>
            
            <Box display="flex" alignItems="center" justifyContent="space-between">
              {subtitle && (
                <Typography variant="body2" color="text.secondary">
                  {subtitle}
                </Typography>
              )}
              {trendValue && (
                <Typography 
                  variant="caption" 
                  color={getTrendColor()}
                  fontWeight={600}
                >
                  {trend === 'up' ? '+' : trend === 'down' ? '-' : ''}
                  {Math.abs(trendValue)}%
                </Typography>
              )}
            </Box>
          </>
        )}
      </CardContent>
    </Card>
  )
}

export default MetricCard
