let socket = null;
let aggregateSocket = null;
const SOCKET_URL = process.env.REACT_APP_SOCKET_URL;


// Connects to the data stream WebSocket

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
// Closes the data stream WebSocket
export const closeDataSocket = () => {
    if (socket) {
        socket.close();
        socket = null;
    }
};

// Connects to the aggregate stream WebSocket

export const connectAggregateSocket = (user, onMessage, onOpen, onClose) => {
    const url = `${SOCKET_URL}/aggregate-stream?user=${user}`;
    aggregateSocket = new WebSocket(url);

    aggregateSocket.onopen = onOpen;
    aggregateSocket.onclose = onClose;
    aggregateSocket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (!('type' in data)) {
            onMessage(data);
        }
    };
};

// Closes the aggregate stream WebSocket

export const closeAggregateSocket = () => {
    if (aggregateSocket) {
        aggregateSocket.close();
        aggregateSocket = null;
    }
};
