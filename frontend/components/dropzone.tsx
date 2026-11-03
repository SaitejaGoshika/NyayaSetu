"use client";

import { useState } from "react";
import { useDropzone } from "react-dropzone";
import { AlertCircle, Check, CloudUpload, FileText, LoaderCircle, LockKeyhole } from "lucide-react";

import { useAuth } from "@/components/auth-provider";
import { Button } from "@/components/ui/button";
import { analyzeDocument, uploadDocument } from "@/lib/api";
import type { AnalysisResponse } from "@/lib/types";

const MAX_FILE_BYTES = 10 * 1024 * 1024;

type UploadPhase = "idle" | "uploading" | "analyzing" | "complete" | "error";

function formatBytes(bytes: number) {
  return bytes >= 1024 * 1024 ? `${(bytes / (1024 * 1024)).toFixed(1)} MB` : `${Math.max(1, Math.round(bytes / 1024))} KB`;
}

export function Dropzone({ onAnalysis }: { onAnalysis: (analysis: AnalysisResponse) => void }) {
  const { user, authReady } = useAuth();
  const [phase, setPhase] = useState<UploadPhase>("idle");
  const [filename, setFilename] = useState("");
  const [fileSize, setFileSize] = useState(0);
  const [errorMessage, setErrorMessage] = useState("");

  async function processFile(file: File) {
    if (!user) {
      setPhase("error");
      setErrorMessage("Sign in with your organization account before uploading a document.");
      return;
    }
    setFilename(file.name);
    setFileSize(file.size);
    setErrorMessage("");
    setPhase("uploading");
    try {
      const uploaded = await uploadDocument(file);
      setPhase("analyzing");
      const analysis = await analyzeDocument(uploaded.documentId);
      onAnalysis(analysis);
      setPhase("complete");
    } catch (error) {
      setPhase("error");
      setErrorMessage(error instanceof Error ? error.message : "The document could not be analyzed.");
    }
  }

  const { getInputProps, getRootProps, isDragActive, fileRejections, open } = useDropzone({
    accept: {
      "application/pdf": [".pdf"],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
    },
    maxFiles: 1,
    maxSize: MAX_FILE_BYTES,
    multiple: false,
    disabled: !authReady || !user || phase === "uploading" || phase === "analyzing",
    onDropAccepted: (files) => void processFile(files[0]),
    onDropRejected: (rejections) => {
      setPhase("error");
      const firstError = rejections[0]?.errors[0];
      setErrorMessage(firstError?.code === "file-too-large"
        ? "This file exceeds the 10 MB limit."
        : firstError?.code === "file-invalid-type"
          ? "Choose a PDF or DOCX document."
          : firstError?.message ?? "Choose one PDF or DOCX document.");
    },
  });

  const busy = phase === "uploading" || phase === "analyzing";
  const isDisabled = !authReady || !user || busy;
  const statusText = phase === "uploading"
    ? "Encrypting transfer to your secure vault"
    : phase === "analyzing"
      ? "Extracting clauses and checking legal signals"
      : phase === "complete"
        ? "Analysis ready"
        : "PDF or DOCX, up to 10 MB";

  return (
    <div>
      <div
        {...getRootProps({
          className: `group relative grid min-h-[242px] cursor-pointer place-items-center overflow-hidden rounded-lg border border-dashed p-6 text-center transition ${isDragActive ? "border-green bg-mint" : "border-[#b8c9bf] bg-[#f8faf8] hover:border-green hover:bg-mint/60"} ${isDisabled ? "cursor-not-allowed opacity-75" : ""}`,
        })}
      >
        <input {...getInputProps()} aria-label="Choose a PDF or DOCX contract" />
        <div className="max-w-sm">
          <div className={`mx-auto mb-4 grid size-12 place-items-center rounded-lg ${busy ? "bg-green text-white" : "bg-white text-green shadow-sm ring-1 ring-line"}`}>
            {busy ? <LoaderCircle aria-hidden="true" className="animate-spin" size={21} /> : phase === "complete" ? <Check aria-hidden="true" size={22} /> : <CloudUpload aria-hidden="true" size={22} />}
          </div>
          <h3 className="text-base font-semibold">{isDragActive ? "Drop your contract here" : busy ? (phase === "uploading" ? "Uploading securely" : "Reviewing document") : "Drop a contract to begin"}</h3>
          <p className="mt-1.5 text-sm text-muted">{statusText}</p>
          {filename && <p className="mt-2 truncate text-xs font-medium text-green">{filename} · {formatBytes(fileSize)}</p>}
          {fileRejections.length > 0 && <p className="mt-3 text-xs text-red-700">{errorMessage}</p>}
          {phase === "error" && errorMessage && <p className="mt-3 flex items-center justify-center gap-1.5 text-xs text-red-700" role="alert"><AlertCircle size={14} />{errorMessage}</p>}
          {phase === "complete" && <p className="mt-3 flex items-center justify-center gap-1.5 text-xs font-medium text-green"><Check size={14} />Your document was processed successfully.</p>}
          <div className="mt-5 flex items-center justify-center gap-2">
            <Button disabled={isDisabled} onClick={(event) => { event.stopPropagation(); open(); }} size="sm" type="button">Choose document</Button>
            <span className="text-xs text-muted">or drag and drop</span>
          </div>
          {!user && authReady && <p className="mt-4 flex items-center justify-center gap-1.5 text-xs text-muted"><LockKeyhole size={13} />Sign in to enable secure upload</p>}
        </div>
      </div>
      <div className="mt-3 flex items-center justify-between text-[11px] text-muted">
        <span className="flex items-center gap-1.5"><LockKeyhole size={12} />Saved to local disk</span>
        <span className="flex items-center gap-1.5"><FileText size={12} />PDF and DOCX</span>
      </div>
    </div>
  );
}
