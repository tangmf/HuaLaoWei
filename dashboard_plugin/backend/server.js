require('dotenv').config();
const express = require('express');
const cors = require('cors');

const {
    initializePool
} = require('./db/pool');

const issuesRoutes = require('./routes/issues');
const metaRoutes = require('./routes/meta');
const forecastRoutes = require('./routes/forecast');
const subzoneRoutes = require('./routes/subzone');

async function startServer() {
    await initializePool();

    const app = express();
    app.use(cors());
    app.use(express.json());

    // Attach routers
    app.use('/api/issues', issuesRoutes);
    app.use('/api/meta', metaRoutes);
    app.use('/api/forecast', forecastRoutes);
    app.use('/api/subzone', subzoneRoutes);


    const port = process.env.PORT || 3001;
    app.listen(port, () => {
        console.log(`Server running at http://localhost:${port}`);
    });
}

startServer();