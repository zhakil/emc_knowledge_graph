import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Grid,
  TextField,
  MenuItem,
  FormControl,
  InputLabel,
  Select,
  Chip,
  Typography,
  Divider,
  Paper
} from '@mui/material';
import { TestConfig } from '../../types/TestTypes';

interface ConfigEditorProps {
  initialConfig?: TestConfig;
  onSave: (config: TestConfig) => void;
  onCancel: () => void;
  availableEquipment: string[];
}

const ConfigEditor: React.FC<ConfigEditorProps> = ({
  initialConfig,
  onSave,
  onCancel,
  availableEquipment
}) => {
  // Default configuration template
  const defaultConfig: TestConfig = {
    testName: '',
    standard: 'FCC Part 15',
    frequencyRange: '30MHz-6GHz',
    equipmentUsed: [],
    notes: '',
    limits: {
      radiated: 40,
      conducted: 60,
      harmonic: 55
    }
  };

  const [config, setConfig] = useState<TestConfig>(
    initialConfig || { ...defaultConfig }
  );
  const [errors, setErrors] = useState<Record<string, boolean>>({});

  // Update form when initialConfig changes
  useEffect(() => {
    if (initialConfig) {
      setConfig(initialConfig);
    }
  }, [initialConfig]);

  const handleChange = (field: keyof TestConfig, value: any) => {
    setConfig(prev => ({ ...prev, [field]: value }));
  };

  const handleLimitChange = (limitType: keyof TestConfig['limits'], value: number) => {
    setConfig(prev => ({
      ...prev,
      limits: {
        ...prev.limits,
        [limitType]: value
      }
    }));
  };

  const validate = () => {
    const newErrors: Record<string, boolean> = {};
    if (!config.testName.trim()) newErrors.testName = true;
    if (!config.standard) newErrors.standard = true;
    if (!config.frequencyRange) newErrors.frequencyRange = true;
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = () => {
    if (validate()) {
      onSave(config);
    }
  };

  return (
    <Paper elevation={1} sx={{ p: 3, border: '1px solid #e0e0e0' }}>
      <Typography variant="h6" gutterBottom>
        {initialConfig ? 'Edit Test Configuration' : 'Create New Test Configuration'}
      </Typography>
      <Divider sx={{ mb: 3 }} />

      <Grid container spacing={3}>
        {/* Test Details Section */}
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Test Name *"
            value={config.testName}
            onChange={(e) => handleChange('testName', e.target.value)}
            error={errors.testName}
            helperText={errors.testName && 'Test name is required'}
            sx={{ mb: 2 }}
          />

          <FormControl fullWidth sx={{ mb: 2 }} error={errors.standard}>
            <InputLabel>Standard *</InputLabel>
            <Select
              value={config.standard}
              label="Standard *"
              onChange={(e) => handleChange('standard', e.target.value)}
            >
              <MenuItem value="FCC Part 15">FCC Part 15</MenuItem>
              <MenuItem value="CE EN 55032">CE EN 55032</MenuItem>
              <MenuItem value="MIL-STD-461">MIL-STD-461</MenuItem>
              <MenuItem value="CISPR 22">CISPR 22</MenuItem>
              <MenuItem value="Other">Other</MenuItem>
            </Select>
          </FormControl>

          <TextField
            fullWidth
            label="Frequency Range *"
            value={config.frequencyRange}
            onChange={(e) => handleChange('frequencyRange', e.target.value)}
            error={errors.frequencyRange}
            helperText={errors.frequencyRange && 'Frequency range is required'}
            sx={{ mb: 2 }}
          />
        </Grid>

        {/* Equipment Selection */}
        <Grid item xs={12} md={6}>
          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel>Select Equipment</InputLabel>
            <Select
              multiple
              value={config.equipmentUsed}
              onChange={(e) => handleChange('equipmentUsed', e.target.value)}
              renderValue={(selected) => (
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                  {selected.map((value) => (
                    <Chip key={value} label={value} size="small" />
                  ))}
                </Box>
              )}
            >
              {availableEquipment.map((equip) => (
                <MenuItem key={equip} value={equip}>
                  {equip}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <TextField
            fullWidth
            label="Notes"
            value={config.notes}
            onChange={(e) => handleChange('notes', e.target.value)}
            multiline
            rows={3}
            sx={{ mb: 2 }}
          />
        </Grid>

        {/* Limits Section */}
        <Grid item xs={12}>
          <Typography variant="subtitle1" gutterBottom>
            Emission Limits (dBµV/m)
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={4}>
              <TextField
                fullWidth
                label="Radiated"
                type="number"
                value={config.limits.radiated}
                onChange={(e) => handleLimitChange('radiated', Number(e.target.value))}
              />
            </Grid>
            <Grid item xs={4}>
              <TextField
                fullWidth
                label="Conducted"
                type="number"
                value={config.limits.conducted}
                onChange={(e) => handleLimitChange('conducted', Number(e.target.value))}
              />
            </Grid>
            <Grid item xs={4}>
              <TextField
                fullWidth
                label="Harmonic"
                type="number"
                value={config.limits.harmonic}
                onChange={(e) => handleLimitChange('harmonic', Number(e.target.value))}
              />
            </Grid>
          </Grid>
        </Grid>

        {/* Action Buttons */}
        <Grid item xs={12}>
          <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
            <Button 
              variant="outlined" 
              onClick={onCancel}
              color="secondary"
            >
              Cancel
            </Button>
            <Button 
              variant="contained" 
              onClick={handleSubmit}
              color="primary"
            >
              {initialConfig ? 'Update Configuration' : 'Create Configuration'}
            </Button>
          </Box>
        </Grid>
      </Grid>
    </Paper>
  );
};

export default ConfigEditor;