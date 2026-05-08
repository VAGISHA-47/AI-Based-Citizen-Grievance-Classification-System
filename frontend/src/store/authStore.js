import { create } from 'zustand';
import { loginUser, registerUser, getMe } from '../services/api';

export const useAuthStore = create((set) => ({
  user: null,
  token: localStorage.getItem("jansetu_token") || null,
  loading: false,
  error: null,

  login: async (mobile, password) => {
    set({ loading: true, error: null });
    try {
      const data = await loginUser({ email: mobile, password });
      localStorage.setItem("jansetu_token", data.access_token);
      set({ token: data.access_token, user: { role: "citizen" }, loading: false });
      return { success: true };
    } catch (err) {
      set({ error: err.message, loading: false });
      return { success: false, error: err.message };
    }
  },

  register: async (name, mobile, password) => {
    set({ loading: true, error: null });
    try {
      await registerUser({ email: mobile, password, name });
      set({ loading: false });
      return { success: true };
    } catch (err) {
      set({ error: err.message, loading: false });
      return { success: false, error: err.message };
    }
  },

  logout: () => {
    localStorage.removeItem("jansetu_token");
    set({ user: null, token: null });
  },

  setRole: (role) => set((state) => ({ user: { ...state.user, role } })),
}));
