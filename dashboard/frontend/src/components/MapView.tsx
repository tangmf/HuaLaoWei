// components/MapView.tsx
import { useEffect, useState, useRef } from 'react'
import { MapContainer, TileLayer, useMap } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet-draw'
import 'leaflet/dist/leaflet.css'
import 'leaflet-draw/dist/leaflet.draw.css'
import 'leaflet-geometryutil'
import MapClickHandler from './MapClickHandler'
import GeoBoundaryLayer from './GeoBoundaryLayer'
import type { Layer } from './LayersPanel'
import LiveIssuesOverlay from './LiveIssuesOverlay'

interface Props {
  onMapClick?: (lat: number, lng: number, result?: any) => void
  onMapReady?: (map: L.Map, markerRef: React.RefObject<L.Marker | null>) => void
  mapRef: React.RefObject<L.Map | null>
  markerRef: React.RefObject<L.Marker | null>
  layers: Layer[]
  highlightRef: React.RefObject<L.Layer | null>
  subzoneData: GeoJSON.FeatureCollection
  plnAreaData: GeoJSON.FeatureCollection
  liveIssues: any[];
}

function DrawControls() {
  const map = useMap()
  const drawnItemsRef = useRef<L.FeatureGroup>(new L.FeatureGroup())
  const drawControlRef = useRef<L.Control.Draw | null>(null)

  useEffect(() => {
    const originalReadableDistance = L.GeometryUtil.readableDistance as (
      distance: number,
      unit?: 'metric' | 'imperial'
    ) => string
    L.GeometryUtil.readableDistance = function (
      this: any,
      distance: any,
      unit?: 'metric' | 'imperial'
    ): string {
      const numericDistance = typeof distance === 'string' ? parseFloat(distance) : distance
      if (typeof numericDistance !== 'number' || isNaN(numericDistance)) {
        console.error('Invalid distance passed to readableDistance:', distance)
        return 'Invalid distance'
      }
      return originalReadableDistance.call(this, numericDistance, unit)
    } as typeof L.GeometryUtil.readableDistance
  }, [])

  useEffect(() => {
    if ((map as any).zoomControl) {
      map.removeControl((map as any).zoomControl)
    }
    const zoomControl = L.control.zoom({ position: 'bottomleft' })
    map.addControl(zoomControl)
    return () => {
      map.removeControl(zoomControl)
    }
  }, [map])

  useEffect(() => {
    const drawnItems = drawnItemsRef.current
    map.addLayer(drawnItems)

    const drawControl = new L.Control.Draw({
      position: 'bottomleft',
      draw: {
        polyline: { shapeOptions: { color: 'red' } },
        polygon: {
          allowIntersection: false,
          drawError: {
            color: '#e1e100',
            message: 'Polygon cannot intersect itself!',
          },
          shapeOptions: { color: 'blue' },
        },
        circle: { shapeOptions: { color: 'green' } },
        rectangle: false,
        marker: false,
        circlemarker: false,
      },
      edit: {
        featureGroup: drawnItems,
      },
    })

    drawControlRef.current = drawControl
    map.addControl(drawControl)

    map.on(L.Draw.Event.CREATED, (event: any) => {
      const layer = event.layer
      const layerType = event.layerType
      drawnItems.addLayer(layer)

      if (layerType === 'polyline') {
        let latlngs = layer.getLatLngs()
        if (Array.isArray(latlngs[0])) latlngs = latlngs.flat()
        let distance = 0
        for (let i = 0; i < latlngs.length - 1; i++) {
          distance += latlngs[i].distanceTo(latlngs[i + 1])
        }
        const readable = L.GeometryUtil.readableDistance(distance || 0, true)
        layer.bindTooltip(`Distance: ${readable}`).openTooltip()
      }

      if (layerType === 'polygon') {
        const latlngs = layer.getLatLngs()
        const area = L.GeometryUtil.geodesicArea(latlngs[0])
        if (!isNaN(area)) {
          const readable = `${(area / 1000000).toFixed(2)} km²`
          layer.bindTooltip(`Area: ${readable}`).openTooltip()
        }
      }

      if (layerType === 'circle') {
        const radius = layer.getRadius()
        const area = Math.PI * radius * radius
        const readable = `${(area / 1000000).toFixed(2)} km²`
        layer.bindTooltip(`Area: ${readable}`).openTooltip()
      }
    })

    return () => {
      if (drawControlRef.current) {
        map.removeControl(drawControlRef.current)
      }
    }
  }, [map])

  return null
}

export default function MapView({ onMapClick, onMapReady, mapRef, markerRef, layers, highlightRef, subzoneData, plnAreaData, liveIssues }: Props) {
  const authTokenRef = useRef('initial_token')

  const email = 'flemingsiow@gmail.com'
  const password = 'fyukiAmane03!'

  async function refreshToken() {
    const res = await fetch('https://www.onemap.gov.sg/api/auth/post/getToken', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    })
    const data = await res.json()
    if (data?.access_token) {
      authTokenRef.current = data.access_token
      return data.access_token
    } else {
      throw new Error('Token refresh failed')
    }
  }

  async function fetchWithAuth(url: string): Promise<any> {
    if (authTokenRef.current === 'initial_token') {
      await refreshToken()
    }

    const token = authTokenRef.current.trim()
    let res = await fetch(url, {
      headers: { Authorization: token },
    })

    if (res.status === 401) {
      await refreshToken()
      res = await fetch(url, {
        headers: { Authorization: authTokenRef.current.trim() },
      })
    }

    return res.json()
  }

  useEffect(() => {
    refreshToken().catch(err => console.error('Initial token fetch failed:', err))
  }, [])

  useEffect(() => {
    if (mapRef.current && onMapReady) {
      onMapReady(mapRef.current, markerRef)
    }
  }, [onMapReady])

  return (
    <MapContainer
      center={[1.3521, 103.8198]}
      zoom={12}
      zoomControl={false}
      className="w-full h-full z-0"
      ref={(node) => {
        if (node && !mapRef.current) {
          mapRef.current = node
          onMapReady?.(mapRef.current, markerRef)
        }
      }}
    >
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution="&copy; OpenStreetMap contributors"
      />

      <DrawControls />

      {subzoneData && subzoneData.features?.length > 0 && (
        <MapClickHandler
          onMapClick={onMapClick!}
          fetchWithAuth={fetchWithAuth}
          markerRef={markerRef}
          highlightRef={highlightRef}
          subzoneData={subzoneData}
          plnAreaData={plnAreaData}
        />
      )}

      {[...layers]
        .filter(l => l.type === 'boundary')
        .reverse()
        .map(layer => {
          if (layer.id === 'subzone' && subzoneData) {
            return (
              <GeoBoundaryLayer
                key={layer.id}
                data={subzoneData}
                color="#8c2834"
                opacity={layer.opacity ?? 0.5}
                enabled={layer.enabled}
                getTooltip={(feature) => {
                  const html = feature.properties?.Description || ''
                  const match = html.match(/<th>SUBZONE_N<\/th>\s*<td>(.*?)<\/td>/i)
                  return match ? match[1] : 'Unnamed'
                }}
              />
            )
          }

          if (layer.id === 'plnarea' && plnAreaData) {
            return (
              <GeoBoundaryLayer
                key={layer.id}
                data={plnAreaData}
                color="#485570ff"
                opacity={layer.opacity ?? 0.5}
                enabled={layer.enabled}
                getTooltip={(feature) => {
                  const html = feature.properties?.Description || ''
                  const match = html.match(/<th>PLN_AREA_N<\/th>\s*<td>(.*?)<\/td>/i)
                  return match ? match[1] : 'Unnamed'
                }}
              />
            )
          }

          return null
        })}

      {layers.find(l => l.id === 'live_issues')?.enabled && (
        <LiveIssuesOverlay
          issues={liveIssues}
          opacity={layers.find(l => l.id === 'live_issues')?.opacity ?? 0.5}
        />
      )}


    </MapContainer>
  )
}