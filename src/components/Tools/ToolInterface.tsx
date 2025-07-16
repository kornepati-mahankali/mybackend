import React, { useState } from "react";
import axios from "axios";
import { Tool } from '../../types';

interface ToolInterfaceProps {
  tool: Tool;
  onBack: () => void;
}

export const ToolInterface: React.FC<ToolInterfaceProps> = ({ tool, onBack }) => {
  const [inputValues, setInputValues] = useState<any>({});
  const [sessionId, setSessionId] = useState("");
  const [showCaptcha, setShowCaptcha] = useState(false);
  const [captcha, setCaptcha] = useState("");
  const [status, setStatus] = useState("");

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInputValues({ ...inputValues, [e.target.name]: e.target.value });
  };

  const handleStartScraping = async () => {
    setStatus("Starting scraping session...");
    try {
      const res = await axios.post<{ session_id: string }>("http://localhost:8000/start-scraping", null, {
        params: inputValues,
      });
      setSessionId(res.data.session_id);
      setShowCaptcha(true);
      setStatus("Please enter the captcha shown in the opened Edge browser.");
    } catch (err: any) {
      setStatus("Failed to start scraping: " + (err.response?.data?.error || err.message));
    }
  };

  const handleSubmitCaptcha = async () => {
    setStatus("Submitting captcha...");
    try {
      const res = await axios.post<{ status: string }>("http://localhost:8000/submit-captcha", {
        session_id: sessionId,
        captcha_value: captcha,
      });
      setStatus(res.data.status || "Captcha submitted!");
    } catch (err: any) {
      setStatus("Failed to submit captcha: " + (err.response?.data?.error || err.message));
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-white mb-2">{tool.name}</h1>
      <p className="text-gray-400 mb-4">{tool.description}</p>
      <form className="space-y-4" onSubmit={e => { e.preventDefault(); handleStartScraping(); }}>
        {tool.inputs && tool.inputs.map((input, idx) => (
          <div key={idx}>
            <label className="block text-gray-300 mb-1">{input.description}</label>
            <input
              className="w-full px-3 py-2 rounded bg-zinc-800 text-white"
              name={input.name}
              type={input.type === 'int' ? 'number' : 'text'}
              required={input.required}
              value={inputValues[input.name] || ''}
              onChange={handleInputChange}
              placeholder={input.description}
            />
          </div>
        ))}
        <div className="flex space-x-4">
          <button type="submit" className="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded">
            Start Scraping
          </button>
          <button type="button" onClick={onBack} className="bg-red-600 hover:bg-red-700 text-white px-6 py-2 rounded">
            Back
          </button>
        </div>
      </form>
      {showCaptcha && (
        <form className="mt-4 flex space-x-2" onSubmit={e => { e.preventDefault(); handleSubmitCaptcha(); }}>
          <input
            value={captcha}
            onChange={e => setCaptcha(e.target.value)}
            placeholder="Enter Captcha"
            className="px-3 py-2 rounded bg-zinc-800 text-white"
            required
          />
          <button type="submit" className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded">
            Submit Captcha
          </button>
        </form>
      )}
      <div className="mt-4 text-green-400">{status}</div>
    </div>
  );
};
