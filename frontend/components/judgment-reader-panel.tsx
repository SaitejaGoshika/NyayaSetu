"use client";

import { useState, type FormEvent } from "react";
import { AlertCircle, Scale, SearchCheck, TriangleAlert } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { findDispositionMentions, type DispositionMention } from "@/lib/judgment-disposition";

const MAX_JUDGMENT_LENGTH = 100_000;

export function JudgmentReaderPanel() {
  const [judgmentText, setJudgmentText] = useState("");
  const [mentions, setMentions] = useState<DispositionMention[]>([]);
  const [analyzed, setAnalyzed] = useState(false);

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setMentions(findDispositionMentions(judgmentText));
    setAnalyzed(true);
  }

  return (
    <div className="rise-in mx-auto max-w-4xl">
      <div className="mb-6">
        <p className="text-[10px] font-semibold uppercase tracking-[0.14em] text-green">Published judgment reader</p>
        <h2 className="mt-1 text-2xl font-semibold">Find recorded disposition language</h2>
        <p className="mt-2 max-w-2xl text-sm leading-6 text-muted">Scan a published judgment for explicit outcome phrases. This does not predict how a pending case will be decided or interpret the court&apos;s reasoning.</p>
      </div>
      <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_minmax(260px,0.75fr)]">
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2"><Scale aria-hidden className="text-green" size={17} /><CardTitle>Published judgment text</CardTitle></div>
            <CardDescription>Text stays in this browser; the reader does not send it to the API or save it.</CardDescription>
          </CardHeader>
          <CardContent>
            <form className="space-y-4" onSubmit={handleSubmit}>
              <label className="block space-y-1.5 text-sm font-medium" htmlFor="judgment-text">
                Judgment text
                <textarea
                  className="min-h-64 w-full resize-y rounded-md border border-line px-3 py-2 text-sm leading-6 outline-none focus:border-green focus:ring-2 focus:ring-green/15"
                  id="judgment-text"
                  maxLength={MAX_JUDGMENT_LENGTH}
                  onChange={(event) => {
                    setJudgmentText(event.target.value);
                    setAnalyzed(false);
                  }}
                  placeholder="Paste text from an already-published judgment..."
                  required
                  value={judgmentText}
                />
              </label>
              <p className="text-right text-xs text-muted">{judgmentText.length.toLocaleString()} / {MAX_JUDGMENT_LENGTH.toLocaleString()} characters</p>
              <Button className="w-full" disabled={!judgmentText.trim()} type="submit"><SearchCheck aria-hidden size={15} />Scan for disposition phrases</Button>
            </form>
          </CardContent>
        </Card>
        <Card className="flex flex-col">
          <CardHeader>
            <CardTitle>Recognized phrases</CardTitle>
            <CardDescription>Exact text matches, shown from the last occurrence to the first.</CardDescription>
          </CardHeader>
          <CardContent className="flex-1">
            {analyzed && mentions.length > 0 ? (
              <ol className="space-y-3">
                {mentions.map((mention) => (
                  <li className="rounded-md border border-line bg-[#f8faf8] p-3" key={`${mention.position}-${mention.phrase}`}>
                    <p className="mb-1 text-xs font-semibold text-foreground">{mention.phrase}</p>
                    <p className="text-xs leading-5 text-muted">{mention.excerpt}</p>
                  </li>
                ))}
              </ol>
            ) : analyzed ? (
              <div className="flex items-start gap-2 rounded-md border border-line bg-[#f8faf8] p-3 text-xs leading-5 text-muted" role="status">
                <AlertCircle aria-hidden className="mt-0.5 shrink-0" size={14} />
                No recognized disposition phrases were found. This reader only checks for a limited list of explicit terms.
              </div>
            ) : (
              <div className="grid min-h-36 place-items-center rounded-md border border-dashed border-line bg-[#f8faf8] px-4 text-center">
                <div><SearchCheck aria-hidden className="mx-auto mb-2 text-muted" size={20} /><p className="text-xs leading-5 text-muted">Recognized phrases will appear here after scanning the text.</p></div>
              </div>
            )}
          </CardContent>
          <div className="mx-5 mb-5 rounded-md border border-amber-200 bg-amber-50 p-3">
            <Badge className="mb-2" variant="medium">Important</Badge>
            <p className="flex items-start gap-2 text-xs font-medium leading-5 text-amber-950">
              <TriangleAlert aria-hidden className="mt-0.5 shrink-0" size={14} />
              A phrase can occur in a citation or discussion and may not be the operative order. Verify the signed judgment with a qualified advocate; this reader gives no legal advice or case prediction.
            </p>
          </div>
        </Card>
      </div>
    </div>
  );
}
