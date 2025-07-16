import React, { useState } from "react";
import axios from "axios";

export default function EProcurementScraper() {
  const [form, setForm] = useState({
    base_url: "",
    tender_type: "",
    days_interval: 1,
    start_page: 1,
  });
  const [sessionId, setSessionId] = useState("");
  const [showCaptcha, setShowCaptcha] = useState(false);
  const [captcha, setCaptcha] = useState("");
  const [status, setStatus] = useState("");

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleStartScraping = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatus("Starting scraping session...");
    try {
      const res = await axios.post<{ session_id: string }>("http://localhost:8000/start-scraping", null, {
        params: form,
      });
      setSessionId(res.data.session_id);
      setShowCaptcha(true);
      setStatus("Please enter the captcha shown in the opened Edge browser.");
    } catch (err: any) {
      setStatus("Failed to start scraping: " + (err.response?.data?.error || err.message));
    }
  };

  const handleSubmitCaptcha = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatus("Submitting captcha...");
    try {
      const res = await axios.post<{ status: string }>("http://localhost:8000/submit-captcha", {
        session_id: sessionId,
        captcha_value: captcha,
      });
      setStatus(res.data.status || "Captcha submitted!");
      // Optionally, you can trigger further scraping or download here
    } catch (err: any) {
      setStatus("Failed to submit captcha: " + (err.response?.data?.error || err.message));
    }
  };

  return (
    <div>
      <form onSubmit={handleStartScraping}>
        <input
          name="base_url"
          value={form.base_url}
          onChange={handleChange}
          placeholder="Enter E-Procurement URL"
          required
        />
        <input
          name="tender_type"
          value={form.tender_type}
          onChange={handleChange}
          placeholder="Tender Type (O/L)"
          required
        />
        <input
          name="days_interval"
          type="number"
          value={form.days_interval}
          onChange={handleChange}
          placeholder="How many days back to scrape"
          required
        />
        <input
          name="start_page"
          type="number"
          value={form.start_page}
          onChange={handleChange}
          placeholder="Starting Page Number"
          required
        />
        <button type="submit" disabled={showCaptcha}>
          Start Scraping
        </button>
      </form>

      {showCaptcha && (
        <form onSubmit={handleSubmitCaptcha}>
          <input
            value={captcha}
            onChange={(e) => setCaptcha(e.target.value)}
            placeholder="Enter Captcha"
            required
          />
          <button type="submit">Submit Captcha</button>
        </form>
      )}

      <div style={{ marginTop: 20, color: "green" }}>{status}</div>
    </div>
  );
} 