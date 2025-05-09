import { useState } from 'react'
import { FaChevronDown } from 'react-icons/fa'

interface CustomDropdownProps {
    value: string
    onChange: (val: string) => void
    options: string[]
    placeholder?: string
}

export default function CustomDropdown({
    value,
    onChange,
    options,
    placeholder = 'Select Option',
}: CustomDropdownProps) {
    const [open, setOpen] = useState(false)

    const displayValue = value || placeholder

    return (
        <div className="relative w-48">
            <button
                onClick={() => setOpen(!open)}
                className={`h-8 w-full px-3 pr-8 text-sm border rounded bg-white text-left relative ${value ? 'text-[#485570] border-[#485570]' : 'text-gray-400 border-gray-300'} hover:bg-[#4855701a]`}
            >
                {displayValue}
                <FaChevronDown className="absolute right-2 top-1/2 transform -translate-y-1/2 text-xs pointer-events-none" />
            </button>
            {open && (
                <ul className="absolute z-10 mt-1 w-full border border-[#485570] rounded bg-white shadow">
                    {options.map((opt) => (
                        <li
                            key={opt}
                            onClick={() => {
                                onChange(opt)
                                setOpen(false)
                            }}
                            className="px-3 py-1 text-sm text-[#485570] hover:bg-[#4855701a] cursor-pointer"
                        >
                            {opt}
                        </li>
                    ))}
                </ul>
            )}
        </div>
    )
}
