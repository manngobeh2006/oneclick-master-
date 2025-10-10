// frontend/src/App.tsx  (REPLACE ENTIRE FILE)
import { useEffect, useMemo, useState } from "react";
import { uploadForPreview, createCheckout, createSubscriptionCheckout, processFull } from "./api";

type Plan = "one_time" | "subscription";

export default function App() {
  const [file, setFile] = useState<File | null>(null);
  const [jobId, setJobId] = useState<string>("");
  const [previewUrl, setPreviewUrl] = useState<string>("");
  const [downloadUrl, setDownloadUrl] = useState<string>("");
  const [loading, setLoading] = useState(false);

  const [plan, setPlan] = useState<Plan>("one_time");
  const [email, setEmail] = useState<string>("");          // for subscription
  const [sessionId, setSessionId] = useState<string>("");  // from Stripe return

  // Grab session_id & job_id from URL after Stripe returns
  useEffect(() => {
    const q = new URLSearchParams(window.location.search);
    const sid = q.get("session_id");
    const jid = q.get("job_id");
    if (sid) setSessionId(sid);
    if (jid) setJobId(jid);
    // Clean URL (optional)
    if (sid || jid) {
      const clean = window.location.origin + window.location.pathname;
      window.history.replaceState({}, "", clean);
    }
  }, []);

  const canPay = useMemo(() => {
    if (!jobId) return false;
    if (plan === "one_time") return true;
    // subscription requires a valid email
    return email.trim().length > 5 && email.includes("@");
  }, [jobId, plan, email]);

  const handlePreview = async () => {
    if (!file) return;
    setLoading(true);
    try {
      const res = await uploadForPreview(file);
      setJobId(res.job_id);
      setPreviewUrl(res.preview_url);
    } finally {
      setLoading(false);
    }
  };

  const handleCheckout = async () => {
    if (!jobId) return;
    if (plan === "one_time") {
      const { url } = await createCheckout(jobId);
      window.location.href = url;
    } else {
      if (!email) return;
      const { url } = await createSubscriptionCheckout(jobId, email);
      window.location.href = url;
    }
  };

  const handleProcess = async () => {
    if (!file || !jobId) return;
    setLoading(true);
    try {
      const res = await processFull({
        job_id: jobId,
        file,
        session_id: sessionId || undefined,
        email: plan === "subscription" ? email : undefined,
      });
      setDownloadUrl(res.download_url);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 760, margin: "2rem auto", padding: 16, fontFamily: "system-ui, -apple-system, Segoe UI, Roboto, Arial" }}>
      <h1>OneClick Master</h1>
      <p>Upload audio → hear full-length preview → pay (one-time or subscribe) → download mastered file</p>

      <input type="file" accept="audio/*" onChange={(e) => setFile(e.target.files?.[0] || null)} />

      {/** Plan selector */}
      <div style={{ marginTop: 12, display: "flex", gap: 16, alignItems: "center" }}>
        <label>
          <input type="radio" name="plan" value="one_time" checked={plan === "one_time"} onChange={() => setPlan("one_time")} />
          {" "}One-time purchase
        </label>
        <label>
          <input type="radio" name="plan" value="subscription" checked={plan === "subscription"} onChange={() => setPlan("subscription")} />
          {" "}Monthly subscription
        </label>
        {plan === "subscription" && (
          <input
            type="email"
            placeholder="your@email.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            style={{ padding: 8, borderRadius: 6, border: "1px solid #ccc" }}
          />
        )}
      </div>

      <div style={{ display: "flex", gap: 8, marginTop: 12 }}>
        <button onClick={handlePreview} disabled={!file || loading}>Get Full Preview</button>
        <button onClick={handleCheckout} disabled={!canPay || loading}>Pay</button>
        <button onClick={handleProcess} disabled={!file || !jobId || loading}>Process Full (after payment)</button>
      </div>

      {previewUrl && (
        <div style={{ marginTop: 16 }}>
          <h3>Preview</h3>
          <audio controls src={previewUrl} />
          <p style={{ color: "#667", fontSize: 14 }}>Note: The preview includes a light watermark beep and lower bitrate for auditioning only.</p>
        </div>
      )}

      {sessionId && (
        <div style={{ marginTop: 10, fontSize: 14, color: "#2a6" }}>
          Payment verified. You can now process your full-quality download.
        </div>
      )}

      {downloadUrl && (
        <div style={{ marginTop: 16 }}>
          <h3>Your Mastered File</h3>
          <a href={downloadUrl}>Download</a>
        </div>
      )}
    </div>
  );
}

