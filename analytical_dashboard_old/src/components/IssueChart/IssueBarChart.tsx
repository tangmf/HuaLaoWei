import React, { useEffect, useState } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import { csv } from "d3-fetch";
import { timeFormat, timeParse } from "d3-time-format";

const dateFormat = "%Y-%m-%d";
const parseDate = timeParse(dateFormat);
const formatDate = timeFormat("%d %b");

const IssueBarChart = () => {
    const [data, setData] = useState<any[]>([]);
    const [selectedType, setSelectedType] = useState<string>("All");
    const [issueTypes, setIssueTypes] = useState<string[]>([]);

    const sortedData = [...data].sort((a, b) =>
        new Date(a.date).getTime() - new Date(b.date).getTime()
    );

    useEffect(() => {
        csv("/assets/mock_municipal_issues.csv").then((rows) => {
            const parsed = rows.map((row: any) => ({
                date: parseDate(row.datetime.slice(0, 10)),
                type: row.type,
            })).filter((d) => d.date);

            const cutoff = new Date();
            cutoff.setDate(cutoff.getDate() - 60);

            const filtered = parsed.filter((d) => d.date != null && d.date >= cutoff);

            const grouped: Record<string, number> = {};
            filtered.forEach((d) => {
                if (selectedType === "All" || d.type === selectedType) {
                    const key = formatDate(d.date!);
                    grouped[key] = (grouped[key] || 0) + 1;
                }
            });

            const chartData = Object.entries(grouped).map(([date, count]) => ({
                date,
                count,
            })).sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());

            setData(chartData);
            setIssueTypes(["All", ...Array.from(new Set(parsed.map((d) => d.type)))]);
        });
    }, [selectedType]);

    return (
        <div className="w-full h-full py-1 bg-[#1c1c1c] rounded text-white">
            {sortedData.length === 0 ? (
                <div className="text-sm text-gray-400 p-4">Loading chart data...</div>
            ) : (
                <ResponsiveContainer width="100%" height="80%">
                    <BarChart data={sortedData} margin={{ top: 20, bottom: 40 }} barCategoryGap="5%">
                        <CartesianGrid 
                            strokeDasharray="3 0" 
                            stroke="#292828" 
                            vertical={true}            
                            horizontal={true}  
                        />
                        <XAxis
                            interval={6}
                            dataKey="date"
                            dy={10}
                            tick={{ fontSize: 12, textAnchor: "middle", fill: "#f2f1ed" }}
                        />
                        <YAxis
                            width={27}
                            dx={-10}
                            tickFormatter={(val) => `${val}`}
                            tickCount={4}
                            tick={{ fontSize: 12, textAnchor: "middle", fill: "#f2f1ed" }}
                        />
                        <Tooltip contentStyle={{ backgroundColor: "#333", borderColor: "#555", color: "#fff" }} />
                        <Bar dataKey="count" fill="#f2f1ed" />
                    </BarChart>
                </ResponsiveContainer>
            )}
        </div>
    );
};

export default IssueBarChart;
