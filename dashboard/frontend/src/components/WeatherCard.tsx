import { useEffect, useMemo, useState } from 'react';
import { format } from 'date-fns';
import { WiCloud, WiDaySunny, WiNightClear, WiDayCloudy, WiNightAltCloudy, WiRain, WiThunderstorm, WiFog } from 'react-icons/wi';

export default function WeatherCard({ subzoneName, lat, lng }: { subzoneName: string | null, lat: number | null, lng: number | null }) {
    const [weatherData, setWeatherData] = useState<any>(null);

    const now = new Date();
    const isDay = weatherData ? weatherData.current.is_day === 1 : (now.getHours() >= 6 && now.getHours() < 18);
    const formattedDate = useMemo(() => format(now, 'EEE, dd MMM yyyy'), [now]);

    useEffect(() => {
        if (lat == null || lng == null) return;

        const fetchWeather = async () => {
            try {
                const res = await fetch(`https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lng}&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max,precipitation_sum,cloud_cover_mean,weather_code&current=temperature_2m,is_day,relative_humidity_2m,rain,precipitation,wind_speed_10m,wind_direction_10m,cloud_cover,weather_code&timezone=auto&forecast_days=3`);
                const data = await res.json();
                setWeatherData(data);
            } catch (error) {
                console.error('Failed to fetch weather:', error);
            }
        };

        fetchWeather();
    }, [lat, lng]);

    const current = weatherData?.current;
    const tomorrow = weatherData?.daily ? {
        tempMin: weatherData.daily.temperature_2m_min[1],
        tempMax: weatherData.daily.temperature_2m_max[1],
        weatherCode: weatherData.daily.weather_code[1]
    } : null;
    const iconSize = 50;

    const getWeatherIcon = (code: number | null, isDaytime: boolean) => {
        if (code == null) return <WiCloud size={iconSize} />;
        if (code === 0) return isDaytime ? <WiDaySunny size={iconSize} /> : <WiNightClear size={iconSize} />;
        if ([1, 2, 3].includes(code)) return isDaytime ? <WiDayCloudy size={iconSize} /> : <WiNightAltCloudy size={iconSize} />;
        if ([45, 48].includes(code)) return <WiFog size={iconSize} />;
        if ([51, 53, 55, 61, 63, 65, 80, 81, 82].includes(code)) return <WiRain size={iconSize} />;
        if ([95, 96, 99].includes(code)) return <WiThunderstorm size={iconSize} />;
        return <WiCloud size={iconSize} />;
    };

    const forecastText = (code: number | null) => {
        if (code == null) return 'Unknown';
        if (code === 0) return 'Clear';
        if ([1, 2, 3].includes(code)) return 'Partly Cloudy';
        if ([45, 48].includes(code)) return 'Fog';
        if ([51, 53, 55].includes(code)) return 'Drizzle';
        if ([61, 63, 65].includes(code)) return 'Rain';
        if ([80, 81, 82].includes(code)) return 'Rain Showers';
        if ([95, 96, 99].includes(code)) return 'Thunderstorm';
        return 'Cloudy';
    };

    const getCompassDirection = (degree: number): string => {
        if (degree >= 348.75 || degree < 11.25) return 'N';
        if (degree >= 11.25 && degree < 33.75) return 'NNE';
        if (degree >= 33.75 && degree < 56.25) return 'NE';
        if (degree >= 56.25 && degree < 78.75) return 'ENE';
        if (degree >= 78.75 && degree < 101.25) return 'E';
        if (degree >= 101.25 && degree < 123.75) return 'ESE';
        if (degree >= 123.75 && degree < 146.25) return 'SE';
        if (degree >= 146.25 && degree < 168.75) return 'SSE';
        if (degree >= 168.75 && degree < 191.25) return 'S';
        if (degree >= 191.25 && degree < 213.75) return 'SSW';
        if (degree >= 213.75 && degree < 236.25) return 'SW';
        if (degree >= 236.25 && degree < 258.75) return 'WSW';
        if (degree >= 258.75 && degree < 281.25) return 'W';
        if (degree >= 281.25 && degree < 303.75) return 'WNW';
        if (degree >= 303.75 && degree < 326.25) return 'NW';
        if (degree >= 326.25 && degree < 348.75) return 'NNW';
        return ''; // fallback
    };

    return (
        <div className="relative overflow-hidden rounded-xl">
            {isDay ? (
                <>
                    <div className="absolute top-0 right-0 translate-x-1/2 w-[65%] h-36 bg-[#7DC6F9] opacity-75 rounded-b-full animate-pulseArc delay-200" />
                    <div className="absolute top-0 right-0 translate-x-1/2 w-[45%] h-32 bg-[#8CCBFA] opacity-75 rounded-b-full animate-pulseArc delay-300" />
                    <div className="absolute top-0 right-0 translate-x-1/2 w-[25%] h-28 bg-[#9AD2FA] opacity-75 rounded-b-full animate-pulseArc delay-400" />
                    <div className="absolute top-[-2.5vh] right-[-2.5vw] w-24 h-24 bg-yellow-300 rounded-full shadow-[0_0_40px_rgba(253,224,71,0.7)] z-10" />
                    <div className="absolute top-[-3vh] right-[25%] z-10 pointer-events-none opacity-75 animate-cloud-float delay-100">
                        <svg className="w-[12vw] h-[8vh]" viewBox="0 0 64 40" xmlns="http://www.w3.org/2000/svg">
                            <g fill="white" fillOpacity="1">
                                <circle cx="20" cy="20" r="10" />
                                <circle cx="30" cy="16" r="14" />
                                <circle cx="42" cy="20" r="10" />
                            </g>
                        </svg>
                    </div>
                    <div className="absolute top-[1vh] right-[45%] z-10 pointer-events-none opacity-60 animate-cloud-float delay-200">
                        <svg className="w-[9vw] h-[5.5vh]" viewBox="0 0 64 40" xmlns="http://www.w3.org/2000/svg">
                            <g fill="white" fillOpacity="1">
                                <circle cx="18" cy="20" r="10" />
                                <circle cx="28" cy="16" r="14" />
                                <circle cx="40" cy="20" r="10" />
                            </g>
                        </svg>
                    </div>
                </>
            ) : (
                <>
                    <div className="absolute top-0 right-[25%] w-[40%] h-28 bg-[#1E5C7A] opacity-80 rounded-b-full animate-pulseArc delay-100" />
                    <div className="absolute top-0 right-[30%] w-[28%] h-22 bg-[#2F657C] opacity-80 rounded-b-full animate-pulseArc delay-200" />
                    <div className="absolute top-[-17%] right-[25%] pointer-events-none rotate-50">
                        <svg className="w-[12vw] h-[12vh]" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M44 32C44 45.2548 34.2548 56 22 56C18.2185 56 14.6632 55.0436 11.5 53.3418C18.4375 50.3418 23.5 42.5 23.5 32C23.5 21.5 18.4375 13.6582 11.5 10.6582C14.6632 8.95639 18.2185 8 22 8C34.2548 8 44 18.7452 44 32Z" fill="#FDE68A" />
                        </svg>
                    </div>
                    <div className="absolute top-6 left-8 w-1 h-1 bg-white rounded-full animate-twinkle" />
                    <div className="absolute top-[10%] right-[60%] w-1 h-1 bg-white rounded-full animate-twinkle delay-1000" />
                    <div className="absolute bottom-10 left-16 w-1 h-1 bg-white rounded-full animate-twinkle delay-1500" />
                    <div className="absolute bottom-[30%] right-[35%] w-1 h-1 bg-white rounded-full animate-twinkle delay-2000" />
                </>
            )}

            <div className="absolute top-4 bottom-4 left-[70%] w-[0.5%] bg-white opacity-50 pointer-events-none" />

            <div className={`grid grid-cols-[20%_20%_25%_35%] grid-rows-3 gap-2 p-4 pb-8 rounded-xl text-white shadow-lg ${isDay ? 'bg-gradient-to-r from-[#4CC2F6] to-[#8CD2F9]' : 'bg-gradient-to-r from-[#0E5A83] to-[#084468]'}`}>
                <div className={`z-10 w-fit h-fit col-span-3 flex items-center gap-1 text-xs`}>
                    <div className={`w-fit h-fit flex rounded-3xl py-0.5 px-3 ${isDay ? 'bg-[#4CA4C2]' : 'bg-[#084468]'}`}>
                        <WiCloud size={18} />
                        <span className='pl-1'><strong>{subzoneName?.toLowerCase().replace(/\b\w/g, c => c.toUpperCase())}</strong>, Singapore</span>
                    </div>
                </div>

                <div className="z-10 text-center text-sm">
                    <span>Tomorrow</span>
                </div>

                <div className="z-10 row-span-2 flex items-end justify-end">
                    <div className="flex flex-col text-sm items-center">
                        {getWeatherIcon(current?.weather_code ?? null, isDay)}
                        <span className="mt-1">{forecastText(current?.weather_code ?? null)}</span>
                    </div>
                </div>

                <div className="z-10 row-span-2 flex items-end justify-center text-center">
                    <div className="flex flex-col">
                        <span className="text-5xl font-semibold">
                            {current ? Math.round(current.temperature_2m) : '--'}
                            <span className="align-top text-lg">°</span>
                        </span>
                        <span className="text-sm mt-1">
                            {tomorrow ? `${Math.round(tomorrow.tempMin)}/${Math.round(tomorrow.tempMax)}°` : '--/--°'}
                        </span>
                    </div>
                </div>

                <div className="z-10 row-span-2 flex items-end justify-start text-center">
                    <div className="flex flex-col text-sm">
                        <span className="border border-[#4CA4C2] text-xs px-2 py-1 rounded-sm">{formattedDate}</span>
                        <span className="mt-1">
                            {current ? (
                                <>
                                    <strong>{getCompassDirection(current.wind_direction_10m)}</strong> {current.wind_speed_10m}km/h
                                </>
                            ) : (
                                '--'
                            )}
                        </span>
                    </div>
                </div>

                <div className="z-10 row-span-2 flex items-center justify-center">
                    <div className="flex flex-col text-sm items-center">
                        {getWeatherIcon(tomorrow?.weatherCode ?? null, true)}
                        <span className="mt-1">
                            {tomorrow ? `${Math.round(tomorrow.tempMin)}/${Math.round(tomorrow.tempMax)}°` : '--/--°'}
                        </span>
                    </div>
                </div>
            </div>
        </div>
    );
}
