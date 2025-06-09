import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

export interface FileInfo {
  name: string;
  size: number; // in bytes
  type: string; // e.g., 'application/pdf', 'text/plain'
  download_url?: string; // Optional download URL from backend
  last_modified?: string; // Optional last modified date
}

interface FileState {
  files: FileInfo[];
  isLoading: boolean;
  error: string | null;
  fetchFiles: () => Promise<void>;
  deleteFile: (filename: string) => Promise<void>;
  // addFile: (fileInfo: FileInfo) => void; // Keep for potential future use
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  clearError: () => void;
}

export const useFileStore = create<FileState>()(
  devtools(
    (set, get) => ({
      files: [],
      isLoading: false,
      error: null,

      setLoading: (loading: boolean) => set({ isLoading: loading }),
      setError: (error: string | null) => set({ error }),
      clearError: () => set({ error: null }),

      fetchFiles: async () => {
        set({ isLoading: true, error: null });
        try {
          const response = await fetch('/api/files'); // Assuming gateway is on the same host
          if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `Failed to fetch files: ${response.statusText}`);
          }
          const files = await response.json();
          set({ files, isLoading: false });
        } catch (error: any) {
          set({ error: error.message, isLoading: false });
        }
      },

      deleteFile: async (filename: string) => {
        set({ isLoading: true, error: null });
        try {
          const response = await fetch(`/api/files/${encodeURIComponent(filename)}`, {
            method: 'DELETE',
          });
          if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `Failed to delete file: ${response.statusText}`);
          }
          // Refresh file list after deletion
          await get().fetchFiles();
          // If fetchFiles sets isLoading to false, no need to set it here again.
          // If not, then: set({ isLoading: false });
        } catch (error: any) {
          set({ error: error.message, isLoading: false });
        }
      },

      // addFile: (fileInfo: FileInfo) => {
      //   set((state) => ({ files: [...state.files, fileInfo] }));
      // },
    }),
    { name: 'file-store' }
  )
);
