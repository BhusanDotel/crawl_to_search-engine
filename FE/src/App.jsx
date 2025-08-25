import React from "react";
import { SearchReport } from "./screens/SearchReport";
import { ClassifyDocument } from "./screens/ClassifyDocument";

const App = () => {
  const [type, setType] = React.useState("search"); // search / classify

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-100 to-white py-10">
      <div className="max-w-6xl mx-auto px-4 sm:px-8 lg:px-12">
        {/* Main Title and Subtitle */}
        <div className="text-center mb-10">
          <h1 className="text-4xl font-extrabold text-blue-500 mb-2 tracking-tight drop-shadow-sm">
            Search & Classify Reports
          </h1>
          <p className="text-lg text-gray-500 font-medium">
            Effortlessly search academic reports or classify your own documents
          </p>
        </div>

        {/* Toggle Buttons */}
        <div className="flex justify-center gap-4 mb-10">
          <button
            onClick={() => setType("search")}
            className={`px-7 py-3 rounded-full font-semibold shadow transition-all duration-200 border focus:outline-none focus:ring-2 focus:ring-blue-100 text-lg ${
              type === "search"
                ? "bg-blue-100 text-blue-800 border-blue-200 scale-105"
                : "bg-white text-blue-700 border-gray-200 hover:bg-gray-100"
            }`}
            aria-pressed={type === "search"}
          >
            🔍 Search Reports
          </button>
          <button
            onClick={() => setType("classify")}
            className={`px-7 py-3 rounded-full font-semibold shadow transition-all duration-200 border focus:outline-none focus:ring-2 focus:ring-blue-100 text-lg ${
              type === "classify"
                ? "bg-blue-100 text-blue-800 border-blue-200 scale-105"
                : "bg-white text-blue-700 border-gray-200 hover:bg-gray-100"
            }`}
            aria-pressed={type === "classify"}
          >
            🗂️ Classify Documents
          </button>
        </div>

        {/* Render the selected screen */}
        {type === "search" ? (
          <SearchReport />
        ) : (
          <div className="bg-white rounded-2xl shadow-lg p-8 min-h-[500px]">
            <ClassifyDocument />
          </div>
        )}
      </div>
    </div>
  );
};

export default App;
