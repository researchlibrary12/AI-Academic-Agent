"use client";

import { useAuth } from "@clerk/nextjs";
import { useEffect, useState } from "react";

const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

type RiskRow = {
  topic: string;
  average_percentage: number;
  risk_level: string;
  attempts: number;
};

type WeeklyPlanRow = {
  topic: string;
  hours: number;
  tasks: string[];
};

type Insights = {
  risk?: { overall_risk: string; confidence: string; driver: string };
  next_best_actions?: string[];
};

type ResultRow = {
  module: string;
  assessment_type: "test" | "exam" | "assignment";
  assessment_name: string;
  topic: string;
  score: number;
  max_score: number;
  assessment_date?: string;
};

type Summary = {
  course: string;
  year: number;
  risk_rate: number;
  overall_risk: string;
};

export function PersonalizedCoach() {
  const { getToken, isLoaded, isSignedIn } = useAuth();
  const [studyStyle, setStudyStyle] = useState("mixed");
  const [hours, setHours] = useState(10);
  const [status, setStatus] = useState("");
  const [riskSummary, setRiskSummary] = useState<RiskRow[]>([]);
  const [weeklyPlan, setWeeklyPlan] = useState<WeeklyPlanRow[]>([]);
  const [insights, setInsights] = useState<Insights>({});
  const [results, setResults] = useState<ResultRow[]>([]);
  const [resultSearch, setResultSearch] = useState("");
  const [resultTypeFilter, setResultTypeFilter] = useState<"all" | "test" | "exam" | "assignment">("all");
  const [modules, setModules] = useState<string[]>([]);
  const [assessmentsByModule, setAssessmentsByModule] = useState<Record<string, string[]>>({});
  const [selectedModule, setSelectedModule] = useState("all");
  const [selectedAssessment, setSelectedAssessment] = useState("all");
  const [summary, setSummary] = useState<Summary | null>(null);
  const filteredResults = results.filter((row) => {
    const matchesSearch =
      !resultSearch ||
      [row.module, row.assessment_name, row.topic].join(" ").toLowerCase().includes(resultSearch.toLowerCase());
    const matchesType = resultTypeFilter === "all" || row.assessment_type === resultTypeFilter;
    return matchesSearch && matchesType;
  });

  const authHeaders = async () => {
    const token = await getToken();
    if (!token) throw new Error("Not authenticated");
    return {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token ?? ""}`
    };
  };

  const saveProfile = async () => {
    setStatus("Saving profile...");
    const res = await fetch(`${apiBase}/api/v1/phase2/profile`, {
      method: "PUT",
      headers: await authHeaders(),
      body: JSON.stringify({
        program: summary?.course ?? "Computer Science",
        year: 2,
        goals: [],
        weak_topics: [],
        study_style: studyStyle,
        available_hours_per_week: hours,
        target_gpa: 3.5,
        attendance_rate: 85,
        preferred_session_minutes: 45
      })
    });
    setStatus(res.ok ? "Profile saved" : "Failed to save profile");
  };

  const loadModuleMetadata = async () => {
    const res = await fetch(`${apiBase}/api/v1/phase2/modules`, { headers: await authHeaders() });
    const json = await res.json();
    setModules(json.modules ?? []);
    setAssessmentsByModule(json.assessments_by_module ?? {});
  };

  const loadResults = async () => {
    setStatus("Loading results...");
    const params = new URLSearchParams({ module: selectedModule, assessment: selectedAssessment });
    const res = await fetch(`${apiBase}/api/v1/phase2/results?${params.toString()}`, {
      headers: await authHeaders()
    });
    const json = await res.json();
    setResults(json.results ?? []);
    setStatus(res.ok ? "Results loaded" : "Could not load results");
  };

  const loadSummary = async () => {
    const res = await fetch(`${apiBase}/api/v1/phase2/summary`, { headers: await authHeaders() });
    const json = await res.json();
    if (res.ok) setSummary(json);
  };

  const runRiskAnalysis = async () => {
    setStatus("Analyzing performance...");
    const params = new URLSearchParams({ module: selectedModule, assessment: selectedAssessment });
    const res = await fetch(`${apiBase}/api/v1/phase2/analyze?${params.toString()}`, { headers: await authHeaders() });
    const json = await res.json();
    setRiskSummary(json.risk_summary ?? []);
    setStatus(res.ok ? "Risk analysis complete" : "Risk analysis failed");
  };

  const generatePlan = async () => {
    setStatus("Generating personalized plan...");
    const params = new URLSearchParams({ module: selectedModule, assessment: selectedAssessment });
    const res = await fetch(`${apiBase}/api/v1/phase2/plan?${params.toString()}`, {
      method: "POST",
      headers: await authHeaders(),
      body: JSON.stringify({ available_hours_per_week: hours })
    });
    const json = await res.json();
    setWeeklyPlan(json.weekly_plan ?? []);
    setStatus(res.ok ? "Plan ready" : "Plan generation failed");
  };

  const loadInsights = async () => {
    setStatus("Loading insights...");
    const params = new URLSearchParams({ module: selectedModule, assessment: selectedAssessment });
    const res = await fetch(`${apiBase}/api/v1/phase2/insights?${params.toString()}`, {
      headers: await authHeaders()
    });
    const json = await res.json();
    setInsights(json);
    setStatus(res.ok ? "Insights loaded" : "Could not load insights");
  };

  useEffect(() => {
    const boot = async () => {
      if (!isLoaded || !isSignedIn) return;
      setStatus("Loading student analytics...");
      try {
        await saveProfile();
        await loadSummary();
        await loadModuleMetadata();
        await loadResults();
        setStatus("Ready");
      } catch {
        setStatus("Session ended. Please sign in again.");
      }
    };
    void boot();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isLoaded, isSignedIn]);

  useEffect(() => {
    if (!isLoaded || !isSignedIn) return;
    void loadResults();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isLoaded, isSignedIn, selectedModule, selectedAssessment]);

  return (
    <section className="rounded-2xl border border-slate-800 bg-slate-900/70 p-5">
      <h2 className="text-lg font-semibold">Personalized Coach</h2>
      <p className="mt-2 text-sm text-slate-400">
        View your module results, filter by assessment (or select all), then run risk analysis, plan, and insights.
      </p>
      <div className="mt-3 rounded-md border border-slate-700 bg-slate-950 p-3 text-xs text-slate-300">
        <p>1) Select module &amp; assessment -&gt; 2) Analyze -&gt; 3) Get plan and insights</p>
      </div>

      <div className="mt-4 grid gap-3 md:grid-cols-2">
        <select
          className="rounded-md bg-slate-900 p-2"
          value={studyStyle}
          onChange={(e) => setStudyStyle(e.target.value)}
        >
          <option value="mixed">mixed</option>
          <option value="visual">visual</option>
          <option value="reading">reading</option>
          <option value="practice">practice</option>
        </select>
        <input
          className="rounded-md bg-slate-900 p-2"
          type="number"
          min={1}
          max={80}
          value={hours}
          onChange={(e) => setHours(Number(e.target.value))}
          placeholder="Available study hours per week"
        />
      </div>

      {summary ? (
        <div className="mt-4 grid gap-3 sm:grid-cols-3">
          <div className="rounded-md border border-slate-700 bg-slate-950 p-3">
            <p className="text-xs text-slate-400">Course</p>
            <p className="font-semibold">{summary.course}</p>
          </div>
          <div className="rounded-md border border-slate-700 bg-slate-950 p-3">
            <p className="text-xs text-slate-400">Year</p>
            <p className="font-semibold">{summary.year}</p>
          </div>
          <div className="rounded-md border border-slate-700 bg-slate-950 p-3">
            <p className="text-xs text-slate-400">Risk Rate</p>
            <p className="font-semibold">
              {summary.risk_rate}% ({summary.overall_risk})
            </p>
          </div>
        </div>
      ) : null}

      <div className="mt-3 grid gap-3 sm:grid-cols-2">
        <select
          className="rounded-md bg-slate-900 p-2"
          value={selectedModule}
          onChange={(e) => {
            setSelectedModule(e.target.value);
            setSelectedAssessment("all");
          }}
        >
          <option value="all">All modules</option>
          {modules.map((module) => (
            <option key={module} value={module}>
              {module}
            </option>
          ))}
        </select>
        <select
          className="rounded-md bg-slate-900 p-2"
          value={selectedAssessment}
          onChange={(e) => setSelectedAssessment(e.target.value)}
        >
          <option value="all">All tests/exams/assignments</option>
          {(
            selectedModule !== "all"
              ? assessmentsByModule[selectedModule] ?? []
              : Array.from(new Set(Object.values(assessmentsByModule).flat()))
          ).map((name) => (
            <option key={name} value={name}>
              {name}
            </option>
          ))}
        </select>
      </div>

      <div className="mt-4 flex flex-wrap gap-2">
        <button className="rounded-md bg-slate-600 px-4 py-2" onClick={loadResults} type="button">
          Refresh Results
        </button>
        <button className="rounded-md bg-amber-600 px-4 py-2" onClick={runRiskAnalysis} type="button">
          Run Risk Analysis
        </button>
        <button className="rounded-md bg-indigo-600 px-4 py-2" onClick={generatePlan} type="button">
          Generate Weekly Plan
        </button>
        <button className="rounded-md bg-cyan-600 px-4 py-2" onClick={loadInsights} type="button">
          Load Insights
        </button>
      </div>

      <p className="mt-3 text-sm text-slate-300">{status}</p>

      {riskSummary.length > 0 ? (
        <div className="mt-4">
          <h3 className="font-medium">Risk Summary</h3>
          <div className="mt-2 space-y-2">
            {riskSummary.map((row) => (
              <div key={row.topic} className="rounded-md border border-slate-700 p-2 text-sm">
                {row.topic} - {row.average_percentage}% - {row.risk_level} risk ({row.attempts} attempts)
              </div>
            ))}
          </div>
        </div>
      ) : null}

      {weeklyPlan.length > 0 ? (
        <div className="mt-4">
          <h3 className="font-medium">Weekly Plan</h3>
          <div className="mt-2 space-y-2">
            {weeklyPlan.map((row) => (
              <div key={row.topic} className="rounded-md border border-slate-700 p-2 text-sm">
                <p className="font-medium">
                  {row.topic} ({row.hours}h)
                </p>
                <ul className="ml-4 list-disc">
                  {row.tasks.map((task) => (
                    <li key={task}>{task}</li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      ) : null}

      {insights.risk ? (
        <div className="mt-4 rounded-md border border-slate-700 p-3 text-sm">
          <p>
            Overall risk: <span className="font-semibold">{insights.risk.overall_risk}</span> ({insights.risk.confidence}
            )
          </p>
          <p className="text-slate-300">Driver: {insights.risk.driver}</p>
          {insights.next_best_actions?.length ? (
            <ul className="ml-4 mt-2 list-disc">
              {insights.next_best_actions.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          ) : null}
        </div>
      ) : null}

      {results.length > 0 ? (
        <div className="mt-4">
          <h3 className="font-medium">Results</h3>
          <div className="mt-2 grid gap-2 sm:grid-cols-2">
            <input
              className="rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-sm"
              value={resultSearch}
              onChange={(e) => setResultSearch(e.target.value)}
              placeholder="Filter by module, assessment, or topic"
            />
            <select
              className="rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-sm"
              value={resultTypeFilter}
              onChange={(e) => setResultTypeFilter(e.target.value as "all" | "test" | "exam" | "assignment")}
            >
              <option value="all">All types</option>
              <option value="test">Test</option>
              <option value="exam">Exam</option>
              <option value="assignment">Assignment</option>
            </select>
          </div>
          <div className="mt-2 max-h-52 overflow-auto rounded-md border border-slate-700">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-800">
                <tr>
                  <th className="px-2 py-2">Module</th>
                  <th className="px-2 py-2">Assessment</th>
                  <th className="px-2 py-2">Type</th>
                  <th className="px-2 py-2">Topic</th>
                  <th className="px-2 py-2">Mark</th>
                </tr>
              </thead>
              <tbody>
                {filteredResults.map((row, idx) => (
                  <tr key={`${row.module}-${row.assessment_name}-${row.topic}-${idx}`} className="border-t border-slate-800">
                    <td className="px-2 py-2">{row.module}</td>
                    <td className="px-2 py-2">{row.assessment_name}</td>
                    <td className="px-2 py-2">{row.assessment_type}</td>
                    <td className="px-2 py-2">{row.topic}</td>
                    <td className="px-2 py-2">
                      {row.score}/{row.max_score}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="mt-2 text-xs text-slate-400">
            Showing {filteredResults.length} of {results.length} results
          </p>
        </div>
      ) : null}
    </section>
  );
}
