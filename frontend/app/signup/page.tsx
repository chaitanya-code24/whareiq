"use client";

import { Auth } from "@supabase/auth-ui-react";
import { ThemeSupa } from "@supabase/auth-ui-shared";
import { supabase } from "@/lib/supabaseClient";

export default function SignupPage() {
  return (
    <main className="min-h-screen flex items-center justify-center">
      <div className="max-w-sm w-full p-6">
        <h2 className="text-xl font-bold mb-4">Create your WhareIQ account</h2>

        <Auth
  supabaseClient={supabase}
  appearance={{
    theme: ThemeSupa,
    variables: {
      default: {
        colors: {
          inputText: "#000000",
          inputBackground: "#ffffff",
          inputBorder: "#d1d5db",
        },
      },
    },
  }}
  theme="light"
  providers={[]}
  view="sign_up" 
/>

      </div>
    </main>
  );
}
