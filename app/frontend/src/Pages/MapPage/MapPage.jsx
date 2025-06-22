import {
    Box
} from '@mui/material';
import { ToastContainer, toast } from 'react-toastify';
import MapLeft from '../../components/MapLeft/MapLeft';
import MapRight from '../../components/MapRight/MapRight';
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { connectDataSocket, closeDataSocket } from '../../services/socket';
import { setConfiguration } from '../../services/api';


const MapPage = () => {
    const navigate  =useNavigate();
    const [config, setConfig] = useState({});
    const [loading, setLoading] = useState(true);
    const [socketDataMap, setSocketDataMap] = useState({});
    const zoom = 8;
    
    useEffect(()=>{
        const user_config = localStorage.getItem('userConfig');
        if(!user_config){
            navigate('/');
        } else {
            const set_config = JSON.parse(user_config)
            setConfig(set_config);
            setLoading(false);
            if('user' in set_config){
                connectDataSocket(
                    set_config['user'],
                    1,
                    (data) => {
                        setSocketDataMap(prevMap => {
                        const key = Object.keys(data)[0];
                        const timestamp = data[key]['timestamp']; // adjust to your format
                        const prev = prevMap[key];

                        if (!prev || prev['timestamp'] < timestamp) {
                            return {
                                ...prevMap,
                                [key]: data[key]
                            };
                        }
                        return prevMap;
                    });
                    },
                    () => {
                        // opened
                        toast('🙂Connected to server',{
                            position: "top-center",
                            autoClose: 2000
                        })
                    },
                    (e) => {
                        // closed
                        if(e.code != 1006){
                            toast('🥹Disconnected from server',{
                                position: "top-center",
                                autoClose: 2000
                            })
                        }
                    }
                );
            }
            return () => {
                closeDataSocket(); // cleanup when component unmounts
            };
        }
    },[]);

    const handleConfigSetting = async (data) => {
        try{
            console.log(data)
            const config = await setConfiguration(data);
            toast.success(config.message,{
                position: "top-center",
                autoClose: 2000
            });
            localStorage.setItem('userConfig', JSON.stringify(data));
        } catch (error) {
            console.log(error)
            toast.error(error.message,{
                position: "top-center",
                autoClose: 2000
            });
        }
    }

    return(
        <Box sx={{ height: '100vh', display: 'flex' }}>
            <ToastContainer />
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
                <MapLeft user_config={config} submitConfig={handleConfigSetting}/>
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
                        <MapRight centre={config['centre']} zoomLevel={zoom} dataStream={socketDataMap}/>
                    </Box>
                }
            </Box>
        
        </Box>
    )
}

export default MapPage