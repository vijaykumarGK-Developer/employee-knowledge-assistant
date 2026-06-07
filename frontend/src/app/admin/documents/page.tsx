"use client";

import { useState, useEffect, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import AdminRoute from "@/components/AdminRoute";
import { documentApi, type Document } from "@/lib/api";
import Link from "next/link";

export default function AdminDocumentsPage() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [departmentFilter, setDepartmentFilter] = useState("");
  const [uploading, setUploading] = useState(false);
  const [uploadTitle, setUploadTitle] = useState("");
  const [uploadDepartment, setUploadDepartment] = useState("all");
  const [deleteConfirm, setDeleteConfirm] = useState<string | null>(null);

  const fetchDocuments = useCallback(async () => {
    setLoading(true);
    try {
      const res = await documentApi.list(departmentFilter || undefined);
      setDocuments(res.items);
    } catch {
      setError("Failed to load documents");
    } finally {
      setLoading(false);
    }
  }, [departmentFilter]);

  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file || !uploadTitle) return;
    setUploading(true);
    setError("");
    try {
      await documentApi.upload(file, uploadTitle, uploadDepartment);
      setSuccess(`"${uploadTitle}" uploaded successfully`);
      setUploadTitle("");
      fetchDocuments();
    } catch (err: unknown) {
      const msg = err && typeof err === "object" && "response" in err
        ? (err as { response: { data: { detail?: string } } }).response?.data?.detail || "Upload failed"
        : "Upload failed";
      setError(msg);
    } finally {
      setUploading(false);
    }
  }, [uploadTitle, uploadDepartment, fetchDocuments]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "application/pdf": [".pdf"], "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"], "text/plain": [".txt"], "text/csv": [".csv"] },
    maxFiles: 1,
    disabled: !uploadTitle,
  });

  const handleDelete = async (id: string) => {
    try {
      await documentApi.delete(id);
      setSuccess("Document deleted");
      setDeleteConfirm(null);
      fetchDocuments();
    } catch {
      setError("Delete failed");
    }
  };

  return (
    <AdminRoute>
      <div className="min-h-screen bg-gray-50">
        <header className="flex items-center justify-between bg-white px-6 py-4 shadow-sm">
          <h1 className="text-lg font-semibold">Admin — Document Management</h1>
          <Link href="/dashboard" className="text-sm text-blue-600 hover:text-blue-800">
            Back to Dashboard
          </Link>
        </header>
        <main className="mx-auto max-w-5xl space-y-6 p-6">
          {error && (
            <div className="rounded-md bg-red-50 p-3 text-sm text-red-700">{error}</div>
          )}
          {success && (
            <div className="rounded-md bg-green-50 p-3 text-sm text-green-700">{success}</div>
          )}

          <div className="rounded-xl bg-white p-6 shadow-sm">
            <h2 className="mb-4 text-lg font-semibold">Upload Document</h2>
            <div className="mb-4 flex gap-4">
              <input
                type="text"
                placeholder="Document title"
                value={uploadTitle}
                onChange={(e) => setUploadTitle(e.target.value)}
                className="flex-1 rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
              />
              <select
                value={uploadDepartment}
                onChange={(e) => setUploadDepartment(e.target.value)}
                className="rounded-md border border-gray-300 px-3 py-2 text-sm"
              >
                <option value="all">All Departments</option>
                <option value="hr">HR</option>
                <option value="engineering">Engineering</option>
                <option value="finance">Finance</option>
              </select>
            </div>
            <div
              {...getRootProps()}
              className={`flex cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed p-8 text-center transition-colors ${
                isDragActive ? "border-blue-500 bg-blue-50" : "border-gray-300 hover:border-gray-400"
              } ${!uploadTitle ? "opacity-50" : ""}`}
            >
              <input {...getInputProps()} />
              {uploading ? (
                <p className="text-sm text-gray-500">Uploading...</p>
              ) : isDragActive ? (
                <p className="text-sm text-blue-600">Drop the file here</p>
              ) : (
                <div>
                  <p className="text-sm text-gray-600">
                    Drag & drop a file here, or click to select
                  </p>
                  <p className="mt-1 text-xs text-gray-400">PDF, DOCX, TXT, CSV (max 50MB)</p>
                </div>
              )}
            </div>
          </div>

          <div className="rounded-xl bg-white p-6 shadow-sm">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-lg font-semibold">Documents</h2>
              <select
                value={departmentFilter}
                onChange={(e) => setDepartmentFilter(e.target.value)}
                className="rounded-md border border-gray-300 px-3 py-2 text-sm"
              >
                <option value="">All Departments</option>
                <option value="hr">HR</option>
                <option value="engineering">Engineering</option>
                <option value="finance">Finance</option>
              </select>
            </div>
            {loading ? (
              <p className="py-8 text-center text-gray-500">Loading...</p>
            ) : documents.length === 0 ? (
              <p className="py-8 text-center text-gray-500">No documents found</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                  <thead>
                    <tr className="border-b text-gray-600">
                      <th className="pb-3 pr-4 font-medium">Title</th>
                      <th className="pb-3 pr-4 font-medium">Type</th>
                      <th className="pb-3 pr-4 font-medium">Department</th>
                      <th className="pb-3 pr-4 font-medium">Version</th>
                      <th className="pb-3 pr-4 font-medium">Status</th>
                      <th className="pb-3 pr-4 font-medium">Uploaded</th>
                      <th className="pb-3 font-medium">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {documents.map((doc) => {
                      const deptColors: Record<string, string> = {
                        hr: "bg-pink-100 text-pink-700",
                        engineering: "bg-blue-100 text-blue-700",
                        finance: "bg-green-100 text-green-700",
                        all: "bg-gray-100 text-gray-700",
                      };
                      const statusColors: Record<string, string> = {
                        completed: "bg-green-100 text-green-700",
                        processing: "bg-yellow-100 text-yellow-700",
                        pending: "bg-gray-100 text-gray-500",
                        failed: "bg-red-100 text-red-700",
                      };
                      return (
                      <tr key={doc.id} className="border-b last:border-0">
                        <td className="py-3 pr-4">{doc.title}</td>
                        <td className="py-3 pr-4">
                          <span className="rounded bg-gray-100 px-2 py-0.5 text-xs font-medium uppercase text-gray-600">
                            {doc.file_type}
                          </span>
                        </td>
                        <td className="py-3 pr-4">
                          <span className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-medium capitalize ${deptColors[doc.department] || "bg-gray-100 text-gray-700"}`}>
                            {doc.department}
                          </span>
                        </td>
                        <td className="py-3 pr-4">v{doc.version}</td>
                        <td className="py-3 pr-4">
                          <span className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-medium ${statusColors[doc.processing_status] || "bg-gray-100 text-gray-500"}`}>
                            {doc.processing_status}
                          </span>
                        </td>
                        <td className="py-3 pr-4 text-gray-500">
                          {new Date(doc.uploaded_at).toLocaleDateString()}
                        </td>
                        <td className="py-3">
                          {deleteConfirm === doc.id ? (
                            <span className="flex gap-2">
                              <button
                                onClick={() => handleDelete(doc.id)}
                                className="text-sm text-red-600 hover:text-red-800"
                              >
                                Confirm
                              </button>
                              <button
                                onClick={() => setDeleteConfirm(null)}
                                className="text-sm text-gray-500 hover:text-gray-700"
                              >
                                Cancel
                              </button>
                            </span>
                          ) : (
                            <button
                              onClick={() => setDeleteConfirm(doc.id)}
                              className="text-sm text-red-600 hover:text-red-800"
                            >
                              Delete
                            </button>
                          )}
                        </td>
                      </tr>
                    );
                      })}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </main>
      </div>
    </AdminRoute>
  );
}
