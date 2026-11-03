"use client";

import { Activity, FileText, ShieldAlert } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useDashboardStore } from "@/store/dashboard-store";
import type { AnalysisResponse, RiskFinding } from "@/lib/types";

function HighlightedText({ text, finding }: { text: string; finding: RiskFinding | undefined }) {
  if (!finding?.matchText) return <>{text}</>;
  const start = text.toLocaleLowerCase().indexOf(finding.matchText.toLocaleLowerCase());
  if (start < 0) return <>{text}</>;
  const end = start + finding.matchText.length;
  return <>{text.slice(0, start)}<mark className="rounded-sm bg-lime px-0.5 text-foreground ring-1 ring-green/20">{text.slice(start, end)}</mark>{text.slice(end)}</>;
}

const riskVariant = { high: "high", medium: "medium", low: "low" } as const;

export function ResultsView({ analysis }: { analysis: AnalysisResponse }) {
  const selectedFindingId = useDashboardStore((state) => state.selectedFindingId);
  const setSelectedFindingId = useDashboardStore((state) => state.setSelectedFindingId);
  const setActiveSection = useDashboardStore((state) => state.setActiveSection);
  const selectedFinding = analysis.findings.find((finding) => finding.id === selectedFindingId);
  const highCount = analysis.findings.filter((finding) => finding.riskLevel === "high").length;

  return (
    <div className="rise-in">
      <div className="mb-5 flex flex-wrap items-end justify-between gap-3">
        <div>
          <p className="text-[10px] font-semibold uppercase tracking-[0.14em] text-green">Contract review</p>
          <h2 className="mt-1 max-w-[70vw] truncate text-xl font-semibold sm:text-2xl">{analysis.filename}</h2>
        </div>
        <div className="flex items-center gap-2 text-xs text-muted"><span className="size-2 rounded-full bg-green" />Analysis complete</div>
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
          <Card className="border-green-dark bg-green-dark p-4 text-white">
            <div className="flex items-start gap-3">
              <div className="grid size-8 shrink-0 place-items-center rounded-md bg-white/10 text-lime"><Activity size={16} /></div>
              <div className="min-w-0 flex-1">
                <h3 className="text-sm font-semibold">Case outcome estimate</h3>
                <p className="mt-1 text-xs leading-5 text-white/75">Explore a statistical estimate using structured case facts.</p>
                <Button className="mt-3" onClick={() => setActiveSection("predictor")} size="sm" variant="secondary">Open case predictor</Button>
              </div>
            </div>
            <p className="mt-3 border-t border-white/15 pt-3 text-[10px] leading-4 text-white/80">Statistical estimate only. Not legal advice under the Advocates Act, 1961.</p>
          </Card>
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
                key={finding.id}
                onClick={() => setSelectedFindingId(finding.id)}
                type="button"
              >
                <div className="mb-2 flex items-start justify-between gap-3">
                  <div className="flex min-w-0 items-center gap-2"><ShieldAlert className={finding.riskLevel === "high" ? "shrink-0 text-red-700" : "shrink-0 text-amber-700"} size={16} /><p className="text-sm font-semibold">{finding.title}</p></div>
                  <Badge className="shrink-0" variant={riskVariant[finding.riskLevel]}>{finding.riskLevel}</Badge>
                </div>
                <p className="text-xs leading-5 text-muted">{finding.explanation}</p>
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
