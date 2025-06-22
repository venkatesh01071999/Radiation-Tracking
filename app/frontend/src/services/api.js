export const getBoundingBox = async (country) => {
    const OSM_URL = process.env.REACT_APP_OSM_URL;
    try{
        const response = await fetch(`${OSM_URL}/search?country=${country}&format=json`);
        if (!response.ok) {
            throw new Error('Failed to fetch bounding box');
        }
        const data = await response.json();
        return data;
    } catch (error) {
        throw error;
    }
}

export const setConfiguration = async(config) => {
    const API_URL = process.env.REACT_APP_API_URL;
    try {
        const response = await fetch(`${API_URL}/set-config`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(config)
        });
        if (!response.ok) {
            throw new Error('Failed to set configuration');
        }
        return await response.json();
    } catch (error) {
        throw error;
    }
}