import React from 'react'
import { Marker, useMap } from 'react-leaflet'
import { divIcon, LatLngExpression } from 'leaflet'
import {
    FaBug, FaDog, FaSmoking, FaTree, FaWater, FaHardHat,
    FaShoppingCart, FaBicycle, FaExclamationCircle, FaToilet
} from 'react-icons/fa'
import ReactDOMServer from 'react-dom/server'
import { JSX } from 'react/jsx-runtime'

const severityGlow: Record<string, string> = {
    Low: 'rgba(0, 255, 0, 0.2)',
    Medium: 'rgba(255, 165, 0, 0.3)',
    High: 'rgba(255, 0, 0, 0.4)',
}

const severityCircle: Record<string, string> = {
    Low: 'rgba(0, 255, 0, 0.8)',
    Medium: 'rgba(255, 165, 0, 0.8)',
    High: 'rgba(255, 0, 0, 0.8)',
}

const issueIcons: Record<string, JSX.Element> = {
    "Pests": <FaBug />,
    "Animals & Bird": <FaDog />,
    "Smoking": <FaSmoking />,
    "Parks & Greenery": <FaTree />,
    "Drains & Sewers": <FaToilet />,
    "Drinking Water": <FaWater />,
    "Construction Sites": <FaHardHat />,
    "Abandoned Trolleys": <FaShoppingCart />,
    "Shared Bicycles": <FaBicycle />,
    "Others": <FaExclamationCircle />,
}

export default function LiveIssuesOverlay({ issues, opacity }: { issues: any[], opacity: number }) {
    return (
        <>
            {issues.map((issue, i) => {
                const iconEl = issueIcons[issue.issue_type] || issueIcons["Others"]
                const fillColor = severityCircle[issue.severity] || 'rgba(0,0,255,0.8)'
                const glowColor = severityGlow[issue.severity] || 'rgba(0,0,255,0.2)'

                // Glow circle behind
                const glowIcon = divIcon({
                    className: '',
                    html: `<div style="
                            width: 40px;
                            height: 40px;
                            border-radius: 50%;
                            background-color: ${glowColor};
                            filter: blur(8px);
                            opacity: ${opacity};
                        "></div>`,
                    iconSize: [40, 40],
                    iconAnchor: [20, 20],
                })

                // Foreground circle with white icon
                const fgIcon = divIcon({
                    className: '',
                    html: `<div style="
            width: 24px;
            height: 24px;
            border-radius: 50%;
            background-color: ${fillColor};
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 14px;
            opacity: 1;
          ">${ReactDOMServer.renderToString(iconEl)}</div>`,
                    iconSize: [24, 24],
                    iconAnchor: [12, 12],
                })

                const position: LatLngExpression = [issue.latitude, issue.longitude]

                return (
                    <React.Fragment key={i}>
                        <Marker position={position} icon={glowIcon} />
                        <Marker position={position} icon={fgIcon} />
                    </React.Fragment>
                )
            })}
        </>
    )
}
