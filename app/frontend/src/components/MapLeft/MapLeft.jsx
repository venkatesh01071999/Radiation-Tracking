import React, { useState, useEffect } from 'react';
import {Box,Typography, Select,MenuItem,TextField,Slider,FormControl,Button} 
from '@mui/material';
import { DateTimePicker } from '@mui/x-date-pickers/DateTimePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import dayjs from 'dayjs';
import './mapleft.css';

const countries = [
  "Germany", "USA", "India", "Togo", "Georgia", "Vanuatu", "Kyrgyzstan",
  "Niger", "China", "Tuvalu", "Comoros", "Bosnia and Herzegovina", "Bahrain",
  "Somalia", "Latvia", "Netherlands", "Lesotho", "Venezuela", "Kenya",
  "Turkey", "Fiji", "Trinidad and Tobago", "Honduras", "Djibouti", "Eswatini",
  "Tajikistan", "Saudi Arabia", "New Zealand", "Belarus", "Gambia", "DR Congo",
  "Costa Rica", "Malawi", "Republic of the Congo", "Oman", "Iraq", "Senegal",
  "Lebanon", "Angola", "Iran", "Ecuador", "Laos", "Sri Lanka", "São Tomé and Príncipe",
  "Grenada", "Guinea", "Panama", "Yemen", "Estonia", "Guyana", "Luxembourg",
  "Namibia", "Kosovo", "Libya", "Myanmar", "Israel", "Mali", "Argentina",
  "Uganda", "Malaysia", "Zambia", "Micronesia", "Slovakia", "Burundi", "Serbia",
  "Turkmenistan", "South Africa", "Kazakhstan", "Canada", "Poland", "San Marino",
  "Qatar", "Croatia", "Mauritius", "Sierra Leone", "Saint Kitts and Nevis", "Iceland",
  "Kuwait", "Cameroon", "El Salvador", "Cuba", "Brazil", "Solomon Islands",
  "Greece", "Norway", "Jamaica", "Tanzania", "Bolivia", "Cyprus", "Mongolia",
  "Monaco", "Tunisia", "Syria", "Chile", "Azerbaijan", "France", "South Korea",
  "Ghana", "Denmark", "Andorra", "Switzerland", "North Macedonia", "South Sudan",
  "Haiti", "Peru", "Guinea-Bissau", "Czechia", "Portugal", "Gabon", "Mexico",
  "Italy", "Finland", "Zimbabwe", "Spain", "Japan", "Seychelles", "Albania",
  "Moldova", "Guatemala", "Bulgaria", "Paraguay", "Eritrea", "Sudan",
  "Equatorial Guinea", "Colombia", "Nigeria", "Montenegro", "Nepal", "Brunei",
  "Austria", "Bahamas", "United Kingdom", "Liberia", "Central African Republic",
  "Algeria", "Saint Lucia", "Romania", "United Arab Emirates", "Morocco",
  "Botswana", "Lithuania", "Cape Verde", "United States", "Australia", "Tonga",
  "Afghanistan", "Nauru", "Hungary", "Mauritania", "Slovenia", "Chad",
  "Vatican City", "Benin", "Singapore", "Malta", "Saint Vincent and the Grenadines",
  "Marshall Islands", "Thailand", "Liechtenstein", "Ireland", "Maldives", "Vietnam",
  "Armenia", "Pakistan", "Ivory Coast", "Russia", "Timor-Leste", "Nicaragua",
  "Papua New Guinea", "Egypt", "Jordan", "Uruguay", "Burkina Faso", "Cambodia",
  "Ethiopia", "Kiribati", "Bhutan", "Dominican Republic", "Suriname", "Bangladesh",
  "Barbados", "North Korea", "Belgium", "Palau", "Philippines", "Indonesia",
  "Dominica", "Rwanda", "Madagascar", "Samoa", "Antigua and Barbuda", "Sweden",
  "Mozambique", "Uzbekistan", "Ukraine", "Belize"
];

const MapLeft = () => {
  const [country, setCountry] = useState('Germany');
  const [threshold, setThreshold] = useState(32);
  const [speed, setSpeed] = useState(1);
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
              {countries.map(c => (
                <MenuItem key={c} value={c}>{c}</MenuItem>
              ))}
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