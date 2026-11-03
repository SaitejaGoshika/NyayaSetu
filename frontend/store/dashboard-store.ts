import { create } from "zustand";

import type { AnalysisResponse } from "@/lib/types";

export type DashboardSection = "overview" | "scanner" | "predictor" | "case-desk" | "court-readiness" | "library" | "vault";

interface DashboardState {
  activeSection: DashboardSection;
  sidebarCollapsed: boolean;
  analysis: AnalysisResponse | null;
  selectedFindingId: string | null;
  setActiveSection: (section: DashboardSection) => void;
  toggleSidebar: () => void;
  setAnalysis: (analysis: AnalysisResponse | null) => void;
  setSelectedFindingId: (findingId: string | null) => void;
}

export const useDashboardStore = create<DashboardState>((set) => ({
  activeSection: "overview",
  sidebarCollapsed: false,
  analysis: null,
  selectedFindingId: null,
  setActiveSection: (activeSection) => set({ activeSection }),
  toggleSidebar: () => set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),
  setAnalysis: (analysis) => set({ analysis, selectedFindingId: analysis?.findings[0]?.id ?? null }),
  setSelectedFindingId: (selectedFindingId) => set({ selectedFindingId }),
}));
