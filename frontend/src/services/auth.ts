
import api from "./api";

interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface User {
  id: number;
  institution_id: number;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
}

const TOKEN_KEY = "school_intelligence_access_token";

export const authService = {
  async login(username: string, password: string): Promise<LoginResponse> {
    const formData = new URLSearchParams();

    formData.append("username", username);
    formData.append("password", password);
    formData.append("grant_type", "password");

    const response = await api.post<LoginResponse>(
      "/auth/login",
      formData,
      {
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
      }
    );

    sessionStorage.setItem(TOKEN_KEY, response.data.access_token);

    return response.data;
  },

  async getCurrentUser(): Promise<User> {
    const response = await api.get<User>("/auth/me");
    return response.data;
  },

  getToken(): string | null {
    return sessionStorage.getItem(TOKEN_KEY);
  },

  logout(): void {
    sessionStorage.removeItem(TOKEN_KEY);
  },

  isAuthenticated(): boolean {
    return Boolean(sessionStorage.getItem(TOKEN_KEY));
  },
};

export default authService;
