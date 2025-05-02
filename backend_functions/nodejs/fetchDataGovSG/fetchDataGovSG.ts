import fetch from 'node-fetch'
import { JSDOM } from 'jsdom'

const SEARCH_URL_BASE = 'https://data.gov.sg/datasets?formats=GEOJSON&sort=createdAt&page=1'
const METADATA_API = 'https://api-production.data.gov.sg/v2/public/api/datasets'
const DOWNLOAD_API = 'https://api-open.data.gov.sg/v1/public/api/datasets'

interface MetadataResponse {
    code: number
    data: {
        createdAt: string
    }
    errorMsg?: string
}

interface DownloadResponse {
    code: number
    data: {
        url: string
    }
    errMsg?: string
}

export async function fetchDataGovSG(query: string, outputName: string, ext: string = 'geojson'): Promise<{ filename: string; content: string } | null> {
    try {
        const searchUrl = `${SEARCH_URL_BASE}&query=${encodeURIComponent(query)}`
        const htmlRes = await fetch(searchUrl)
        const html = await htmlRes.text()
        const dom = new JSDOM(html)

        const anchor = dom.window.document.querySelector('a[href*="resultId"]')
        if (!anchor) throw new Error('No dataset result with resultId found.')

        const href = anchor.getAttribute('href')!
        const resultId = new URLSearchParams(href.split('?')[1]).get('resultId')
        if (!resultId) throw new Error('resultId not found in URL.')

        const metadataRes = await fetch(`${METADATA_API}/${resultId}/metadata`)
        const metadataJson = (await metadataRes.json()) as MetadataResponse
        if (metadataJson.code !== 1) throw new Error(metadataJson.errorMsg)

        const createdDate = new Date(metadataJson.data.createdAt)
        const dateStr = createdDate.toISOString().slice(0, 10).replace(/-/g, '') // yyyymmdd
        const filename = `${dateStr}_${outputName}.${ext}`

        const downloadRes = await fetch(`${DOWNLOAD_API}/${resultId}/poll-download`)
        const downloadJson = (await downloadRes.json()) as DownloadResponse
        if (downloadJson.code !== 0) throw new Error(downloadJson.errMsg)

        const fileRes = await fetch(downloadJson.data.url)
        const content = await fileRes.text()

        return { filename, content }
    } catch (err) {
        console.error('Error:', err)
        return null
    }
}