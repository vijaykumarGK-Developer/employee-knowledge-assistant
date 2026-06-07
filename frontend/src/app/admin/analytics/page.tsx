"use client";

import { useState, useEffect } from "react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from "recharts";
import AdminRoute from "@/components/AdminRoute";
import StatsCard from "@/components/StatsCard";
import { analyticsApi, type OverviewStats, type PopularQuestion, type UserActivity } from "@/lib/api";
import Link from "next/link";

export default function AdminAnalyticsPage() {
  const [overview, setOverview] = useState<OverviewStats | null>(null);
  const [popular, setPopular] = useState<PopularQuestion[]>([]);
  const [activity, setActivity] = useState<UserActivity[]>([]);
  const [unanswered, setUnanswered] = useState<Array<{ content: string; created_at: string }>>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([
      analyticsApi.overview(),
      analyticsApi.popularQuestions(),
      analyticsApi.userActivity(),
      analyticsApi.unanswered(),
    ])
      .then(([o, p, a, u]) => {
        setOverview(o);
        setPopular(p);
        setActivity(a);
        setUnanswered(u);
      })
      .catch(() => setError("Failed to load analytics"));
  }, []);

  return (
    <AdminRoute>
      <div className="min-h-screen bg-gray-50">
        <header className="flex items-center justify-between bg-white px-6 py-4 shadow-sm">
          <h1 className="text-lg font-semibold">Admin — Analytics</h1>
          <Link href="/dashboard" className="text-sm text-blue-600 hover:text-blue-800">
            Back to Dashboard
          </Link>
        </header>
        <main className="mx-auto max-w-6xl space-y-6 p-6">
          {error && <div className="rounded-md bg-red-50 p-3 text-sm text-red-700">{error}</div>}

          {overview && (
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
              <StatsCard label="Total Users" value={overview.total_users} icon="👤" />
              <StatsCard label="Documents" value={overview.total_documents} icon="📄" />
              <StatsCard label="Questions Today" value={overview.questions_today} icon="❓" />
              <StatsCard
                label="Unanswered"
                value={`${overview.unanswered_count} (${overview.unanswered_percentage}%)`}
                icon="⚠️"
              />
            </div>
          )}

          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            <div className="rounded-xl bg-white p-6 shadow-sm">
              <h2 className="mb-4 text-lg font-semibold">Most Asked Questions</h2>
              {popular.length === 0 ? (
                <p className="text-sm text-gray-500">No data yet</p>
              ) : (
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={popular} layout="vertical" margin={{ left: 20 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis type="number" />
                    <YAxis type="category" dataKey="question" width={180} tick={{ fontSize: 12 }} />
                    <Tooltip />
                    <Bar dataKey="count" fill="#3b82f6" radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              )}
            </div>

            <div className="rounded-xl bg-white p-6 shadow-sm">
              <h2 className="mb-4 text-lg font-semibold">User Activity (30 days)</h2>
              {activity.length === 0 ? (
                <p className="text-sm text-gray-500">No data yet</p>
              ) : (
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={activity}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                    <YAxis allowDecimals={false} />
                    <Tooltip />
                    <Line type="monotone" dataKey="active_users" stroke="#3b82f6" strokeWidth={2} dot={false} />
                  </LineChart>
                </ResponsiveContainer>
              )}
            </div>
          </div>

          <div className="rounded-xl bg-white p-6 shadow-sm">
            <h2 className="mb-4 text-lg font-semibold">Unanswered Questions</h2>
            {unanswered.length === 0 ? (
              <p className="text-sm text-gray-500">No unanswered questions</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                  <thead>
                    <tr className="border-b text-gray-600">
                      <th className="pb-3 pr-4 font-medium">Question</th>
                      <th className="pb-3 font-medium">Date</th>
                    </tr>
                  </thead>
                  <tbody>
                    {unanswered.slice(0, 20).map((q, i) => (
                      <tr key={i} className="border-b last:border-0">
                        <td className="py-3 pr-4">{q.content}</td>
                        <td className="py-3 text-gray-500">
                          {new Date(q.created_at).toLocaleDateString()}
                        </td>
                      </tr>
                    ))}
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
