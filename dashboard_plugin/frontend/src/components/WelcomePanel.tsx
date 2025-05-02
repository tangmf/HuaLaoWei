import { useEffect, useState } from 'react';
import { FaArrowRight } from 'react-icons/fa';

function WelcomePanel() {
    const [isNight, setIsNight] = useState(false);

    useEffect(() => {
        const hour = new Date().getHours();
        setIsNight(false);
        // setIsNight(hour < 6 || hour >= 18); // Night if before 6AM or after 6PM
    }, []);

    return (
        <div
            className="relative flex flex-col justify-between h-full w-full overflow-hidden text-gray-700"
            style={{
                background: isNight
                    ? 'linear-gradient(to bottom, #001f3f 0%, #001f3f 100%)' // Night sky
                    : 'linear-gradient(to bottom, #b3e0ff 0%, #e6f7ff 100%)', // Day sky
            }}
        >
            {/* Top Content */}
            <div className="flex flex-col items-start text-left px-10 pt-10 gap-4 z-10">
                {/* Logo */}
                <img
                    src="/images/dashboard-title.png"
                    alt="HuaLaoWei Dashboard Logo"
                    className="w-[48%] h-auto" // Adjust width to your preference
                />

                {/* Short description */}
                <p className="text-sm text-gray-600 max-w pl-2 pr-8">
                    With this dashboard, we aim to help Singapore to stay updated with the latest municipal issues in real-time. Beyond simple monitoring, it empowers users with advanced analytics capabilities — including trend analysis, forecasting of future municipal needs, and actionable insights. The platform also offers rich urban visualisations that map issues geographically, helping planners identify emerging patterns and proactively allocate resources.
                    With this tool, you can shift from reactive problem-solving to forward-thinking urban management, enhancing operational efficiency and the quality of life for residents.
                </p>

                {/* Start Tour Button */}
                <button
                    className="group mt-2 flex items-center gap-2 bg-gradient-to-r from-[#00a7a5] to-[#008a88] text-white font-semibold py-2 px-6 rounded-full shadow-md hover:shadow-lg hover:brightness-110 transition duration-300 cursor-pointer"
                >
                    Start Tour
                    <FaArrowRight className="text-white text-sm transform transition-transform duration-300 group-hover:translate-x-1.5" />
                </button>
            </div>

            {/* Skyline at bottom */}
            <div className="w-full absolute bottom-0 left-0 right-0">
                <img
                    src={
                        isNight
                            ? '/images/skyline_silhouette_sg_night.png'
                            : '/images/skyline_silhouette_sg.png'
                    }
                    alt="Skyline Silhouette"
                    className="w-full object-cover"
                />
            </div>
        </div>
    );
}

export default WelcomePanel;
