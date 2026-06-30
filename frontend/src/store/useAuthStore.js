import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'

export const useAuthStore = create(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      currentPage: 'discover',

      setAuth: (user, token) => set({ user, token }),

      updateUser: (partial) =>
        set((state) => ({ user: { ...state.user, ...partial } })),

      setPage: (page) => set({ currentPage: page }),

      logout: () => set({ user: null, token: null, currentPage: 'discover' }),

      isAuthenticated: () => !!get().token && !!get().user,
    }),
    {
      name: 'nf-auth',
      storage: createJSONStorage(() => localStorage),
    }
  )
)
