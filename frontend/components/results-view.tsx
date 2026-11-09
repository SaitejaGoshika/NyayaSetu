"use client";

import { useEffect } from "react";
import { FileText, ShieldAlert } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { exportDocumentReport } from "@/lib/api";
import type { AnalysisResponse, RiskFinding } from "@/lib/types";
import { useDashboardStore } from "@/store/dashboard-store";

function HighlightedText({ text, finding }: { text: string; finding: RiskFinding | undefined }) {
  if (!finding || !Number.isFinite(finding.start) || !Number.isFinite(finding.end)) return <>{text}</>;
  const start = Math.max(0, Math.min(finding.start, text.length));
  const end = Math.max(start, Math.min(finding.end, text.length));
  if (start >= end || end <= start) return <>{text}</>;
  return <>{text.slice(0, start)}<mark className="rounded-sm bg-lime px-0.5 text-foreground ring-1 ring-green/20">{text.slice(start, end)}</mark>{text.slice(end)}</>;
}

const riskVariant = { high: "high", medium: "medium", low: "low" } as const;

export function ResultsView({ analysis }: { analysis: AnalysisResponse }) {
  const selectedFindingId = useDashboardStore((state) => state.selectedFindingId);
  const setSelectedFindingId = useDashboardStore((state) => state.setSelectedFindingId);
  const selectedFinding = analysis.findings.find((finding) => finding.id === selectedFindingId);
  const highCount = analysis.findings.filter((finding) => finding.riskLevel === "high").length;

  useEffect(() => {
    if (!selectedFindingId) return;
    const node = document.getElementById(`finding-${selectedFindingId}`) as HTMLButtonElement | null;
    if (node) node.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }, [selectedFindingId]);

  return (
    <div className="rise-in">
      <div className="mb-5 flex flex-wrap items-end justify-between gap-3">
        <div>
          <p className="text-[10px] font-semibold uppercase tracking-[0.14em] text-green">Contract review</p>
          <h2 className="mt-1 max-w-[70vw] truncate text-xl font-semibold sm:text-2xl">{analysis.filename}</h2>
        </div>
        <div className="flex flex-wrap items-center gap-2 text-xs text-muted">
          <span className="size-2 rounded-full bg-green" />Analysis complete
          <Button className="h-8 px-3 text-[11px]" onClick={() => exportDocumentReport(analysis.documentId, "pdf")} size="sm" variant="secondary">Export PDF</Button>
          <Button className="h-8 px-3 text-[11px]" onClick={() => exportDocumentReport(analysis.documentId, "docx")} size="sm" variant="secondary">Export DOCX</Button>
        </div>
      </div>
      <div className="grid items-start gap-4 xl:grid-cols-[minmax(0,1.35fr)_minmax(320px,0.8fr)]">
        <Card className="overflow-hidden">
          <div className="flex items-center justify-between border-b border-line px-5 py-3.5">
            <div className="flex items-center gap-2"><FileText className="text-green" size={16} /><h3 className="text-sm font-semibold">Document text</h3></div>
            <span className="text-[11px] text-muted">{analysis.extractedText.length.toLocaleString()} characters</span>
          </div>
          <div className="max-h-[70vh] min-h-[440px] overflow-auto bg-[#fbfcfb] px-5 py-6 sm:px-8">
            {analysis.extractedText ? (
              <div className="mx-auto max-w-[68ch] whitespace-pre-wrap font-serif text-[14px] leading-7 text-[#33413a]">
                <HighlightedText finding={selectedFinding} text={analysis.extractedText} />
              </div>
            ) : (
              <div className="grid min-h-[380px] place-items-center text-center">
                <div className="max-w-xs"><FileText className="mx-auto mb-3 text-muted" size={24} /><p className="text-sm font-medium">No selectable text found</p><p className="mt-1 text-xs leading-5 text-muted">This document may be image-only. OCR processing is not enabled in this foundation.</p></div>
              </div>
            )}
          </div>
        </Card>
        <div className="space-y-3">
          <div className="flex items-center justify-between px-1">
            <div><h3 className="text-sm font-semibold">Review signals</h3><p className="mt-0.5 text-xs text-muted">Rule-based screening, not legal conclusions</p></div>
            <Badge variant={highCount ? "high" : "neutral"}>{analysis.findings.length} found</Badge>
          </div>
          {analysis.findings.length ? analysis.findings.map((finding) => {
            const selected = finding.id === selectedFindingId;
            return (
              <button
                aria-pressed={selected}
                className={`w-full rounded-lg border bg-white p-4 text-left transition hover:border-green/50 hover:shadow-sm ${selected ? "border-green ring-1 ring-green/20" : "border-line"}`}
                id={`finding-${finding.id}`}
                key={finding.id}
                onClick={() => setSelectedFindingId(finding.id)}
                type="button"
              >
                <div className="mb-2 flex items-start justify-between gap-3">
                  <div className="flex min-w-0 items-center gap-2"><ShieldAlert className={finding.riskLevel === "high" ? "shrink-0 text-red-700" : "shrink-0 text-amber-700"} size={16} /><p className="text-sm font-semibold">{finding.title}</p></div>
                  <Badge className="shrink-0" variant={riskVariant[finding.riskLevel]}>{finding.riskLevel}</Badge>
                </div>
                {finding.status && (
                  <div className="mb-2 flex flex-wrap gap-2 text-[10px] font-medium">
                    <Badge variant="neutral">{finding.status === "draft" ? "Draft rule" : `Reviewed by ${finding.reviewedBy ?? "advocate"}`}</Badge>
                    {finding.needsCitationCheck && <Badge variant="neutral">Citation check needed</Badge>}
                  </div>
                )}
                <p className="text-xs leading-5 text-muted">{finding.explanation}</p>
                {finding.whatToAsk && <p className="mt-2 text-[11px] leading-5 text-[#3e4d45]"><span className="font-semibold text-green">Ask:</span> {finding.whatToAsk}</p>}
                <p className="mt-3 border-t border-line pt-2.5 text-[11px] font-medium text-green">{finding.legalBasis}</p>
                <p className="mt-2 line-clamp-2 rounded bg-[#f4f7f4] px-2.5 py-2 font-mono text-[10px] leading-4 text-[#526159]">{finding.matchText}</p>
              </button>
            );
          }) : (
            <Card className="grid min-h-40 place-items-center p-6 text-center">
              <div><div className="mx-auto mb-2 grid size-9 place-items-center rounded-full bg-mint text-green"><ShieldAlert size={17} /></div><p className="text-sm font-semibold">No configured signals matched</p><p className="mt-1 max-w-[240px] text-xs leading-5 text-muted">A clean scan is not a legal clearance. Review the complete contract with qualified counsel.</p></div>
            </Card>
          )}
          <p className="px-1 text-[10px] leading-4 text-muted">Select a signal to locate its matching text. Rule coverage is limited and should be reviewed by qualified Indian counsel.</p>
        </div>
      </div>
    </div>
  );
}
