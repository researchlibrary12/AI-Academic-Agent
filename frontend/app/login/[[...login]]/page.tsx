import { SignIn } from "@clerk/nextjs";

export default function LoginPage() {
  return (
    <main className="mx-auto flex min-h-screen max-w-5xl items-center justify-center p-8">
      <SignIn path="/login" routing="path" signUpUrl="/sign-up" />
    </main>
  );
}
