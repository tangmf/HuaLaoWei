import { useEffect, useState } from "react";

interface GeoJsonLayerConfig {
  key: string;
  file: string;
}

export const useGeoJsonLoader = (
  layers: GeoJsonLayerConfig[]
): Record<string, GeoJSON.FeatureCollection | undefined> => {
  const [geojsons, setGeojsons] = useState<Record<string, GeoJSON.FeatureCollection>>({});

  useEffect(() => {
    let cancelled = false;

    const loadGeojsons = async () => {
      const toLoad = layers.filter((layer) => !geojsons[layer.key]);
      const loaded: Record<string, GeoJSON.FeatureCollection> = {};

      await Promise.all(
        toLoad.map(async (layer) => {
          try {
            const res = await fetch(layer.file);
            const json = await res.json();
            loaded[layer.key] = json;
          } catch (err) {
            console.error(`Failed to load GeoJSON for ${layer.key}:`, err);
          }
        })
      );

      if (!cancelled) {
        setGeojsons((prev) => ({ ...prev, ...loaded }));
      }
    };

    loadGeojsons();

    return () => {
      cancelled = true;
    };
  }, [layers]);
  
  return geojsons;
};
