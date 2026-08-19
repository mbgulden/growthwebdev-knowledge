export type AotIntent = "tour" | "rental" | "guide" | "support" | "booking" | "language" | "legal" | "contact" | "social" | "trust";

export interface AotNavItem {
  id: string;
  label: string;
  sourceText: string;
  href: string;
  intent: AotIntent;
  aiSummary: string;
  children?: AotNavItem[];
}

export interface AotFooterGroup {
  id: string;
  heading: string;
  priority: "primary" | "secondary" | "legal";
  items: AotNavItem[];
}

export interface AotBookingConfig {
  shortname: "activeoahutours";
  href: string;
  ctaLabel: string;
  fallback: "simple";
  analyticsEvent: "booking_click";
  source: string;
}
