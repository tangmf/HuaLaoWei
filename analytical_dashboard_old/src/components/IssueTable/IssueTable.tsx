import React, { useEffect, useState } from "react";
import type { FeatureCollection } from "geojson";

type BoundaryInfo = {
    name: string;
    count: number;
};

function extractValueFromDescription(description: string, key: string): string | null {
    const parser = new DOMParser();
    const doc = parser.parseFromString(description, "text/html");
    const rows = doc.querySelectorAll("table tr");

    for (const row of rows) {
        const th = row.querySelector("th");
        const td = row.querySelector("td");

        if (th && td && th.textContent?.trim() === key) {
            return td.textContent?.trim() || null;
        }
    }

    return null;
}

const IssueTable: React.FC = () => {
    const [boundaries, setBoundaries] = useState<BoundaryInfo[]>([]);

    useEffect(() => {
        const fetchGeoData = async () => {
            try {
                const res = await fetch("/assets/forecast_result.geojson");
                const data: FeatureCollection = await res.json();

                const countMap: Record<string, number> = {};

                for (const feature of data.features) {
                    const description = feature.properties?.Description;
                    const count = parseInt(feature.properties?.predicted_issue_count || "0");
                    const nameRaw = typeof description === "string" ? extractValueFromDescription(description, "SUBZONE_N") : null;

                    if (!nameRaw) continue;
                    const name = nameRaw.toLowerCase().replace(/\b\w/g, (l) => l.toUpperCase());

                    countMap[name] = (countMap[name] || 0) + count;
                }

                const result: BoundaryInfo[] = Object.entries(countMap).map(([name, count]) => ({
                    name,
                    count,
                }));

                setBoundaries(result.sort((a, b) => b.count - a.count));
            } catch (error) {
                console.error("Failed to load boundaries:", error);
            }
        };

        fetchGeoData();
    }, []);

    const renderMiniSVG = (name: string) => {
        const safeName = name.replace("/", "-");
        const url = `/svg_boundaries/${safeName}.svg`;
        return (
            <img
                src={url}
                alt={`${name} outline`}
                className="w-16 h-16 object-contain"
                onError={(e) => {
                    (e.target as HTMLImageElement).style.display = "none";
                }}
            />
        );
    };

    return (
        <div className="space-y-2">
            {boundaries.map((b, idx) => (
                <div
                    key={idx}
                    className="m-0 p-0 hover:bg-[#0d0d0d] border-y-1 border-[#4d4d4d] transition" // full-row highlightd
                >
                    <div className="py-3 px-2">
                        <div className="flex items-center justify-between bg-inherit shadow-[2px_2px_4px_rgba(0,0,0,0.8)] px-4 py-5">
                            <div className="text-white font-semibold w-1/3 truncate">{b.name}</div>
                            <div className="w-1/3 flex justify-center">{renderMiniSVG(b.name)}</div>
                            <div className="text-white font-bold w-1/3 text-right text-lg">{b.count}</div>
                        </div>
                    </div>
                </div>
            ))}
        </div>


    );
};

export default IssueTable;
