import {
    DndContext,
    closestCenter,
    PointerSensor,
    useSensor,
    useSensors
} from '@dnd-kit/core'
import {
    arrayMove,
    SortableContext,
    useSortable,
    verticalListSortingStrategy
} from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import { Bars3Icon } from '@heroicons/react/24/outline'

export interface Layer {
    id: string
    name: string
    enabled: boolean
    type: 'basemap' | 'boundary' | 'overlay'
    opacity?: number
}

export const initialLayers: Layer[] = [
    { id: 'onemap', name: 'OneMap', enabled: false, type: 'basemap' },
    { id: 'mpaa', name: 'Master Plan Approved Amendments', enabled: false, type: 'basemap' },
    { id: 'landlot', name: 'Land Lot', enabled: false, type: 'basemap' },
    { id: 'plnarea', name: 'Planning Areas', enabled: false, type: 'boundary' },
    { id: 'subzone', name: 'Subzones', enabled: false, type: 'boundary' },
    { id: 'live_issues', name: 'Live Issues', enabled: false, type: 'overlay', opacity: 0.7 },
    { id: 'tree', name: 'NParks Tree Conservation Layer', enabled: false, type: 'overlay' },
    { id: 'heritage', name: 'NParks Heritage Trees', enabled: false, type: 'overlay' },
]

function SortableLayerItem({
    layer,
    onToggle,
    onOpacityChange,
}: {
    layer: Layer
    onToggle: (id: string) => void
    onOpacityChange: (id: string, value: number) => void
}) {
    const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({ id: layer.id })

    const style = {
        transform: CSS.Transform.toString(transform),
        transition,
        opacity: isDragging ? 0.5 : 1,
    }

    return (
        <div
            ref={setNodeRef}
            style={style}
            className="will-change-transform bg-white border-b border-gray-200 px-3 py-3 text-sm"
            {...attributes}
        >
            <div className="flex items-start gap-3">
                <Bars3Icon {...listeners} className="w-5 h-5 text-gray-500 cursor-grab mt-1" />
                <div className="flex-1">
                    <div className="flex justify-between items-center">
                        <span>{layer.name}</span>
                        <label className="relative inline-flex items-center cursor-pointer">
                            <input
                                type="checkbox"
                                checked={layer.enabled}
                                onChange={() => onToggle(layer.id)}
                                className="sr-only peer"
                            />
                            <div className="w-11 h-6 bg-gray-300 rounded-full peer-checked:bg-red-600 transition-all duration-200"></div>
                            <div className="absolute left-1 top-1 w-4 h-4 bg-white rounded-full transition-transform duration-200 transform peer-checked:translate-x-5"></div>
                        </label>
                    </div>
                    {layer.enabled && (
                        <div className="mt-2">
                            <span className="text-xs text-gray-400">Opacity</span>
                            <input
                                type="range"
                                min={0}
                                max={1}
                                step={0.05}
                                value={layer.opacity ?? 0.5}
                                onChange={(e) => onOpacityChange(layer.id, parseFloat(e.target.value))}
                                className="accent-red-600 mt-1 w-full"
                            />
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}

export default function LayersPanel({ layers, setLayers }: {
    layers: Layer[]
    setLayers: React.Dispatch<React.SetStateAction<Layer[]>>
}) {
    // const [layers, setLayers] = useState(initialLayers)
    const sensors = useSensors(useSensor(PointerSensor))

    const handleDragEnd = (event: any) => {
        const { active, over } = event
        if (!over || active.id === over.id) return

        setLayers(prev => {
            const activeLayer = prev.find(l => l.id === active.id)
            const overLayer = prev.find(l => l.id === over.id)
            if (!activeLayer || !overLayer) return prev

            // Only reorder if same type
            if (activeLayer.type !== overLayer.type) return prev

            // Get all layers of the same type
            const sameTypeLayers = prev.filter(l => l.type === activeLayer.type)

            const oldIndex = sameTypeLayers.findIndex(l => l.id === active.id)
            const newIndex = sameTypeLayers.findIndex(l => l.id === over.id)

            const reordered = arrayMove(sameTypeLayers, oldIndex, newIndex)

            // Reconstruct full layer list preserving order
            const result: Layer[] = []
            for (const l of prev) {
                if (l.type === activeLayer.type) {
                    result.push(reordered.shift()!)
                } else {
                    result.push(l)
                }
            }

            return result
        })
    }

    const toggleLayer = (id: string) => {
        setLayers(prev =>
            prev.map(layer =>
                layer.id === id ? { ...layer, enabled: !layer.enabled } : layer
            )
        )
    }

    const handleOpacityChange = (id: string, value: number) => {
        setLayers(prev =>
            prev.map(layer =>
                layer.id === id ? { ...layer, opacity: value } : layer
            )
        )
    }


    const basemaps = layers.filter(l => l.type === 'basemap')
    const boundaries = layers.filter(l => l.type === 'boundary')
    const overlays = layers.filter(l => l.type === 'overlay')

    return (
        <div className="flex flex-col h-full">
            <div className="bg-gray-100 px-4 py-2 font-semibold text-sm">BASEMAPS</div>
            <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
                <SortableContext items={basemaps.map(l => l.id)} strategy={verticalListSortingStrategy}>
                    {basemaps.map(layer => (
                        <SortableLayerItem
                            key={layer.id}
                            layer={layer}
                            onToggle={toggleLayer}
                            onOpacityChange={handleOpacityChange}
                        />
                    ))}
                </SortableContext>

                <div className="bg-gray-100 px-4 py-2 font-semibold text-sm mt-4">BOUNDARIES</div>
                <SortableContext items={boundaries.map(l => l.id)} strategy={verticalListSortingStrategy}>
                    {boundaries.map(layer => (
                        <SortableLayerItem
                            key={layer.id}
                            layer={layer}
                            onToggle={toggleLayer}
                            onOpacityChange={handleOpacityChange}
                        />
                    ))}
                </SortableContext>

                <div className="bg-gray-100 px-4 py-2 font-semibold text-sm mt-4">OVERLAYS</div>
                <SortableContext items={overlays.map(l => l.id)} strategy={verticalListSortingStrategy}>
                    {overlays.map(layer => (
                        <SortableLayerItem
                            key={layer.id}
                            layer={layer}
                            onToggle={toggleLayer}
                            onOpacityChange={handleOpacityChange}
                        />
                    ))}
                </SortableContext>
            </DndContext>
        </div>
    )
}