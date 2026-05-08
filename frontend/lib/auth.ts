export type AuthProvider = "clerk" | "authjs";

export function getAuthProvider(): AuthProvider {
  const value = process.env.NEXT_PUBLIC_AUTH_PROVIDER;
  return value === "authjs" ? "authjs" : "clerk";
}
