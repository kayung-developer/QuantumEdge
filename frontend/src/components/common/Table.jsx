import React from 'react';

/**
 * A generic, styled table component that provides a consistent container
 * for displaying tabular data.
 * @param {Array<{key: string, label: string}>} headers - An array of header objects.
 * @param {React.ReactNode} children - The table body content (<tr> and <td> elements).
 */
const Table = ({ headers, children }) => {
    return (
        <div className="overflow-x-auto bg-dark-surface border border-dark-secondary rounded-lg shadow-md">
            <table className="min-w-full divide-y divide-dark-secondary">
                <thead className="bg-dark-tertiary">
                    <tr>
                        {headers.map((header) => (
                            <th
                                key={header.key}
                                scope="col"
                                className="px-6 py-3 text-left text-xs font-medium text-text-secondary uppercase tracking-wider"
                            >
                                {header.label}
                            </th>
                        ))}
                    </tr>
                </thead>
                <tbody className="divide-y divide-dark-secondary">
                    {children}
                </tbody>
            </table>
        </div>
    );
};

export default Table;