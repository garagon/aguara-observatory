/**
 * Shared constants used across the Aguara Observatory UI.
 * Single source of truth for grades, colors, registry names, etc.
 */

// --- Grade colors ---

/** Grade colors for badge/pill components (bg + text + border) */
export const gradeColors: Record<string, { bg: string; text: string; border: string; css: string }> = {
  A: { bg: "bg-emerald-500/20", text: "text-emerald-400", border: "border-emerald-500/40", css: "bg-emerald-500/20 text-emerald-400 border-emerald-500/40" },
  B: { bg: "bg-green-500/20", text: "text-green-400", border: "border-green-500/40", css: "bg-green-500/20 text-green-400 border-green-500/40" },
  C: { bg: "bg-yellow-500/20", text: "text-yellow-400", border: "border-yellow-500/40", css: "bg-yellow-500/20 text-yellow-400 border-yellow-500/40" },
  D: { bg: "bg-orange-500/20", text: "text-orange-400", border: "border-orange-500/40", css: "bg-orange-500/20 text-orange-400 border-orange-500/40" },
  F: { bg: "bg-red-500/20", text: "text-red-400", border: "border-red-500/40", css: "bg-red-500/20 text-red-400 border-red-500/40" },
};

/** Solid grade background colors (for bar charts, progress bars) */
export const gradeBarColors: Record<string, string> = {
  A: "bg-emerald-500",
  B: "bg-green-500",
  C: "bg-yellow-500",
  D: "bg-orange-500",
  F: "bg-red-500",
};

// --- Grade metadata ---

export const gradeDescriptions: Record<string, string> = {
  A: "Minimal or no security issues detected.",
  B: "Minor issues found, generally safe.",
  C: "Moderate security concerns.",
  D: "Significant security issues detected.",
  F: "Critical security problems.",
};

export const gradeRanges: Record<string, string> = {
  A: "90-100",
  B: "75-89",
  C: "50-74",
  D: "25-49",
  F: "0-24",
};

/** Ordered list of grades from best to worst */
export const gradeOrder = ["A", "B", "C", "D", "F"] as const;

// --- Score/grade conversion ---

export function scoreToGrade(score: number): string {
  if (score >= 90) return "A";
  if (score >= 75) return "B";
  if (score >= 50) return "C";
  if (score >= 25) return "D";
  return "F";
}

// --- Registry mappings ---

export const registryNames: Record<string, string> = {
  "skills-sh": "Skills.sh",
  clawhub: "ClawHub",
  "mcp-registry": "PulseMCP",
  "mcp-so": "mcp.so",
  lobehub: "LobeHub",
};

export const registryDescriptions: Record<string, string> = {
  "skills-sh": "Community AI agent skills marketplace",
  clawhub: "AI agent skills registry",
  "mcp-registry": "MCP server directory",
  "mcp-so": "MCP server discovery platform",
  lobehub: "Plugin marketplace",
};

// --- Severity mappings ---

export const severityColors: Record<string, string> = {
  CRITICAL: "bg-red-500/20 text-red-400 border-red-500/30",
  HIGH: "bg-orange-500/20 text-orange-400 border-orange-500/30",
  MEDIUM: "bg-yellow-500/20 text-yellow-400 border-yellow-500/30",
  LOW: "bg-blue-500/20 text-blue-400 border-blue-500/30",
  INFO: "bg-gray-500/20 text-gray-400 border-gray-500/30",
};

/** Severity ordering from most to least severe */
export const severityOrder: string[] = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"];

/** Numeric severity rank (lower = more severe) for sorting */
export const severityRank: Record<string, number> = {
  CRITICAL: 0,
  HIGH: 1,
  MEDIUM: 2,
  LOW: 3,
  INFO: 4,
};

// --- Category descriptions ---

export const categoryDescriptions: Record<string, string> = {
  "external-download": "Skills that download or reference external files, URLs, or resources",
  "command-execution": "Skills that execute shell commands, system calls, or subprocess operations",
  "prompt-injection": "Skills with patterns that could enable prompt injection attacks",
  "mcp-config": "MCP server configuration issues or insecure defaults",
  "third-party-content": "Skills that load or embed untrusted third-party content",
  "ssrf-cloud": "Server-side request forgery risks targeting cloud metadata or internal services",
  "exfiltration": "Skills with patterns that could leak sensitive data to external endpoints",
  "supply-chain": "Supply chain risks: typosquatting, dependency confusion, or untrusted packages",
  "credential-leak": "Skills that handle, expose, or hardcode credentials and secrets",
  "mcp-attack": "MCP protocol abuse: tool poisoning, rug pulls, or cross-origin attacks",
  "unicode-attack": "Unicode/homoglyph tricks used to obfuscate malicious content",
  "indirect-injection": "Indirect prompt injection via external data sources",
  "toxic-flow": "Multi-step flows that combine benign tools into dangerous chains",
};
