// DiffTable.js
import React from "react";

const DiffTable = ({ diffData }) => {
  const prettifyPath = (path) =>
    path.replace("root", "").replace(/\['/g, " > ").replace(/'\]/g, "").replace(/^ > /, "").trim();

  const renderChangeRow = (type, path, oldValue, newValue, index) => {
    const typeColors = {
      Added: "bg-green-100",
      Removed: "bg-red-100",
      Changed: "bg-yellow-100"
    };
    const bgColor = typeColors[type] || "bg-white";

    const renderCell = (value) => {
      if (value === null || value === undefined) return "-";
      if (typeof value === "object") {
        return (
          <pre className="whitespace-pre-wrap break-words text-xs max-w-xs">
            {JSON.stringify(value, null, 2)}
          </pre>
        );
      }
      return value.toString();
    };

    return (
      <tr key={`${type}-${path}-${index}`} className="border-b">
        <td className={`px-4 py-2 font-semibold text-sm w-32 whitespace-nowrap ${bgColor}`}>{type}</td>
        <td className={`px-4 py-2 text-sm max-w-xs truncate whitespace-nowrap ${bgColor}`}>{prettifyPath(path)}</td>
        <td className={`px-4 py-2 text-sm w-40 whitespace-nowrap ${bgColor}`}>{renderCell(oldValue)}</td>
        <td className={`px-4 py-2 text-sm w-40 whitespace-nowrap ${bgColor}`}>{renderCell(newValue)}</td>
      </tr>
    );
  };

  const parsedRows = [];
  if (diffData.values_changed) {
    Object.entries(diffData.values_changed).forEach(([path, change], index) =>
      parsedRows.push(renderChangeRow("Changed", path, change.old_value, change.new_value, index))
    );
  }
  if (diffData.dictionary_item_added) {
    Object.entries(diffData.dictionary_item_added).forEach(([path, value], index) =>
      parsedRows.push(renderChangeRow("Added", path, "-", value, index))
    );
  }
  if (diffData.dictionary_item_removed) {
    Object.entries(diffData.dictionary_item_removed).forEach(([path, value], index) =>
      parsedRows.push(renderChangeRow("Removed", path, value, "-", index))
    );
  }

  return (
    <div className="flex-1 bg-white rounded-lg shadow-lg p-4 overflow-auto max-h-[80vh]">
      <h3 className="text-2xl font-semibold mb-4">🔍 Differences</h3>
      <div className="overflow-x-auto max-h-[70vh] overflow-y-auto border rounded-lg shadow">
        <table className="min-w-full bg-white">
          <thead className="sticky top-0 bg-gray-200">
            <tr className="text-gray-700">
              <th className="px-4 py-2 text-left">Type</th>
              <th className="px-4 py-2 text-left">Path</th>
              <th className="px-4 py-2 text-left">Old Value</th>
              <th className="px-4 py-2 text-left">New Value</th>
            </tr>
          </thead>
          <tbody>{parsedRows}</tbody>
        </table>
      </div>
    </div>
  );
};

export default DiffTable;
