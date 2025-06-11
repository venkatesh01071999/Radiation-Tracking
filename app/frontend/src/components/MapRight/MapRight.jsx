import { MapContainer, TileLayer, useMap, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import { useEffect } from 'react';
import 'leaflet/dist/leaflet.css';
import {
    Box
} from '@mui/material';

const greenIcon = new L.Icon({
  iconUrl: "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-green.png",
  iconSize: [25, 25],
  iconAnchor: [12, 25],
});

const redIcon = new L.Icon({
  iconUrl:  'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png',
  iconSize: [25, 25],
  iconAnchor: [12, 25],
});


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

const MapRight = ({centre, zoomLevel, dataStream}) => {
    return(
        <Box sx={{width:'100%', height:'100%'}}>
            <MapContainer center={centre} zoom={zoomLevel} scrollWheelZoom={false} style={{ height: '100%', width: '100%' }}>
            <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            <RecenterMap centre={centre} /> 
            {
                Object.entries(dataStream).map(([key, value]) => {
                    const position = [value['Latitude'], value['Longitude']];
                    const icon = value['status'] === 'green' ? greenIcon : redIcon;

                    return (
                        <Marker key={key} position={position} icon={icon}>
                            <Popup>
                                <strong>Value:</strong> {value['Value'].toString().concat(value['Unit'])}<br />
                                <strong>Captured Time:</strong> {value['Captured Time']}<br />
                                <strong>Latitude:</strong> {value['Latitude']}<br />
                                <strong>Longitude:</strong> {value['Longitude']}<br />
                            </Popup>
                        </Marker>
                    );
                })
            }
            </MapContainer>
        </Box>
    )
}

export default MapRight