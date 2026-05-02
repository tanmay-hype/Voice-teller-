import { create } from 'zustand';

interface User {
  id: string;
  email: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  hasHydrated: boolean;
  login: (user: User, token: string) => void;
  logout: () => void;
}

const STORAGE_KEY = 'auth-storage';

const defaultAuthState = {
  user: null,
  token: null,
  isAuthenticated: false,
};

const readStoredAuthState = (): Pick<AuthState, 'user' | 'token' | 'isAuthenticated'> => {
  if (typeof window === 'undefined') {
    return defaultAuthState;
  }

  const raw = window.localStorage.getItem(STORAGE_KEY);
  if (!raw) {
    return defaultAuthState;
  }

  try {
    const parsed = JSON.parse(raw) as {
      state?: {
        user?: User | null;
        token?: string | null;
      };
    };

    const user = parsed.state?.user ?? null;
    const token = parsed.state?.token ?? null;

    return {
      user,
      token,
      isAuthenticated: Boolean(token),
    };
  } catch {
    window.localStorage.removeItem(STORAGE_KEY);
    return defaultAuthState;
  }
};

const writeStoredAuthState = (state: Pick<AuthState, 'user' | 'token'>) => {
  if (typeof window === 'undefined') {
    return;
  }

  window.localStorage.setItem(
    STORAGE_KEY,
    JSON.stringify({
      state: {
        user: state.user,
        token: state.token,
      },
      version: 0,
    })
  );
};

export const useAuthStore = create<AuthState>()(
  (set) => ({
    ...readStoredAuthState(),
    hasHydrated: true,
    login: (user, token) => {
      set({ user, token, isAuthenticated: true });
      writeStoredAuthState({ user, token });
    },
    logout: () => {
      set({ user: null, token: null, isAuthenticated: false });
      writeStoredAuthState({ user: null, token: null });
    },
  })
);
