"use client";

import { useState } from "react";
import { supabase } from "@/lib/supabaseClient";
import { useRouter } from "next/navigation";

export default function ConnectDatabasePage() {
  const router = useRouter();

  const [form, setForm] = useState({
    host: "localhost",
    port: 5432,
    db_name: "",
    username: "",
    password: "",
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async () => {
    setLoading(true);
    setError(null);

    const {
      data: { session },
    } = await supabase.auth.getSession();

    if (!session) {
      setError("Not authenticated");
      setLoading(false);
      return;
    }

    const res = await fetch("http://127.0.0.1:8000/connect-database", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${session.access_token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(form),
    });

    if (!res.ok) {
      const err = await res.json();
      setError(err.detail || "Failed to connect database");
      setLoading(false);
      return;
    }

    router.push("/app");
  };

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="w-96 space-y-4">
        <h1 className="text-2xl font-bold">Connect your database</h1>

        <input name="host" placeholder="Host" value={form.host} onChange={handleChange} className="w-full p-2 border" />
        <input name="port" placeholder="Port" value={form.port} onChange={handleChange} className="w-full p-2 border" />
        <input name="db_name" placeholder="Database Name" value={form.db_name} onChange={handleChange} className="w-full p-2 border" />
        <input name="username" placeholder="Username" value={form.username} onChange={handleChange} className="w-full p-2 border" />
        <input name="password" type="password" placeholder="Password" value={form.password} onChange={handleChange} className="w-full p-2 border" />

        {error && <p className="text-red-600">{error}</p>}

        <button
          onClick={handleSubmit}
          disabled={loading}
          className="w-full bg-black text-white p-2"
        >
          {loading ? "Connecting..." : "Connect"}
        </button>
      </div>
    </div>
  );
}
