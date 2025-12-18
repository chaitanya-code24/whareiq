import Link from "next/link";

export default function LandingPage() {
  return (
    <main className="min-h-screen flex items-center justify-center">
      <div className="max-w-md w-full p-6">
        <h1 className="text-2xl font-bold mb-4">WhareIQ</h1>

        <p className="mb-6">
          Ask your PostgreSQL database questions in plain English — safely.
        </p>

        <div className="flex gap-4">
          <Link href="/login">
            <button className="px-4 py-2 border rounded">
              Login
            </button>
          </Link>

          <Link href="/signup">
            <button className="px-4 py-2 border rounded">
              Sign Up
            </button>
          </Link>
        </div>
      </div>
    </main>
  );
}
