import React, { useRef, useEffect, useState } from "react";
import ForecastMap from "./components/ForecastMap/ForecastMap";
import MapSidebarControls from "./components/ForecastMap/MapSidebarControls";
import IssueBarChart from "./components/IssueChart/IssueBarChart";
import IssueTable from "./components/IssueTable/IssueTable";
import { pluginSettings } from "./config/pluginSettings";
import type { FeatureCollection } from "geojson";
import {
  Combobox,
  ComboboxInput,
  ComboboxButton,
  ComboboxOption,
  ComboboxOptions,
} from "@headlessui/react";
import {
  ChevronDownIcon,
  MapPinIcon,
  MagnifyingGlassIcon,
} from "@heroicons/react/24/outline";

function extractValueFromDescription(description: string, key: string): string | null {
  const parser = new DOMParser();
  const doc = parser.parseFromString(description, "text/html");
  const rows = doc.querySelectorAll("table tr");
  for (const row of rows) {
    const th = row.querySelector("th");
    const td = row.querySelector("td");
    if (th?.textContent?.trim() === key && td) return td.textContent?.trim() || null;
  }
  return null;
}

function toTitleCase(input: string): string {
  return input
    .toLowerCase()
    .split(" ")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

const Card: React.FC<{ id: string; title?: string; children: React.ReactNode }> = ({ id, title, children }) => {
  const [fullscreenCard, setFullscreenCard] = useState<string | null>(null);
  const isFullscreen = fullscreenCard === id;
  return (
    <div className={`relative group rounded transition-all duration-300 ${isFullscreen ? "left-0 w-full h-full z-50" : "relative h-full"}`}>
      {title && (
        <div className="p-2 border-b bg-[#3b3c3d] text-center text-white border-b-3 border-[#6f6f6f] z-10">
          <h2 className="text-lg font-semibold">{title}</h2>
        </div>
      )}
      <button
        onClick={() => setFullscreenCard(isFullscreen ? null : id)}
        className="absolute -top-2 -right-2 w-5 h-5 rounded-full border border-[#6f6f6f] bg-[#0b1017] flex items-center justify-center hover:bg-gray-50 z-20 opacity-0 group-hover:opacity-100 transition-opacity duration-200"
        title={isFullscreen ? "Minimise" : "Expand"}
      >
        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          {isFullscreen ? (
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 12h16" />
          ) : (
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8V4h4M20 8V4h-4M4 16v4h4M20 16v4h-4" />
          )}
        </svg>
      </button>
      <div className="py-2 px-1 overflow-auto h-full bg-[#1c1c1c]">{children}</div>
    </div>
  );
};

const App: React.FC = () => {
  const [selectedIssue, setSelectedIssue] = useState<string>("All");
  const [fullscreenCard, setFullscreenCard] = useState<string | null>(null);
  const [forecastData, setForecastData] = useState<FeatureCollection | null>(null);

  const [activePOILayers, setActivePOILayers] = useState(() => Object.fromEntries(pluginSettings.poiLayers.map(layer => [layer.key, layer.visibleByDefault ?? false])));
  const [activeLineLayers, setActiveLineLayers] = useState(() => Object.fromEntries(pluginSettings.lineLayers?.map(layer => [layer.key, layer.visibleByDefault ?? false]) || []));

  const [selectedBoundary, setSelectedBoundary] = useState<{ name: string } | null>(null);
  const [lastValidBoundary, setLastValidBoundary] = useState<{ name: string } | null>(null);
  const [query, setQuery] = useState<string>("");
  const [boundaryOptions, setBoundaryOptions] = useState<{ name: string }[]>([]);

  useEffect(() => {
    fetch(pluginSettings.forecast.geojsonPath)
      .then(res => res.json())
      .then(data => {
        setForecastData(data);
        const names = Array.from(
          new Set(
            data.features.map((f: any) => {
              const desc = f.properties?.Description;
              return typeof desc === "string" ? extractValueFromDescription(desc, "SUBZONE_N") : null;
            }).filter((name: any) => typeof name === "string")
          )
        ).map(name => ({ name: toTitleCase(name as string) }))
          .sort((a, b) => a.name.localeCompare(b.name));
        setBoundaryOptions(names);
      })
      .catch(err => console.error("Failed to load forecast data:", err));
  }, []);

  useEffect(() => {
    if (selectedBoundary === null && lastValidBoundary) setSelectedBoundary(lastValidBoundary);
  }, [selectedBoundary, lastValidBoundary]);

  const filteredBoundaries = boundaryOptions.filter(b => query.trim() === "" || b.name.toLowerCase().includes(query.toLowerCase()));

  return (
    <div className="h-screen w-screen flex flex-col bg-[#1c1c1c] overflow-hidden">
      <header className="w-full px-3 pt-3">
        <div className="flex items-center bg-[#1c1c1c] rounded-lg h-[72px]">
          <div
            className="flex items-center h-full w-[60%] bg-cover bg-center px-4"
            style={{
              backgroundImage: pluginSettings.banner.backgroundImage
                ? `url(${pluginSettings.banner.backgroundImage})`
                : undefined,
              backgroundColor: pluginSettings.banner.backgroundImage ? undefined : "#1f1f1f",
            }}
          >
            {pluginSettings.banner.logo && (
              <img src={pluginSettings.banner.logo} alt="Logo" className="w-13 h-13 mr-4" />
            )}

            <div className="text-white leading-tight">
              <h1 className="font-inter text-2xl font-semibold">{pluginSettings.banner.title}</h1>
              <p className="  text-sm opacity-80">{pluginSettings.banner.subtitle}</p>
            </div>
          </div>
          <div className="flex items-center space-x-6 pl-4 text-white">
            {/* Select a Boundary Dropdown */}
            <div className="h-full text-white relative w-75">
              <Combobox
                value={selectedBoundary}
                onChange={(value) => {
                  setSelectedBoundary(value);

                  if (value && boundaryOptions.find((b) => b.name === value.name)) {
                    setLastValidBoundary(value);
                    setQuery(""); // Clear input on valid selection
                  }
                }}
              >
                {({ open }) => {
                  // Clear input when dropdown closes
                  React.useEffect(() => {
                    if (!open) setQuery("");
                  }, [open]);

                  // Fix the ref typing by using HTMLInputElement
                  const inputRef = useRef<HTMLInputElement>(null);

                  const handleBoxClick = () => {
                    // Focus on the input when the box is clicked
                    if (inputRef.current) {
                      inputRef.current.focus();
                    }
                  };

                  return (
                    <div className="relative w-75">
                      {/* Clickable Box */}
                      <ComboboxButton
                        onClick={handleBoxClick} // Focus the input on click
                        className="w-full h-full cursor-pointer rounded-md bg-[#1c1c1c] px-4 py-2 flex items-center space-x-2"
                      >
                        <MapPinIcon className="h-8 w-8 mr-5 text-gray-300" />
                        <div className="flex flex-col text-left">
                          <span className="text-md font-semibold">Select a Boundary</span>
                          <span className="text-md text-gray-400 truncate">
                            {selectedBoundary?.name || "None"}
                          </span>
                        </div>
                        <ChevronDownIcon className="h-5 w-5 text-gray-400 ml-auto" />
                      </ComboboxButton>

                      {open && (
                        <div className="absolute right-0 z-50 mt-1 w-92 p-2 rounded-md bg-[#1a1a1a] text-sm shadow-lg overflow-hidden">
                          {/* Search input only appears when dropdown is open */}
                          <div className="px-2 py-1 mb-2 relative">
                            <ComboboxInput
                              ref={inputRef} // Reference for focusing
                              className="w-full py-2 pl-12 rounded bg-[#2a2a2a] text-white focus:outline-none focus:border-[#009af2] border-2 border-transparent"
                              placeholder="Search..."
                              onChange={(e) => setQuery(e.target.value)}
                            />
                            {/* Search Icon */}
                            <MagnifyingGlassIcon className="absolute left-6 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                          </div>

                          <ComboboxOptions className="max-h-130 pl-2 mr-2 overflow-auto rounded-md custom-scrollbar bg-[#1a1a1a]">
                            {filteredBoundaries.length > 0 ? (
                              filteredBoundaries.map((b) => (
                                <ComboboxOption
                                  key={b.name}
                                  value={b}
                                  className="group flex cursor-default items-center gap-2 rounded-md px-4 py-3 text-white text-md data-[focus]:bg-black"
                                >
                                  {/* Custom radio-style indicator */}
                                  <div className="relative w-4 h-4 mr-2">
                                    {/* Outer circle */}
                                    <div className="w-full h-full border-2 border-gray-400 rounded-full group-data-[selected]:border-[#009af2]" />

                                    {/* Inner dot */}
                                    <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
                                      <div className="w-2 h-2 bg-[#009af2] rounded-full opacity-0 group-data-[selected]:opacity-100 transition-all duration-150" />
                                    </div>
                                  </div>
                                  <span>{b.name}</span>
                                </ComboboxOption>
                              ))
                            ) : (
                              <div className="text-white px-3 py-2 text-md italic opacity-60">
                                No Matching Boundaries
                              </div>
                            )}
                          </ComboboxOptions>
                        </div>
                      )}
                    </div>
                  );
                }}
              </Combobox>
            </div>
            {/* Map View Icon + Label */}
            <div className="flex items-center space-x-2">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                strokeWidth={1.5}
                stroke="currentColor"
                className="w-6 h-6 text-white"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M3.75 4.5l16.5 0m-16.5 5.25h16.5m-16.5 5.25h16.5M3.75 20.25h16.5"
                />
              </svg>
              <span className="text-white font-medium">Map View</span>
            </div>

            {/* Toggle Buttons */}
            <div className="flex border border-blue-400 overflow-hidden">
              <button
                className="px-4 py-2 text-sm font-medium bg-blue-400 text-white"
                disabled={false}
              >
                Historical
              </button>
              <button
                className="px-4 py-2 text-sm font-medium text-blue-500 border-l border-blue-400 opacity-50 cursor-not-allowed"
                disabled
              >
                Live
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="p-3 flex flex-1 relative">
        {/* Fullscreen Card Overlay */}
        {fullscreenCard && (
          <div className="top-16 left-0 w-full h-full bg-[#1c1c1c]">
            {fullscreenCard === "map" && forecastData && (
              <div className="relative w-full h-full">
                <ForecastMap
                  forecastData={forecastData}
                  selectedIssue={selectedIssue}
                  activePOILayers={activePOILayers}
                  activeLineLayers={activeLineLayers}
                />
                <button
                  onClick={() => setFullscreenCard(null)}
                  className="absolute -top-2 -right-2 w-5 h-5 rounded-full border-1 border-[#6f6f6f] bg-[#0b1017] flex items-center justify-center hover:bg-gray-50 z-50"
                  title="Minimise"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className="h-4 w-4 text-gray-400"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 12h16" />
                  </svg>
                </button>

                <div className="absolute top-4 left-4 bg-white p-4 rounded shadow-md z-40">
                  <MapSidebarControls
                    activePOILayers={activePOILayers}
                    setActivePOILayers={setActivePOILayers}
                    activeLineLayers={activeLineLayers}
                    setActiveLineLayers={setActiveLineLayers}
                  />
                </div>
              </div>
            )}
            {fullscreenCard !== "map" && (
              <Card id={fullscreenCard} title={fullscreenCard}>
                <div className="text-gray-500 text-sm">--Content TBD--</div>
              </Card>
            )}
          </div>
        )}

        {/* Main Content */}
        {!fullscreenCard && (
          <>
            <div className="relative w-[30%] bg-[#3b3c3d] mr-3 flex flex-col">
              <Card id="table" title="Issue Count per Boundary">
                <div className="max-h-[calc(72vh)] overflow-y-auto custom-scrollbar pr-1">
                  <IssueTable />
                </div>
              </Card>
            </div>

            <div className="relative w-[25%] flex flex-col mx-2">
              <Card
                id="boundary"
                title={`Boundary Info for ${selectedBoundary?.name || "Admiralty"}`}
              >
                <div className="text-gray-500 text-sm">--Info TBD--</div>
              </Card>
              <Card id="tbd" title="TBD Section">
                <div className="text-gray-500 text-sm">--Content TBD--</div>
              </Card>
            </div>

            <div className="flex-1 flex flex-col relative ml-3">
              <div className="flex-1 relative">
                <div className="relative h-full bg-[#1c1c1c] group">
                  {forecastData && (
                    <ForecastMap
                      forecastData={forecastData}
                      selectedIssue={selectedIssue}
                      activePOILayers={activePOILayers}
                      activeLineLayers={activeLineLayers}
                    />
                  )}
                  <button
                    onClick={() => setFullscreenCard("map")}
                    className="absolute -top-2 -right-2 w-5 h-5 rounded-full border-1 border-[#6f6f6f] bg-[#0b1017] flex items-center justify-center hover:bg-gray-50 z-50 opacity-0 group-hover:opacity-100 transition-opacity"
                    title="Expand"
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      className="h-4 w-4 text-gray-400"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M4 8V4h4M20 8V4h-4M4 16v4h4M20 16v4h-4"
                      />
                    </svg>
                  </button>
                </div>
              </div>

              <div className="h-[2%]">
              </div>

              <div className="h-[40%]">
                <Card id="trends" title="Issue Trend">
                  <div className="h-full w-full">
                    <IssueBarChart />
                  </div>
                </Card>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default App;

