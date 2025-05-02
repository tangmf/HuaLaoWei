import { FaLayerGroup, FaMapMarkerAlt, FaListUl } from 'react-icons/fa'

interface LeftAlignedButtonsProps {
  activePanel: 'Layers' | 'Legend' | 'Parameters' | null
  onPanelSelect: (panel: 'Layers' | 'Legend' | 'Parameters' | null) => void
}

export default function LeftAlignedButtons({ activePanel, onPanelSelect }: LeftAlignedButtonsProps) {
  const buttons = [
    { label: 'Layers', icon: <FaLayerGroup /> },
    { label: 'Legend', icon: <FaListUl /> },
    { label: 'Parameters', icon: <FaMapMarkerAlt /> },
  ]

  return (
    <div className="flex flex-col gap-2">
      {buttons.map(({ label, icon }) => {
        const isActive = activePanel === label
        return (
          <button
            key={label}
            onClick={() => onPanelSelect(isActive ? null : (label as any))}
            className={`bg-white shadow px-3 py-2 rounded flex flex-col items-center transition-colors ${isActive ? 'bg-gray-100 text-red-500' : 'text-gray-700 hover:text-red-500 hover:bg-gray-100'
              }`}
          >
            <div className="text-xl">{icon}</div>
            <div className="text-xs mt-1">{label}</div>
          </button>
        )
      })}
    </div>
  )
}