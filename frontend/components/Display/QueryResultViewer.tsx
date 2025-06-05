import React, { useState, useMemo } from 'react';
import {
  DataGrid,
  GridColDef,
  GridToolbar,
  GridSortModel,
  GridFilterModel,
  GridRowParams,
  GridValueFormatterParams
} from '@mui/x-data-grid';
import { Box, Chip, Typography, LinearProgress, Alert } from '@mui/material';
import { TestResult } from '../../types/TestTypes';

interface QueryResultViewerProps {
  data: TestResult[];
  loading?: boolean;
  error?: string | null;
  onRowClick?: (result: TestResult) => void;
}

const QueryResultViewer: React.FC<QueryResultViewerProps> = ({
  data,
  loading = false,
  error = null,
  onRowClick
}) => {
  const [sortModel, setSortModel] = useState<GridSortModel>([
    { field: 'date', sort: 'desc' }
  ]);
  
  const [filterModel, setFilterModel] = useState<GridFilterModel>({
    items: []
  });

  // Column definitions with EMC-specific formatting
  const columns: GridColDef[] = [
    {
      field: 'id',
      headerName: 'ID',
      width: 80,
      hide: true
    },
    {
      field: 'testName',
      headerName: 'Test Name',
      width: 200,
      renderCell: (params) => (
        <Typography variant="body2" fontWeight="medium">
          {params.value}
        </Typography>
      )
    },
    {
      field: 'standard',
      headerName: 'Standard',
      width: 150,
      valueFormatter: (params: GridValueFormatterParams) => 
        params.value || 'N/A'
    },
    {
      field: 'status',
      headerName: 'Status',
      width: 120,
      renderCell: (params) => (
        <Chip
          label={params.value}
          color={
            params.value === 'Pass' ? 'success' : 
            params.value === 'Fail' ? 'error' : 'warning'
          }
          size="small"
        />
      )
    },
    {
      field: 'date',
      headerName: 'Date',
      type: 'date',
      width: 120,
      valueFormatter: (params: GridValueFormatterParams) => 
        new Date(params.value).toLocaleDateString()
    },
    {
      field: 'frequencyRange',
      headerName: 'Frequency',
      width: 150,
      valueFormatter: (params: GridValueFormatterParams) => 
        params.value || 'N/A'
    },
    {
      field: 'testEngineer',
      headerName: 'Engineer',
      width: 150
    },
    {
      field: 'equipmentUsed',
      headerName: 'Equipment',
      width: 200,
      valueFormatter: (params: GridValueFormatterParams) => 
        params.value?.join(', ') || 'N/A'
    },
    {
      field: 'complianceMargin',
      headerName: 'Margin (dB)',
      width: 120,
      type: 'number',
      renderCell: (params) => (
        <Typography 
          color={params.value < 0 ? 'error' : 'success.main'}
          fontWeight={500}
        >
          {params.value ? `${params.value.toFixed(1)} dB` : 'N/A'}
        </Typography>
      )
    }
  ];

  // Handle row click
  const handleRowClick = (params: GridRowParams) => {
    if (onRowClick) {
      onRowClick(params.row as TestResult);
    }
  };

  return (
    <Box sx={{ 
      height: '70vh', 
      width: '100%',
      backgroundColor: 'background.paper',
      borderRadius: 2,
      overflow: 'hidden',
      border: '1px solid',
      borderColor: 'divider'
    }}>
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      
      <DataGrid
        rows={data}
        columns={columns}
        loading={loading}
        sortModel={sortModel}
        filterModel={filterModel}
        onSortModelChange={(model) => setSortModel(model)}
        onFilterModelChange={(model) => setFilterModel(model)}
        onRowClick={handleRowClick}
        components={{
          Toolbar: GridToolbar,
          LoadingOverlay: LinearProgress
        }}
        componentsProps={{
          toolbar: {
            showQuickFilter: true,
            quickFilterProps: { debounceMs: 500 },
            printOptions: { disableToolbarButton: true }
          }
        }}
        disableColumnMenu
        disableSelectionOnClick
        pageSize={10}
        rowsPerPageOptions={[5, 10, 25]}
        sx={{
          '& .MuiDataGrid-cell:focus': { outline: 'none' },
          '& .MuiDataGrid-row:hover': { 
            backgroundColor: 'action.hover',
            cursor: 'pointer'
          }
        }}
      />
    </Box>
  );
};

export default QueryResultViewer;