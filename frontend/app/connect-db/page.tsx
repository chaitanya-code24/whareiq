"use client";

import { useAuth } from "@/lib/useAuth";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

export default function ConnectDBPage() {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !user) {
      router.push("/");
    }
  }, [user, loading, router]);

  if (loading) return null;
  if (!user) return null;

  return (
    <main className="min-h-screen flex items-center justify-center">
      <div className="max-w-md w-full p-6">
        <h2 className="text-xl font-bold mb-4">Connect your database</h2>

        <p>
          Database onboarding will go here.
        </p>
      </div>
    </main>
  );
}
