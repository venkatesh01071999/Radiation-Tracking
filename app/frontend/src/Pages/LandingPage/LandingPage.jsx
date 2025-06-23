import {
  Avatar,
  Box,
  Button,
  Card,
  CardContent,
  Container,
  TextField,
  Typography,
  InputAdornment,
} from '@mui/material';
import PersonOutlineIcon from '@mui/icons-material/PersonOutline';
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import configData from '../../config/config.json';
import { setConfiguration } from '../../services/api';
import { toast, ToastContainer } from 'react-toastify';


const LandingPage = () => {
  const [userName, setUserName] = useState('');
  const navigate = useNavigate();


  useEffect(()=>{
    const user_config = localStorage.getItem('userConfig');
    if(user_config){
      navigate('/map-view');
    }
  },[]) ;

  const storUserName = async() => {
    try{
        const config = JSON.parse(JSON.stringify(configData)); // deepcopy
        config['user'] = userName;
        const _ = await setConfiguration(config);
        localStorage.setItem('userConfig', JSON.stringify(config));
        navigate('/map-view');
    } catch (error) {
        toast.error('Failed to set user configuration', {
          position: "top-center",
          autoClose: 2000,
        });
    }
  }

  return (
    <Box
      sx={{
        height: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: '#f5f9ff', // white
      }}
    >
      <ToastContainer />
      <Container maxWidth="sm">
        <Card elevation={3} sx={{ borderRadius: 3 }}>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'center', mb: 2 }}>
               <Avatar alt='radiation' src='static/tracking.png' sx={{ bgcolor: '#e3f2fd', width: 56, height: 56 }} />
            </Box>

            <Typography variant="h5" align="center" fontWeight="bold">
              Radiation Tracking
            </Typography>
            <Typography variant="subtitle2" align="center" sx={{ mb: 3 }}>
              A comprehensive system to track the radiation around the world
            </Typography>

            <Typography variant="body2" sx={{ mb: 1, fontWeight: '500', fontSize: 16 }}>
              Username
            </Typography>
            <TextField
              fullWidth
              placeholder="Enter your username"
              variant="outlined"
              value={userName}
              required={true}
              onChange={(e)=> setUserName(e.target.value)}
              slotProps={{
                    input: {
                    startAdornment: (
                        <InputAdornment position="start">
                        <PersonOutlineIcon />
                        </InputAdornment>
                    ),
                    },
                }} // for user icon
              sx={{ mb: 3 }}
            />

            <Box sx={{ display:"flex", justifyContent: "center"}}>
                <Button variant="contained" size="large" disabled={!userName} onClick={storUserName}>
                Get Started
                </Button>
            </Box>
          </CardContent>
        </Card>
      </Container>
    </Box>
  );
};

export default LandingPage;