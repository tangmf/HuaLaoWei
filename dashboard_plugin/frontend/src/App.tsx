// App.tsx
import { useState, useEffect, useRef } from 'react'
import MapView from './components/MapView'
import SidebarInfo from './components/SidebarInfo'
import SidebarControl from './components/SidebarControl'
import LeftAlignedButtons from './components/LeftAlignedButtons'
import { FaChevronLeft, FaChevronRight } from 'react-icons/fa'
import L from 'leaflet'
import { initialLayers } from './components/LayersPanel'

export default function App() {
  const mapRef = useRef<L.Map | null>(null)
  const markerRef = useRef<L.Marker | null>(null)
  const isFromMapRef = useRef(false)

  const highlightRef = useRef<L.Layer | null>(null)

  const [isSidebarOpen, setIsSidebarOpen] = useState(true)
  const [sidebarWidth, setSidebarWidth] = useState(isSidebarOpen ? window.innerWidth * 0.4 : 0)
  const [activePanel, setActivePanel] = useState<'Layers' | 'Legend' | 'Parameters' | null>(null)
  const [sidebarData, setSidebarData] = useState<any>(null)
  const [loadingInfo, setLoadingInfo] = useState(false)
  const [showContent, setShowContent] = useState(true)
  const [layers, setLayers] = useState(initialLayers)
  const [subzoneData, setSubzoneData] = useState<GeoJSON.FeatureCollection | null>(null)
  const [plnAreaData, setPlnAreaData] = useState<GeoJSON.FeatureCollection | null>(null)
  const [liveIssues, setLiveIssues] = useState<any[]>([])

  useEffect(() => {
    fetch('http://localhost:3001/api/issues/open')
      .then(res => res.json())
      .then(data => {
        setLiveIssues(data)
      })
      .catch(console.error)
  }, [])

  // Load GeoJSON on mount
  useEffect(() => {
    fetch('/data/2019_SG_Subzone.geojson').then(res => res.json()).then(setSubzoneData)
    fetch('/data/2019_SG_PlnArea.geojson').then(res => res.json()).then(setPlnAreaData)
  }, [])

  useEffect(() => {
    if (!isSidebarOpen) {
      const timeout = setTimeout(() => setShowContent(false), 300)
      return () => clearTimeout(timeout)
    } else {
      setShowContent(true)
    }
  }, [isSidebarOpen])

  useEffect(() => {
    const updateWidth = () => {
      const width = isSidebarOpen ? window.innerWidth * 0.4 : 0
      setSidebarWidth(width)
      document.documentElement.style.setProperty('--sidebar-width', `${width}px`)
    }

    window.addEventListener('resize', updateWidth)
    updateWidth()

    return () => window.removeEventListener('resize', updateWidth)
  }, [isSidebarOpen])

  useEffect(() => {
    document.documentElement.style.setProperty('--sidebar-width', `${sidebarWidth}px`)
  }, [sidebarWidth])

  const toggleButtonLeft = sidebarWidth

  const handleMapClick = (_lat: number, _lng: number, info?: any) => {
    isFromMapRef.current = true
    setLoadingInfo(true)
    setSidebarData(info)
    setTimeout(() => {
      setLoadingInfo(false)
    }, 300)
  }

  const handleSelectResult = (lat: number, lng: number, info: any) => {
    mapRef.current?.flyTo([lat, lng], 18)
    isFromMapRef.current = false
    setSidebarData(info)
  }

  const handleMapReady = (map: L.Map, _marker: React.RefObject<L.Marker | null>) => {
    mapRef.current = map
    // markerRef.current = marker.current
  }

  return (
    <div className="w-screen h-screen relative overflow-hidden">
      <MapView
        onMapClick={handleMapClick}
        onMapReady={handleMapReady}
        mapRef={mapRef}
        markerRef={markerRef}
        layers={layers}
        highlightRef={highlightRef}
        subzoneData={subzoneData!}
        plnAreaData={plnAreaData!}
        liveIssues={liveIssues}
      />

      <div
        className="absolute top-0 left-0 h-full bg-white shadow transition-all duration-300 overflow-hidden z-30"
        style={{ width: sidebarWidth }}
      >
        <div
          className={`transition-opacity duration-200 ${isSidebarOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'}`}
        >
          {showContent && (
            <SidebarInfo
              info={sidebarData}
              loading={loadingInfo}
              onSelectResult={handleSelectResult}
              isFromMapRef={isFromMapRef}
              map={mapRef.current!}
              markerRef={markerRef}
              highlightRef={highlightRef}
              subzoneData={subzoneData!}
              plnAreaData={plnAreaData!}
            />
          )}
        </div>
      </div>

      <button
        onClick={() => setIsSidebarOpen(prev => !prev)}
        className="fixed top-1/2 -translate-y-1/2 bg-gray-200 hover:bg-gray-300 p-2 rounded-l z-10 shadow transition-all duration-300 group"
        style={{ left: toggleButtonLeft }}
      >
        <span className="text-gray-700 group-hover:text-red-500">
          {isSidebarOpen ? <FaChevronLeft /> : <FaChevronRight />}
        </span>
      </button>

      <div
        className="absolute top-4 transition-all duration-300 z-20"
        style={{ left: sidebarWidth + 16 }}
      >
        <LeftAlignedButtons activePanel={activePanel} onPanelSelect={setActivePanel} />
      </div>

      <SidebarControl
        activePanel={activePanel === 'Layers' ? activePanel : null}
        onClose={() => setActivePanel(null)}
        layers={layers}
        setLayers={setLayers}
      />
    </div>
  )
}