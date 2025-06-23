import React, { useState, useEffect, useRef } from 'react';
import {Box,Typography, Select,MenuItem,TextField,Slider,FormControl,Button,Radio,RadioGroup, FormControlLabel} 
from '@mui/material';
import { DateTimePicker } from '@mui/x-date-pickers/DateTimePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import dayjs from 'dayjs';
import './mapleft.css';
import { countries } from '../../config/countries';
import { getBoundingBox } from '../../services/api';
import { ToastContainer, toast } from 'react-toastify';


const MapLeft = ({ user_config, submitConfig, speedConfig }) => {
  const [country, setCountry] = useState('');
  const [threshold, setThreshold] = useState(0);
  const [boundingBox, setBoundingBox] = useState(null);
  const [centre, setCentre] = useState(null);
  const [thresholdType, setThresholdType] = useState('');
  const [speed, setSpeed] = useState(1);
  const [from, setFrom] = useState(null);
  const [to, setTo] = useState(null);
  const initialized = useRef(false);
  const [stats, setStats] = useState({
    highest: '',
    lowest: '',
    average: '',
    stdDev: ''
  });

  useEffect(() => {
      if (Object.keys(user_config).length > 0 && !initialized.current) {
        setCountry(user_config.country);
        setThreshold(user_config.threshold);
        setThresholdType(user_config['threshold-type']);
        setBoundingBox(user_config.boundingbox);
        setFrom(user_config.timeframe?.start ? dayjs(user_config.timeframe.start) : null);
        setTo(user_config.timeframe?.end ? dayjs(user_config.timeframe.end) : null);
        setCentre(user_config.centre);
        initialized.current = true;
      }
    }, [user_config]);

  const handleSubmit = async () => {
    const config = {
      country,
      threshold,
      'threshold-type': thresholdType,
      'boundingbox': boundingBox,
      centre,
      'user': user_config.user
    };
    if (from) {
      config.timeframe = { start: from.format('YYYY-MM-DD HH:mm:ss') };
    }
    if (to) {
      config.timeframe = { ...config.timeframe, end: to.format('YYYY-MM-DD HH:mm:ss') };
    }
    submitConfig(config);
  };

  const handleCountryChange = async (event) => {
    const selectedCountry = event.target.value;
    try {
      const boundingBox = await getBoundingBox(selectedCountry);
      const mappedbb = boundingBox[0].boundingbox.map(Number);
      setBoundingBox(mappedbb);
      setCentre([Number(boundingBox[0].lat), Number(boundingBox[0].lon)]);
    } catch (error) {
      toast.error(error.message,{
          position: "top-center",
          autoClose: 2000
      })
    }
    setCountry(selectedCountry);
  }

  const setFromTimeframe = (value) => {
    if(to && value && value.isAfter(to)) {
      toast.error('Start time cannot be after end time',{
          position: "top-center",
          autoClose: 2000
      });
      setFrom(null);
    } else {
      setFrom(value);
    }
  }

  const setToTimeframe = (value) => {
   if(from && value && value.isBefore(from)) {
      toast.error('End time cannot be before start time',{
          position: "top-center",
          autoClose: 2000
      });
      setTo(null);
   } else {
      setTo(value);
    }
  }

  const speedChange = (value) => {
    setSpeed(value);
    speedConfig(value);
  };

  return (
    <LocalizationProvider dateAdapter={AdapterDayjs}>
      <ToastContainer />
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
            onChange={setFromTimeframe}
            format="YYYY-MM-DD HH:mm:ss"
            ampm={false}
            slotProps={{ textField: { size: 'small', fullWidth: true } }}
          />
        </Box>

        <Box className="form-control">
          <Typography className="field-label">Timeframe (To)</Typography>
          <DateTimePicker
            value={to || null}
            onChange={setToTimeframe}
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
            onChange={(e, val) => speedChange(val)}
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