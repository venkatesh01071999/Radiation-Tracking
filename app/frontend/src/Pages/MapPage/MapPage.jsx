import {
    Box
} from '@mui/material';
import { ToastContainer, toast } from 'react-toastify';
import MapLeft from '../../components/MapLeft/MapLeft';
import MapRight from '../../components/MapRight/MapRight';
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { connectDataSocket, closeDataSocket, sendData, connectAggregateSocket, closeAggregateSocket } from '../../services/socket';
import { setConfiguration } from '../../services/api';


const MapPage = () => {
    const navigate  =useNavigate();
    const [config, setConfig] = useState({});
    const [loading, setLoading] = useState(true);
    const [socketDataMap, setSocketDataMap] = useState({});
    const [aggregateData, setAggregateData] = useState({});
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

                // ➕ Connect aggregate socket
                connectAggregateSocket(
                    set_config['user'],
                    (data) => {
                        setAggregateData(data);
                    },
                    () => {
                        toast('📊 Aggregate stream connected', {
                            position: "top-center",
                            autoClose: 2000
                        });
                    },
                    (e) => {
                        if(e.code != 1006){
                            toast('⚠️ Aggregate stream disconnected', {
                                position: "top-center",
                                autoClose: 2000
                            });
                        }
                    }
                );
            }
            return () => {
                closeDataSocket(); // cleanup when component unmounts
                 closeAggregateSocket(); // cleanup
            };
        }
    },[]);

    function toCsv(obj){
        const rows = Object.entries(obj).map(([key, vals]) => ({
            id: key,
            ...vals
        }));

        const headers = Object.keys(rows[0]);
        
        const esc = v =>
            `"${String(v).replace(/"/g, '""')}"`;

        const lines = [
            headers.map(esc).join(','),
            ...rows.map(r => headers.map(h => esc(r[h] ?? '')).join(','))
        ];

        return lines.join('\r\n');
    }
    
    const downloadDocument = () => {
        if(Object.keys(socketDataMap).length !== 0){  
            const csv = toCsv(socketDataMap);
            const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
            const url  = URL.createObjectURL(blob);
            // make temporary link
            const link = Object.assign(document.createElement('a'), {
                href: url,
                download: 'radiation.csv',
                style: 'display:none'
            });
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(url);
        }
    }

    const handleConfigSetting = async (data) => {
        try{
            const config = await setConfiguration(data);
            toast.success(config.message,{
                position: "top-center",
                autoClose: 2000
            });
            localStorage.setItem('userConfig', JSON.stringify(data));
            setConfig(data);     
        } catch (error) {
            toast.error(error.message,{
                position: "top-center",
                autoClose: 2000
            });
        }
    }

    const handleSpeedSetting = (speed) => {
        try{
            sendData({ 
                'speed': speed
             });
        } catch (error) {
            toast.error(error.message,{
                position: "top-center",
                autoClose: 2000
            });
        }
    };

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
                <MapLeft user_config={config} submitConfig={handleConfigSetting} speedConfig={handleSpeedSetting} aggregateData={aggregateData} download={downloadDocument}/>
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