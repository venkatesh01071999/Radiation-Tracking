import {
    Box
} from '@mui/material';
import MapLeft from '../../components/MapLeft/MapLeft';
import MapRight from '../../components/MapRight/MapRight';
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';



const MapPage = () => {
    const navigate  =useNavigate();
    const [config, setConfig] = useState({});
    const [loading, setLoading] = useState(true);
    const zoom = 8;
    
    useEffect(()=>{
        const user_config = localStorage.getItem('userConfig');
        if(!user_config){
            navigate('/');
        } else {
            setConfig(JSON.parse(user_config));
        }
        setLoading(false);
    },[]);
    return(
        <Box sx={{ height: '100vh', display: 'flex' }}>
            <Box
                sx={{
                width: '350px',
                p: 2,
                bgcolor: '#f7f7f7',
                display: 'flex',
                flexDirection: 'column',
                gap: 2,
                borderRight: '1px solid #ddd',
                }}
            >
                <MapLeft/>
            </Box>
            <Box sx={{ flexGrow: 1 }}>
                {
                    loading ? 
                    <Box sx={{ 
                        height: '100vh', 
                        width: '100%',
                        display: 'flex',
                        justifyContent: 'center',
                        alignItems: 'center' 
                    }}>Loading...</Box> :
                    <Box sx={{ height: '100%', width: '100%', backgroundColor: '#f7f7f7' }}>
                        <MapRight centre={config['centre']} zoomLevel={zoom}/>
                    </Box>
                }
            </Box>
        
        </Box>
    )
}

export default MapPage