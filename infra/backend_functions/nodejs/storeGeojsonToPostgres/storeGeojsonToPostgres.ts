import { Client } from 'pg'
import { fetchDataGovSG } from '../fetchDataGovSG/fetchDataGovSG'

const PG_CONFIG = {
    user: 'your_user',
    host: 'localhost',
    database: 'your_db',
    password: 'your_password',
    port: 5432,
}

export async function storeGeojsonToPostgres(query: string, outputName: string) {
    const result = await fetchDataGovSG(query, outputName, 'geojson')
    if (!result) {
        console.error('Failed to fetch dataset')
        return
    }

    const geojson = JSON.parse(result.content)
    if (!geojson.features || !Array.isArray(geojson.features)) {
        console.error('Invalid GeoJSON format')
        return
    }

    const client = new Client(PG_CONFIG)
    await client.connect()

    await client.query(`
    CREATE TABLE IF NOT EXISTS geojson_data (
      id SERIAL PRIMARY KEY,
      filename TEXT,
      feature JSONB
    )
  `)

    const insertQuery = `INSERT INTO geojson_data (filename, feature) VALUES ($1, $2)`
    for (const feature of geojson.features) {
        await client.query(insertQuery, [result.filename, feature])
    }

    await client.end()
    console.log(`Inserted ${geojson.features.length} features into database.`)
}