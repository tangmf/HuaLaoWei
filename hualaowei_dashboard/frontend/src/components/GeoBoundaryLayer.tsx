import { useEffect } from 'react'
import { useMap } from 'react-leaflet'
import L from 'leaflet'

interface Props {
  data: GeoJSON.FeatureCollection
  color: string
  opacity: number
  enabled: boolean
  getTooltip?: (feature: GeoJSON.Feature) => string
}

export default function GeoBoundaryLayer({ data, color, opacity, enabled, getTooltip }: Props) {
  const map = useMap()

  useEffect(() => {
    const layer = L.geoJSON(data, {
      style: {
        color,
        weight: 2,
        opacity,
        fillOpacity: 0,
      },
      onEachFeature: (feature, layer) => {
        if (getTooltip) {
          layer.bindTooltip(getTooltip(feature))
        }
      },
    })

    if (enabled) {
      layer.addTo(map)
    }

    return () => {
      map.removeLayer(layer)
    }
  }, [map, data, color, opacity, enabled, getTooltip])

  return null
}