export interface BaseLayerConfig {
  key: string;
  name: string;
  enabled: boolean;
  visibleByDefault: boolean;
  file: string;
}

export interface PoiLayerConfig extends BaseLayerConfig {
  iconUrl: string;
  color: [number, number, number, number];
  iconSize?: number;
}

export interface LineLayerConfig extends BaseLayerConfig {
  color: [number, number, number, number];
  width?: number;
}

export interface SocialStatusLayerConfig extends BaseLayerConfig {
  variable: string; // e.g., "income", "age", etc.
  colorRamp: string; // e.g., "Viridis", "Plasma"
}

export interface EnvironmentalLayerConfig extends BaseLayerConfig {
  variable: string; // e.g., "temperature"
  unit: string;     // e.g., "°C"
  colorRamp: string;
}

export const pluginSettings = {
  banner: {
    backgroundImage: "/assets/banner-bg.jpg", 
    logo: "/assets/logo.svg",                 
    title: "HuaLaoWei Analytical Dashboard",
    subtitle: "To identify key boundaries with high municipal issues",
  },

  forecast: {
    enable: true,
    geojsonPath: "/assets/forecast_result.geojson",
    showZeroPredictions: false,
    simplifyTolerance: 0.0005,
    defaultIssueType: "All",
    tooltip: true,
  },
  map: {
    center: [1.3521, 103.8198],
    zoom: 11,
    pitch: 30,
    basemapStyle: "https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json",
  },
  poiLayers: <PoiLayerConfig[]>[
    {
      key: "mrt",
      name: "MRT Stations",
      enabled: true,
      visibleByDefault: false,
      file: "/assets/pois/mrt.geojson",
      iconUrl: "",
      iconSize: 3,
      color: [255, 0, 0, 180],
    },
    {
      key: "hospital",
      name: "Hospitals",
      enabled: true,
      visibleByDefault: false,
      file: "/assets/pois/hospital.geojson",
      iconUrl: "",
      iconSize: 3,
      color: [255, 0, 0, 180],
    },
    {
      key: "hawker",
      name: "Hawker Centres",
      enabled: true,
      visibleByDefault: false,
      file: "/assets/pois/hawker.geojson",
      iconUrl: "",
      iconSize: 3,
      color: [255, 0, 0, 180],
    },
  ],
  lineLayers: <LineLayerConfig[]>[
    {
      key: "mrtLines",
      name: "MRT Lines",
      enabled: true,
      visibleByDefault: false,
      file: "/assets/lines/mrt.geojson",
      color: [3, 82, 159, 255], 
      width: 100,
    }
  ],
  socialStatusLayers: <SocialStatusLayerConfig[]>[],
  environmentalLayers: <EnvironmentalLayerConfig[]>[],
};
