import {
    useReactTable,
    getCoreRowModel,
    getSortedRowModel,
    getFilteredRowModel,
    getPaginationRowModel,
    flexRender,
    ColumnDef,
    SortingState,
    ColumnFiltersState,
} from '@tanstack/react-table';
import { useState, useMemo } from 'react';
import { FaSort, FaSortUp, FaSortDown, FaChevronLeft, FaChevronRight, FaTimes } from 'react-icons/fa';

interface ClosedIssue {
    issue_id: string;
    datetime_updated: string;
    severity: string;
    issue_type: string;
    description: string;
}

declare module '@tanstack/react-table' {
    interface ColumnMeta<TData extends unknown, TValue> {
        width?: string;
    }
}

export default function ClosedIssuesTable({ data }: { data: ClosedIssue[] }) {
    const [sorting, setSorting] = useState<SortingState>([]);
    const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
    const [pagination, setPagination] = useState({
        pageIndex: 0,
        pageSize: 5,
    });

    const columns = useMemo<ColumnDef<ClosedIssue>[]>(
        () => [
            {
                accessorKey: 'datetime_updated',
                header: 'Last Updated',
                cell: (info) =>
                    new Date(info.getValue<string>()).toLocaleDateString('en-GB'),
                enableColumnFilter: false,
                meta: { width: '20%' },
            },
            {
                accessorKey: 'severity',
                header: 'Severity',
                cell: (info) => {
                    const severity = info.getValue<string>();
                    const color =
                        severity === 'High'
                            ? 'text-red-600'
                            : severity === 'Medium'
                                ? 'text-yellow-600'
                                : 'text-green-600';
                    return <span className={`font-medium ${color}`}>{severity}</span>;
                },
                filterFn: 'includesString',
                meta: { width: '15%' },
            },
            {
                accessorKey: 'issue_type',
                header: 'Issue Type',
                cell: (info) => {
                    const issueType = info.getValue<string>();
                    const tooltip =
                        issueType.length <= 30 ? issueType : 'Click view for full text';
                    return <span title={tooltip}>{issueType}</span>;
                },
                filterFn: 'includesString',
                meta: { width: '20%' },
            },
            {
                accessorKey: 'description',
                header: 'Description',
                cell: (info) => {
                    const desc = info.getValue<string>();
                    const tooltip =
                        desc.length <= 30 ? desc : 'Click view for full text';
                    return <span title={tooltip}>{desc}</span>;
                },
                filterFn: 'includesString',
                meta: { width: '30%' },
            },
            {
                header: 'Action',
                cell: () => (
                    <div className="text-center">
                        <button className="border-1 border-[#6a909eff] hover:bg-[#6a909eff] text-[#6a909eff] hover:text-white px-3 py-0.5 rounded text-sm">
                            View
                        </button>
                    </div>
                ),
                enableSorting: false,
                enableColumnFilter: false,
                meta: { width: '15%' },
            },
        ],
        []
    );

    const table = useReactTable({
        data,
        columns,
        state: {
            sorting,
            columnFilters,
            pagination,
        },
        onSortingChange: setSorting,
        onColumnFiltersChange: setColumnFilters,
        onPaginationChange: setPagination,
        getCoreRowModel: getCoreRowModel(),
        getSortedRowModel: getSortedRowModel(),
        getFilteredRowModel: getFilteredRowModel(),
        getPaginationRowModel: getPaginationRowModel(),
        debugTable: false,
    });

    return (
        <div className="space-y-4">
            {/* Filter Inputs */}
            <div className="flex gap-4">
                {table.getHeaderGroups()[0].headers.map((header) => {
                    const column = header.column;

                    if (!column.getCanFilter()) return null;

                    const filterValue = (column.getFilterValue() ?? '') as string;

                    return (
                        <div key={column.id} className="flex flex-col">
                            <label className="text-xs text-gray-500">
                                {column.columnDef.header as string}
                            </label>
                            <div className="relative">
                                <input
                                    className="border border-gray-300 px-2 py-1 rounded text-xs focus:border-[#6a909eff] focus:outline-none focus:text-gray-800 pr-6"
                                    value={filterValue}
                                    onChange={(e) => column.setFilterValue(e.target.value)}
                                    placeholder="Filter..."
                                />
                                {filterValue && (
                                    <button
                                        onClick={() => column.setFilterValue('')}
                                        className="absolute right-1 top-1/2 -translate-y-1/2 text-gray-400 text-xs hover:text-[#6a909eff]"
                                        title="Clear"
                                    >
                                        <FaTimes/>
                                    </button>
                                )}
                            </div>
                        </div>
                    );
                })}
            </div>


            {/* Table */}
            <div className="overflow-x-auto rounded-lg  shadow text-[#3f3f3f] border-[#dfe7ea]">
                <table className="table table-fixed w-full divide-y divide-gray-200 text-sm">
                    <thead className="bg-gray-50">
                        {table.getHeaderGroups().map((headerGroup) => (
                            <tr key={headerGroup.id}>
                                {headerGroup.headers.map((header) => (
                                    <th
                                        key={header.id}
                                        style={{
                                            width: header.column.columnDef.meta?.width,
                                            maxWidth: header.column.columnDef.meta?.width,
                                            minWidth: header.column.columnDef.meta?.width,
                                        }}

                                        className="pl-4 py-3 text-left text-xs bg-[#6a909eff] text-white font-bold uppercase tracking-wider cursor-pointer"
                                        onClick={header.column.getToggleSortingHandler()}
                                    >
                                        {flexRender(header.column.columnDef.header, header.getContext())}
                                        <span className="ml-1 inline-block align-middle">
                                            {{
                                                asc: <FaSortUp className="inline-block text-white" />,
                                                desc: <FaSortDown className="inline-block text-white" />,
                                            }[header.column.getIsSorted() as string] ?? (
                                                    <FaSort className="inline-block text-white" />
                                                )}
                                        </span>
                                    </th>
                                ))}
                            </tr>
                        ))}
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                        {table.getRowModel().rows.map((row) => (
                            <tr key={row.id} className="hover:bg-gray-50">
                                {row.getVisibleCells().map((cell) => (
                                    <td
                                        key={cell.id}
                                        style={{
                                            width: cell.column.columnDef.meta?.width,
                                            maxWidth: cell.column.columnDef.meta?.width,
                                            minWidth: cell.column.columnDef.meta?.width,
                                        }}
                                        className="px-4 py-2 truncate"
                                    >

                                        {flexRender(cell.column.columnDef.cell, cell.getContext())}
                                    </td>
                                ))}
                            </tr>
                        ))}
                        {table.getRowModel().rows.length === 0 && (
                            <tr>
                                <td colSpan={columns.length} className="px-6 py-4 text-center text-gray-400 italic">
                                    No closed issues found.
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>

            {/* Pagination */}
            <div className="flex flex-wrap items-center justify-between gap-4 text-sm mt-2 text-[#3f3f3f]">
                {/* Left: Range Display */}
                <div>
                    {table.getRowModel().rows.length > 0 && (
                        <>
                            {pagination.pageIndex * pagination.pageSize + 1}–{Math.min((pagination.pageIndex + 1) * pagination.pageSize, data.length)} of {data.length}
                        </>
                    )}
                </div>

                {/* Right: Controls */}
                <div className="flex items-center gap-2">
                    {/* Page size selector */}
                    <select
                        value={pagination.pageSize}
                        onChange={(e) => table.setPageSize(Number(e.target.value))}
                        className="border border-gray-300 rounded px-2 py-1"
                    >
                        {[5, 10, 20, 50].map((size) => (
                            <option key={size} value={size}>
                                Show {size}
                            </option>
                        ))}
                    </select>

                    {/* Prev */}
                    <button
                        onClick={() => table.previousPage()}
                        disabled={!table.getCanPreviousPage()}
                        className="p-1 rounded bg-[#6a909eff] hover:bg-[#55737eff] text-white disabled:opacity-60"
                    >
                        <FaChevronLeft />
                    </button>

                    {/* Page input */}
                    <input
                        type="number"
                        min={1}
                        max={table.getPageCount()}
                        value={pagination.pageIndex + 1}
                        onChange={(e) => {
                            const page = e.target.value ? Number(e.target.value) - 1 : 0;
                            table.setPageIndex(page);
                        }}
                        className="border border-gray-300 rounded px-2 py-1 w-14 text-center"
                    />

                    <span>of {table.getPageCount()}</span>

                    {/* Next */}
                    <button
                        onClick={() => table.nextPage()}
                        disabled={!table.getCanNextPage()}
                        className="p-1 rounded bg-[#6a909eff] hover:bg-[#55737eff] text-white disabled:opacity-60"
                    >
                        <FaChevronRight />
                    </button>
                </div>
            </div>
        </div>
    );
}
