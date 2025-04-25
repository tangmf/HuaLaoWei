import React, { useEffect, useState } from "react";
import type { FeatureCollection } from "geojson";

interface SidebarControlsProps {
  selectedIssue: string;
  setSelectedIssue: (issue: string) => void;
  activePOILayers: Record<string, boolean>;
  setActivePOILayers: React.Dispatch<React.SetStateAction<Record<string, boolean>>>;
  activeLineLayers: Record<string, boolean>;
  setActiveLineLayers: React.Dispatch<React.SetStateAction<Record<string, boolean>>>;
  forecastData?: FeatureCollection | null;
}

const SidebarControls: React.FC<SidebarControlsProps> = ({
  selectedIssue,
  setSelectedIssue,
  forecastData,
}) => {
  const [issueTypes, setIssueTypes] = useState<string[]>([]);

  useEffect(() => {
    if (forecastData) {
      const uniqueIssues = new Set<string>();
      forecastData.features.forEach((f) => {
        const issue = f?.properties?.issue_type;
        if (issue) uniqueIssues.add(issue);
      });
      setIssueTypes(["All", ...Array.from(uniqueIssues).sort()]);
    }
  }, [forecastData]);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold mb-2">Filter by Issue Type</h2>
        <select
          className="w-full p-2 border border-gray-300 rounded"
          value={selectedIssue}
          onChange={(e) => setSelectedIssue(e.target.value)}
        >
          {issueTypes.map((issue) => (
            <option key={issue} value={issue}>
              {issue}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
};

export default SidebarControls;
