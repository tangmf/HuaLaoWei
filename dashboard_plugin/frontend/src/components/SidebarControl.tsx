import { useEffect, useState } from 'react'
import LayersPanel from './LayersPanel'
import { FaLayerGroup, FaMapMarkerAlt, FaListUl, FaTimes } from 'react-icons/fa'
import type { Layer } from './LayersPanel'

function getPanelIcon(panel: SidebarControlProps['activePanel']) {
    switch (panel) {
        case 'Layers':
            return <FaLayerGroup className="w-5 h-5" />
        // case 'Legend':
        //     return <FaMapMarkerAlt className="w-5 h-5" />
        // case 'Parameters':
        //     return <FaListUl className="w-5 h-5" />
        default:
            return null
    }
}

export interface SidebarControlProps {
    // activePanel: 'Layers' | 'Legend' | 'Parameters' | null
    activePanel: 'Layers' | null
    onClose: () => void
    layers: Layer[]
    setLayers: React.Dispatch<React.SetStateAction<Layer[]>>
}

export default function SidebarControl({ activePanel, onClose, layers, setLayers }: SidebarControlProps) {
    const [shouldRender, setShouldRender] = useState(false)
    const [isVisible, setIsVisible] = useState(false)

    useEffect(() => {
        if (activePanel) {
            setShouldRender(true)
            // Allow DOM to render before applying visible class
            setTimeout(() => setIsVisible(true), 10)
        } else {
            setIsVisible(false)
            const timeout = setTimeout(() => setShouldRender(false), 300)
            return () => clearTimeout(timeout)
        }
    }, [activePanel])

    if (!shouldRender) return null

    return (
        <div
            className={`fixed top-0 right-0 h-full w-[30%] bg-white shadow-lg z-40 flex flex-col transition-all duration-300 ease-in-out transform ${isVisible ? 'translate-x-0 opacity-100' : 'translate-x-full opacity-0'
                }`}
        >
            <div className="border-b border-gray-300">
                <div className="h-1 bg-red-600 w-full" />
                <div className="flex justify-between items-center px-4 py-3">
                    <div className="flex items-center gap-2 text-gray-700 font-semibold text-lg">
                        {getPanelIcon(activePanel)}
                        <span>{activePanel?.toUpperCase()}</span>
                    </div>
                    <button onClick={onClose}>
                        <FaTimes className="text-xl text-gray-600 hover:text-red-600" />
                    </button>
                </div>
            </div>
            <div className="flex-1 overflow-auto p-4">
                {activePanel === 'Layers' && <LayersPanel layers={layers} setLayers={setLayers} />}

            </div>
        </div>
    )
}