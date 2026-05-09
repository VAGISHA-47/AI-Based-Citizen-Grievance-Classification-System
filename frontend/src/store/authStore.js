import { create } from 'zustand';

export const useAuthStore = create((set) => ({
  user: null, // { id, role: "citizen" | "officer", token }
  login: (role) => set({
    user: {
      id: Math.random().toString(36).substr(2, 9),
      role,
      token: 'mock-jwt-token-123'
    }
  }),
  logout: () => set({ user: null })
}));
