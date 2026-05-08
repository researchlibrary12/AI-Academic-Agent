"use client";

import { useAuth } from "@clerk/nextjs";
import { useEffect, useState } from "react";

const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

type ExamRow = {
  exam_id: string;
  module: string;
  exam_name: string;
  date: string;
  time: string;
  venue: string;
  topics: string[];
};

type PlanRow = {
  day: number;
  topic: string;
  hours: number;
  tasks: string[];
};

export function ExamPrepTimetable() {
  const { getToken, isLoaded, isSignedIn } = useAuth();
  const [exams, setExams] = useState<ExamRow[]>([]);
  const [selectedExam, setSelectedExam] = useState("");
  const [plan, setPlan] = useState<PlanRow[]>([]);
  const [status, setStatus] = useState("");

  const headers = async () => {
    const token = await getToken();
    if (!token) throw new Error("Not authenticated");
    return { Authorization: `Bearer ${token ?? ""}` };
  };

  const loadTimetable = async () => {
    try {
      const res = await fetch(`${apiBase}/api/v1/phase3/exam-timetable`, { headers: await headers() });
      const json = await res.json();
      const rows = json.exams ?? [];
      setExams(rows);
      if (rows.length > 0 && !selectedExam) setSelectedExam(rows[0].exam_id);
    } catch {
      setStatus("Session ended. Please sign in again.");
    }
  };

  const generatePrepPlan = async () => {
    if (!selectedExam) return;
    setStatus("Generating prep plan...");
    const token = await getToken();
    const res = await fetch(`${apiBase}/api/v1/phase3/exam-prep-plan`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token ?? ""}`
      },
      body: JSON.stringify({ exam_id: selectedExam, available_hours_per_day: 2 })
    });
    const json = await res.json();
    setPlan(json.plan ?? []);
    setStatus(res.ok ? "Prep plan ready" : "Could not generate prep plan");
  };

  useEffect(() => {
    if (!isLoaded || !isSignedIn) return;
    void loadTimetable();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isLoaded, isSignedIn]);

  return (
    <section className="rounded-2xl border border-slate-800 bg-slate-900/70 p-5">
      <h2 className="text-lg font-semibold">Exam Timetable & Prep</h2>
      <p className="mt-1 text-sm text-slate-400">View upcoming exams and generate a focused daily prep plan.</p>

      <div className="mt-4">
        <select
          className="rounded-md border border-slate-700 bg-slate-950 px-3 py-2"
          value={selectedExam}
          onChange={(e) => setSelectedExam(e.target.value)}
        >
          <option value="">Select exam</option>
          {exams.map((exam) => (
            <option key={exam.exam_id} value={exam.exam_id}>
              {exam.module} - {exam.exam_name} ({exam.date})
            </option>
          ))}
        </select>
      </div>

      <div className="mt-4 flex gap-2">
        <button className="rounded-md bg-slate-700 px-4 py-2" onClick={loadTimetable} type="button">
          Refresh Timetable
        </button>
        <button className="rounded-md bg-purple-600 px-4 py-2" onClick={generatePrepPlan} type="button">
          Generate Exam Prep Plan
        </button>
      </div>

      <p className="mt-3 text-sm text-slate-300">{status}</p>

      {exams.length > 0 ? (
        <div className="mt-4 max-h-48 overflow-auto rounded-md border border-slate-700">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-800">
              <tr>
                <th className="px-2 py-2">Module</th>
                <th className="px-2 py-2">Exam</th>
                <th className="px-2 py-2">Date</th>
                <th className="px-2 py-2">Time</th>
                <th className="px-2 py-2">Venue</th>
              </tr>
            </thead>
            <tbody>
              {exams.map((exam) => (
                <tr key={exam.exam_id} className="border-t border-slate-800">
                  <td className="px-2 py-2">{exam.module}</td>
                  <td className="px-2 py-2">{exam.exam_name}</td>
                  <td className="px-2 py-2">{exam.date}</td>
                  <td className="px-2 py-2">{exam.time}</td>
                  <td className="px-2 py-2">{exam.venue}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}

      {plan.length > 0 ? (
        <div className="mt-4 space-y-2">
          {plan.map((row) => (
            <div key={`${row.day}-${row.topic}`} className="rounded-md border border-slate-700 p-3 text-sm">
              <p className="font-medium">
                Day {row.day}: {row.topic} ({row.hours}h)
              </p>
              <ul className="ml-4 mt-1 list-disc">
                {row.tasks.map((task) => (
                  <li key={task}>{task}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      ) : null}
    </section>
  );
}
