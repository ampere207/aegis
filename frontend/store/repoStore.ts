import { create } from 'zustand'

export interface Repo {
  id: number
  owner: string
  name: string
  full_name: string
  html_url: string
  clone_url?: string
  description?: string
  visibility?: string
}

interface Analysis {
  id: number
  status: string
  created_at: string
}

export interface RepoStatus {
  repository_id: number
  full_name: string
  analyses: Analysis[]
}

interface RepoState {
  importedRepos: Repo[]
  statuses: Record<number, RepoStatus>
  setImportedRepos: (repos: Repo[]) => void
  updateStatus: (repoId: number, status: RepoStatus) => void
}

export const useRepoStore = create<RepoState>((set) => ({
  importedRepos: [],
  statuses: {},
  setImportedRepos: (repos) => set({ importedRepos: repos }),
  updateStatus: (repoId, status) => set((state) => ({ 
    statuses: { ...state.statuses, [repoId]: status } 
  }))
}))
