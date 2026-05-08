"use client";

import { useAuth } from "@clerk/nextjs";
import { useMemo, useState } from "react";

const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

type QuizQuestion = {
  id: string;
  question: string;
  options: string[];
};

export function AdvancedLearning() {
  const { getToken } = useAuth();
  const moduleTopicMap: Record<string, string[]> = useMemo(
    () => ({
      "Data Structures": ["Arrays", "Linked Lists", "Trees", "Graphs"],
      Databases: ["Normalization", "SQL Joins", "Transactions", "Indexing"],
      Calculus: ["Limits", "Derivatives", "Integrals", "Series"],
      Algorithms: ["Sorting", "Greedy", "Dynamic Programming", "Complexity Analysis"],
    }),
    []
  );
  const moduleNames = Object.keys(moduleTopicMap);
  const [moduleName, setModuleName] = useState(moduleNames[0]);
  const [topic, setTopic] = useState(moduleTopicMap[moduleNames[0]][0]);
  const [difficulty, setDifficulty] = useState("medium");
  const [quizId, setQuizId] = useState("");
  const [questions, setQuestions] = useState<QuizQuestion[]>([]);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [result, setResult] = useState<null | {
    score: number;
    total: number;
    percentage: number;
    mastery_score: number;
    recommendation: string;
  }>(null);
  const [actions, setActions] = useState<string[]>([]);
  const [status, setStatus] = useState("");
  const allAnswered = questions.length > 0 && questions.every((q) => Boolean(answers[q.id]));

  const headers = async () => {
    const token = await getToken();
    return {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token ?? ""}`
    };
  };

  const loadActions = async () => {
    setStatus("Loading recommendations...");
    const res = await fetch(`${apiBase}/api/v1/phase3/next-actions`, {
      headers: await headers()
    });
    const json = await res.json();
    setActions(json.actions ?? []);
    setStatus(res.ok ? "Recommendations ready" : "Could not load recommendations");
  };

  const generateQuiz = async () => {
    setStatus("Generating quiz...");
    const res = await fetch(`${apiBase}/api/v1/phase3/quiz`, {
      method: "POST",
      headers: await headers(),
      body: JSON.stringify({ module: moduleName, topic, difficulty, question_count: 10 })
    });
    const json = await res.json();
    if (!res.ok) {
      setStatus("Could not generate quiz");
      return;
    }
    setQuizId(json.quiz_id ?? "");
    setQuestions(json.questions ?? []);
    setAnswers({});
    setResult(null);
    setStatus("Quiz ready. Answer all 10 questions to unlock submission.");
  };

  const submitQuiz = async () => {
    if (!quizId || questions.length === 0) {
      setStatus("Generate a quiz first.");
      return;
    }
    if (!allAnswered) {
      setStatus("Please answer all questions before submitting.");
      return;
    }
    setStatus("Marking quiz...");
    const res = await fetch(`${apiBase}/api/v1/phase3/quiz/submit`, {
      method: "POST",
      headers: await headers(),
      body: JSON.stringify({ quiz_id: quizId, answers })
    });
    const json = await res.json();
    if (!res.ok) {
      setStatus(json.detail ?? "Could not submit quiz");
      return;
    }
    setResult(json);
    setStatus("Quiz marked.");
  };

  return (
    <section className="rounded-2xl border border-slate-800 bg-slate-900/70 p-5">
      <h2 className="text-lg font-semibold">Smart Practice</h2>
      <p className="mt-1 text-sm text-slate-400">
        Select module and topic, answer 10 questions, then get instant grading and mastery feedback.
      </p>

      <div className="mt-4 grid gap-3 sm:grid-cols-2">
        <select
          className="rounded-md border border-slate-700 bg-slate-950 px-3 py-2"
          value={moduleName}
          onChange={(e) => {
            const selectedModule = e.target.value;
            setModuleName(selectedModule);
            setTopic(moduleTopicMap[selectedModule][0]);
          }}
        >
          {moduleNames.map((name) => (
            <option key={name} value={name}>
              {name}
            </option>
          ))}
        </select>
        <select
          className="rounded-md border border-slate-700 bg-slate-950 px-3 py-2"
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
        >
          {(moduleTopicMap[moduleName] ?? []).map((topicName) => (
            <option key={topicName} value={topicName}>
              {topicName}
            </option>
          ))}
        </select>
        <select
          className="rounded-md border border-slate-700 bg-slate-950 px-3 py-2"
          value={difficulty}
          onChange={(e) => setDifficulty(e.target.value)}
        >
          <option value="easy">easy</option>
          <option value="medium">medium</option>
          <option value="hard">hard</option>
        </select>
        <select
          className="rounded-md border border-slate-700 bg-slate-950 px-3 py-2"
          value={questions.length}
          disabled
        >
          <option value={0}>10 questions per quiz</option>
          <option value={10}>10 questions per quiz</option>
        </select>
      </div>

      <div className="mt-4 flex flex-wrap gap-2">
        <button className="rounded-md bg-indigo-600 px-4 py-2" onClick={generateQuiz} type="button">
          Generate Quiz
        </button>
        <button className="rounded-md bg-emerald-600 px-4 py-2" onClick={loadActions} type="button">
          Show Next Actions
        </button>
      </div>

      <p className="mt-3 text-sm text-slate-400">{status}</p>
      {questions.length > 0 && !allAnswered ? (
        <p className="text-xs text-amber-300">
          Answered {Object.keys(answers).length}/{questions.length}. Submission unlocks when all are answered.
        </p>
      ) : null}

      {actions.length > 0 ? (
        <ul className="mt-4 space-y-2 text-sm">
          {actions.map((action) => (
            <li key={action} className="rounded-md border border-slate-700 p-2">
              {action}
            </li>
          ))}
        </ul>
      ) : null}

      {questions.length > 0 ? (
        <div className="mt-4 space-y-3">
          {questions.map((q, idx) => (
            <div key={q.id} className="rounded-md border border-slate-700 bg-slate-950 p-3">
              <p className="text-sm font-medium">
                {idx + 1}. {q.question}
              </p>
              <div className="mt-2 grid gap-2">
                {q.options.map((option) => {
                  const letter = option.slice(0, 1);
                  return (
                    <label key={option} className="flex items-center gap-2 text-sm">
                      <input
                        type="radio"
                        name={q.id}
                        checked={answers[q.id] === letter}
                        onChange={() => setAnswers((prev) => ({ ...prev, [q.id]: letter }))}
                      />
                      <span>{option}</span>
                    </label>
                  );
                })}
              </div>
            </div>
          ))}
          <div className="pt-2">
            {allAnswered ? (
              <button className="w-full rounded-md bg-blue-600 px-4 py-3 font-medium" onClick={submitQuiz} type="button">
                Submit & Mark
              </button>
            ) : (
              <button className="w-full rounded-md bg-slate-700 px-4 py-3 font-medium text-slate-300" disabled type="button">
                Answer all questions to submit
              </button>
            )}
          </div>
        </div>
      ) : null}

      {result ? (
        <div className="mt-4 rounded-md border border-slate-700 bg-slate-950 p-3 text-sm">
          <p>
            Score: {result.score}/{result.total} ({result.percentage}%)
          </p>
          <p>Mastery score: {result.mastery_score}</p>
          <p className="text-slate-300">{result.recommendation}</p>
        </div>
      ) : null}
    </section>
  );
}
