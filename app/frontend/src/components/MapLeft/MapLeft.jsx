import React, { useState } from 'react';
import {Box,Typography, Select,MenuItem,TextField,Slider,FormControl,Button} 
from '@mui/material';
import { DateTimePicker } from '@mui/x-date-pickers/DateTimePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import dayjs from 'dayjs';
import './mapleft.css';

const MapLeft = () => {
  const [country, setCountry] = useState('Germany');
  const [threshold, setThreshold] = useState(32);
  const [speed, setSpeed] = useState(5);
  const [from, setFrom] = useState(dayjs());
  const [to, setTo] = useState(dayjs());

  const stats = {
    highest: 50,
    lowest: 10,
    average: 30,
    stdDev: 7.5
  };

  const handleSubmit = async () => {
    const config = {
      user: "john_doe",
      boundingbox: [5.0, 50.0, 15.0, 55.0],
      country,
      threshold,
      "threshold-type": "static",
      timeframe: {
        start: from.format("YYYY-MM-DD HH:mm:ss"),
        end: to.format("YYYY-MM-DD HH:mm:ss")
      }
    };

    try {
      const res = await fetch("http://localhost:8000/set-config", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(config)
      });

      const data = await res.json();
      console.log("Config sent:", data);
    } catch (err) {
      console.error("Error sending config:", err);
    }
  };

  return (
    <LocalizationProvider dateAdapter={AdapterDayjs}>
      <Box className="map-left-container">
        <Typography variant="h6" className="section-title">Configuration Settings</Typography>

        <Box className="form-control">
          <Typography className="field-label">Country</Typography>
          <FormControl fullWidth>
            <Select value={country} onChange={e => setCountry(e.target.value)}>
              <MenuItem value="Germany">Germany</MenuItem>
              <MenuItem value="USA">USA</MenuItem>
              <MenuItem value="India">India</MenuItem>
            </Select>
          </FormControl>
        </Box>

        <Box className="form-control">
          <Typography className="field-label">Threshold</Typography>
          <TextField
            type="number"
            fullWidth
            value={threshold}
            onChange={e => setThreshold(Number(e.target.value))}
          />
        </Box>

        <Box className="form-control">
          <Typography className="field-label">Timeframe (From)</Typography>
          <DateTimePicker
            value={from}
            onChange={setFrom}
            format="YYYY-MM-DD HH:mm:ss"
            ampm={false}
          />
        </Box>

        <Box className="form-control">
          <Typography className="field-label">Timeframe (To)</Typography>
          <DateTimePicker
            value={to}
            onChange={setTo}
            format="YYYY-MM-DD HH:mm:ss"
            ampm={false}
          />
        </Box>

        <Box className="form-control">
          <Typography className="field-label">Speed (1-10)</Typography>
          <Slider
            value={speed}
            onChange={(e, val) => setSpeed(val)}
            min={1}
            max={10}
            step={1}
            marks
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


        <Box mt={3}>
          <Button
            variant="contained"
            color="primary"
            fullWidth
            onClick={handleSubmit}
            className="submit-button"
          >
            Retrieve Data
          </Button>
        </Box>
      </Box>
    </LocalizationProvider>
  );
};
export default MapLeft;