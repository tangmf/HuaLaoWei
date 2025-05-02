import { useEffect, useState, useMemo } from 'react'
import Papa from 'papaparse'
import { Bar } from 'react-chartjs-2'
import React from 'react'
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    TooltipItem,
    Legend,
} from 'chart.js'
import { FaExpand, FaCompress } from 'react-icons/fa'
import CustomDropdown from './CustomDropdown'

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

interface Props {
    subzoneName: string | null
}

interface Row {
    Subzone: string
    Age: string
    Sex: string
    Population: string
}

const AgeHistogram = React.memo(function AgeHistogram({ subzoneName }: Props) {
    const [csvData, setCsvData] = useState<Row[]>([])
    const [sex, setSex] = useState<'Males' | 'Females' | 'Total'>('Total')
    const [expanded, setExpanded] = useState(false)

    useEffect(() => {
        const csvUrl = `${window.location.origin}/data/2024_SG_AgeData.csv`
        Papa.parse(csvUrl, {
            header: true,
            download: true,
            worker: true,
            dynamicTyping: true,
            complete: (result) => {
                const rows = (result.data as any[]).filter(
                    r => r && r.Subzone && r.Age !== undefined && r.Sex && r.Population !== undefined
                )
                setCsvData(rows)
            },
            error: (err) => {
                console.error('PapaParse error:', err)
            },
        })
    }, [])

    const { chartData, y1Max, y2Max } = useMemo(() => {
        if (!subzoneName || csvData.length === 0) return { chartData: null, y1Max: 0, y2Max: 0 }

        const ageSet = new Set<string>()
        const subzoneMap: Record<string, Record<string, Record<string, number>>> = {}

        for (const row of csvData) {
            const { Subzone, Age, Sex, Population } = row
            if (!Subzone || !Age || !Sex || !Population) continue
            ageSet.add(Age)
            const pop = parseInt(Population) || 0
            subzoneMap[Subzone] ??= {}
            subzoneMap[Subzone][Age] ??= {}
            subzoneMap[Subzone][Age][Sex] = pop
        }

        const allAges = Array.from(ageSet).sort((a, b) => +a - +b)
        const subzones = Object.keys(subzoneMap)

        const getPop = (data: any, age: string, sex: string) => {
            if (sex === 'Total') {
                return (data[age]?.['Males'] || 0) + (data[age]?.['Females'] || 0)
            }
            return data[age]?.[sex] || 0
        }

        const normalizedName = subzoneName?.trim().toLowerCase()
        const matchedKey = Object.keys(subzoneMap).find(
            key => key.trim().toLowerCase() === normalizedName
        )

        const subzoneData = matchedKey ? subzoneMap[matchedKey] : {}
        const subzonePop = allAges.map(age => getPop(subzoneData, age, sex))
        const totalPop = allAges.map(age => {
            return subzones.reduce((sum, sz) => {
                return sum + getPop(subzoneMap[sz], age, sex)
            }, 0)
        })

        const y1Max = Math.max(...subzonePop)
        const y2Max = Math.max(...totalPop)

        const chartData = {
            labels: allAges,
            datasets: [
                {
                    label: `${subzoneName.toLowerCase().split(' ').map(w => w[0].toUpperCase() + w.slice(1)).join(' ')} Population`,
                    data: subzonePop,
                    backgroundColor: 'rgba(0, 167, 165, 0.8)',
                    yAxisID: 'y1',
                    barPercentage: 1,
                    categoryPercentage: 1,
                    borderWidth: 1,
                    grouped: false,
                },
                {
                    label: 'Total Population',
                    data: totalPop,
                    backgroundColor: 'rgba(0, 0, 0, 0.2)',
                    yAxisID: 'y2',
                    barPercentage: 1,
                    categoryPercentage: 1,
                    borderWidth: 1,
                    grouped: false,
                },
            ],
        }

        return { chartData, y1Max, y2Max }
    }, [csvData, subzoneName, sex])

    const options = useMemo(() => ({
        responsive: true,
        layout: {
            padding: {
                top: 0,
                bottom: 0,
            },
        },
        interaction: {
            mode: 'index' as const,
            intersect: false,
        },
        plugins: {
            legend: {
                position: 'bottom' as const,
                align: 'start' as const,
                labels: {
                    font: { size: expanded ? 16 : 10 },
                    color: '#888',
                    boxWidth: 12,
                    padding: expanded ? 20 : 10,
                },
            },
            title: {
                display: true,
                text: 'Age Distribution',
                font: { size: expanded ? 20 : 14 },
                color: '#565656',
                padding: {
                    bottom: 30,
                },
            },
            tooltip: {
                callbacks: {
                    title: (tooltipItems: TooltipItem<'bar'>[]) => {
                        return `Age: ${tooltipItems[0].label}`
                    },
                    label: (tooltipItem: TooltipItem<'bar'>) => {
                        const label = tooltipItem.dataset.label || ''
                        const value = tooltipItem.formattedValue
                        return `${label}: ${value.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}`
                    },
                },
                titleFont: { size: expanded ? 14 : 12 },
                bodyFont: { size: expanded ? 12 : 11 },
                backgroundColor: 'rgba(0,0,0,0.8)',
                titleColor: '#fff',
                bodyColor: '#eee',
            }
        },
        scales: {
            y1: {
                type: 'linear' as const,
                position: 'left' as const,
                beginAtZero: true,
                max: y1Max,
                title: {
                    display: true,
                    text: 'Subzone Population',
                    font: { size: expanded ? 16 : 10 },
                    color: '#898989',
                    padding: expanded ? 20 : 6,
                },
                ticks: {
                    font: { size: expanded ? 16 : 8 },
                    color: '#dadada',
                },
                grid: {
                    drawOnChartArea: false,
                },
            },
            y2: {
                type: 'linear' as const,
                position: 'right' as const,
                beginAtZero: true,
                max: y2Max,
                title: {
                    display: true,
                    text: 'Total Population',
                    font: { size: expanded ? 16 : 10 },
                    color: '#898989',
                    padding: expanded ? 20 : 6,
                },
                ticks: {
                    font: { size: expanded ? 16 : 8 },
                    color: '#dadada',
                },
                grid: {
                    drawOnChartArea: false,
                },
            },
            x: {
                ticks: {
                    font: { size: expanded ? 16 : 8 },
                    color: '#dadada',
                    maxRotation: 0,
                    minRotation: 0,
                },
                grid: {
                    display: false,
                },
            },
        },
    }), [y1Max, y2Max, expanded])

    if (!chartData) return null

    return (
        <div className={`${expanded ? 'fixed inset-0 bg-white z-50 p-5' : 'w-full'} flex flex-col justify-around items-center`}>
            <div className="flex justify-between items-center mb-5 w-full max-w-6xl">
                <CustomDropdown
                    value={sex}
                    onChange={(val) => setSex(val as 'Males' | 'Females' | 'Total')}
                    options={['Total', 'Males', 'Females']}
                    placeholder="Select Sex"
                />
                <button
                    onClick={() => setExpanded(!expanded)}
                    className="h-8 flex items-center gap-2 px-3 text-sm text-[#485570] border border-[#485570] rounded hover:bg-[#4855701a]"
                >
                    {expanded ? (
                        <>
                            <FaCompress className="w-4 h-4" />
                            Minimise
                        </>
                    ) : (
                        <>
                            <FaExpand className="w-4 h-4" />
                            Expand
                        </>
                    )}
                </button>
            </div>
            <div className="w-full max-w-7xl flex flex-col items-center">
                <div className="w-full aspect-[2/1]">
                    <Bar
                        data={chartData}
                        options={{
                            ...options,
                            maintainAspectRatio: true,
                            scales: {
                                y1: {
                                    ...options.scales.y1,
                                    grid: { display: false },
                                },
                                y2: {
                                    ...options.scales.y2,
                                    grid: { display: false },
                                },
                                x: {
                                    ...options.scales.x,
                                    grid: { display: false },
                                },
                            },
                        }}
                    />
                </div>
                <p className="mt-1 text-xs text-[#c2c2c2] self-start">
                    All data and information are retrieved from{' '}
                    <a
                        href="https://www.singstat.gov.sg/find-data/search-by-theme/population/geographic-distribution/latest-data"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="underline text-[#a3b4d7]"
                    >
                        singstat.gov.sg
                    </a>
                </p>
            </div>
        </div>
    )
})

export default AgeHistogram;
