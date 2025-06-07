import {
    Box
} from '@mui/material';
import MapLeft from '../../components/MapLeft/MapLeft';
import MapRight from '../../components/MapRight/MapRight';


const MapPage = () => {
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
                <Box sx={{ height: '100%', width: '100%', backgroundColor: '#f7f7f7' }}>
                    <MapRight/>
                </Box>
            </Box>
        
        </Box>
    )
}

export default MapPage