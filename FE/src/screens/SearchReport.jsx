import { useState } from "react";

export const SearchReport = () => {
  const [searchQuery, setSearchQuery] = useState("");
  const [results, setResults] = useState([]);
  const [total, setTotal] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const perPage = 10;
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [expandedAbstracts, setExpandedAbstracts] = useState({});

  const handleSearch = async (page = 1) => {
    if (!searchQuery.trim()) return;

    setLoading(true);
    setError("");
    setCurrentPage(page);
    setExpandedAbstracts({}); // Reset expanded abstracts on new search

    try {
      const response = await fetch(
        `https://crawl-to-search-engine.onrender.com/search?q=${encodeURIComponent(
          searchQuery
        )}&page=${page}&per_page=${perPage}`
      );

      if (!response.ok) {
        throw new Error("Search request failed");
      }

      const data = await response.json();
      setResults(data.results || []);
      setTotal(data.total || 0);
      // eslint-disable-next-line no-unused-vars
    } catch (err) {
      setError(
        "Failed to fetch search results. Please check your connection and try again."
      );
      setResults([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  };

  const toggleAbstract = (index) => {
    setExpandedAbstracts((prev) => ({
      ...prev,
      [index]: !prev[index],
    }));
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter") {
      handleSearch(1);
    }
  };

  const totalPages = Math.ceil(total / perPage);
  const startItem = (currentPage - 1) * perPage + 1;
  const endItem = Math.min(currentPage * perPage, total);

  const renderPagination = () => {
    if (totalPages <= 1) return null;

    const pages = [];

    // Show all pages when there are few pages, otherwise show smart range
    if (totalPages <= 10) {
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i);
      }
    } else {
      const maxVisible = 7;
      let startPage = Math.max(1, currentPage - Math.floor(maxVisible / 2));
      let endPage = Math.min(totalPages, startPage + maxVisible - 1);

      if (endPage - startPage + 1 < maxVisible) {
        startPage = Math.max(1, endPage - maxVisible + 1);
      }

      for (let i = startPage; i <= endPage; i++) {
        pages.push(i);
      }
    }

    return (
      <div className="flex items-center justify-center gap-2 mt-6 flex-wrap">
        <button
          onClick={() => handleSearch(1)}
          disabled={currentPage === 1}
          className="px-3 py-1 text-sm border rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          First
        </button>

        <button
          onClick={() => handleSearch(currentPage - 1)}
          disabled={currentPage === 1}
          className="px-3 py-1 text-sm border rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Prev
        </button>

        {pages.map((page) => (
          <button
            key={page}
            onClick={() => handleSearch(page)}
            className={`px-3 py-1 text-sm border rounded-md ${
              currentPage === page
                ? "bg-blue-600 text-white border-blue-600"
                : "hover:bg-gray-50"
            }`}
          >
            {page}
          </button>
        ))}

        <button
          onClick={() => handleSearch(currentPage + 1)}
          disabled={currentPage === totalPages}
          className="px-3 py-1 text-sm border rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Next
        </button>

        <button
          onClick={() => handleSearch(totalPages)}
          disabled={currentPage === totalPages}
          className="px-3 py-1 text-sm border rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Last
        </button>
      </div>
    );
  };

  const renderAuthors = (authors) => {
    if (!authors || authors.length === 0) return null;

    return (
      <div className="flex flex-wrap gap-2 mt-2">
        {authors.map((author, index) => (
          <div
            key={index}
            className="flex items-center gap-1 text-sm text-gray-600"
          >
            <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
              <path
                fillRule="evenodd"
                d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z"
                clipRule="evenodd"
              />
            </svg>
            {author.link ? (
              <a
                href={author.link}
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-blue-600 hover:underline text-blue-500 cursor-pointer"
              >
                {author.name || "Unknown Author"}
              </a>
            ) : (
              <span>{author.name || "Unknown Author"}</span>
            )}
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-white py-8 rounded-2xl">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 ">
        {/* Search Bar */}
        <div className="bg-white rounded-lg mb-6">
          <div className="flex flex-col sm:flex-row gap-4">
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
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Enter your search query..."
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <button
              onClick={() => handleSearch(1)}
              disabled={loading || !searchQuery.trim()}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 min-w-[120px]"
            >
              {loading ? (
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              ) : (
                <>
                  <svg
                    className="w-4 h-4"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fillRule="evenodd"
                      d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z"
                      clipRule="evenodd"
                    />
                  </svg>
                  Search
                </>
              )}
            </button>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}

        {/* Results Summary */}
        {total > 0 && (
          <div className="mb-4 text-sm text-gray-600">
            Showing {startItem}-{endItem} of {total} results
          </div>
        )}

        {/* Results List */}
        <div className="space-y-4">
          {results.map((report, index) => (
            <div
              key={index}
              className="bg-white rounded-lg shadow-sm border p-6 hover:shadow-md transition-shadow"
            >
              {/* Title */}
              <div className="flex items-start justify-between mb-3">
                <h3 className="text-lg font-semibold text-gray-900 leading-tight">
                  {report.link ? (
                    <a
                      href={report.link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="hover:text-blue-600 hover:underline flex items-center gap-2"
                    >
                      {report.title || "Untitled Report"}
                      <svg
                        className="w-4 h-4 flex-shrink-0"
                        fill="currentColor"
                        viewBox="0 0 20 20"
                      >
                        <path d="M11 3a1 1 0 100 2h2.586l-6.293 6.293a1 1 0 101.414 1.414L15 6.414V9a1 1 0 102 0V4a1 1 0 00-1-1h-5z" />
                        <path d="M5 5a2 2 0 00-2 2v8a2 2 0 002 2h8a2 2 0 002-2v-3a1 1 0 10-2 0v3H5V7h3a1 1 0 000-2H5z" />
                      </svg>
                    </a>
                  ) : (
                    report.title || "Untitled Report"
                  )}
                </h3>
                {report.score > 0 && (
                  <div className="flex items-center gap-1 text-sm text-amber-600 ml-4">
                    <svg
                      className="w-4 h-4"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                    </svg>
                    <span>{report.score.toFixed(2)}</span>
                  </div>
                )}
              </div>

              {/* Authors */}
              {renderAuthors(report.authors)}

              {/* Published Date */}
              {report.published && (
                <div className="flex items-center gap-1 text-sm text-gray-600 mt-2">
                  <svg
                    className="w-4 h-4"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fillRule="evenodd"
                      d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z"
                      clipRule="evenodd"
                    />
                  </svg>
                  <span>Published: {report.published}</span>
                </div>
              )}

              {/* Abstract */}
              {report.abstract && (
                <div className="mt-3">
                  <p className="text-gray-700 text-sm leading-relaxed">
                    {expandedAbstracts[index] || report.abstract.length <= 300
                      ? report.abstract
                      : `${report.abstract.substring(0, 300)}...`}
                  </p>
                  {report.abstract.length > 300 && (
                    <button
                      onClick={() => toggleAbstract(index)}
                      className="text-blue-600 hover:text-blue-800 text-sm font-medium mt-2 focus:outline-none"
                    >
                      {expandedAbstracts[index] ? "Read less" : "Read more"}
                    </button>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Empty State */}
        {!loading && results.length === 0 && searchQuery && !error && (
          <div className="text-center py-12">
            <svg
              className="w-12 h-12 text-gray-400 mx-auto mb-4"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path
                fillRule="evenodd"
                d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z"
                clipRule="evenodd"
              />
            </svg>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              No results found
            </h3>
            <p className="text-gray-600">
              Try adjusting your search terms or check the spelling.
            </p>
          </div>
        )}

        {/* Pagination */}
        {renderPagination()}

        {/* Results Summary Footer */}
        {total > 0 && (
          <div className="mt-6 text-center text-sm text-gray-500">
            Page {currentPage} of {totalPages} • {total} total results
          </div>
        )}
      </div>
    </div>
  );
};
