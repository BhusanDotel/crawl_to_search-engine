import React, { useState } from "react";

export const ClassifyDocument = () => {
  const [query, setQuery] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleClassify = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const res = await fetch(
        `https://crawl-to-search-engine.onrender.com/classify?q=${encodeURIComponent(
          query
        )}`
      );
      if (!res.ok) throw new Error("Classification failed");
      const data = await res.json();
      setResult(data);
    } catch (err) {
      console.log("error:", err);
      setError("Failed to classify. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter") handleClassify();
  };

  return (
    <div>
      <div className="flex flex-col sm:flex-row gap-4 mb-6 justify-center">
        <div className="flex-1 relative">
          <svg
            className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5"
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path
              fillRule="evenodd"
              d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z"
              clipRule="evenodd"
            />
          </svg>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Enter your search query..."
            className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
        <button
          onClick={handleClassify}
          disabled={loading || !query.trim()}
          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-400 disabled:opacity-50 disabled:cursor-not-allowed min-w-[120px]"
        >
          {loading ? (
            <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
          ) : (
            "Classify"
          )}
        </button>
      </div>
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6 text-center">
          {error}
        </div>
      )}
      {result && (
        <div className="max-w-md mx-auto bg-gray-50 border border-gray-200 rounded-xl p-6 shadow text-center">
          <div className="mb-4">
            <span className="text-gray-500">Predicted Category:</span>
            <span className="ml-2 text-xl font-semibold text-blue-700">
              {result.predicted_category}
            </span>
          </div>
          <div>
            <span className="text-gray-500 font-medium">Probabilities:</span>
            <ul className="mt-2 space-y-1">
              {result.probabilities &&
                Object.entries(result.probabilities).map(([cat, prob]) => (
                  <li key={cat} className="flex justify-between px-2">
                    <span className="text-gray-700">{cat}</span>
                    <span className="text-gray-900 font-mono">
                      {prob.toFixed(2)}%
                    </span>
                  </li>
                ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};
