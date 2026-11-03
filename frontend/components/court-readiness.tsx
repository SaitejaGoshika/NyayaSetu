"use client";

import { useMemo, useState } from "react";
import { CalendarDays, Check, ClipboardCheck, Download, ExternalLink, Printer } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

const checklists = {
  hearing: [
    "I have reviewed the latest notice or order and confirmed the next date and purpose with my advocate.",
    "My advocate has checked which filings, replies, and copies are needed for this hearing.",
    "Relevant documents are in date order; originals are available if the court or my advocate requires them.",
    "Any service, notice, or filing steps required for my case have been checked with my advocate.",
    "I have a short timeline of key events and a list of questions for my advocate.",
    "People whose attendance or instructions may be needed have confirmed availability.",
    "I have checked court location, travel time, accessibility needs, or the official virtual-hearing instructions.",
  ],
  mediation: [
    "I understand participation and any settlement are voluntary and have discussed suitability with my advocate.",
    "I have listed the issues that may be resolved and those that remain disputed.",
    "I have organized relevant records and can explain my position without sharing unnecessary personal data.",
    "I know who has authority to discuss or approve a proposal for each party.",
    "I have considered practical options, payment or implementation steps, and what needs clarification.",
    "I have discussed confidentiality, written terms, review, and next steps with my advocate or mediator.",
    "I understand any agreement should be recorded and checked through the appropriate legal process.",
  ],
} as const;

type PreparationType = keyof typeof checklists;

export function CourtReadiness() {
  const [preparationType, setPreparationType] = useState<PreparationType>("hearing");
  const [date, setDate] = useState("");
  const [checked, setChecked] = useState<Record<string, boolean>>({});
  const [notes, setNotes] = useState("");
  const checklist = checklists[preparationType];
  const completed = useMemo(() => checklist.filter((_, index) => checked[`${preparationType}-${index}`]).length, [checked, checklist, preparationType]);

  function changePreparationType(nextType: PreparationType) {
    setPreparationType(nextType);
  }

  function downloadPlan() {
    const lines = [
      "NYAYASETU — PRIVATE PREPARATION CHECKLIST",
      `Preparation type: ${preparationType === "hearing" ? "Court hearing" : "Mediation / settlement discussion"}`,
      `Date: ${date || "Not entered"}`,
      `Checklist progress: ${completed} of ${checklist.length} items reviewed`,
      "",
      ...checklist.map((item, index) => `${checked[`${preparationType}-${index}`] ? "[x]" : "[ ]"} ${item}`),
      "",
      "Questions or neutral agenda notes:",
      notes.trim() || "(none added)",
      "",
      "Reminder: Confirm requirements, deadlines, and procedure with your advocate or the relevant court. This checklist is general information, not legal advice.",
    ];
    const file = new Blob([lines.join("\n")], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(file);
    const link = document.createElement("a");
    link.href = url;
    link.download = "nyayasetu-preparation-checklist.txt";
    document.body.append(link);
    link.click();
    link.remove();
    window.setTimeout(() => URL.revokeObjectURL(url), 1000);
  }

  return (
    <section className="rise-in mx-auto max-w-6xl">
      <div className="mb-6">
        <p className="text-[10px] font-semibold uppercase tracking-[0.14em] text-green">Court readiness</p>
        <h2 className="mt-1 text-2xl font-semibold">Arrive prepared. Avoid preventable gaps.</h2>
        <p className="mt-2 max-w-3xl text-sm leading-6 text-muted">A private, practical checklist for a hearing or a voluntary mediation conversation. It cannot confirm filing compliance or replace instructions from the court, your advocate, or mediator.</p>
      </div>

      <div className="grid items-start gap-5 lg:grid-cols-[minmax(0,1.2fr)_minmax(270px,0.8fr)]">
        <Card className="overflow-hidden">
          <div className="flex flex-wrap items-center justify-between gap-3 border-b border-line p-5">
            <div className="flex items-center gap-2"><div className="grid size-9 place-items-center rounded-md bg-mint text-green"><ClipboardCheck size={17} /></div><div><h3 className="text-sm font-semibold">Preparation checklist</h3><p className="mt-1 text-xs text-muted">Choose the next step you are preparing for</p></div></div>
            <Badge aria-live="polite" variant="neutral">{completed}/{checklist.length} reviewed</Badge>
          </div>
          <div className="space-y-3 p-5">
            <div aria-label="Preparation type" className="flex flex-wrap gap-2" role="group">
              <button aria-pressed={preparationType === "hearing"} className={`min-h-9 rounded-md px-3 text-xs font-semibold ${preparationType === "hearing" ? "bg-green text-white" : "border border-line bg-white hover:bg-mint"}`} onClick={() => changePreparationType("hearing")} type="button">Court hearing</button>
              <button aria-pressed={preparationType === "mediation"} className={`min-h-9 rounded-md px-3 text-xs font-semibold ${preparationType === "mediation" ? "bg-green text-white" : "border border-line bg-white hover:bg-mint"}`} onClick={() => changePreparationType("mediation")} type="button">Mediation discussion</button>
            </div>
            <label className="block space-y-1.5 text-xs font-medium" htmlFor="preparation-date">Date (optional)
              <input className="h-10 w-full rounded-md border border-line bg-white px-3 text-sm outline-none focus:border-green focus:ring-2 focus:ring-green/15 sm:max-w-xs" id="preparation-date" onChange={(event) => setDate(event.target.value)} type="date" value={date} />
            </label>
            <ul className="divide-y divide-line rounded-md border border-line">
              {checklist.map((item, index) => {
                const key = `${preparationType}-${index}`;
                return (
                  <li className="p-3" key={item}>
                    <label className="flex cursor-pointer items-start gap-3 text-xs leading-5">
                      <input checked={Boolean(checked[key])} className="mt-0.5 size-4 shrink-0 accent-green" onChange={(event) => setChecked((previous) => ({ ...previous, [key]: event.target.checked }))} type="checkbox" />
                      <span>{item}</span>
                    </label>
                  </li>
                );
              })}
            </ul>
            <label className="block space-y-1.5 text-xs font-medium" htmlFor="preparation-notes">Questions or neutral agenda notes (optional)
              <textarea className="min-h-24 w-full resize-y rounded-md border border-line px-3 py-2 text-sm leading-5 outline-none placeholder:text-muted focus:border-green focus:ring-2 focus:ring-green/15" id="preparation-notes" maxLength={800} onChange={(event) => setNotes(event.target.value)} placeholder="Keep notes brief. Do not include names, account numbers, privileged communications, or highly sensitive details." value={notes} />
              <span className="block text-right text-[11px] font-normal text-muted">{notes.length}/800</span>
            </label>
            <div className="flex flex-wrap gap-2 pt-1">
              <Button onClick={downloadPlan} size="sm"><Download size={14} />Download checklist</Button>
              <Button onClick={() => window.print()} size="sm" variant="secondary"><Printer size={14} />Print</Button>
            </div>
          </div>
          <p className="border-t border-line px-5 py-3 text-xs leading-5 text-muted">Privacy: this checklist stays in page memory and is not sent to the server or saved after you leave or refresh. Downloaded files are saved by your browser.</p>
        </Card>

        <div className="space-y-4">
          <Card className="p-5">
            <div className="mb-3 flex items-center gap-2"><CalendarDays className="text-green" size={17} /><h3 className="text-sm font-semibold">Check official court information</h3></div>
            <p className="text-xs leading-5 text-muted">For case status, listing details, or court services, use the official eCourts portal and confirm details with the court or your advocate. Online information may not reflect the latest update.</p>
            <a className="mt-4 inline-flex min-h-9 items-center gap-2 text-xs font-semibold text-green hover:text-green-dark" href="https://services.ecourts.gov.in/ecourtindia_v6/" rel="noreferrer" target="_blank">Open eCourts Services<ExternalLink size={13} /></a>
          </Card>
          <Card className="p-5">
            <div className="mb-3 flex items-center gap-2"><Check className="text-green" size={17} /><h3 className="text-sm font-semibold">Explore legal aid</h3></div>
            <p className="text-xs leading-5 text-muted">NALSA and State Legal Services Authorities publish information about legal services and Lok Adalats. Check eligibility and local availability directly with the relevant authority.</p>
            <a className="mt-4 inline-flex min-h-9 items-center gap-2 text-xs font-semibold text-green hover:text-green-dark" href="https://nalsa.gov.in/" rel="noreferrer" target="_blank">Visit NALSA<ExternalLink size={13} /></a>
          </Card>
          <p className="rounded-md border border-amber-200 bg-amber-50 p-4 text-xs leading-5 text-amber-950">Do not miss a court date or filing deadline based on this tool. Follow the latest court notice, applicable rules, and your advocate&apos;s advice. Mediation is not suitable or available for every matter.</p>
        </div>
      </div>
    </section>
  );
}
