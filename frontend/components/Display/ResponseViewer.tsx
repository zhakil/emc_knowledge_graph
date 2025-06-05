import React from 'react';
import { 
  Box, 
  Typography, 
  Chip, 
  Divider, 
  Table, 
  TableBody, 
  TableCell, 
  TableContainer, 
  TableHead, 
  TableRow, 
  Paper,
  Alert,
  Grid
} from '@mui/material';
import { TestResult } from '../../types/TestTypes';

interface ResponseViewerProps {
  result: TestResult | null;
  error?: string | null;
}

const ResponseViewer: React.FC<ResponseViewerProps> = ({ result, error }) => {
  if (error) {
    return (
      <Alert severity="error" sx={{ mt: 2 }}>
        {error}
      </Alert>
    );
  }

  if (!result) {
    return (
      <Box sx={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: 300,
        border: '1px dashed #e0e0e0',
        borderRadius: 2
      }}>
        <Typography variant="h6" color="textSecondary">
          No test result to display
        </Typography>
      </Box>
    );
  }

  // Determine status color
  const statusColor = result.status === 'Pass' ? 'success.main' : 
                     result.status === 'Fail' ? 'error.main' : 'warning.main';

  return (
    <Paper elevation={0} sx={{ 
      border: '1px solid #e0e0e0', 
      borderRadius: 2, 
      p: 3,
      mt: 2
    }}>
      {/* Header Section */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
        <Typography variant="h5" fontWeight="bold">
          {result.testName}
        </Typography>
        <Chip 
          label={result.status} 
          sx={{ 
            bgcolor: statusColor, 
            color: 'white', 
            fontWeight: 'bold',
            fontSize: '1rem',
            px: 2
          }} 
        />
      </Box>

      <Divider sx={{ my: 2 }} />

      {/* Key Details Section */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={6}>
          <DetailItem label="Standard" value={result.standard} />
          <DetailItem 
            label="Frequency Range" 
            value={result.frequencyRange || 'N/A'} 
          />
          <DetailItem 
            label="Compliance Margin" 
            value={result.complianceMargin ? 
              `${result.complianceMargin.toFixed(1)} dB` : 'N/A'
            }
            color={result.complianceMargin && result.complianceMargin < 0 ? 
              'error.main' : 'success.main'
            }
          />
        </Grid>
        <Grid item xs={12} md={6}>
          <DetailItem label="Test Engineer" value={result.testEngineer} />
          <DetailItem 
            label="Date" 
            value={new Date(result.date).toLocaleDateString()} 
          />
          <DetailItem 
            label="Equipment Used" 
            value={result.equipmentUsed?.join(', ') || 'N/A'} 
          />
        </Grid>
      </Grid>

      {/* Measurements Table */}
      {result.measurements && result.measurements.length > 0 && (
        <>
          <Typography variant="h6" sx={{ mb: 1, mt: 3 }}>
            Measurement Data
          </Typography>
          <TableContainer component={Paper} variant="outlined">
            <Table size="small">
              <TableHead>
                <TableRow sx={{ bgcolor: '#f5f5f5' }}>
                  <TableCell><strong>Frequency (MHz)</strong></TableCell>
                  <TableCell><strong>Amplitude (dBµV)</strong></TableCell>
                  <TableCell><strong>Limit (dBµV)</strong></TableCell>
                  <TableCell><strong>Margin (dB)</strong></TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {result.measurements.map((meas, index) => (
                  <TableRow key={index}>
                    <TableCell>{meas.frequency}</TableCell>
                    <TableCell>{meas.amplitude}</TableCell>
                    <TableCell>{meas.limit}</TableCell>
                    <TableCell sx={{ 
                      color: meas.margin && meas.margin < 0 ? 
                        'error.main' : 'success.main',
                      fontWeight: 500
                    }}>
                      {meas.margin ? meas.margin.toFixed(1) : 'N/A'}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </>
      )}

      {/* Issues Section */}
      {result.issues && (
        <>
          <Typography variant="h6" sx={{ mt: 3, mb: 1 }}>
            Issues & Observations
          </Typography>
          <Alert 
            severity={result.status === 'Fail' ? 'error' : 'warning'} 
            sx={{ mb: 2 }}
          >
            {result.issues}
          </Alert>
        </>
      )}
    </Paper>
  );
};

// Helper component for detail items
const DetailItem: React.FC<{
  label: string;
  value: React.ReactNode;
  color?: string;
}> = ({ label, value, color }) => (
  <Box sx={{ mb: 1.5 }}>
    <Typography variant="subtitle2" color="textSecondary">
      {label}
    </Typography>
    <Typography variant="body1" sx={{ color: color || 'inherit' }}>
      {value}
    </Typography>
  </Box>
);

export default ResponseViewer;