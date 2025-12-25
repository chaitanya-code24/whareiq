"use client";

import { useState } from "react";
import { supabase } from "@/lib/supabaseClient";

export default function AppPage() {
  const [question, setQuestion] = useState("");
  const [response, setResponse] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const askQuestion = async () => {
    setLoading(true);

    const {
      data: { session },
    } = await supabase.auth.getSession();

    const res = await fetch("http://127.0.0.1:8000/query", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${session?.access_token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ question }),
    });

    const data = await res.json();
    setResponse(data);
    setLoading(false);
  };

  return (
    <div className="p-6 max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Ask WhareIQ</h1>

      <textarea
        className="w-full border p-2"
        rows={3}
        placeholder="Ask a question about your data..."
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
      />

      <button
        onClick={askQuestion}
        disabled={loading}
        className="mt-3 px-4 py-2 bg-black text-white"
      >
        {loading ? "Thinking..." : "Ask"}
      </button>

      {response && (
        <pre className="mt-6 bg-gray-100 p-4 rounded text-sm overflow-x-auto">
          {JSON.stringify(response, null, 2)}
        </pre>
      )}
    </div>
  );
}
