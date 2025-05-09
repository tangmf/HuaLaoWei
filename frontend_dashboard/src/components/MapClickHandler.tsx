// MapClickHandler.tsx
import { useEffect, useRef, useState } from 'react'
import { useMap } from 'react-leaflet'
import L from 'leaflet'
import { debounce } from 'lodash'
import { updateMarker } from '../utils/updateMarker'
import { highlightSubzone } from '../utils/highlightSubzone'
import * as turf from '@turf/turf'

interface Props {
  onMapClick: (lat: number, lng: number, result?: any) => void
  fetchWithAuth: (url: string) => Promise<any>
  markerRef: React.RefObject<L.Marker | null>
  highlightRef: React.RefObject<L.Layer | null>
  subzoneData: GeoJSON.FeatureCollection
  plnAreaData: GeoJSON.FeatureCollection
}

export default function MapClickHandler({ onMapClick, fetchWithAuth, markerRef, highlightRef, subzoneData, plnAreaData }: Props) {
  const [drawing, setDrawing] = useState(false)
  const map = useMap()
  const mountedRef = useRef(false)

  plnAreaData;

  const debouncedClick = useRef(
    debounce(async (lat: number, lng: number) => {
      const url = `https://www.onemap.gov.sg/api/public/revgeocode?location=${lat},${lng}&buffer=40&addressType=All&otherFeatures=N`
      try {
        const data = await fetchWithAuth(url)
        let result: any = {}

        if (data.GeocodeInfo?.length) {
          const info = data.GeocodeInfo[0]
          result = {
            BUILDING: info.BUILDINGNAME && info.BUILDINGNAME !== 'NIL'
              ? info.BUILDINGNAME
              : (info.ROAD && info.ROAD !== 'NIL' ? info.ROAD : 'Unknown Location'),
            ADDRESS: `${(info.BLOCK && info.BLOCK !== 'NIL') ? info.BLOCK : ''} ${(info.ROAD && info.ROAD !== 'NIL') ? info.ROAD : ''}`.trim(),
            POSTAL: info.POSTALCODE && info.POSTALCODE !== 'NIL' ? info.POSTALCODE : '',
            LATITUDE: lat.toString(),
            LONGITUDE: lng.toString(),
          }
        }

        // Find subzone
        const point = turf.point([lng, lat])
        const match = subzoneData.features.find(f => turf.booleanPointInPolygon(point, f as any))
        if (match) {
          const subzoneName = highlightSubzone(map, lat, lng, subzoneData, highlightRef) || match.properties?.SUBZONE_N || 'Unknown Subzone'
          const areaSqMeters = turf.area(match)
          const areaSqKm = +(areaSqMeters / 1_000_000).toFixed(3)

          result.SUBZONE = {
            NAME: subzoneName,
            AREA: areaSqKm,
          }
        }

        onMapClick(lat, lng, result)
        updateMarker(markerRef, map, lat, lng)
      } catch (err) {
        console.error('Reverse geocode failed:', err)
      }
    }, 200)
  ).current

  useEffect(() => {
    if (mountedRef.current) return
    mountedRef.current = true

    const handleClick = (e: L.LeafletMouseEvent) => {
      if (!drawing) {
        console.log('click handler triggered')
        debouncedClick(e.latlng.lat, e.latlng.lng)
      }
    }

    const start = () => setDrawing(true)
    const stop = () => setDrawing(false)

    map.on('click', handleClick)
    map.on('draw:drawstart', start)
    map.on('draw:drawstop', stop)
    map.on('draw:editstart', start)
    map.on('draw:editstop', stop)
    map.on('draw:deletestart', start)
    map.on('draw:deletestop', stop)

    return () => {
      map.off('click', handleClick)
      map.off('draw:drawstart', start)
      map.off('draw:drawstop', stop)
      map.off('draw:editstart', start)
      map.off('draw:editstop', stop)
      map.off('draw:deletestart', start)
      map.off('draw:deletestop', stop)
      mountedRef.current = false
    }
  }, [map, drawing, debouncedClick])

  return null
}