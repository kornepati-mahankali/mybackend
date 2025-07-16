import React, { useState, useEffect } from "react";
import { createClient, Session } from "@supabase/supabase-js";
import { DashboardHome } from "./Dashboard/DashboardHome";
import { DashboardLayout } from "./Layout/DashboardLayout";
import { Sidebar } from "./Layout/Sidebar";
const supabase = createClient(
  'https://zjfjaezztfydiryzsyvd.supabase.co',
  'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpqZmphZXp6dGZ5ZGlyeXpzeXZkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEwMjcwMjEsImV4cCI6MjA2NjYwMzAyMX0.6ZVMwXK4aMGmR68GTYo0yt_L7bOg5QWtElTaa8heQos'
);

function App() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [userData, setUserData] = useState<{ session: Session | null } | null>(null);

  useEffect(() => {
    async function checkAuth() {
      const { data, error } = await supabase.auth.getSession();
      setUserData(data);
    }
    checkAuth();
  }, []);

  async function signUp() {
    console.log(email, password);
    const { data, error } = await supabase.auth.signUp({
      email: email,
      password: password,
    });

    if (error) {
      alert("Error signing up!");
    } else {
      setUserData(data);
      console.log(data);
    }
  }
  async function logIn() {
    console.log(email, password);
    const { data, error } = await supabase.auth.signInWithPassword({
      email: email,
      password: password,
    });

    if (error) {
      console.log("Error logging in.");
    } else {
      setUserData(data);
      console.log(data);
    }
  }

  async function logout() {
    const { error } = await supabase.auth.signOut();
    if (error) {
      console.error("Logout error:", error.message);
    }
    setUserData(null);
  }


  return userData?.session != null ? (
    <div>
        <DashboardHome/>
        <DashboardLayout/>
      

      <button onClick={logout}>Logout</button>
    </div>
  ) : (
    <div>
      <input
        onChange={(e) => {
          setEmail(e.target.value);
        }}
        type="text"
        placeholder="Enter your email..."
      />
      <input
        onChange={(e) => {
          setPassword(e.target.value);
        }}
        type="password"
        placeholder="Choose a password..."
      />
      <button onClick={signUp}>Sign up!</button>
      <hr />
      <input
        onChange={(e) => {
          setEmail(e.target.value);
        }}
        type="text"
        placeholder="Enter your email..."
      />
      <input
        onChange={(e) => {
          setPassword(e.target.value);
        }}
        type="password"
        placeholder="Enter your password..."
      />
      <button onClick={logIn}>Login!</button>
    </div>
  );
}

export default App;