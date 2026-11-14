
import { useCallback, useEffect, useState } from "react";

import {
  getImportHistory,
  getImportRejections,
  uploadImportFile,
} from "../../services/imports";

import type {
  ImportHistoryItem,
  ImportRejection,
  ImportSummary,
  ImportType,
} from "../../types/imports";

import "./Imports.css";

const PAGE_SIZE = 10;

const IMPORT_TYPES: { value: ImportType; label: string }[] = [
  { value: "students", label: "Students" },
  { value: "marks", label: "Marks" },
  { value: "attendance", label: "Attendance" },
];

const formatDate = (value: string | null) => {
  if (!value) return "—";

  return new Date(value).toLocaleString();
};


const getErrorMessage = (error: unknown): string => {
  const apiError = error as {
    response?: {
      data?: {
        detail?: unknown;
      };
    };
    message?: string;
  };

  const detail = apiError.response?.data?.detail;

  if (typeof detail === "string") {
    return detail;
  }

  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        if (typeof item === "string") {
          return item;
        }

        if (item && typeof item === "object") {
          const errorItem = item as {
            loc?: unknown[];
            msg?: string;
          };

          const location = errorItem.loc
            ?.filter((part) => part !== "body")
            .join(".");

          return location
            ? `${location}: ${errorItem.msg || "Invalid value"}`
            : errorItem.msg || "Invalid request";
        }

        return String(item);
      })
      .join("; ");
  }

  if (detail && typeof detail === "object") {
    return JSON.stringify(detail);
  }

  return (
    apiError.message ||
    "Something went wrong. Please try again."
  );
};


function Imports() {
  const [importType, setImportType] =
    useState<ImportType>("students");

  const [selectedFile, setSelectedFile] = useState<File | null>(
    null
  );

  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState("");
  const [uploadResult, setUploadResult] =
    useState<ImportSummary | null>(null);

  const [history, setHistory] = useState<ImportHistoryItem[]>([]);
  const [totalHistory, setTotalHistory] = useState(0);
  const [historyFilter, setHistoryFilter] = useState<
    ImportType | "all"
  >("all");

  const [page, setPage] = useState(0);
  const [loadingHistory, setLoadingHistory] = useState(true);
  const [historyError, setHistoryError] = useState("");

  const [selectedImportId, setSelectedImportId] =
    useState<number | null>(null);

  const [rejections, setRejections] = useState<ImportRejection[]>(
    []
  );
  const [rejectionTotal, setRejectionTotal] = useState(0);
  const [rejectionPage, setRejectionPage] = useState(0);
  const [loadingRejections, setLoadingRejections] = useState(false);
  const [rejectionError, setRejectionError] = useState("");

  const loadHistory = useCallback(async () => {
    setLoadingHistory(true);
    setHistoryError("");

    try {
      const response = await getImportHistory({
        limit: PAGE_SIZE,
        offset: page * PAGE_SIZE,
        ...(historyFilter !== "all"
          ? { import_type: historyFilter }
          : {}),
      });

      setHistory(response.items);
      setTotalHistory(response.total);
    } catch (error) {
      setHistoryError(getErrorMessage(error));
    } finally {
      setLoadingHistory(false);
    }
  }, [page, historyFilter]);

  useEffect(() => {
  // Load import history when the page, filter, or component changes.
  // State updates are also handled after the asynchronous API request.
  // eslint-disable-next-line react-hooks/set-state-in-effect
        void loadHistory();
    }, [loadHistory]);

  const handleFileChange = (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const file = event.target.files?.[0] || null;

    setSelectedFile(file);
    setUploadError("");
    setUploadResult(null);

    if (file) {
      const extension = file.name
        .split(".")
        .pop()
        ?.toLowerCase();

      if (!["csv", "xlsx", "xls"].includes(extension || "")) {
        setUploadError(
          "Unsupported file format. Please select CSV, XLSX or XLS."
        );
        setSelectedFile(null);
      }
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setUploadError("Please select a file before uploading.");
      return;
    }

    setUploading(true);
    setUploadError("");
    setUploadResult(null);

    try {
      const result = await uploadImportFile(
        importType,
        selectedFile
      );

      setUploadResult(result);
      setSelectedFile(null);

      const fileInput = document.getElementById(
        "import-file"
      ) as HTMLInputElement | null;

      if (fileInput) {
        fileInput.value = "";
      }

      setPage(0);
      setHistoryFilter("all");
      setSelectedImportId(null);
      setRejections([]);

      await loadHistory();
    } catch (error) {
      setUploadError(getErrorMessage(error));
    } finally {
      setUploading(false);
    }
  };

  const loadRejections = async (
    importId: number,
    requestedPage = 0
  ) => {
    setSelectedImportId(importId);
    setLoadingRejections(true);
    setRejectionError("");
    setRejectionPage(requestedPage);

    try {
      const response = await getImportRejections(importId, {
        limit: PAGE_SIZE,
        offset: requestedPage * PAGE_SIZE,
      });

      setRejections(response.items);
      setRejectionTotal(response.total);
    } catch (error) {
      setRejectionError(getErrorMessage(error));
      setRejections([]);
      setRejectionTotal(0);
    } finally {
      setLoadingRejections(false);
    }
  };

  const totalPages = Math.ceil(totalHistory / PAGE_SIZE);
  const rejectionPages = Math.ceil(
    rejectionTotal / PAGE_SIZE
  );

  const closeRejections = () => {
    setSelectedImportId(null);
    setRejections([]);
    setRejectionTotal(0);
    setRejectionError("");
  };

  return (
    <div className="imports-page">
      <div className="imports-header">
        <div>
          <h1>Data Imports</h1>
          <p>
            Upload academic datasets and monitor import activity.
          </p>
        </div>

        <div className="imports-header-total">
          <span>Total Imports</span>
          <strong>{totalHistory}</strong>
        </div>
      </div>

      {/* Upload Section */}
      <section className="imports-card">
        <div className="imports-section-heading">
          <div>
            <h2>Upload Academic Data</h2>
            <p>
              Import student, examination marks or attendance
              records.
            </p>
          </div>
        </div>

        <div className="imports-upload-grid">
          <div className="imports-field">
            <label htmlFor="import-type">
              Import Category
            </label>

            <select
              id="import-type"
              value={importType}
              onChange={(event) => {
                setImportType(
                  event.target.value as ImportType
                );
                setUploadResult(null);
                setUploadError("");
              }}
              disabled={uploading}
            >
              {IMPORT_TYPES.map((type) => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
          </div>

          <div className="imports-field">
            <label htmlFor="import-file">
              Select File
            </label>

            <input
              id="import-file"
              name="file"
              type="file"
              accept=".csv,.xlsx,.xls"
              onChange={handleFileChange}
              disabled={uploading}
            />

            <small>
              Supported formats: CSV, XLSX and XLS
            </small>
          </div>
        </div>

        {selectedFile && (
          <div className="imports-selected-file">
            <span>{selectedFile.name}</span>
            <span>
              {(selectedFile.size / 1024).toFixed(1)} KB
            </span>
          </div>
        )}

        {uploadError && (
          <div className="imports-alert imports-alert-error">
            {uploadError}
          </div>
        )}

        <div className="imports-upload-actions">
          <button
            type="button"
            className="imports-primary-button"
            onClick={handleUpload}
            disabled={uploading || !selectedFile}
          >
            {uploading ? "Uploading..." : "Upload File"}
          </button>
        </div>

        {uploadResult && (
          <div className="imports-result">
            <h3>Import Completed</h3>

            <p>
              File: <strong>{uploadResult.file_name}</strong>
            </p>

            <div className="imports-result-grid">
              <div>
                <span>Total Rows</span>
                <strong>{uploadResult.total_rows}</strong>
              </div>

              <div>
                <span>Accepted</span>
                <strong className="imports-success-text">
                  {uploadResult.accepted_rows}
                </strong>
              </div>

              <div>
                <span>Rejected</span>
                <strong className="imports-danger-text">
                  {uploadResult.rejected_rows}
                </strong>
              </div>
            </div>
          </div>
        )}
      </section>

      {/* Import History */}
      <section className="imports-card">
        <div className="imports-section-heading imports-history-heading">
          <div>
            <h2>Import History</h2>
            <p>
              Review previous uploads and their processing results.
            </p>
          </div>

          <div className="imports-filter">
            <label htmlFor="history-filter">
              Filter by type
            </label>

            <select
              id="history-filter"
              value={historyFilter}
              onChange={(event) => {
                setHistoryFilter(
                  event.target.value as ImportType | "all"
                );
                setPage(0);
                closeRejections();
              }}
            >
              <option value="all">All Imports</option>
              {IMPORT_TYPES.map((type) => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        {historyError && (
          <div className="imports-alert imports-alert-error">
            {historyError}
          </div>
        )}

        <div className="imports-table-wrapper">
          <table className="imports-table">
            <thead>
              <tr>
                <th>File Name</th>
                <th>Type</th>
                <th>Total</th>
                <th>Accepted</th>
                <th>Rejected</th>
                <th>Status</th>
                <th>Uploaded At</th>
                <th>Action</th>
              </tr>
            </thead>

            <tbody>
              {loadingHistory ? (
                <tr>
                  <td colSpan={8} className="imports-empty">
                    Loading import history...
                  </td>
                </tr>
              ) : history.length === 0 ? (
                <tr>
                  <td colSpan={8} className="imports-empty">
                    No import records found.
                  </td>
                </tr>
              ) : (
                history.map((item) => (
                  <tr key={item.id}>
                    <td className="imports-file-name">
                      {item.file_name}
                    </td>

                    <td>
                      {item.import_type}
                    </td>

                    <td>{item.total_rows}</td>

                    <td className="imports-success-text">
                      {item.accepted_rows}
                    </td>

                    <td className="imports-danger-text">
                      {item.rejected_rows}
                    </td>

                    <td>
                      <span
                        className={`imports-status imports-status-${item.status}`}
                      >
                        {item.status}
                      </span>
                    </td>

                    <td>{formatDate(item.created_at)}</td>

                    <td>
                      {item.rejected_rows > 0 ? (
                        <button
                          type="button"
                          className="imports-view-button"
                          onClick={() =>
                            void loadRejections(item.id)
                          }
                        >
                          View Rejections
                        </button>
                      ) : (
                        <span className="imports-no-action">
                          —
                        </span>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        <div className="imports-pagination">
          <span>
            Showing {history.length} of {totalHistory} imports
          </span>

          <div>
            <button
              type="button"
              onClick={() => setPage((current) => current - 1)}
              disabled={page === 0 || loadingHistory}
            >
              Previous
            </button>

            <span>
              Page {totalPages === 0 ? 0 : page + 1} of{" "}
              {totalPages}
            </span>

            <button
              type="button"
              onClick={() => setPage((current) => current + 1)}
              disabled={
                loadingHistory ||
                page + 1 >= totalPages
              }
            >
              Next
            </button>
          </div>
        </div>
      </section>

      {/* Rejection Details */}
      {selectedImportId !== null && (
        <section className="imports-card imports-rejections-card">
          <div className="imports-section-heading">
            <div>
              <h2>Rejected Records</h2>
              <p>
                Import ID: {selectedImportId} · Total rejected:{" "}
                {rejectionTotal}
              </p>
            </div>

            <button
              type="button"
              className="imports-close-button"
              onClick={closeRejections}
            >
              Close
            </button>
          </div>

          {rejectionError && (
            <div className="imports-alert imports-alert-error">
              {rejectionError}
            </div>
          )}

          <div className="imports-rejection-list">
            {loadingRejections ? (
              <p className="imports-empty">
                Loading rejected records...
              </p>
            ) : rejections.length === 0 ? (
              <p className="imports-empty">
                No rejected records found.
              </p>
            ) : (
              rejections.map((item: ImportRejection) => (
                <article
                  className="imports-rejection-item"
                  key={item.id}
                >
                  <div className="imports-rejection-top">
                    <strong>CSV Row {item.row_number}</strong>
                    <span>ID: {item.id}</span>
                  </div>

                  <p className="imports-rejection-reason">
                    {item.rejection_reason}
                  </p>

                  <details>
                    <summary>View original row data</summary>
                    <pre>
                      {JSON.stringify(item.raw_data, null, 2)}
                    </pre>
                  </details>

                  <small>
                    Recorded: {formatDate(item.created_at)}
                  </small>
                </article>
              ))
            )}
          </div>

          {rejectionTotal > PAGE_SIZE && (
            <div className="imports-pagination">
              <span>
                Showing {rejections.length} of {rejectionTotal}{" "}
                rejected records
              </span>

              <div>
                <button
                  type="button"
                  onClick={() =>
                    void loadRejections(
                      selectedImportId,
                      rejectionPage - 1
                    )
                  }
                  disabled={
                    rejectionPage === 0 || loadingRejections
                  }
                >
                  Previous
                </button>

                <span>
                  Page {rejectionPage + 1} of {rejectionPages}
                </span>

                <button
                  type="button"
                  onClick={() =>
                    void loadRejections(
                      selectedImportId,
                      rejectionPage + 1
                    )
                  }
                  disabled={
                    loadingRejections ||
                    rejectionPage + 1 >= rejectionPages
                  }
                >
                  Next
                </button>
              </div>
            </div>
          )}
        </section>
      )}
    </div>
  );
}

export default Imports;
