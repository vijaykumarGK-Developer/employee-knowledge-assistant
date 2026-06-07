import axios from "axios";

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
});

api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && typeof window !== "undefined") {
      localStorage.removeItem("token");
      if (!window.location.pathname.startsWith("/login")) {
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: string;
  department: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface Document {
  id: string;
  title: string;
  file_type: string;
  department: string;
  uploaded_by: string;
  version: number;
  uploaded_at: string;
  is_active: boolean;
}

export interface DocumentListResponse {
  items: Document[];
  total: number;
}

export const authApi = {
  register: (data: { email: string; password: string; full_name: string; department?: string }) =>
    api.post<TokenResponse>("/api/auth/register", data).then((r) => r.data),
  login: (data: { email: string; password: string }) =>
    api.post<TokenResponse>("/api/auth/login", data).then((r) => r.data),
  me: () => api.get<User>("/api/auth/me").then((r) => r.data),
};

export const documentApi = {
  upload: (file: File, title: string, department: string) => {
    const form = new FormData();
    form.append("file", file);
    form.append("title", title);
    form.append("department", department);
    return api.post<Document>("/api/documents/upload", form).then((r) => r.data);
  },
  list: (department?: string) =>
    api.get<DocumentListResponse>("/api/documents/", { params: department ? { department } : {} }).then((r) => r.data),
  get: (id: string) => api.get<Document>(`/api/documents/${id}`).then((r) => r.data),
  delete: (id: string) => api.delete(`/api/documents/${id}`).then((r) => r.data),
  reprocess: (id: string) => api.post<Document>(`/api/documents/${id}/reprocess`).then((r) => r.data),
};

export interface Chat {
  id: string;
  user_id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface Message {
  id: string;
  chat_id: string;
  role: string;
  content: string;
  sources: { sources: Array<{ doc_title: string; page_num: number | null; text_snippet: string }> } | null;
  feedback: boolean | null;
  created_at: string;
}

export interface ChatDetail extends Chat {
  messages: Message[];
}

export interface SendMessageResponse {
  message: Message;
  answer: Message;
}

export interface OverviewStats {
  total_users: number;
  total_documents: number;
  questions_today: number;
  unanswered_count: number;
  unanswered_percentage: number;
}

export interface PopularQuestion {
  question: string;
  count: number;
}

export interface UserActivity {
  date: string;
  active_users: number;
}

export const analyticsApi = {
  overview: () => api.get<OverviewStats>("/api/analytics/overview").then((r) => r.data),
  popularQuestions: (limit = 10) =>
    api.get<PopularQuestion[]>("/api/analytics/popular-questions", { params: { limit } }).then((r) => r.data),
  unanswered: () => api.get<Array<{ content: string; created_at: string }>>("/api/analytics/unanswered").then((r) => r.data),
  userActivity: (days = 30) =>
    api.get<UserActivity[]>("/api/analytics/user-activity", { params: { days } }).then((r) => r.data),
};

export const chatApi = {
  list: () => api.get<Chat[]>("/api/chats/").then((r) => r.data),
  create: () => api.post<Chat>("/api/chats/").then((r) => r.data),
  get: (id: string) => api.get<ChatDetail>(`/api/chats/${id}`).then((r) => r.data),
  delete: (id: string) => api.delete(`/api/chats/${id}`).then((r) => r.data),
  sendMessage: (chatId: string, content: string) =>
    api.post<SendMessageResponse>(`/api/chats/${chatId}/messages`, { content }).then((r) => r.data),
  submitFeedback: (messageId: string, feedback: boolean) =>
    api.post(`/api/chats/messages/${messageId}/feedback`, { feedback }).then((r) => r.data),
};

export default api;
