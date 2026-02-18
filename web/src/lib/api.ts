/**
 * Helpers to load static JSON API data at build time.
 * Files are in public/api/v1/ and loaded via fs during SSG.
 */

import fs from "node:fs";
import path from "node:path";

const API_DIR = path.join(process.cwd(), "public", "api", "v1");

function loadJson<T>(filePath: string): T | null {
  const full = path.join(API_DIR, filePath);
  if (!fs.existsSync(full)) return null;
  return JSON.parse(fs.readFileSync(full, "utf-8")) as T;
}

// --- Types ---

export interface GlobalStats {
  total_skills: number;
  skills_scanned: number;
  total_findings: number;
  avg_score: number;
  registries_count: number;
  grade_distribution: Record<string, number>;
  severity_distribution: Record<string, number>;
  generated_at: string;
}

export interface RegistryInfo {
  id: string;
  name: string;
  url: string;
  description: string;
  skill_count: number;
  avg_score: number;
}

export interface CategoryCount {
  category: string;
  count: number;
}

export interface SkillReport {
  skill_id: string;
  registry_id: string;
  slug: string;
  name: string;
  url: string;
  description?: string;
  first_seen?: string;
  last_seen?: string;
  score: number;
  grade: string;
  findings: SkillFinding[];
}

export interface SkillFinding {
  rule_id: string;
  severity: string;
  category: string;
  subcategory?: string;
  line?: number;
  matched_text?: string;
  message?: string;
}

export interface FeedItem {
  skill_id: string;
  slug: string;
  rule_id: string;
  severity: string;
  category: string;
  message: string;
  updated_at: string;
  skill_name: string;
  registry_id: string;
}

export interface RegistrySkill {
  skill_id: string;
  slug: string;
  name: string;
  score: number;
  grade: string;
  finding_count: number;
  critical_count: number;
  high_count: number;
}

export interface SearchEntry {
  slug: string;
  name: string;
  registry: string;
  score: number;
  grade: string;
  findings: number;
}

export interface BenchmarkResult {
  skills_compared: number;
  metrics: {
    per_category: Record<
      string,
      { tp: number; fp: number; fn: number; tn: number; precision: number; recall: number; f1: number }
    >;
    overall: { tp: number; fp: number; fn: number; tn: number; precision: number; recall: number; f1: number };
  };
}

export interface WeeklyTrend {
  week_start: string;
  week_end: string;
  totals: {
    total_skills: number;
    total_findings: number;
    critical_count: number;
    high_count: number;
    avg_score: number;
    new_skills: number;
  };
  registries: Record<string, Record<string, number>>;
}

// --- Loaders ---

export function getStats(): GlobalStats | null {
  return loadJson<GlobalStats>("stats.json");
}

export function getRegistries(): RegistryInfo[] {
  return loadJson<RegistryInfo[]>("registries.json") ?? [];
}

export function getCategories(): CategoryCount[] {
  return loadJson<CategoryCount[]>("categories.json") ?? [];
}

export function getRecentFeed(): FeedItem[] {
  return loadJson<FeedItem[]>("feed/recent.json") ?? [];
}

export function getBenchmarks(): BenchmarkResult | null {
  return loadJson<BenchmarkResult>("benchmarks/vendors.json");
}

export function getWeeklyTrends(): WeeklyTrend[] {
  return loadJson<WeeklyTrend[]>("trends/weekly.json") ?? [];
}

export function getSkillReport(registryId: string, slug: string): SkillReport | null {
  const safeSlug = slug.replace(/\//g, "_").replace(/:/g, "_");
  return loadJson<SkillReport>(`skills/${registryId}/${safeSlug}.json`);
}

export function getRegistryStats(registryId: string): Record<string, unknown> | null {
  return loadJson<Record<string, unknown>>(`registries/${registryId}/stats.json`);
}

export function getRegistrySkills(registryId: string): RegistrySkill[] {
  return loadJson<RegistrySkill[]>(`registries/${registryId}/skills.json`) ?? [];
}

export function getSearchIndex(): SearchEntry[] {
  return loadJson<SearchEntry[]>("search-index.json") ?? [];
}

/** List all available skill report files for static path generation. */
export function listSkillReports(): { registry: string; slug: string }[] {
  const skillsDir = path.join(API_DIR, "skills");
  if (!fs.existsSync(skillsDir)) return [];

  const results: { registry: string; slug: string }[] = [];
  const registries = fs.readdirSync(skillsDir).filter((f) => {
    return fs.statSync(path.join(skillsDir, f)).isDirectory();
  });

  for (const reg of registries) {
    const regDir = path.join(skillsDir, reg);
    const files = fs.readdirSync(regDir).filter((f) => f.endsWith(".json"));
    for (const file of files) {
      results.push({ registry: reg, slug: file.replace(".json", "") });
    }
  }
  return results;
}
