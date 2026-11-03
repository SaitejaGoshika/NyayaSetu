export interface DispositionMention {
  phrase: string;
  excerpt: string;
  position: number;
}

const DISPOSITION_PHRASES = [
  "Dismissed not complying condition order",
  "Proceedings closed/dropped",
  "Leave Granted & Disposed off",
  "Leave Granted & Dismissed",
  "Leave Granted & Allowed",
  "Dismissed as withdrawn",
  "Case Partly allowed",
  "Appeal(s) allowed",
  "Appeal partly allowed",
  "Appeal is allowed",
  "Appeal is dismissed",
  "Disposed off",
  "Disposed of",
  "Set Aside",
  "Remitted to Lower Court",
  "Transferred to High Court",
  "Reference answered",
  "Directions issued",
  "Hearing Adjourned",
  "Case Allowed",
  "Dismissed",
  "Rejected",
  "Reversed",
  "Modified",
  "Order modified",
  "IA disposed",
  "Amount Awarded",
  "Granted",
  "Leave granted",
  "Decided Case",
];

function escapeRegExp(value: string) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

export function findDispositionMentions(text: string): DispositionMention[] {
  const matches: DispositionMention[] = [];

  for (const phrase of DISPOSITION_PHRASES) {
    const pattern = new RegExp(`\\b${escapeRegExp(phrase)}\\b`, "gi");
    for (const match of text.matchAll(pattern)) {
      const position = match.index ?? 0;
      const start = Math.max(0, position - 90);
      const end = Math.min(text.length, position + match[0].length + 110);
      matches.push({
        phrase: match[0],
        excerpt: text.slice(start, end).replace(/\s+/g, " ").trim(),
        position,
      });
    }
  }

  matches.sort((first, second) => first.position - second.position || second.phrase.length - first.phrase.length);

  const nonOverlapping: DispositionMention[] = [];
  let acceptedEnd = -1;
  for (const match of matches) {
    const matchEnd = match.position + match.phrase.length;
    if (match.position < acceptedEnd) continue;
    nonOverlapping.push(match);
    acceptedEnd = matchEnd;
  }

  return nonOverlapping.slice(-10).reverse();
}
