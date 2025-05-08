import L from 'leaflet'

let lastLat: number | null = null
let lastLng: number | null = null

export function updateMarker(
    markerRef: React.RefObject<L.Marker | null>,
    map: L.Map | null,
    lat: number,
    lng: number
) {
    if (!map) {
        console.warn('Map is not ready yet.')
        return
    }

    if (lat === lastLat && lng === lastLng) {
        console.log('Same location, skipping marker update')
        return
    }

    lastLat = lat
    lastLng = lng

    console.log(markerRef)

    if (markerRef.current) {
        console.log('Removing marker')
        map.removeLayer(markerRef.current)
        markerRef.current = null
    }

    const marker = L.marker([lat, lng], {
        icon: L.divIcon({
            className: '',
            html: `
                <svg xmlns="http://www.w3.org/2000/svg" width="50" height="70" viewBox="0 -2 24 38">
                <defs>
                    <mask id="hole-mask">
                    <rect width="100%" height="100%" fill="white"/>
                    <circle cx="12" cy="9" r="3" fill="black"/>
                    </mask>
                </defs>
                
                <!-- Outline path -->
                <path d="M12 0C7.03 0 3 4.03 3 9c0 7.5 9 18 9 18s9-10.5 9-18c0-4.97-4.03-9-9-9z"
                        fill="none" stroke="#006C6A" stroke-width="2"/>
                
                <!-- Main shape with mask -->
                <path d="M12 0C7.03 0 3 4.03 3 9c0 7.5 9 18 9 18s9-10.5 9-18c0-4.97-4.03-9-9-9z"
                        fill="#00A7A5" mask="url(#hole-mask)"/>
                
                <!-- Optional outline around the hole -->
                <circle cx="12" cy="9" r="3" fill="none" stroke="#006C6A" stroke-width="1"/>
                
                </svg>
            `,
            iconSize: [60, 80],
            iconAnchor: [25, 55],
        }),
    });

    marker.addTo(map)
    markerRef.current = marker
    console.log('Added marker and updated markerRef:', markerRef.current)
}