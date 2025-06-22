import React, { useState, useEffect } from 'react';
import {Box,Typography, Select,MenuItem,TextField,Slider,FormControl,Button,Radio,RadioGroup, FormControlLabel} 
from '@mui/material';
import { DateTimePicker } from '@mui/x-date-pickers/DateTimePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import dayjs from 'dayjs';
import './mapleft.css';
import { countries } from '../../config/countries';


const MapLeft = ({ user_config, submitConfig }) => {
  const [country, setCountry] = useState('');
  const [threshold, setThreshold] = useState(0);
  const [thresholdType, setThresholdType] = useState('');
  const [speed, setSpeed] = useState(1);
  const [from, setFrom] = useState(null);
  const [to, setTo] = useState(null);
  const [stats, setStats] = useState({
    highest: '',
    lowest: '',
    average: '',
    stdDev: ''
  });

  useEffect(() => {
      if (user_config) {
        setCountry(user_config.country);
        setThreshold(user_config.threshold);
        setThresholdType(user_config['threshold-type']);
        setFrom(user_config.timeframe?.start ? dayjs(user_config.timeframe.start) : dayjs())
      }
    }, [user_config]);

  const handleSubmit = async () => {
    submitConfig({
      country,
      threshold,
      'threshold-type': thresholdType,
      timeframe: {
        start: from ? from.format('YYYY-MM-DD HH:mm:ss') : null,
        end: to ? to.format('YYYY-MM-DD HH:mm:ss') : null
      },
      'user': user_config.user
    });
  };

  const handleCountryChange = (event) => {
    const selectedCountry = event.target.value;
    setCountry(selectedCountry);
    
  }

  return (
    <LocalizationProvider dateAdapter={AdapterDayjs}>
      <Box className="map-left-container">
        <Typography variant="h6" className="section-title">Configuration Settings</Typography>

        <Box className="form-control">
          <Typography className="field-label">Country</Typography>
          <FormControl fullWidth size='small'>
            <Select  value={country || ''} onChange={handleCountryChange}>
              {countries.map(c => (
                <MenuItem key={c} value={c}>{c}</MenuItem>
              ))}
            </Select>
          </FormControl>
        </Box>

        <Box className="form-control">
          <Box display="flex">
              <Typography className="field-label">Threshold</Typography>
              <FormControl sx={{ ml: 1.2, mt: -0.5 }} component="fieldset">
                <RadioGroup
                  row
                  name="threshold-type"
                  value={thresholdType || ''}
                  onChange={(e) => setThresholdType(e.target.value)}
                >
                  <FormControlLabel
                    value="below"
                    control={<Radio size="sm" />}
                    label="Below"
                  />
                  <FormControlLabel
                    value="both"
                    control={<Radio size="sm" />}
                    label="Both"
                  />
                  <FormControlLabel
                    value="above"
                    control={<Radio size="sm" />}
                    label="Above"
                  />
                </RadioGroup>
              </FormControl>
          </Box>
          <TextField
            type="number"
            fullWidth
            size="small"
            value={threshold || 0}
            onChange={e => setThreshold(Number(e.target.value))}
          />
        </Box>

        <Box className="form-control">
          <Typography className="field-label">Timeframe (From)</Typography>
          <DateTimePicker
            value={from || null}
            onChange={setFrom}
            format="YYYY-MM-DD HH:mm:ss"
            ampm={false}
            slotProps={{ textField: { size: 'small', fullWidth: true } }}
          />
        </Box>

        <Box className="form-control">
          <Typography className="field-label">Timeframe (To)</Typography>
          <DateTimePicker
            value={to || null}
            onChange={setTo}
            format="YYYY-MM-DD HH:mm:ss"
            ampm={false}
            slotProps={{ textField: { size: 'small', fullWidth: true } }}
          />
        </Box>

        <Box mt={3} className="submit-container">
          <Button
            variant="contained"
            color="primary"
            onClick={handleSubmit}
          >
            Retrieve Data
          </Button>
        </Box>

        <Box className="form-control">
          <Typography className="field-label">Speed: {speed}</Typography>
          <Slider
            value={speed}
            onChange={(e, val) => setSpeed(val)}
            min={1}
            max={10}
            step={1}
            marks
            size='small'
          />
        </Box>

        <Box className="form-control">
          <Typography className="field-label" fontWeight="bold">Statistics</Typography>
          <Box className="stat-row">
            <Typography variant="body2">Highest: {stats.highest} CPM</Typography>
            <Typography variant="body2">Lowest: {stats.lowest} CPM</Typography>
          </Box>
          <Box className="stat-row">
            <Typography variant="body2">Average: {stats.average} CPM</Typography>
            <Typography variant="body2">Std Dev: {stats.stdDev} CPM</Typography>
          </Box>
        </Box>
      </Box>
    </LocalizationProvider>
  );
};
export default MapLeft;