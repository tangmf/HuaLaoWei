import * as turf from '@turf/turf'
import L from 'leaflet'

let lastLat: number | null = null
let lastLng: number | null = null

export function highlightSubzone(
    map: L.Map,
    lat: number,
    lng: number,
    subzoneData: GeoJSON.FeatureCollection,
    highlightRef: React.RefObject<L.Layer | null>
): { NAME: string; AREA: number } | null {
    if (!map || !subzoneData?.features?.length) return null

    if (lat === lastLat && lng === lastLng) {
        console.log('Same location, skipping subzone highlight')

        const point = turf.point([lng, lat])
        const match = subzoneData.features.find(f => turf.booleanPointInPolygon(point, f as any))

        if (!match) return null

        const desc = match.properties?.Description || ''
        const name = desc.match(/<th>SUBZONE_N<\/th>\s*<td>(.*?)<\/td>/i)
        const areaSqKm = +(turf.area(match) / 1_000_000).toFixed(3)

        return {
            NAME: name ? name[1] : 'Unknown Subzone',
            AREA: areaSqKm,
        }
    }

    lastLat = lat
    lastLng = lng

    const point = turf.point([lng, lat])
    const match = subzoneData.features.find(f => turf.booleanPointInPolygon(point, f as any))

    if (highlightRef.current) {
        map.removeLayer(highlightRef.current)
        highlightRef.current = null
    }

    if (match) {
        const layer = L.geoJSON(match, {
            style: {
                color: '#000',
                dashArray: '4 4',
                weight: 2,
                fillOpacity: 0,
            },
        }).addTo(map)

        highlightRef.current = layer
        const desc = match.properties?.Description || ''
        const name = desc.match(/<th>SUBZONE_N<\/th>\s*<td>(.*?)<\/td>/i)
        const areaSqKm = +(turf.area(match) / 1_000_000).toFixed(3)
        console.log(name ? name[1] : 'Unknown Subzone')
        console.log(areaSqKm)
        return {
            NAME: name ? name[1] : 'Unknown Subzone',
            AREA: areaSqKm,
        }
    }

    return null
}