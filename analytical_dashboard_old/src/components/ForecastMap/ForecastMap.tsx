import React, { useEffect, useMemo, useState } from "react";
import DeckGL from "@deck.gl/react";
import Map from "react-map-gl/maplibre";
import { GeoJsonLayer, IconLayer, ScatterplotLayer } from "@deck.gl/layers";
import type { FeatureCollection } from "geojson";
import type { MapViewState } from "@deck.gl/core";
import { pluginSettings } from "../../config/pluginSettings";
import { useGeoJsonLoader } from "../../hooks/useGeoJsonLoader";
import throttle from "lodash.throttle";
import { FlyToInterpolator } from "@deck.gl/core";

interface ForecastMapProps {
  forecastData: FeatureCollection;
  selectedIssue: string;
  activePOILayers: Record<string, boolean>;
  activeLineLayers: Record<string, boolean>;
}

const ForecastMap: React.FC<ForecastMapProps> = ({
  forecastData,
  selectedIssue,
  activePOILayers,
  activeLineLayers,
}) => {
  const [viewState, setViewState] = useState<MapViewState>({
    latitude: 1.3521,
    longitude: 103.8198,
    zoom: 11,
    pitch: 30,
    bearing: 0,
    minZoom: 10,
    maxZoom: 18,
  });

  const handleZoom = (delta: number) => {
    setViewState((prev) => ({
      ...prev,
      zoom: Math.min(Math.max(prev.zoom + delta, 10), 18),
      transitionDuration: 500, // duration in ms
      transitionInterpolator: new FlyToInterpolator(),
    }));
  };

  const throttledSetViewState = useMemo(() => throttle(setViewState, 100), []);

  const [processedFeatures, setProcessedFeatures] = useState<any[]>([]);

  useEffect(() => {
    if (!forecastData) return;

    const counts = forecastData.features.map(f => f.properties?.predicted_issue_count || 0);
    const max = counts.length > 0 ? Math.max(...counts) : 0;

    const filtered = forecastData.features
      .filter(f => selectedIssue === "All" || f.properties?.issue_type === selectedIssue)
      .map(f => {
        const count = f.properties?.predicted_issue_count || 0;
        const scaled = max > 0 ? 255 - Math.floor((count / max) * 255) : 255;
        return {
          ...f,
          properties: {
            ...f.properties,
            scaled_color: scaled,
          },
        };
      });

    setProcessedFeatures(filtered);
  }, [forecastData, selectedIssue]);

  const forecastLayer = useMemo(() => {
    return new GeoJsonLayer({
      id: "forecast",
      data: {
        type: "FeatureCollection",
        features: processedFeatures,
      },
      pickable: true,
      getFillColor: (d: any) => [255, d.properties.scaled_color, 0, 180],
      updateTriggers: {
        getFillColor: selectedIssue,
      },
      getLineColor: [0, 0, 0, 30],
      lineWidthMinPixels: 1,
    });
  }, [processedFeatures]);

  // Load only active layers' geojson
  const activePoiConfigs = useMemo(() => pluginSettings.poiLayers.filter((l) => activePOILayers[l.key]), [activePOILayers]);
  const activeLineConfigs = useMemo(() => pluginSettings.lineLayers.filter((l) => activeLineLayers[l.key]), [activeLineLayers]);

  const geoJsonConfigs = useMemo(() => [...activePoiConfigs, ...activeLineConfigs], [activePOILayers, activeLineLayers]);
  const geojsons = useGeoJsonLoader(geoJsonConfigs);

  const poiLayers = useMemo(() => {
    return activePoiConfigs
      .map((layer) => {
        const data = geojsons[layer.key];
        if (!data) return null;

        if (layer.iconUrl) {
          return new IconLayer({
            id: `${layer.key}-icon`,
            data: data.features.map((f: any) => ({ ...f, icon: layer.iconUrl })),
            pickable: true,
            getIcon: (d: any) => ({
              url: d.icon,
              width: 128,
              height: 128,
              anchorY: 128,
            }),
            getPosition: (d: any) => d.geometry.coordinates,
            getSize: layer.iconSize || 3,
            sizeScale: 10,
          });
        }

        return new ScatterplotLayer({
          id: `${layer.key}-dot`,
          data: data.features,
          pickable: true,
          getPosition: (d: any) => d.geometry.coordinates,
          getFillColor: layer.color || [200, 200, 200, 180],
          getRadius: 80,
          radiusMinPixels: 3,
        });
      })
      .filter(Boolean);
  }, [activePoiConfigs, geojsons]);

  const lineLayers = useMemo(() => {
    return activeLineConfigs
      .map((layer) => {
        const data = geojsons[layer.key];
        if (!data) return null;
  
        return new GeoJsonLayer({
          id: `${layer.key}-line`,
          data,
          pickable: true,
          getLineColor: ((d: any) => {
            const hex = d?.properties?.color;
            if (hex) {
              const rgb = hex
                .replace("#", "")
                .match(/.{1,2}/g)
                ?.map((c: string) => parseInt(c, 16));
              if (rgb && rgb.length === 3) {
                return [...rgb, 255];
              }
            }
            return layer.color || [150, 150, 150, 255];
          }) as (d: any) => [number, number, number, number],
          getLineWidth: layer.width || 100,
          lineWidthMinPixels: 1,
        });
      })
      .filter(Boolean);
  }, [activeLineConfigs, geojsons]);
  
  return (
    <DeckGL
      viewState={viewState}
      onViewStateChange={({ viewState }) => throttledSetViewState(viewState as MapViewState)}
      controller={true}
      layers={[forecastLayer, ...lineLayers, ...poiLayers]}
      getTooltip={({ object }) => {
        if (!object) return null;
        if (object.properties?.predicted_issue_count !== undefined) {
          return `${object.properties.boundary_id} (${object.properties.issue_type}): ${object.properties.predicted_issue_count} issues`;
        }
        if (object.properties?.type === "line") {
          return `${object.properties.name} Line`;
        }
        return object.name || object.properties?.name || null;
      }}
    >
      <Map
        mapStyle="https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json"
        reuseMaps
        attributionControl={false}
      />

      <div className="absolute bottom-4 right-4 z-1150 flex flex-col rounded overflow-hidden shadow-md">
        <button
          className="bg-[#1a1a1a] text-white text-lg h-9 w-9 flex items-center justify-center border-b border-gray-600 hover:bg-[#2a2a2a]"
          onClick={() => handleZoom(1)}
        >
          +
        </button>
        <button
          className="bg-[#1a1a1a] text-white text-lg h-9 w-9 flex items-center justify-center hover:bg-[#2a2a2a]"
          onClick={() => handleZoom(-1)}
        >
          −
        </button>
      </div>
    </DeckGL>
  );
};

export default ForecastMap;
