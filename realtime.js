const express = require("express");
const http = require("http");
const { Server } = require("socket.io");

const app = express();
const server = http.createServer(app);
const io = new Server(server);

io.on("connection", (socket) => {
    console.log("A player connected!");

    socket.on("update", (data) => {
        io.emit("update", data);
    });

    socket.on("disconnect", () => {
        console.log("A player disconnected!");
    });
});

server.listen(3000, () => {
    console.log("Real-time server running on port 3000!");
});