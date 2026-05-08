import { UserButton } from "@clerk/nextjs";
import { PersonalizedCoach } from "@/components/personalized-coach";
import { AdvancedLearning } from "@/components/advanced-learning";
import { FloatingChat } from "@/components/floating-chat";
import { ExamPrepTimetable } from "@/components/exam-prep-timetable";

export default function DashboardPage() {
  return (
    <main className="mx-auto min-h-screen max-w-6xl p-6 md:p-8">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-semibold">AI Academic Workspace</h1>
          <p className="mt-1 text-slate-400">Learn faster with personalized coaching, smart practice, and live chat.</p>
        </div>
        <UserButton afterSignOutUrl="/sign-in" />
      </div>

      <div className="grid gap-5 lg:grid-cols-1">
        <PersonalizedCoach />
      </div>

      <div className="mt-5">
        <AdvancedLearning />
      </div>

      <div className="mt-5">
        <ExamPrepTimetable />
      </div>

      <FloatingChat />
    </main>
  );
}
