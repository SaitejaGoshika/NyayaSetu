"use client";

import { useState, type FormEvent } from "react";
import { ArrowRight, CheckCircle2, ClipboardList, FileText, ShieldAlert } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

const caseTypes = {
  civil: {
    label: "Civil dispute",
    documents: ["Court notices, orders, and case number", "Contracts, correspondence, and dated records", "A timeline of events and claimed loss"],
    actions: ["Check every court notice for a response date with your advocate.", "Arrange the facts and supporting records in date order.", "Ask counsel which court or forum has jurisdiction and whether any time limit applies."],
    resolution: "Ask counsel whether negotiation, mediation, Lok Adalat, or another lawful settlement route fits this dispute.",
  },
  commercial: {
    label: "Commercial or contract dispute",
    documents: ["Signed agreement and amendments", "Invoices, payment records, and delivery or acceptance proof", "Notices sent, replies received, and any dispute-resolution clause"],
    actions: ["Compare each disputed obligation with the agreement and its amendments.", "Prepare a dated ledger of amounts claimed, paid, and still disputed.", "Have counsel review notice requirements, limitation, forum, and any arbitration clause."],
    resolution: "Depending on the agreement and dispute, counsel can assess negotiation, mediation, pre-institution mediation where applicable, or arbitration.",
  },
  criminal: {
    label: "Criminal matter",
    documents: ["FIR or complaint details, police-station details, and case number if available", "Court orders, summons, and dates for any appearance", "Original messages, records, or other material relevant to the matter"],
    actions: ["Contact a qualified criminal advocate promptly, especially if a notice, summons, or court date is near.", "Keep original records unchanged and share them privately with your advocate.", "Do not publish case details or contact other parties about the matter without legal advice."],
    resolution: "Criminal proceedings are not generally resolved through private settlement alone. Ask a qualified advocate whether any lawful compounding or other route applies to the specific offence.",
  },
  consumer: {
    label: "Consumer dispute",
    documents: ["Invoice, order confirmation, and proof of payment", "Warranty, service records, and complaint reference numbers", "Copies of messages, notices, and the response from the seller or provider"],
    actions: ["Write down the purchase date, issue, attempts to resolve it, and the remedy sought.", "Keep copies of receipts, product records, and complaint acknowledgements.", "Ask counsel or an official consumer resource about the appropriate commission, filing steps, and time limits."],
    resolution: "A direct complaint process or mediation may be available depending on the dispute. Confirm the current official process before filing.",
  },
  family: {
    label: "Family matter",
    documents: ["Existing court orders, notices, and case numbers", "Relevant financial records and dated communications", "A list of questions and practical arrangements to discuss with counsel"],
    actions: ["Have an advocate review any order or deadline before taking action.", "Keep records relevant to the matter securely and avoid sharing them publicly.", "If anyone is in immediate danger, contact local emergency services and a qualified advocate."],
    resolution: "Where safe and legally suitable, counsel can explain whether counselling or mediation is available. Participation should be voluntary and informed.",
  },
} as const;

type CaseType = keyof typeof caseTypes;

export function CaseDesk() {
  const [caseType, setCaseType] = useState<CaseType>("civil");
  const [facts, setFacts] = useState("");
  const [deadline, setDeadline] = useState("unknown");
  const [prepared, setPrepared] = useState(false);
  const [error, setError] = useState("");
  const selectedCase = caseTypes[caseType];

  function prepareBrief(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (facts.trim().length < 20) {
      setError("Add at least 20 characters so you have a useful summary to review.");
      setPrepared(false);
      return;
    }
    setError("");
    setPrepared(true);
  }

  return (
    <section className="rise-in mx-auto max-w-6xl">
      <div className="mb-6">
        <p className="text-[10px] font-semibold uppercase tracking-[0.14em] text-green">Case desk</p>
        <h2 className="mt-1 text-2xl font-semibold">Turn case facts into a clearer brief</h2>
        <p className="mt-2 max-w-3xl text-sm leading-6 text-muted">Organize what happened, gather relevant records, and prepare questions for a qualified advocate. This tool does not predict a court decision or determine your legal rights.</p>
      </div>

      <div className="grid items-start gap-5 lg:grid-cols-[minmax(0,1.1fr)_minmax(280px,0.9fr)]">
        <Card className="p-5 sm:p-6">
          <form className="space-y-5" onSubmit={prepareBrief}>
            <label className="block space-y-1.5 text-sm font-medium" htmlFor="case-type">
              Matter type
              <select className="h-10 w-full rounded-md border border-line bg-white px-3 text-sm outline-none focus:border-green focus:ring-2 focus:ring-green/15" id="case-type" onChange={(event) => setCaseType(event.target.value as CaseType)} value={caseType}>
                {Object.entries(caseTypes).map(([value, matter]) => <option key={value} value={value}>{matter.label}</option>)}
              </select>
            </label>

            <label className="block space-y-1.5 text-sm font-medium" htmlFor="case-deadline">
              Is there a known upcoming date or deadline?
              <select className="h-10 w-full rounded-md border border-line bg-white px-3 text-sm outline-none focus:border-green focus:ring-2 focus:ring-green/15" id="case-deadline" onChange={(event) => setDeadline(event.target.value)} value={deadline}>
                <option value="unknown">Not sure / no known date</option>
                <option value="urgent">Within 7 days</option>
                <option value="soon">Within 30 days</option>
                <option value="later">More than 30 days away</option>
              </select>
            </label>

            <label className="block space-y-1.5 text-sm font-medium" htmlFor="case-facts">
              Briefly describe what happened and what you need help with
              <textarea className="min-h-36 w-full resize-y rounded-md border border-line px-3 py-2.5 text-sm leading-6 outline-none placeholder:text-muted/80 focus:border-green focus:ring-2 focus:ring-green/15" id="case-facts" maxLength={1500} onChange={(event) => setFacts(event.target.value)} placeholder="Include key dates, what each side did, any notices or orders, and your main question. Avoid names, account numbers, or other sensitive personal details." required value={facts} />
              <span className="block text-right text-[11px] font-normal text-muted">{facts.length}/1,500</span>
            </label>

            {error && <p className="rounded-md border border-red-200 bg-red-50 p-3 text-xs leading-5 text-red-800" role="alert">{error}</p>}
            <Button className="w-full sm:w-auto" type="submit"><ClipboardList size={15} />Prepare my case brief<ArrowRight size={14} /></Button>
          </form>
          <p className="mt-4 border-t border-line pt-4 text-xs leading-5 text-muted">Privacy: your notes stay in this browser session; they are not sent to the server or saved by this page. Avoid entering sensitive personal information.</p>
        </Card>

        <div className="space-y-4">
          {prepared ? (
            <Card className="overflow-hidden">
              <div className="border-b border-line px-5 py-4">
                <div className="mb-2 flex items-center gap-2 text-green"><CheckCircle2 size={16} /><Badge variant="low">Preparation guide</Badge></div>
                <h3 className="text-sm font-semibold">Your {selectedCase.label.toLowerCase()} brief</h3>
                <p className="mt-1 text-xs leading-5 text-muted">Use this checklist to prepare for a conversation with an advocate. It is not a merits assessment.</p>
              </div>
              <div className="space-y-5 p-5">
                <div><h4 className="mb-2 text-xs font-semibold">Your notes</h4><p className="whitespace-pre-wrap break-words rounded-md bg-[#f7faf7] p-3 text-xs leading-5 text-muted">{facts.trim()}</p></div>
                <div><h4 className="mb-2 text-xs font-semibold">Documents to gather</h4><ul className="space-y-2">{selectedCase.documents.map((item) => <li className="flex items-start gap-2 text-xs leading-5 text-muted" key={item}><FileText className="mt-0.5 shrink-0 text-green" size={13} />{item}</li>)}</ul></div>
                <div><h4 className="mb-2 text-xs font-semibold">Questions and next steps</h4><ul className="space-y-2">{selectedCase.actions.map((item) => <li className="flex items-start gap-2 text-xs leading-5 text-muted" key={item}><span className="mt-1.5 size-1.5 shrink-0 rounded-full bg-green" />{item}</li>)}</ul></div>
                <div className="rounded-md border border-line bg-[#f7faf7] p-3"><h4 className="text-xs font-semibold">Resolution options to discuss</h4><p className="mt-1.5 text-xs leading-5 text-muted">{selectedCase.resolution}</p></div>
              </div>
            </Card>
          ) : (
            <Card className="p-5">
              <div className="mb-3 grid size-9 place-items-center rounded-md bg-mint text-green"><ClipboardList size={17} /></div>
              <h3 className="text-sm font-semibold">A calmer first step</h3>
              <p className="mt-1.5 text-xs leading-5 text-muted">Share only what is needed to organize your preparation. Your notes stay on this page and are cleared when you leave or refresh it.</p>
              <div className="mt-4 rounded-md border border-line p-3"><p className="text-xs font-medium">A useful summary includes</p><p className="mt-1 text-xs leading-5 text-muted">Key dates · notices or orders · documents available · the outcome you are seeking</p></div>
            </Card>
          )}

          {deadline === "urgent" && (
            <div className="flex items-start gap-3 rounded-md border border-amber-200 bg-amber-50 p-4 text-amber-950" role="status">
              <ShieldAlert className="mt-0.5 shrink-0" size={16} />
              <p className="text-xs leading-5"><strong>Time-sensitive:</strong> You selected a date within 7 days. Verify it directly from the court notice or order and contact a qualified advocate promptly. This tool cannot check or extend deadlines.</p>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
