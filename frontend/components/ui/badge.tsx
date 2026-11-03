import type { HTMLAttributes } from "react";

import { cn } from "@/lib/utils";

const variants = {
  high: "bg-red-50 text-red-800 ring-red-200",
  medium: "bg-amber-50 text-amber-900 ring-amber-200",
  low: "bg-blue-50 text-blue-800 ring-blue-200",
  neutral: "bg-mint text-green-dark ring-green/15",
} as const;

export function Badge({
  className,
  variant = "neutral",
  ...props
}: HTMLAttributes<HTMLSpanElement> & { variant?: keyof typeof variants }) {
  return (
    <span
      className={cn("inline-flex items-center gap-1 rounded px-2 py-1 text-[11px] font-semibold capitalize ring-1 ring-inset", variants[variant], className)}
      {...props}
    />
  );
}
