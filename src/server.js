const express = require('express');

const server = express();

server.all('/', (req, res) => {
    res.send('⚡ Chromo está online e operante!');
});

function keepAlive() {
    const port = process.env.PORT || 3000;
    server.listen(port, () => {
        console.log(`🌐 Servidor web rodando na porta ${port} (Render Keep-Alive)`);
    });
}

module.exports = keepAlive;