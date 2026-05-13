import { create } from 'zustand';

export type Repository = {
  id: number;
  owner: string;
  name: string;
  full_name: string;
  html_url: string;
  description?: string;
  visibility?: string;
};

export type Analysis = {
  id: number;
  repository_id: number;
  status: 'pending' | 'running' | 'completed' | 'failed';
  error_message?: string;
  created_at: string;
};

type Store = {
  availableRepos: Repository[];
  importedRepos: Repository[];
  analyses: Record<number, Analysis[]>;
  loading: boolean;
  error: string | null;
  
  setAvailableRepos: (repos: Repository[]) => void;
  setImportedRepos: (repos: Repository[]) => void;
  setAnalyses: (repoId: number, analyses: Analysis[]) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
};

export const useStore = create<Store>((set) => ({
  availableRepos: [],
  importedRepos: [],
  analyses: {},
  loading: false,
  error: null,
  
  setAvailableRepos: (repos) => set({ availableRepos: repos }),
  setImportedRepos: (repos) => set({ importedRepos: repos }),
  setAnalyses: (repoId, analyses) =>
    set((state) => ({
      analyses: { ...state.analyses, [repoId]: analyses },
    })),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
}));
