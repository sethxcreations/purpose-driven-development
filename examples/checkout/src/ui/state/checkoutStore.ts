// Single normalized store for checkout (UI-001). Derived values are selectors, never extra flags.
export type CartLine = { sku: string; qty: number; unitCents: number };
export type CheckoutState =
  | { status: "editing"; lines: CartLine[] }
  | { status: "paying"; lines: CartLine[] }
  | { status: "declined"; lines: CartLine[]; reason: string }
  | { status: "paid"; lines: CartLine[]; reference: string };

export const totalCents = (s: CheckoutState) =>
  s.lines.reduce((sum, l) => sum + l.qty * l.unitCents, 0);

export type Action =
  | { type: "setQty"; sku: string; qty: number }
  | { type: "submit" }
  | { type: "declined"; reason: string }
  | { type: "paid"; reference: string };

export function reduce(s: CheckoutState, a: Action): CheckoutState {
  switch (a.type) {
    case "setQty":
      return s.status === "editing"
        ? { ...s, lines: s.lines.map((l) => (l.sku === a.sku ? { ...l, qty: a.qty } : l)) }
        : s;
    case "submit":
      return s.status === "editing" ? { status: "paying", lines: s.lines } : s;
    case "declined":
      return { status: "declined", lines: s.lines, reason: a.reason };
    case "paid":
      return { status: "paid", lines: s.lines, reference: a.reference };
  }
}
