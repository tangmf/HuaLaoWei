import { useState, useLayoutEffect, useEffect, useRef, memo, useMemo } from 'react'
import { FaMapMarkerAlt, FaTimes, FaChevronUp, FaChevronDown, FaRegCalendarAlt } from 'react-icons/fa'
import { updateMarker } from '../utils/updateMarker'
import { highlightSubzone } from '../utils/highlightSubzone'
import * as turf from '@turf/turf'
import L from 'leaflet'
import Select from 'react-select';
import AgeHistogram from './AgeHistogram'
import IssueForecastGraph from './IssueForecastGraph'
import WeatherCard from './WeatherCard'
import ClosedIssuesTable from './ClosedIssuesTable';
import OpenIssuesTable from './OpenIssuesTable';
import WelcomePanel from './WelcomePanel';

// Date range picker
import { DateRange, Range as DateRangeObject } from 'react-date-range';
import { useFloating, offset, flip, shift, autoUpdate, type ReferenceType } from '@floating-ui/react';
import { addDays, parseISO } from 'date-fns';
import 'react-date-range/dist/styles.css';
import 'react-date-range/dist/theme/default.css';

const API_URL = 'https://www.onemap.gov.sg/api/common/elastic/search'

const TABS = ['Subzone Info', 'Past Issues', 'Live Issues'] as const
const SUBZONE_TABS = ['Socioeconomic Profile', 'Trends & Forecasting', 'TBC'] as const

const userTimeZone = Intl.DateTimeFormat().resolvedOptions().timeZone; // Auto-detects IANA time zone
const now = new Date();
const oneWeekAgo = addDays(now, -7);
const oneYearAgo = addDays(now, -365);

interface Props {
    info: any
    loading: boolean
    onSelectResult: (lat: number, lng: number, info: any) => void
    isFromMapRef: React.RefObject<boolean>
    map: L.Map
    markerRef: React.RefObject<L.Marker | null>
    highlightRef: React.RefObject<L.Layer | null>
    subzoneData: GeoJSON.FeatureCollection
    plnAreaData: GeoJSON.FeatureCollection
}

type IssuesClosedFilters = {
    from: string
    to: string
    types: string[]
    subtypes: string[]
    severity: string
}

type IssuesLiveFilters = {
    from: string
    to: string
    types: string[]
    subtypes: string[]
    severity: string
}

type OptionType = {
    value: string;
    label: string;
};

export default function SidebarInfo({ info, loading, onSelectResult, isFromMapRef, map, markerRef, highlightRef, subzoneData, plnAreaData }: Props) {
    const [query, setQuery] = useState('')
    const [results, setResults] = useState<any[]>([])
    const [searchLoading, setSearchLoading] = useState(false)
    const [selectedResult, setSelectedResult] = useState<any | null>(null)
    const [activeTab, setActiveTab] = useState<typeof TABS[number]>('Subzone Info')
    const [collapsed, setCollapsed] = useState(false)
    const [subzoneTab, setSubzoneTab] = useState<typeof SUBZONE_TABS[number]>('Socioeconomic Profile')
    const [displayValue, setDisplayValue] = useState('');
    const [subzoneName, setSubzoneName] = useState<string | null>(null)
    const [subzoneArea, setSubzoneArea] = useState<string | null>(null)

    const [closedIssues, setClosedIssues] = useState<any[]>([])
    const [issuesClosedFilters, setIssuesClosedFilters] = useState<IssuesClosedFilters>({
        from: '',
        to: '',
        types: [],
        subtypes: [],
        severity: ''
    })

    const [liveIssues, setLiveIssues] = useState<any[]>([]);
    const [issuesLiveFilters, setIssuesLiveFilters] = useState<IssuesLiveFilters>({
        from: '',
        to: '',
        types: [],
        subtypes: [],
        severity: ''
    });


    const [dateRange, setDateRange] = useState<{ start: Date; end: Date }>({
        start: oneYearAgo,
        end: now,
    });

    const contentRef = useRef<HTMLDivElement>(null)
    const isSelectingRef = useRef(false)

    const resetSidebar = () => {
        setSelectedResult(null);
        setDisplayValue('');
        setQuery('');
        setSubzoneName(null);
        setSubzoneArea(null);
    };

    useEffect(() => {
        if (!info || !map || !subzoneData) return

        const lat = parseFloat(info.LATITUDE)
        const lng = parseFloat(info.LONGITUDE)
        if (isNaN(lat) || isNaN(lng)) return

        const subzoneInfo = highlightSubzone(map, lat, lng, subzoneData, highlightRef);

        setSubzoneName(
            subzoneInfo?.NAME || info.SUBZONE?.NAME || null
        )
        setSubzoneArea(
            subzoneInfo?.AREA || info.SUBZONE?.AREA || null
        )
    }, [info, map, subzoneData])

    useEffect(() => {
        if (!subzoneName) return

        const params = new URLSearchParams({
            subzoneName,
            ...issuesClosedFilters.from && { from: issuesClosedFilters.from },
            ...issuesClosedFilters.to && { to: issuesClosedFilters.to },
            ...issuesClosedFilters.types.length && { types: issuesClosedFilters.types.join(',') },
            ...issuesClosedFilters.subtypes.length && { subtypes: issuesClosedFilters.subtypes.join(',') },
            ...issuesClosedFilters.severity && { severity: issuesClosedFilters.severity },
        })
        console.log(params.toString())
        fetch(`http://localhost:3001/api/issues/resolved?${params.toString()}`)
            .then(res => res.json())
            .then(setClosedIssues)
            .catch(console.error)
    }, [subzoneName, issuesClosedFilters])

    useEffect(() => {
        if (!subzoneName) return;

        const params = new URLSearchParams({
            subzoneName,
            ...issuesLiveFilters.from && { from: issuesLiveFilters.from },
            ...issuesLiveFilters.to && { to: issuesLiveFilters.to },
            ...issuesLiveFilters.types.length && { types: issuesLiveFilters.types.join(',') },
            ...issuesLiveFilters.subtypes.length && { subtypes: issuesLiveFilters.subtypes.join(',') },
            ...issuesLiveFilters.severity && { severity: issuesLiveFilters.severity },
        });

        fetch(`http://localhost:3001/api/issues/open?${params.toString()}`)
            .then(res => res.json())
            .then(setLiveIssues)
            .catch(console.error);
    }, [subzoneName, issuesLiveFilters]);


    useEffect(() => {
        if (!info || !map || !markerRef) return

        const lat = parseFloat(info.LATITUDE)
        const lng = parseFloat(info.LONGITUDE)

        if (!isNaN(lat) && !isNaN(lng)) {
            updateMarker(markerRef, map, lat, lng)
        }
    }, [info])

    useEffect(() => {
        if (info) {
            setSelectedResult(info);
            if (!isFromMapRef.current) {
                setDisplayValue(
                    info.BUILDING && info.BUILDING !== 'NIL'
                        ? info.BUILDING
                        : (info.ROAD_NAME && info.ROAD_NAME !== 'NIL' ? info.ROAD_NAME : info.ADDRESS));
            } else {
                setDisplayValue('');
            };
            setQuery('');
            isFromMapRef.current = false;
        } else {
            setDisplayValue('');
        }
    }, [info]);

    useEffect(() => {
        const el = contentRef.current
        if (!el) return
        el.style.transition = 'height 300ms ease'
        el.style.height = collapsed ? `${el.scrollHeight}px` : '0px'
        requestAnimationFrame(() => {
            el.style.height = collapsed ? '0px' : `${el.scrollHeight}px`
        })
    }, [collapsed])

    useEffect(() => {
        if (isSelectingRef.current) {
            isSelectingRef.current = false
            return
        }

        if (query.length < 3) {
            setResults([])
            setSearchLoading(false)
            return
        }

        const timer = setTimeout(() => {
            setSearchLoading(true)
            fetchResults(query).then(setResults).finally(() => setSearchLoading(false))
        }, 300)

        return () => clearTimeout(timer)
    }, [query])

    const fetchResults = async (query: string) => {
        const allResults: any[] = []
        for (let page = 1; page <= 3; page++) {
            const url = `${API_URL}?searchVal=${encodeURIComponent(query)}&returnGeom=Y&getAddrDetails=Y&pageNum=${page}`
            try {
                const res = await fetch(url)
                const data = await res.json()
                if (data.results?.length) allResults.push(...data.results)
                else break
            } catch {
                break
            }
        }
        return allResults
    }

    const handleSelect = (r: any) => {
        const lat = parseFloat(r.LATITUDE)
        const lng = parseFloat(r.LONGITUDE)
        onSelectResult(lat, lng, r)
        updateMarker(markerRef, map, lat, lng)
        setSelectedResult(r)
        setQuery('')
    }

    return (
        <div className="flex flex-col h-[100vh] min-h-0">
            <SearchBar
                query={query}
                setQuery={setQuery}
                displayValue={displayValue}
                setDisplayValue={setDisplayValue}
                clear={() => {
                    setDisplayValue('');
                    setQuery('');
                    setSelectedResult(null);
                }}
            />
            <div className="flex-1 flex flex-col overflow-x-hidden overflow-y-auto divide-y h-[100vh] min-h-0 custom-scrollbar">
                {displayValue.length > 0 && displayValue.length < 3 ? (
                    <div className="p-4 text-sm text-gray-500 italic">
                        Please enter 3 or more characters to start searching
                    </div>
                ) : query.length >= 3 ? (
                    searchLoading ? (
                        <LoadingList />
                    ) : results.length > 0 ? (
                        results.map((r, i) => (
                            <ResultItem key={i} result={r} onSelect={() => handleSelect(r)} />
                        ))
                    ) : (
                        <NoInfoMessage />
                    )
                ) : selectedResult ? (
                    loading ? (
                        <LoadingSkeleton />
                    ) : info && Object.keys(info).length > 0 ? (
                        <>
                            <LocationHeader result={selectedResult} subzoneName={subzoneName} onClear={resetSidebar} />
                            <TabSelector tabs={TABS} active={activeTab} setActive={setActiveTab} />
                            <CollapsibleSection
                                collapsed={collapsed}
                                setCollapsed={setCollapsed}
                                contentRef={contentRef}
                                activeTab={activeTab}
                                subzoneName={subzoneName}
                                selectedResult={selectedResult}
                            />
                            <TabContent
                                results={results}
                                activeTab={activeTab}
                                subzoneTab={subzoneTab}
                                setSubzoneTab={setSubzoneTab}
                                subzoneName={subzoneName}
                                closedIssues={closedIssues}
                                setIssuesClosedFilters={setIssuesClosedFilters}
                                liveIssues={liveIssues}
                                setIssuesLiveFilters={setIssuesLiveFilters}
                            />
                        </>
                    ) : (
                        <NoInfoMessage />
                    )
                ) : isFromMapRef.current && !info ? (
                    <NoInfoMessage />
                ) : (
                    <WelcomePanel />
                )}
            </div>
        </div>
    )
}

function SearchBar({
    query,
    setQuery,
    displayValue,
    setDisplayValue,
    clear,
}: {
    query: string;
    setQuery: (v: string) => void;
    displayValue: string;
    setDisplayValue: (v: string) => void;
    clear: () => void;
}) {
    return (
        <div className="flex items-center px-4 py-3 gap-2">
            <img src="/hualaowei.svg" alt="Logo" className="h-8 w-8 mr-2" />
            <input
                type="text"
                value={displayValue}
                onChange={e => {
                    const val = e.target.value;
                    setDisplayValue(val);
                    if (val.length >= 3) setQuery(val);
                    else setQuery('');
                }}
                placeholder="Search address..."
                className="flex-1 border-none outline-none text-xl"
            />
            {displayValue && (
                <button onClick={clear}>
                    <FaTimes className="text-gray-500 hover:text-red-500" />
                </button>
            )}
        </div>
    )
}

function ResultItem({ result, onSelect }: { result: any, onSelect: () => void }) {
    return (
        <div className="p-3 flex items-start gap-2 cursor-pointer hover:bg-gray-100 text-gray-700 border-gray-400" onClick={onSelect}>
            <FaMapMarkerAlt className="text-gray-400 mt-1 h-6 w-6" />
            <div>
                <div className="font-medium">
                    {result.BUILDING && result.BUILDING !== 'NIL'
                        ? result.BUILDING
                        : result.ROAD_NAME && result.ROAD_NAME !== 'NIL'
                            ? result.ROAD_NAME
                            : result.ADDRESS?.includes('NIL')
                                ? ''
                                : result.ADDRESS}
                </div>
                <div className="text-xs text-gray-500">{result.ADDRESS}</div>
            </div>
        </div>
    )
}

function LoadingList() {
    return (
        <div className="animate-pulse divide-y">
            {Array.from({ length: 10 }).map((_, i) => (
                <div key={i} className="p-3 flex items-start gap-2">
                    <FaMapMarkerAlt className="text-gray-300 mt-1 h-6 w-6" />
                    <div className="flex-1 space-y-2">
                        <div className="h-4 bg-gray-300 rounded w-3/4" />
                        <div className="h-3 bg-gray-200 rounded w-1/2" />
                    </div>
                </div>
            ))}
        </div>
    )
}

function LoadingSkeleton() {
    return (
        <div className="p-4 animate-pulse">
            <div className="h-4 bg-gray-300 rounded w-3/4 mb-2"></div>
            <div className="h-3 bg-gray-200 rounded w-1/2 mb-4"></div>
            <div className="flex justify-center mt-8">
                <div className="w-8 h-8 border-4 border-orange-400 border-t-transparent rounded-full animate-spin"></div>
            </div>
        </div>
    )
}

function NoInfoMessage() {
    return (
        <div className="p-4 text-sm text-gray-500 italic text-center">
            No Information Available
        </div>
    )
}

function LocationHeader({ result, subzoneName, onClear }: { result: any, subzoneName: any, onClear: () => void }) {
    return (
        <div className="relative flex-shrink-0 h-[20vh] p-4 flex flex-col justify-between border-t-6 border-t-[#00a7a5ff] border-b-gray-300">
            <div className="space-y-1">
                <div className="text-xl font-bold text-gray-700">
                    {result.BUILDING && result.BUILDING !== 'NIL'
                        ? result.BUILDING
                        : result.ROAD_NAME && result.ROAD_NAME !== 'NIL'
                            ? result.ROAD_NAME
                            : result.ADDRESS?.includes('NIL')
                                ? ''
                                : result.ADDRESS}
                </div>
                {result.ADDRESS && !result.ADDRESS.includes('NIL') && (
                    <div className="text-md text-gray-700">
                        {result.ADDRESS.split('SINGAPORE')[0].trim()}
                    </div>
                )}
                <div className="text-sm text-gray-500">
                    {result.POSTAL && result.POSTAL !== 'NIL' ? 'SINGAPORE ' + result.POSTAL : ''}
                </div>
            </div>
            <div className="text-sm text-gray-400">
                <strong>{subzoneName || result.SUBZONE?.NAME || 'Unknown'}</strong> SUBZONE
            </div>
            <div className="absolute top-[12%] right-[5%]">
                <button onClick={onClear}>
                    <FaTimes className="text-gray-400 hover:text-red-500 w-5 h-5" />
                </button>
            </div>
        </div>
    )
}

function TabSelector({
    tabs,
    active,
    setActive,
}: {
    tabs: readonly string[];
    active: string;
    setActive: (tab: any) => void;
}) {
    return (
        <div className="flex justify-around items-center px-5 pt-5 pb-5 text-sm font-medium bg-gray-100 border-none">
            {tabs.map((tab) => (
                <button
                    key={tab}
                    className={`flex-1 text-center px-4 py-2 ${active === tab ? 'text-white bg-[#00a7a5ff] rounded-sm' : 'text-gray-600'
                        }`}
                    onClick={() => setActive(tab)}
                >
                    {tab}
                </button>
            ))}
        </div>
    );
}

const CollapsibleSection = memo(function CollapsibleSection({
    collapsed,
    setCollapsed,
    contentRef,
    activeTab,
    subzoneName,
    selectedResult,
}: {
    collapsed: boolean;
    setCollapsed: (v: boolean) => void;
    contentRef: React.RefObject<HTMLDivElement | null>;
    activeTab: string;
    subzoneName: string | null;
    selectedResult: any | null;
}) {
    const innerRef = useRef<HTMLDivElement | null>(null);
    const hasMounted = useRef(false);

    // Set initial height before first paint
    useLayoutEffect(() => {
        const outer = contentRef.current;
        if (!outer) return;

        if (collapsed) {
            outer.style.height = '0px';
        } else if (innerRef.current) {
            outer.style.height = innerRef.current.offsetHeight + 'px';
        }
    }, []);

    // Animate height on collapse/expand after first mount
    useEffect(() => {
        const outer = contentRef.current;
        const inner = innerRef.current;
        if (!outer || !inner) return;

        if (!hasMounted.current) {
            hasMounted.current = true;
            return;
        }

        const startHeight = outer.offsetHeight;
        const endHeight = collapsed ? 0 : inner.offsetHeight;

        outer.style.height = `${startHeight}px`;
        // Force reflow
        outer.getBoundingClientRect();
        outer.style.transition = 'height 300ms ease-in-out';
        outer.style.height = `${endHeight}px`;

        const cleanup = () => {
            outer.style.transition = '';
            if (!collapsed) {
                outer.style.height = 'auto';
            }
        };

        outer.addEventListener('transitionend', cleanup, { once: true });

        return () => {
            outer.removeEventListener('transitionend', cleanup);
        };
    }, [collapsed]);


    const tabInfoText = useMemo(() => {
        switch (activeTab) {
            case 'Subzone Info':
                return (
                    <div className="text-sm text-gray-700 px-1 pb-10 h-[20vh]">
                        <WeatherCard
                            subzoneName={subzoneName}
                            lat={selectedResult ? parseFloat(selectedResult.LATITUDE) : null}
                            lng={selectedResult ? parseFloat(selectedResult.LONGITUDE) : null}
                        />
                    </div>
                );
            case 'Past Issues':
                return (
                    <div className="text-sm text-gray-400 pb-10 px-3 h-[20vh]">
                        The past issues shown below are based on historical reports collected in this area.
                    </div>
                );
            case 'Live Issues':
                return (
                    <div className="text-sm text-gray-400 pb-10 px-3 h-[20vh]">
                        Live issues are updated in real-time and reflect current reported problems.
                    </div>
                );
            default:
                return '';
        }
    }, [activeTab]);

    return (
        <div className="relative bg-gray-100 border-none">
            <div
                ref={contentRef}
                className="overflow-hidden transition-[height] duration-300 ease-in-out overflow-y-auto custom-subscrollbar"
                onTransitionEnd={() => {
                    if (!collapsed && contentRef.current) {
                        contentRef.current.style.height = 'auto';
                    }
                }}
            >
                <div className="text-xs text-gray-600 px-4 py-2">{tabInfoText}</div>
            </div>
            <div className="absolute left-1/2 -bottom-3 transform -translate-x-1/2 z-10">
                <button
                    className="bg-white border-gray-600 rounded-full p-1 shadow hover:bg-gray-200"
                    onClick={() => setCollapsed(!collapsed)}
                >
                    {collapsed ? (
                        <FaChevronDown className="text-gray-400 w-5 h-5" />
                    ) : (
                        <FaChevronUp className="text-gray-400 w-5 h-5" />
                    )}
                </button>
            </div>
        </div>
    );
});

function TabContent({
    results,
    activeTab,
    subzoneTab,
    subzoneName,
    setSubzoneTab,
    closedIssues,
    setIssuesClosedFilters,
    liveIssues,
    setIssuesLiveFilters,
}: {
    results: any,
    activeTab: string,
    subzoneTab: string,
    subzoneName: any,
    setSubzoneTab: (v: any) => void,
    closedIssues: any[],
    setIssuesClosedFilters: (f: any) => void,
    liveIssues: any[],
    setIssuesLiveFilters: (f: any) => void,
}) {
    const [closedFilters, setClosedFilters] = useState<IssuesClosedFilters>({
        from: '',
        to: '',
        types: [],
        subtypes: [],
        severity: ''
    });

    const [liveFilters, setLiveFilters] = useState<IssuesLiveFilters>({
        from: '',
        to: '',
        types: [],
        subtypes: [],
        severity: ''
    });

    const [calendarRange, setCalendarRange] = useState<DateRangeObject[]>([
        { startDate: oneWeekAgo, endDate: now, key: 'selection' }
    ]);
    const [showCalendar, setShowCalendar] = useState(false);
    const [pendingRange, setPendingRange] = useState<DateRangeObject[]>(calendarRange);

    const {
        x, y, strategy, refs: floatingRefs, update, floatingStyles,
    } = useFloating({
        placement: 'bottom-start',
        middleware: [offset(8), flip(), shift()],
        whileElementsMounted: autoUpdate,
    });
    const referenceRef = useRef<HTMLButtonElement | null>(null);

    const [issueTypes, setIssueTypes] = useState<any[]>([])

    const groupedIssueOptions = issueTypes.map((item: any) => ({
        label: item.category,
        options: [
            { label: `All ${item.category}`, value: item.category },
            ...item.subcategories.map((sub: string) => ({
                label: sub,
                value: sub,
            })),
        ],
    }));

    // Link the two refs
    useEffect(() => {
        floatingRefs.setReference(referenceRef.current);
    }, [referenceRef.current]);


    useEffect(() => {
        function handleClickOutside(event: MouseEvent) {
            if (
                floatingRefs.floating.current &&
                !floatingRefs.floating.current?.contains(event.target as Node) &&
                referenceRef.current &&
                !referenceRef.current?.contains(event.target as Node)
            ) {
                setShowCalendar(false);
            }
        }
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, [referenceRef, floatingRefs]);


    useEffect(() => {
        // Fetch issue categories and subcategories
        fetch('http://localhost:3001/api/meta/issue-types')
            .then(response => response.json())
            .then(data => {
                const formatted = Object.entries(data).map(([category, subcategories]) => ({
                    category,
                    subcategories
                }));
                setIssueTypes(formatted);
            })
            .catch(error => {
                console.error('Failed to fetch issue categories:', error);
            });
    }, []);


    if (activeTab === 'Subzone Info') {
        return (
            <div className="flex flex-col h-full pt-5">
                <div className="flex border-b border-gray-300 overflow-x-auto text-sm">
                    {SUBZONE_TABS.map(t => (
                        <button
                            key={t}
                            className={`px-4 py-2 whitespace-nowrap ${subzoneTab === t ? 'font-bold text-[#00a7a5] border-b-2 border-[#00a7a5]' : 'text-gray-600'}`}
                            onClick={() => setSubzoneTab(t)}
                        >
                            {t}
                        </button>
                    ))}
                </div>
                <div className="text-sm text-gray-700">
                    {activeTab === 'Subzone Info' && subzoneTab === 'Socioeconomic Profile' && (
                        <div className="p-4">
                            <AgeHistogram subzoneName={subzoneName || results.SUBZONE?.NAME || ''} />
                        </div>
                    )}

                    {activeTab === 'Subzone Info' && subzoneTab === 'Trends & Forecasting' && (
                        <div className="p-4">
                            <IssueForecastGraph subzoneName={subzoneName || results.SUBZONE?.NAME || ''} />
                        </div>
                    )}
                </div>
            </div>
        )
    }

    if (activeTab === 'Past Issues') {
        return (
            <div className="p-4 space-y-4">
                <div className="flex justify-between items-center mt-[3%] mb-[5%] flex-wrap gap-y-2">
                    {/* Left Group: Date picker + Severity */}
                    <div className="flex items-center gap-2">
                        {/* Date Range Picker */}
                        <div className="relative">
                            <button
                                ref={referenceRef}
                                onClick={() => {
                                    setPendingRange(calendarRange);
                                    setShowCalendar((prev) => !prev);
                                    update();
                                }}
                                className="flex items-center justify-between gap-2 w-fit bg-white border border-[#6a909eff] text-[#b2b2b2] rounded px-3 py-2 shadow-sm text-sm hover:border-[#95c3d3ff] hover:text-[#3f3f3f] cursor-pointer"
                            >
                                <span>
                                    {calendarRange[0].startDate?.toLocaleDateString("en-GB")} — {calendarRange[0].endDate?.toLocaleDateString("en-GB")}
                                </span>
                                <FaRegCalendarAlt className="text-base" />
                            </button>

                            {showCalendar && (
                                <div
                                    ref={floatingRefs.floating as React.RefObject<HTMLDivElement>}
                                    style={{ position: strategy, top: y ?? 0, left: x ?? 0, zIndex: 20 }}
                                    className="bg-white border shadow-lg rounded p-2 absolute"
                                >
                                    <DateRange
                                        ranges={pendingRange}
                                        onChange={(item) => {
                                            const { startDate, endDate } = item.selection || {};
                                            if (startDate && endDate) {
                                                setPendingRange([item.selection]);
                                            }
                                        }}
                                        months={1}
                                        direction="horizontal"
                                        moveRangeOnFirstSelection={false}
                                        rangeColors={['#00a7a5']}
                                        minDate={oneYearAgo}
                                        maxDate={now}
                                    />
                                    <div className="flex justify-end mt-2 mr-2">
                                        <button
                                            className="border border-[#00a7a5] text-[#00a7a5] px-4 py-1 rounded hover:bg-[#00a7a5] hover:text-white"
                                            onClick={() => {
                                                const selection = pendingRange[0];
                                                const { startDate, endDate } = selection ?? {};

                                                if (startDate && endDate) {
                                                    const adjustedEndDate = new Date(endDate.getTime() + (24 * 60 * 60 * 1000) - 1);

                                                    setCalendarRange([selection]);
                                                    setClosedFilters((prev) => ({
                                                        ...prev,
                                                        from: startDate.toLocaleDateString('en-CA'),
                                                        to: adjustedEndDate.toLocaleDateString('en-CA'),
                                                    }));
                                                    setShowCalendar(false);
                                                }
                                            }}
                                        >
                                            Confirm
                                        </button>
                                    </div>
                                </div>
                            )}
                        </div>

                        {/* Issue Type Multi-Select Dropdown */}
                        <div className="flex relative">
                            <Select<OptionType, true>
                                isMulti
                                options={groupedIssueOptions}
                                className="text-sm"
                                classNamePrefix="select"
                                placeholder="Select issue types..."
                                value={[
                                    ...closedFilters.types.map((t) => ({ value: t, label: `All ${t}` })),
                                    ...closedFilters.subtypes.map((s) => ({ value: s, label: s }))
                                ]}

                                onChange={(selectedOptions) => {
                                    const selected = selectedOptions as OptionType[];

                                    const selectedTypes = new Set<string>();
                                    const selectedSubtypes = new Set<string>();

                                    for (const opt of selected) {
                                        const isCategory = issueTypes.some((c) => c.category === opt.value);
                                        if (isCategory) {
                                            // Add the full category and all its subcategories
                                            const cat = issueTypes.find((c) => c.category === opt.value);
                                            if (cat) {
                                                selectedTypes.add(cat.category);
                                                cat.subcategories.forEach((sub: string) => selectedSubtypes.add(sub));
                                            }
                                        } else {
                                            // It's a subcategory – just add the subcategory
                                            selectedSubtypes.add(opt.value);
                                            // DO NOT add parent to types
                                        }
                                    }

                                    // Clean out subcategories that are under any selected category
                                    const cleanedSubtypes = Array.from(selectedSubtypes).filter((sub) => {
                                        return !issueTypes.some((cat) =>
                                            selectedTypes.has(cat.category) &&
                                            cat.subcategories.includes(sub)
                                        );
                                    });

                                    setClosedFilters((prev) => ({
                                        ...prev,
                                        types: Array.from(selectedTypes),
                                        subtypes: cleanedSubtypes,
                                    }));
                                }}


                                isOptionDisabled={(option: OptionType) => {
                                    const isSubcategory = issueTypes.some((cat) =>
                                        cat.subcategories.includes(option.value)
                                    );
                                    if (!isSubcategory) return false;

                                    return issueTypes.some(
                                        (cat) =>
                                            closedFilters.types.includes(cat.category) &&
                                            cat.subcategories.includes(option.value)
                                    );
                                }}

                                styles={{
                                    container: (base) => ({
                                        ...base,
                                        width: '12vw',
                                        minWidth: '12vw',
                                    }),
                                    control: (base) => ({
                                        ...base,
                                        whiteSpace: 'nowrap',
                                        overflow: 'hidden',
                                    }),
                                    valueContainer: (base) => ({
                                        ...base,
                                        maxHeight: '38px',
                                        overflow: 'hidden',
                                        flexWrap: 'nowrap',
                                    }),
                                    multiValue: (base) => ({
                                        ...base,
                                        maxWidth: '100%',
                                        overflow: 'hidden',
                                        textOverflow: 'ellipsis',
                                        whiteSpace: 'nowrap',
                                    }),
                                    multiValueLabel: (base) => ({
                                        ...base,
                                        overflow: 'hidden',
                                        textOverflow: 'ellipsis',
                                        whiteSpace: 'nowrap',
                                        maxWidth: '100px',
                                    }),
                                    menu: (base) => ({
                                        ...base,
                                        zIndex: 9999,
                                    }),
                                }}

                            />
                        </div>

                        {/* Severity Dropdown */}
                        <select
                            className="border border-[#6a909eff] text-[#b2b2b2] hover:border-[#95c3d3ff] hover:text-[#3f3f3f] cursor-pointer px-3 py-2 rounded text-sm"
                            value={closedFilters.severity}
                            onChange={(e) =>
                                setClosedFilters((prev: IssuesClosedFilters) => ({
                                    ...prev,
                                    severity: e.target.value,
                                }))
                            }
                        >
                            <option value="">All Severities</option>
                            <option value="Low">Low</option>
                            <option value="Medium">Medium</option>
                            <option value="High">High</option>
                        </select>
                    </div>

                    {/* Query Button aligned right */}
                    <div className="flex-shrink-0">
                        <button
                            className="border border-[#00a7a5ff] text-[#00a7a5ff] px-4 py-[7%] rounded hover:bg-[#00a7a5ff] hover:text-white cursor-pointer"
                            onClick={() => {
                                setIssuesClosedFilters(closedFilters);
                                console.log("Filters committed:", closedFilters);
                            }}
                        >
                            Query
                        </button>
                    </div>
                </div>
                <ClosedIssuesTable data={closedIssues} />
            </div>
        );
    }

    if (activeTab === 'Live Issues') {
        return (
            <div className="p-4 space-y-4">
                <div className="flex justify-between items-center mt-[3%] mb-[5%] flex-wrap gap-y-2">
                    {/* Left Group: Date picker + Severity */}
                    <div className="flex items-center gap-2">
                        {/* Date Range Picker */}
                        <div className="relative">
                            <button
                                ref={referenceRef}
                                onClick={() => {
                                    setPendingRange(calendarRange);
                                    setShowCalendar((prev) => !prev);
                                    update();
                                }}
                                className="flex items-center justify-between gap-2 w-fit bg-white border border-[#6a909eff] text-[#b2b2b2] rounded px-3 py-2 shadow-sm text-sm hover:border-[#95c3d3ff] hover:text-[#3f3f3f] cursor-pointer"
                            >
                                <span>
                                    {calendarRange[0].startDate?.toLocaleDateString("en-GB")} — {calendarRange[0].endDate?.toLocaleDateString("en-GB")}
                                </span>
                                <FaRegCalendarAlt className="text-base" />
                            </button>

                            {showCalendar && (
                                <div
                                    ref={floatingRefs.floating as React.RefObject<HTMLDivElement>}
                                    style={{ position: strategy, top: y ?? 0, left: x ?? 0, zIndex: 20 }}
                                    className="bg-white border shadow-lg rounded p-2 absolute"
                                >
                                    <DateRange
                                        ranges={pendingRange}
                                        onChange={(item) => {
                                            const { startDate, endDate } = item.selection || {};
                                            if (startDate && endDate) {
                                                setPendingRange([item.selection]);
                                            }
                                        }}
                                        months={1}
                                        direction="horizontal"
                                        moveRangeOnFirstSelection={false}
                                        rangeColors={['#00a7a5']}
                                        minDate={oneYearAgo}
                                        maxDate={now}
                                    />
                                    <div className="flex justify-end mt-2 mr-2">
                                        <button
                                            className="border border-[#00a7a5] text-[#00a7a5] px-4 py-1 rounded hover:bg-[#00a7a5] hover:text-white"
                                            onClick={() => {
                                                const selection = pendingRange[0];
                                                const { startDate, endDate } = selection ?? {};

                                                if (startDate && endDate) {
                                                    const adjustedEndDate = new Date(endDate.getTime() + (24 * 60 * 60 * 1000) - 1);

                                                    setCalendarRange([selection]);
                                                    setLiveFilters((prev) => ({
                                                        ...prev,
                                                        from: startDate.toLocaleDateString('en-CA'),
                                                        to: adjustedEndDate.toLocaleDateString('en-CA'),
                                                    }));
                                                    setShowCalendar(false);
                                                }
                                            }}
                                        >
                                            Confirm
                                        </button>
                                    </div>
                                </div>
                            )}
                        </div>

                        {/* Issue Type Multi-Select Dropdown */}
                        <div className="flex relative">
                            <Select<OptionType, true>
                                isMulti
                                options={groupedIssueOptions}
                                className="text-sm"
                                classNamePrefix="select"
                                placeholder="Select issue types..."
                                value={[
                                    ...liveFilters.types.map((t) => ({ value: t, label: `All ${t}` })),
                                    ...liveFilters.subtypes.map((s) => ({ value: s, label: s }))
                                ]}

                                onChange={(selectedOptions) => {
                                    const selected = selectedOptions as OptionType[];

                                    const selectedTypes = new Set<string>();
                                    const selectedSubtypes = new Set<string>();

                                    for (const opt of selected) {
                                        const isCategory = issueTypes.some((c) => c.category === opt.value);
                                        if (isCategory) {
                                            // Add the full category and all its subcategories
                                            const cat = issueTypes.find((c) => c.category === opt.value);
                                            if (cat) {
                                                selectedTypes.add(cat.category);
                                                cat.subcategories.forEach((sub: string) => selectedSubtypes.add(sub));
                                            }
                                        } else {
                                            // It's a subcategory – just add the subcategory
                                            selectedSubtypes.add(opt.value);
                                            // DO NOT add parent to types
                                        }
                                    }

                                    // Clean out subcategories that are under any selected category
                                    const cleanedSubtypes = Array.from(selectedSubtypes).filter((sub) => {
                                        return !issueTypes.some((cat) =>
                                            selectedTypes.has(cat.category) &&
                                            cat.subcategories.includes(sub)
                                        );
                                    });

                                    setLiveFilters((prev) => ({
                                        ...prev,
                                        types: Array.from(selectedTypes),
                                        subtypes: cleanedSubtypes,
                                    }));
                                }}


                                isOptionDisabled={(option: OptionType) => {
                                    const isSubcategory = issueTypes.some((cat) =>
                                        cat.subcategories.includes(option.value)
                                    );
                                    if (!isSubcategory) return false;

                                    return issueTypes.some(
                                        (cat) =>
                                            closedFilters.types.includes(cat.category) &&
                                            cat.subcategories.includes(option.value)
                                    );
                                }}

                                styles={{
                                    container: (base) => ({
                                        ...base,
                                        width: '12vw',
                                        minWidth: '12vw',
                                    }),
                                    control: (base) => ({
                                        ...base,
                                        whiteSpace: 'nowrap',
                                        overflow: 'hidden',
                                    }),
                                    valueContainer: (base) => ({
                                        ...base,
                                        maxHeight: '38px',
                                        overflow: 'hidden',
                                        flexWrap: 'nowrap',
                                    }),
                                    multiValue: (base) => ({
                                        ...base,
                                        maxWidth: '100%',
                                        overflow: 'hidden',
                                        textOverflow: 'ellipsis',
                                        whiteSpace: 'nowrap',
                                    }),
                                    multiValueLabel: (base) => ({
                                        ...base,
                                        overflow: 'hidden',
                                        textOverflow: 'ellipsis',
                                        whiteSpace: 'nowrap',
                                        maxWidth: '100px',
                                    }),
                                    menu: (base) => ({
                                        ...base,
                                        zIndex: 9999,
                                    }),
                                }}

                            />
                        </div>

                        {/* Severity Dropdown */}
                        <select
                            className="border border-[#6a909eff] text-[#b2b2b2] hover:border-[#95c3d3ff] hover:text-[#3f3f3f] cursor-pointer px-3 py-2 rounded text-sm"
                            value={liveFilters.severity}
                            onChange={(e) =>
                                setLiveFilters((prev: IssuesLiveFilters) => ({
                                    ...prev,
                                    severity: e.target.value,
                                }))
                            }
                        >
                            <option value="">All Severities</option>
                            <option value="Low">Low</option>
                            <option value="Medium">Medium</option>
                            <option value="High">High</option>
                        </select>
                    </div>

                    {/* Query Button aligned right */}
                    <div className="flex-shrink-0">
                        <button
                            className="border border-[#00a7a5ff] text-[#00a7a5ff] px-4 py-[7%] rounded hover:bg-[#00a7a5ff] hover:text-white cursor-pointer"
                            onClick={() => {
                                setIssuesLiveFilters(liveFilters);
                                console.log("Filters committed:", liveFilters);
                            }}
                        >
                            Query
                        </button>
                    </div>
                </div>
                <OpenIssuesTable data={liveIssues} />
            </div>
        );
    }

    return null
}