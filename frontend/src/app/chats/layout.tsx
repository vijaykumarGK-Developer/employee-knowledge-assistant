"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import { chatApi, type Chat } from "@/lib/api";
import ChatSidebar from "@/components/ChatSidebar";
import ProtectedRoute from "@/components/ProtectedRoute";

export default function ChatsLayout({ children }: { children: React.ReactNode }) {
  const [chats, setChats] = useState<Chat[]>([]);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const { user, logout } = useAuth();
  const router = useRouter();

  const fetchChats = useCallback(async () => {
    try {
      const data = await chatApi.list();
      setChats(data);
    } catch {
      // handled by interceptor
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchChats();
  }, [fetchChats]);

  const handleNewChat = async () => {
    try {
      const chat = await chatApi.create();
      setChats((prev) => [chat, ...prev]);
      router.push(`/chats/${chat.id}`);
      setSidebarOpen(false);
    } catch {
      // handled by interceptor
    }
  };

  const handleDeleteChat = async (id: string) => {
    try {
      await chatApi.delete(id);
      setChats((prev) => prev.filter((c) => c.id !== id));
      router.push("/chats");
    } catch {
      // handled by interceptor
    }
  };

  return (
    <ProtectedRoute>
      <div className="flex h-screen bg-gray-100">
        <ChatSidebar
          chats={chats}
          loading={loading}
          onNewChat={handleNewChat}
          onDeleteChat={handleDeleteChat}
          open={sidebarOpen}
          onClose={() => setSidebarOpen(false)}
        />
        <div className="flex flex-1 flex-col min-w-0">
          <header className="flex items-center justify-between border-b bg-white px-4 py-3 md:px-6">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="mr-3 rounded-md p-1.5 hover:bg-gray-100 md:hidden"
              aria-label="Toggle sidebar"
            >
              <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
            <h1 className="text-sm font-semibold text-gray-700">Employee Knowledge Assistant</h1>
            <div className="flex items-center gap-3">
              <span className="text-xs text-gray-500">{user?.full_name}</span>
              {user?.role === "admin" && (
                <Link
                  href="/admin/documents"
                  className="rounded-md bg-blue-100 px-2.5 py-1 text-xs text-blue-700 hover:bg-blue-200"
                >
                  Admin
                </Link>
              )}
              <button
                onClick={logout}
                className="rounded-md bg-gray-200 px-2.5 py-1 text-xs hover:bg-gray-300"
              >
                Logout
              </button>
            </div>
          </header>
          {children}
        </div>
      </div>
    </ProtectedRoute>
  );
}
