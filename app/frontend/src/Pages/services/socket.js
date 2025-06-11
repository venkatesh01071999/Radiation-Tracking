let socket = null;
const SOCKET_URL = `ws://localhost:8000`;

export const connectDataSocket = (username, speed, onData, onOpen, onClose) => {
    socket = new WebSocket(`${SOCKET_URL}/data-stream?user=${username}&speed=${speed}`);

    socket.onopen = () => {
        onOpen(); //callback
    }

    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (!('type' in data)) {
            onData(data);
        }
    };

    socket.onclose = (e) => {
        onClose(e);
    }
};

export const closeDataSocket = () => {
    if (socket) {
        socket.close();
        socket = null;
    }
};