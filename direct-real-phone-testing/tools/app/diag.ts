import { useEffect, useSyncExternalStore } from "react";

// What the app just did, for the real-phone runner. Only a test build carries it
// (EXPO_PUBLIC_DIAG=1 at build time, set by phone.sh / android.sh build); everywhere else
// every call below is a no-op. The runner reads the trail from one invisible element (testID
// "diag", see diag-probe.tsx), so there is no endpoint and nothing leaves the phone.
// No numbers, codes, tokens or names: ids and long digit runs are masked before a line is kept.
//
//   diag("api", { path: "/items", status: 200, ms: 140 })   // "ms=" over 1000 is flagged slow
//   diag("invite.open", { sms: true })
//   <DiagMark event="list" detail={{ rows: items.length, empty: !items.length }} />

export const DIAG = process.env.EXPO_PUBLIC_DIAG === "1";

// The runner reads the whole trail at once; keep it short enough to read.
const KEEP = 200;
const start = Date.now();
let trail: readonly string[] = [];
const listeners = new Set<() => void>();

/** Masks ids and anything that looks like a phone number or a code. */
export function mask(text: string): string {
  return text
    .replace(/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/gi, ":id")
    .replace(/\+?\d[\d ]{4,}\d/g, "#");
}

/** One line: seconds since launch, the event, then key=value details. */
export function diag(event: string, detail: Detail = {}): void {
  if (!DIAG) return;
  const parts = Object.entries(detail)
    .filter(([, value]) => value !== undefined)
    .map(([key, value]) => `${key}=${String(value)}`);
  const at = ((Date.now() - start) / 1000).toFixed(1);
  const line = mask([at, event, ...parts].join(" "));
  trail = [...trail.slice(-(KEEP - 1)), line];
  listeners.forEach((listener) => listener());
}

/** A short, safe name for an error: its code, else its class. Never its message. */
export function errorName(error: unknown): string {
  if (error && typeof error === "object") {
    const code = (error as { code?: unknown }).code;
    if (typeof code === "string" && code) return code;
    const name = (error as { name?: unknown }).name;
    if (typeof name === "string" && name) return name;
  }
  return typeof error;
}

function subscribe(listener: () => void) {
  listeners.add(listener);
  return () => void listeners.delete(listener);
}

export function useDiagTrail(): readonly string[] {
  return useSyncExternalStore(subscribe, () => trail, () => trail);
}

type Detail = Record<string, string | number | boolean | null | undefined>;

/**
 * Renders nothing; records `event` each time its details change. For what a screen shows,
 * where a hook cannot go (after an early return): a state that is on screen for a moment
 * is in the trail even when no screenshot caught it.
 */
export function DiagMark({ event, detail }: { event: string; detail: Detail }): null {
  const key = JSON.stringify(detail);
  useEffect(() => {
    diag(event, detail);
    // The details are compared by value (`key`), not by object.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [event, key]);
  return null;
}
