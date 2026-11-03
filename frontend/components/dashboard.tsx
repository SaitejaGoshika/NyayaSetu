"use client";

import { useEffect, useState, type ComponentType } from "react";
import {
  Activity,
  Archive,
  ArrowDownToLine,
  ArrowUpRight,
  BookOpen,
  ChevronLeft,
  ChevronRight,
  ClipboardList,
  ClipboardCheck,
  FileCheck2,
  FileClock,
  FileText,
  FolderLock,
  LayoutDashboard,
  Menu,
  Scale,
  ShieldCheck,
  Sparkles,
  TriangleAlert,
  Upload,
} from "lucide-react";

import { AuthControls } from "@/components/auth-controls";
import { useAuth } from "@/components/auth-provider";
import { CaseDesk } from "@/components/case-desk";
import { CourtReadiness } from "@/components/court-readiness";
import { Dropzone } from "@/components/dropzone";
import { LawLibrary } from "@/components/law-library";
import { JudgmentReaderPanel } from "@/components/judgment-reader-panel";
import { ResultsView } from "@/components/results-view";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { analyzeDocument, listDocuments } from "@/lib/api";
import type { AnalysisResponse, DocumentRecord } from "@/lib/types";
import { useDashboardStore, type DashboardSection } from "@/store/dashboard-store";

interface NavigationItem {
  id: DashboardSection;
  label: string;
  icon: ComponentType<{ size?: number; "aria-hidden"?: boolean }>;
}

const navigation: NavigationItem[] = [
  { id: "overview", label: "Overview", icon: LayoutDashboard },
  { id: "scanner", label: "Contract scanner", icon: FileCheck2 },
  { id: "predictor", label: "Judgment reader", icon: Scale },
  { id: "case-desk", label: "Case desk", icon: ClipboardList },
  { id: "court-readiness", label: "Court readiness", icon: ClipboardCheck },
  { id: "library", label: "Law library", icon: BookOpen },
  { id: "vault", label: "Secure vault", icon: FolderLock },
];

const sectionTitle: Record<DashboardSection, string> = {
  overview: "Overview",
  scanner: "Contract scanner",
  predictor: "Judgment reader",
  "case-desk": "Case desk",
  "court-readiness": "Court readiness",
  library: "Law library",
  vault: "Secure vault",
};

function formatDate(value: string) {
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? "Date unavailable" : date.toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" });
}

export default function Dashboard() {
  const { user, authReady, authError } = useAuth();
  const activeSection = useDashboardStore((state) => state.activeSection);
  const setActiveSection = useDashboardStore((state) => state.setActiveSection);
  const sidebarCollapsed = useDashboardStore((state) => state.sidebarCollapsed);
  const toggleSidebar = useDashboardStore((state) => state.toggleSidebar);
  const analysis = useDashboardStore((state) => state.analysis);
  const setAnalysis = useDashboardStore((state) => state.setAnalysis);
  const [mobileNavOpen, setMobileNavOpen] = useState(false);
  const [documentSnapshot, setDocumentSnapshot] = useState<{ uid: string; documents: DocumentRecord[] } | null>(null);
  const [documentErrorState, setDocumentErrorState] = useState<{ uid: string; message: string } | null>(null);
  const [openingId, setOpeningId] = useState("");
  const documents = user && documentSnapshot?.uid === user.uid ? documentSnapshot.documents : [];
  const documentError = user && documentErrorState?.uid === user.uid ? documentErrorState.message : "";
  const shouldLoadDocuments = Boolean(user && (activeSection === "overview" || activeSection === "vault"));
  const documentsLoading = Boolean(shouldLoadDocuments && documentSnapshot?.uid !== user?.uid && !documentError);

  useEffect(() => {
    if (!user || (activeSection !== "overview" && activeSection !== "vault")) return;
    let cancelled = false;
    void listDocuments()
      .then((result) => {
        if (!cancelled) setDocumentSnapshot({ uid: user.uid, documents: result });
      })
      .catch((error: unknown) => {
        if (!cancelled) setDocumentErrorState({ uid: user.uid, message: error instanceof Error ? error.message : "Document history is unavailable." });
      });
    return () => { cancelled = true; };
  }, [activeSection, user]);

  function navigate(section: DashboardSection) {
    setActiveSection(section);
    setMobileNavOpen(false);
  }

  function handleAnalysis(nextAnalysis: AnalysisResponse) {
    setAnalysis(nextAnalysis);
    setActiveSection("scanner");
  }

  async function openDocument(documentId: string) {
    if (!user) return;
    setOpeningId(documentId);
    try {
      const result = await analyzeDocument(documentId);
      handleAnalysis(result);
    } catch (error) {
      setDocumentErrorState({ uid: user.uid, message: error instanceof Error ? error.message : "The document could not be opened." });
    } finally {
      setOpeningId("");
    }
  }

  return (
    <div className="min-h-screen bg-background text-foreground">
      {mobileNavOpen && <button aria-label="Close navigation" className="fixed inset-0 z-30 bg-slate-950/30 md:hidden" onClick={() => setMobileNavOpen(false)} type="button" />}
      <aside className={`fixed inset-y-0 left-0 z-40 flex flex-col border-r border-line bg-white transition-[width,transform] duration-200 md:translate-x-0 ${mobileNavOpen ? "translate-x-0" : "-translate-x-full"} ${sidebarCollapsed ? "w-[76px]" : "w-[248px]"}`}>
        <div className={`flex h-[72px] items-center border-b border-line ${sidebarCollapsed ? "justify-center px-3" : "gap-3 px-5"}`}>
          <div className="grid size-9 shrink-0 place-items-center rounded-lg bg-green text-white"><ShieldCheck aria-hidden="true" size={19} /></div>
          {!sidebarCollapsed && <div className="min-w-0"><p className="text-[15px] font-bold leading-5">NyayaSetu</p><p className="text-[10px] font-medium uppercase tracking-[0.12em] text-muted">Contract intelligence</p></div>}
        </div>
        <div className={`px-3 pt-6 ${sidebarCollapsed ? "text-center" : ""}`}>
          {!sidebarCollapsed && <p className="px-2 pb-2 text-[10px] font-semibold uppercase tracking-[0.14em] text-muted">Workspace</p>}
          <nav aria-label="Main navigation" className="space-y-1">
            {navigation.map(({ id, label, icon: Icon }) => {
              const selected = activeSection === id;
              return (
                <button aria-current={selected ? "page" : undefined} aria-label={sidebarCollapsed ? label : undefined} className={`flex h-10 w-full items-center gap-3 rounded-md px-3 text-left text-[13px] transition ${selected ? "bg-mint font-semibold text-green-dark" : "text-[#56645d] hover:bg-[#f4f7f4] hover:text-foreground"} ${sidebarCollapsed ? "justify-center px-0" : ""}`} key={id} onClick={() => navigate(id)} title={sidebarCollapsed ? label : undefined} type="button">
                  <Icon aria-hidden size={17} />
                  {!sidebarCollapsed && <span>{label}</span>}
                  {id === "vault" && !sidebarCollapsed && documents.length > 0 && <span className="ml-auto text-[10px] text-muted">{documents.length}</span>}
                </button>
              );
            })}
          </nav>
        </div>
        <div className="mt-auto p-3">
          {!sidebarCollapsed && (
            <div className="rounded-md border border-line bg-[#f7faf7] p-3">
              <div className="mb-2 flex items-center gap-2 text-green"><LockLabelIcon /><p className="text-xs font-semibold text-foreground">Private workspace</p></div>
              <p className="text-[11px] leading-5 text-muted">Documents are stored under your signed-in account.</p>
            </div>
          )}
          <Button aria-label={sidebarCollapsed ? "Expand sidebar" : "Collapse sidebar"} className={`mt-3 w-full ${sidebarCollapsed ? "" : "justify-start"}`} onClick={toggleSidebar} size={sidebarCollapsed ? "icon" : "sm"} variant="ghost">
            {sidebarCollapsed ? <ChevronRight aria-hidden size={16} /> : <><ChevronLeft aria-hidden size={15} /><span>Collapse sidebar</span></>}
          </Button>
        </div>
      </aside>

      <div className={`min-h-screen transition-[padding] duration-200 ${sidebarCollapsed ? "md:pl-[76px]" : "md:pl-[248px]"}`}>
        <header className="sticky top-0 z-20 flex h-[72px] items-center justify-between border-b border-line bg-white/95 px-4 backdrop-blur sm:px-7">
          <div className="flex min-w-0 items-center gap-3">
            <Button aria-label="Open navigation" className="md:hidden" onClick={() => setMobileNavOpen(true)} size="icon" variant="ghost"><Menu aria-hidden size={18} /></Button>
            <div className="min-w-0"><p className="truncate text-xs text-muted">Workspace / {sectionTitle[activeSection]}</p><h1 className="truncate text-sm font-semibold sm:text-base">{sectionTitle[activeSection]}</h1></div>
          </div>
          <div className="flex items-center gap-3"><div className="hidden items-center gap-1.5 rounded-full bg-[#f3f7f4] px-2.5 py-1.5 text-[10px] font-medium text-muted sm:flex"><span className={`size-1.5 rounded-full ${user ? "bg-green" : "bg-amber-500"}`} />{authReady ? (user ? "Secure session" : "Sign in required") : "Checking session"}</div><AuthControls /></div>
        </header>

        <main className="mx-auto max-w-[1500px] px-4 py-6 sm:px-7 sm:py-8">
          {authError && <p className="mb-5 rounded-md border border-red-200 bg-red-50 p-3 text-xs leading-5 text-red-800" role="alert">The workspace API could not be reached: {authError}</p>}
          {activeSection === "overview" && (
            <section className="rise-in">
              <div className="mb-6 flex flex-wrap items-end justify-between gap-3">
                <div><p className="text-[10px] font-semibold uppercase tracking-[0.14em] text-green">SME legal workspace</p><h2 className="mt-1 text-2xl font-semibold sm:text-[28px]">A clearer view of your contracts</h2><p className="mt-1.5 text-sm text-muted">Screen key clauses, understand review signals, and keep your documents in one local workspace.</p></div>
                <Badge variant="neutral"><ShieldCheck size={13} />Locally stored data</Badge>
              </div>
              {!user && authReady && <div className="mb-5 flex items-start gap-3 rounded-md border border-amber-200 bg-amber-50 p-3.5 text-sm text-amber-950"><TriangleAlert className="mt-0.5 shrink-0" size={16} /><p>Sign in before uploading or viewing documents. The API requires a valid local session.</p></div>}
              <div className="grid items-start gap-5 xl:grid-cols-[minmax(0,1.35fr)_minmax(300px,0.8fr)]">
                <Card className="overflow-hidden">
                  <div className="flex flex-wrap items-center justify-between gap-2 border-b border-line px-5 py-4">
                    <div className="flex items-center gap-2"><div className="grid size-8 place-items-center rounded-md bg-mint text-green"><Upload size={15} /></div><div><h3 className="text-sm font-semibold">Start a contract review</h3><p className="text-[11px] text-muted">A copy is stored in this workspace</p></div></div>
                    <Button onClick={() => navigate("scanner")} size="sm" variant="ghost">Open scanner<ArrowUpRight size={14} /></Button>
                  </div>
                  <div className="p-5"><Dropzone onAnalysis={handleAnalysis} /></div>
                </Card>
                <Card className="overflow-hidden">
                  <div className="flex items-center justify-between border-b border-line px-5 py-4"><div><h3 className="text-sm font-semibold">Recent documents</h3><p className="mt-1 text-[11px] text-muted">Your account&apos;s stored files</p></div><Button aria-label="Open secure vault" onClick={() => navigate("vault")} size="icon" title="Open secure vault" variant="ghost"><Archive size={16} /></Button></div>
                  <div className="divide-y divide-line">
                    {!user ? <EmptyDocuments message="Sign in to see documents in your vault." /> : documentsLoading ? <div className="px-5 py-8 text-center text-xs text-muted">Loading your documents...</div> : documents.length ? documents.slice(0, 5).map((document) => <DocumentRow document={document} key={document.documentId} loading={openingId === document.documentId} onOpen={() => void openDocument(document.documentId)} />) : <EmptyDocuments message={documentError || "Your vault is ready for its first document."} />}
                  </div>
                  {documents.length > 5 && <button className="flex w-full items-center justify-center gap-1 border-t border-line py-3 text-xs font-medium text-green hover:bg-[#f7faf7]" onClick={() => navigate("vault")} type="button">View all documents<ArrowUpRight size={13} /></button>}
                </Card>
              </div>
              <div className="mt-5 grid gap-3 sm:grid-cols-3">
                <CoverageItem icon={FileClock} label="Payment terms" detail="MSME 45-day screening signal" />
                <CoverageItem icon={Scale} label="Exit provisions" detail="Lock-in and termination wording" />
                <CoverageItem icon={Activity} label="GST references" detail="Invoice and tax allocation signals" />
              </div>
            </section>
          )}

          {activeSection === "scanner" && (
            analysis ? <ResultsView analysis={analysis} /> : (
              <div className="rise-in mx-auto grid max-w-5xl items-start gap-5 lg:grid-cols-[minmax(0,1.25fr)_minmax(260px,0.75fr)]">
                <div><div className="mb-5"><p className="text-[10px] font-semibold uppercase tracking-[0.14em] text-green">Contract scanner</p><h2 className="mt-1 text-2xl font-semibold">Upload for a clause review</h2><p className="mt-1.5 text-sm text-muted">PDF and DOCX documents are validated before they are stored and analyzed.</p></div><Dropzone onAnalysis={handleAnalysis} /></div>
                <Card className="mt-1">
                  <div className="border-b border-line p-5"><div className="mb-2 grid size-8 place-items-center rounded-md bg-mint text-green"><Sparkles size={16} /></div><h3 className="text-sm font-semibold">Screening coverage</h3><p className="mt-1 text-xs leading-5 text-muted">Current rules flag review signals only. They do not determine legality or replace counsel.</p></div>
                  <div className="space-y-4 p-5"><CoverageItem icon={FileClock} label="MSME payment terms" detail="Potential terms beyond 45 days" compact /><CoverageItem icon={Scale} label="Lock-in and termination" detail="Duration, exit cost, unilateral rights" compact /><CoverageItem icon={Activity} label="GST references" detail="Tax invoices and registration" compact /></div>
                </Card>
              </div>
            )
          )}

          {activeSection === "predictor" && <JudgmentReaderPanel />}

          {activeSection === "case-desk" && <CaseDesk />}

          {activeSection === "court-readiness" && <CourtReadiness />}

          {activeSection === "library" && <LawLibrary />}

          {activeSection === "vault" && (
            <section className="rise-in mx-auto max-w-5xl">
              <div className="mb-6 flex flex-wrap items-end justify-between gap-3"><div><p className="text-[10px] font-semibold uppercase tracking-[0.14em] text-green">Secure vault</p><h2 className="mt-1 text-2xl font-semibold">Your document history</h2><p className="mt-1.5 text-sm text-muted">Documents are scoped to your local account.</p></div><Badge variant="neutral"><FolderLock size={13} />{user ? `${documents.length} documents` : "Sign in required"}</Badge></div>
              {documentError && <p className="mb-4 rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-800" role="alert">{documentError}</p>}
              <Card className="overflow-hidden">
                {!user ? <EmptyDocuments message="Sign in to securely view your document history." /> : documentsLoading ? <div className="p-10 text-center text-sm text-muted">Loading your secure vault...</div> : documents.length ? <div className="divide-y divide-line">{documents.map((document) => <DocumentRow document={document} key={document.documentId} loading={openingId === document.documentId} onOpen={() => void openDocument(document.documentId)} />)}</div> : <EmptyDocuments message="No documents in your vault yet. Upload a PDF or DOCX to get started." />}
              </Card>
              <p className="mt-3 text-xs text-muted">History is stored in SQLite. Document files are kept in the local data directory.</p>
            </section>
          )}
        </main>
      </div>
    </div>
  );
}

function LockLabelIcon() {
  return <ShieldCheck aria-hidden="true" size={14} />;
}

function EmptyDocuments({ message }: { message: string }) {
  return <div className="grid min-h-36 place-items-center px-6 py-8 text-center"><div><div className="mx-auto mb-2 grid size-9 place-items-center rounded-full bg-[#f1f5f2] text-muted"><FolderLock size={16} /></div><p className="max-w-xs text-xs leading-5 text-muted">{message}</p></div></div>;
}

function DocumentRow({ document, loading, onOpen }: { document: DocumentRecord; loading: boolean; onOpen: () => void }) {
  return (
    <div className="flex items-center gap-3 px-4 py-3.5 sm:px-5">
      <div className="grid size-9 shrink-0 place-items-center rounded-md bg-[#f2f6f3] text-green"><FileText size={16} /></div>
      <div className="min-w-0 flex-1"><p className="truncate text-xs font-semibold">{document.filename}</p><p className="mt-1 text-[10px] text-muted">{formatDate(document.createdAt)} · {document.status}</p></div>
      <Button aria-label={`Open ${document.filename}`} disabled={loading} onClick={onOpen} size="icon" title="Open and analyze document" variant="ghost">{loading ? <span className="size-3 animate-spin rounded-full border-2 border-green border-r-transparent" /> : <ArrowDownToLine size={15} />}</Button>
    </div>
  );
}

function CoverageItem({ icon: Icon, label, detail, compact = false }: { icon: ComponentType<{ size?: number; className?: string }>; label: string; detail: string; compact?: boolean }) {
  return <div className={`flex items-start gap-3 ${compact ? "" : "rounded-md border border-line bg-white px-4 py-3"}`}><div className="mt-0.5 grid size-7 shrink-0 place-items-center rounded-md bg-mint text-green"><Icon aria-hidden size={14} /></div><div><p className="text-xs font-semibold">{label}</p><p className="mt-0.5 text-[11px] leading-4 text-muted">{detail}</p></div></div>;
}
