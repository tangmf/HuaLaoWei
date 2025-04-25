import React from "react";
import { pluginSettings } from "../../config/pluginSettings";

interface MapSidebarControlsProps {
  activePOILayers: Record<string, boolean>;
  setActivePOILayers: React.Dispatch<React.SetStateAction<Record<string, boolean>>>;
  activeLineLayers: Record<string, boolean>;
  setActiveLineLayers: React.Dispatch<React.SetStateAction<Record<string, boolean>>>;
}

const MapSidebarControls: React.FC<MapSidebarControlsProps> = ({
  activePOILayers,
  setActivePOILayers,
  activeLineLayers,
  setActiveLineLayers,
}) => {
  const handleTogglePOI = (key: string) => {
    setActivePOILayers((prev) => ({
      ...prev,
      [key]: !prev[key],
    }));
  };

  const handleToggleLine = (key: string) => {
    setActiveLineLayers((prev) => ({
      ...prev,
      [key]: !prev[key],
    }));
  };

  return (
    <div className="space-y-4 text-sm text-black w-64">
      {/* POI Layers */}
      <div>
        <h3 className="font-bold text-base mb-2">POI Layers</h3>
        <ul className="space-y-1">
          {pluginSettings.poiLayers.map((layer) => (
            <li key={layer.key} className="flex items-center">
              <input
                type="checkbox"
                checked={activePOILayers[layer.key]}
                onChange={() => handleTogglePOI(layer.key)}
                className="mr-2"
              />
              <label className="text-gray-500">{layer.name}</label>
            </li>
          ))}
        </ul>
      </div>

      {/* Line Layers */}
      <div>
        <h3 className="font-bold text-base mb-2">Line Layers</h3>
        <ul className="space-y-1">
          {pluginSettings.lineLayers.map((layer) => (
            <li key={layer.key} className="flex items-center">
              <input
                type="checkbox"
                checked={activeLineLayers[layer.key]}
                onChange={() => handleToggleLine(layer.key)}
                className="mr-2"
              />
              <label className="text-gray-500">{layer.name}</label>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default MapSidebarControls;
