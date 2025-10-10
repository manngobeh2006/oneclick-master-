import React, { useEffect, useMemo, useState } from "react";
import {
  uploadForPreview,
  createCheckout,
  createSubscriptionCheckout,
  processFull,
} from "./api";

type Plan = "one_time" | "subscription";

function ProgressBar({ value, label }: { value: number; label?: string }) {
  if (!value || value <= 0 || value > 100) return null;
  return (
    <div style={{ width: "100%", marginTop: 10 }}>
      <div
        style={{
          height: 8,
          background: "#ffffff22",
          borderRadius: 8,
          overflow: "hidden",
        }}
      >
        <div
          style={{
            height: "100%",
            width: `${Math.min(100, Math.max(1, value))}%`,
            background: "#6ea8fe",
            transition: "width .1s linear",
          }}
        />
      </div>
      <div style={{ marginTop: 6, fontSize: 12, color: "#9fb0cc" }}>
        {label ?? "Progress"}: {Math.round(value)}%
      </div>
    </div>
  );
}

export default function App() {
  // Core state
  const [file, setFile] = useState<File | null>(null);
  const [jobId, setJobId] = useState("");
  const [previewUrl, setPreviewUrl] = useState("");
  const [downloadUrl, setDownloadUrl] = useState("");

  // UI state
  const [status, setStatus] = useState("Idle");
  const [error, setError] = useState("");

  // Billing state
  const [plan, setPlan] = useState<Plan>("one_time");
  const [email, setEmail] = useState("");          // for subscription
  const [sessionId, setSessionId] = useState("");  // from Stripe return (dev uses stub)

  // Progress state
  const [uploadPct, setUploadPct] = useState(0);
  const [processPct, setProcessPct] = useState(0);

  // Capture session_id & job_id after Stripe redirect
  useEffect(() => {
    const q = new URLSearchParams(window.location.search);
    const sid = q.get("session_id");
    const jid = q.get("job_id");
    if (sid) setSessionId(sid);
    if (jid) setJobId(jid);
    if (sid || jid) {
      const clean = window.location.origin + window.location.pathname;
      window.history.replaceState({}, "", clean);
    }
  }, []);

  const canPay = useMemo(() => {
    if (!jobId) return false;
    if (plan === "one_time") return true;
    return email.trim().length > 5 && email.includes("@");
  }, [jobId, plan, email]);

  async function startPreview() {
    if (!file) return;
    setError("");
    setStatus("Uploading & generating preview…");
    setUploadPct(0);
    try {
      // upload with progress
      const res = await uploadForPreview(file, setUploadPct);
      setJobId(res.job_id);
      // IMPORTANT: prefix with /api so the browser hits Vite proxy → FastAPI
      setPreviewUrl(`/api${res.preview_url}`);
      setStatus("Preview ready. Listen below.");
    } catch (e: any) {
      setError(e?.message || "Preview failed.");
      setStatus("Idle");
    }
  }

  async function onCheckout() {
    if (!jobId) return;
    setError("");
    setStatus("Opening checkout…");
    try {
      if (plan === "one_time") {
        const { url } = await createCheckout(jobId);
        window.location.href = url;
      } else {
        if (!email || !email.includes("@")) {
          setError("Enter a valid email to subscribe.");
          setStatus("Idle");
          return;
        }
        const { url } = await createSubscriptionCheckout(jobId, email);
        window.location.href = url;
      }
    } catch (e: any) {
      setError(e?.message || "Checkout failed.");
      setStatus("Idle");
    }
  }

  async function onProcessFull() {
    if (!file || !jobId) return;
    setError("");
    setStatus("Processing full-quality export…");
    setProcessPct(0);
    try {
      const res = await processFull(
        {
          job_id: jobId,
          file,
          session_id: sessionId || undefined,
          email: plan === "subscription" ? email : undefined,
        },
        setProcessPct
      );
      // Backend returns /files/outputs/<id>.mp3 → prefix with /api for the proxy
      setDownloadUrl(`/api${res.download_url}`);
      setStatus("Your download is ready.");
    } catch (e: any) {
      setError(e?.message || "Processing failed.");
      setStatus("Idle");
    }
  }

  return (
    <div className="app">
      <div className="card">
        {/* Header */}
        <div className="row" style={{ justifyContent: "space-between" }}>
          <div>
            <h1>OneClick Master</h1>
            <div className="sub">
              AI audio cleanup & mastering — full-length preview, pay to download
            </div>
          </div>
          <div className="badge">
            <span>Status:</span>
            <strong>{status}</strong>
          </div>
        </div>

        <hr className="sep" />

        {/* File + Start */}
        <div className="row">
          <label className="input">
            <input
              type="file"
              accept="audio/*"
              style={{ display: "none" }}
              onChange={(e) => {
                setFile(e.target.files?.[0] || null);
                setError("");
                setPreviewUrl("");
                setDownloadUrl("");
                setUploadPct(0);
                setProcessPct(0);
              }}
            />
            {file ? `Selected: ${file.name}` : "Choose audio file (MP3/WAV/M4A/AIFF)"}
          </label>

          <button className="btn" onClick={startPreview} disabled={!file}>
            {!file ? "Select a file to start" : "Start (Generate Preview)"}
          </button>

          <a className="btn secondary" href="/api/health" target="_blank" rel="noreferrer">
            API Health
          </a>
        </div>

        {/* Upload progress */}
        <ProgressBar value={uploadPct} label="Upload" />

        {/* Error line */}
        {error && (
          <div style={{ marginTop: 10 }} className="error">
            {error}
          </div>
        )}

        {/* Preview player */}
        {previewUrl && (
          <>
            <hr className="sep" />
            <div className="row">
              <span className="pill">Preview (watermarked, stream only)</span>
            </div>
            <div className="audio-wrap" style={{ marginTop: 10 }}>
              <audio controls src={previewUrl} style={{ width: "100%" }} />
              <div className="small" style={{ marginTop: 6 }}>
                If it doesn’t play, the link may have expired (presigned). Click{" "}
                <strong>Start</strong> again to refresh.
              </div>
            </div>
          </>
        )}

        <hr className="sep" />

        {/* Payment plan */}
        <div className="row">
          <label className="radio">
            <input
              type="radio"
              name="plan"
              value="one_time"
              checked={plan === "one_time"}
              onChange={() => setPlan("one_time")}
            />
            One-time export
          </label>
          <label className="radio">
            <input
              type="radio"
              name="plan"
              value="subscription"
              checked={plan === "subscription"}
              onChange={() => setPlan("subscription")}
            />
            Monthly subscription
          </label>
          {plan === "subscription" && (
            <input
              type="email"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          )}
        </div>

        {/* Pay / Process */}
        <div className="row" style={{ marginTop: 10 }}>
          <button
            className="btn"
            onClick={onCheckout}
            disabled={!jobId || !((plan === "one_time") || (plan === "subscription" && email.includes("@")))}
          >
            Pay
          </button>
          <button
            className="btn secondary"
            onClick={onProcessFull}
            disabled={!file || !jobId}
          >
            Process Full (after payment)
          </button>
        </div>

        {/* Processing progress */}
        <ProgressBar value={processPct} label="Uploading for full export" />

        {/* Payment badge */}
        {sessionId && (
          <div className="pill" style={{ marginTop: 10 }}>
            Payment session detected. You can process your full-quality download now.
          </div>
        )}

        {/* Download link */}
        {downloadUrl && (
          <>
            <hr className="sep" />
            <div className="row">
              <span className="pill" style={{ background: "#1f2b46" }}>
                Your mastered file
              </span>
              <a className="btn" href={downloadUrl}>Download</a>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

