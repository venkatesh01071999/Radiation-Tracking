import { MapContainer, TileLayer, useMap } from 'react-leaflet';
import { useEffect } from 'react';
import 'leaflet/dist/leaflet.css';
import {
    Box
} from '@mui/material';

// to recentre map listenting to parent
const RecenterMap = ({ centre }) => {
    const map = useMap();

    useEffect(() => {
        if (centre) {
            map.setView(centre);
        }
    }, [centre, map]);

    return null;
};

const MapRight = ({centre, zoomLevel}) => {
    return(
        <Box sx={{width:'100%', height:'100%'}}>
            <MapContainer center={centre} zoom={zoomLevel} scrollWheelZoom={false} style={{ height: '100%', width: '100%' }}>
            <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            <RecenterMap centre={centre} />
            </MapContainer>
        </Box>
    )
}

export default MapRight