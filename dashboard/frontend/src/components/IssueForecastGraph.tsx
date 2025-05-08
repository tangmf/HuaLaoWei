import React, { useEffect, useRef, useMemo, useState } from 'react';
import {
    Chart as ChartJS,
    LineElement,
    PointElement,
    CategoryScale,
    LinearScale,
    Tooltip,
    Legend,
    TooltipItem,
} from 'chart.js';
import annotationPlugin from 'chartjs-plugin-annotation';
import { Line } from 'react-chartjs-2';
import { addDays, format } from 'date-fns';
import { FaExpand, FaCompress } from 'react-icons/fa';
import CustomDropdown from './CustomDropdown';
import { toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { TimeScale } from 'chart.js';
import 'chartjs-adapter-date-fns';   // important!

ChartJS.register(LineElement, PointElement, CategoryScale, LinearScale, Tooltip, Legend, annotationPlugin, TimeScale);

interface IssueForecastGraphProps {
    subzoneName: string | null;
}
interface DailyIssueDataPoint {
    report_date: string;
    issue_count: number;
}

const IssueForecastGraph: React.FC<IssueForecastGraphProps> = ({ subzoneName }) => {
    const [totalDailyData, setTotalDailyData] = useState<DailyIssueDataPoint[]>([]);
    const [issueTypes, setIssueTypes] = useState<string[]>([]);
    const [selectedType, setSelectedType] = useState<string>('');
    const [expanded, setExpanded] = useState(false);
    const [plottedData, setPlottedData] = useState<Record<string, { filtered: DailyIssueDataPoint[], forecast: DailyIssueDataPoint[] }>>({});
    const [isLoading, setIsLoading] = useState(false);

    const today = new Date();

    const chartRef = useRef<ChartJS<'line'>>(null);

    useEffect(() => {
        if (chartRef.current) {
            setTimeout(() => {
                chartRef.current?.resize();
            }, 50);
        }
    }, [expanded]);

    useEffect(() => {
        fetch('http://localhost:3001/api/meta/issue-types')
            .then(res => res.json())
            .then((data: Record<string, string[]>) => {
                const types = Object.keys(data);
                setIssueTypes(types);
            })
            .catch(console.error);
    }, []);

    useEffect(() => {
        if (!subzoneName) return;
        fetch(`http://localhost:3001/api/issues/daily-count?subzoneName=${subzoneName}`)
            .then(res => res.json())
            .then((data: DailyIssueDataPoint[]) => {
                setTotalDailyData(data);
            })
            .catch(console.error);
    }, [subzoneName]);

    const handlePlotAndForecast = async () => {
        if (!subzoneName || !selectedType) return;
        if (plottedData[selectedType]) return;

        setIsLoading(true); // Start loading

        try {
            const [dailyRes, forecastRes] = await Promise.all([
                fetch(`http://localhost:3001/api/issues/daily-count?subzoneName=${subzoneName}&issueTypeName=${encodeURIComponent(selectedType)}`),
                fetch(`http://localhost:3001/api/forecast/issues?subzoneName=${subzoneName}&issueTypeName=${encodeURIComponent(selectedType)}`)
            ]);
            const dailyData = await dailyRes.json();
            const forecastData = await forecastRes.json();

            setPlottedData(prev => ({
                ...prev,
                [selectedType]: {
                    filtered: dailyData,
                    forecast: forecastData.forecast?.map((p: any) => ({
                        report_date: p.forecastDate,
                        issue_count: p.forecast_value,
                    })),
                }
            }));

        } catch (error) {
            console.error(error);
        } finally {
            setIsLoading(false); // Stop loading
        }
    };

    const chartData = useMemo(() => {
        const allDates: string[] = [];
        for (let i = -20; i <= 6; i++) {
            const day = format(addDays(today, i), 'yyyy-MM-dd');
            allDates.push(day);
        }

        const forecastCut = allDates.indexOf(format(today, 'yyyy-MM-dd'));

        const totalGrouped: { [date: string]: number } = {};
        for (const d of totalDailyData) {
            totalGrouped[d.report_date] = (totalGrouped[d.report_date] || 0) + d.issue_count;
        }

        const currentFilteredData = plottedData[selectedType]?.filtered ?? [];
        const currentForecastData = plottedData[selectedType]?.forecast ?? [];

        const filteredGrouped: { [date: string]: number } = {};
        for (const d of currentFilteredData) {
            filteredGrouped[d.report_date] = (filteredGrouped[d.report_date] || 0) + d.issue_count;
        }

        const forecastGrouped: { [date: string]: number } = {};
        for (const d of currentForecastData) {
            forecastGrouped[d.report_date] = (forecastGrouped[d.report_date] || 0) + d.issue_count;
        }

        return {
            labels: allDates,
            datasets: [
                {
                    label: 'Total Issues',
                    data: allDates.map((date, idx) => idx <= forecastCut ? (totalGrouped[date] || 0) : null),
                    borderColor: 'rgba(0,0,0,0.2)',
                    borderWidth: 2,
                    pointRadius: 2,
                    fill: false,
                    yAxisID: 'y1',
                },
                ...(currentFilteredData.length > 0 ? [{
                    label: `${selectedType} Issues`,
                    data: allDates.map((date, idx) => idx <= forecastCut ? (filteredGrouped[date] || 0) : null),
                    borderColor: 'rgba(0, 167, 165, 1)',
                    borderWidth: 2,
                    pointRadius: 2,
                    fill: false,
                    yAxisID: 'y1',
                }] : []),
                ...(currentForecastData.length > 0 ? [{
                    label: `${selectedType} Forecast`,
                    data: allDates.map(date => forecastGrouped[date] || null),
                    borderColor: 'rgba(0, 167, 165, 1)',
                    borderWidth: 2,
                    borderDash: [6, 6],
                    pointRadius: 2,
                    fill: false,
                    yAxisID: 'y1',
                }] : []),
            ],
        };
    }, [totalDailyData, plottedData, selectedType]);

    const chartOptions = useMemo(() => ({
        responsive: true,
        plugins: {
            legend: {
                position: 'bottom' as const,
                align: 'start' as const,
                labels: {
                    usePointStyle: true,
                    pointStyle: 'line',
                    font: { size: expanded ? 16 : 10 },
                    color: '#888',
                    padding: expanded ? 20 : 10,
                },
            },
            tooltip: {
                callbacks: {
                    label: (context: TooltipItem<'line'>) => `Issues: ${context.raw}`,
                },
            },
            annotation: {
                annotations: {
                    todayLine: {
                        type: "line" as const,
                        xMin: format(today, 'yyyy-MM-dd'),
                        xMax: format(today, 'yyyy-MM-dd'),
                        borderColor: 'gray',
                        borderWidth: expanded ? 5 : 3,
                        label: {
                            display: true,
                            content: 'Today',
                            position: 'start' as const,
                            backgroundColor: 'rgba(0,0,0,0.7)',
                            color: 'white',
                            font: { size: expanded ? 18 : 10 },
                        },
                    },
                },
            },
        },
        scales: {
            y1: {
                type: "linear" as const,
                position: "left" as const,
                beginAtZero: true,
                ticks: { stepSize: 1, precision: 0 },
                title: { display: true, text: "Selected Issue Type Count" },
                grid: {
                    display: true,
                    color: "rgba(0, 0, 0, 0.05)",
                    borderDash: [3, 3],
                },
            },
            // y2: {
            //     type: "linear" as const,
            //     position: "right" as const,
            //     beginAtZero: true,
            //     ticks: { stepSize: 1, precision: 0 },
            //     title: { display: true, text: "Total Issues Count" },
            //     grid: { drawOnChartArea: false },
            // },
            x: {
                type: 'time' as const,
                time: {
                    unit: 'day' as const,
                    tooltipFormat: 'yyyy-MM-dd',
                },
                title: { display: true, text: 'Date' },
                ticks: { maxRotation: 45, autoSkip: true, maxTicksLimit: 14 },
                grid: {
                    display: true,
                    color: 'rgba(0, 0, 0, 0.05)',
                    borderDash: [3, 3],
                },
            },
        },
    }), [expanded]);

    return (
        <div className={`${expanded ? 'fixed inset-0 bg-white z-50 p-5' : 'w-full'} flex flex-col justify-around items-center`}>
            <div className="flex justify-between items-center mb-5 w-full max-w-6xl">
                <div className="flex gap-2 items-center">
                    <CustomDropdown
                        value={selectedType}
                        onChange={setSelectedType}
                        options={issueTypes}
                        placeholder="Select Issue Type"
                    />
                    <button
                        onClick={handlePlotAndForecast}
                        disabled={!selectedType || !!plottedData[selectedType]}
                        className={`h-8 flex items-center gap-2 px-3 text-sm ${selectedType && !plottedData[selectedType] ? 'bg-[#00a7a5] hover:bg-[#008b8a] text-white cursor-pointer' : 'bg-gray-300 text-gray-600'} rounded`}
                    >
                        Plot & Forecast
                    </button>
                </div>
                <button
                    onClick={() => setExpanded(!expanded)}
                    className="h-8 flex items-center gap-2 px-3 text-sm text-[#485570] border border-[#485570] rounded hover:bg-[#4855701a]"
                >
                    {expanded ? (<><FaCompress className="w-4 h-4" />Minimise</>) : (<><FaExpand className="w-4 h-4" />Expand</>)}
                </button>
            </div>
            <div className="w-full max-w-7xl flex flex-col items-center">
                <div className="w-full aspect-[2/1] relative">
                    {isLoading && (
                        <div className="absolute inset-0 bg-white bg-opacity-70 flex items-center justify-center z-10">
                            <div className="border-4 border-[#00a7a5] border-t-transparent rounded-full w-12 h-12 animate-spin"></div>
                        </div>
                    )}
                    <Line
                        key={expanded ? 'expanded' : 'normal'}
                        ref={chartRef}
                        data={chartData}
                        options={{
                            ...chartOptions,
                            maintainAspectRatio: true,

                        }}
                    />
                </div>
            </div>
        </div>
    );
};

export default IssueForecastGraph;