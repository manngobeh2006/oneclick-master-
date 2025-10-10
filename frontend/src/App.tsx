import React, { useEffect, useMemo, useState, useRef } from "react";
import {
  uploadForPreview,
  createCheckout,
  createSubscriptionCheckout,
  processFull,
} from "./api";

type Plan = "one_time" | "subscription";

export default function App() {
  // Core state
  const [file, setFile] = useState<File | null>(null);
  const [jobId, setJobId] = useState("");
  const [previewUrl, setPreviewUrl] = useState("");
  const [downloadUrl, setDownloadUrl] = useState("");
  const [originalAudioUrl, setOriginalAudioUrl] = useState("");

  // UI state
  const [status, setStatus] = useState("Ready to master your audio");
  const [error, setError] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const [showComparison, setShowComparison] = useState(false);

  // Billing state
  const [plan, setPlan] = useState<Plan>("one_time");
  const [email, setEmail] = useState("");          // for subscription
  const [sessionId, setSessionId] = useState("");  // from Stripe return (dev uses stub)

  // Progress state
  const [uploadPct, setUploadPct] = useState(0);
  const [processPct, setProcessPct] = useState(0);

  // Audio refs for comparison
  const originalAudioRef = useRef<HTMLAudioElement>(null);
  const masteredAudioRef = useRef<HTMLAudioElement>(null);

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
    setStatus("Processing your audio...");
    setIsProcessing(true);
    setUploadPct(0);
    setShowComparison(false);
    
    // Create original audio URL for comparison
    const originalUrl = URL.createObjectURL(file);
    setOriginalAudioUrl(originalUrl);
    
    try {
      // upload with progress
      const res = await uploadForPreview(file, setUploadPct);
      setJobId(res.job_id);
      // IMPORTANT: prefix with /api so the browser hits Vite proxy → FastAPI
      setPreviewUrl(`/api${res.preview_url}`);
      setStatus("✨ Your mastered preview is ready!");
      setShowComparison(true);
    } catch (e: any) {
      setError(e?.message || "Processing failed. Please try again.");
      setStatus("Ready to master your audio");
    } finally {
      setIsProcessing(false);
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

  // Audio comparison functions
  function playOriginal() {
    if (masteredAudioRef.current) masteredAudioRef.current.pause();
    if (originalAudioRef.current) {
      originalAudioRef.current.currentTime = 0;
      originalAudioRef.current.play();
    }
  }

  function playMastered() {
    if (originalAudioRef.current) originalAudioRef.current.pause();
    if (masteredAudioRef.current) {
      masteredAudioRef.current.currentTime = 0;
      masteredAudioRef.current.play();
    }
  }

  return (
    <div className="app">
      {/* Hero Section */}
      <div className="hero">
        <div className="hero-content">
          <h1 className="hero-title">OneClick Master</h1>
          <p className="hero-subtitle">
            Professional AI audio mastering in seconds. Upload, preview, and download your polished tracks.
          </p>
          <div className="status-badge">
            <span className="status-dot" style={{ backgroundColor: isProcessing ? '#f59e0b' : (previewUrl ? '#10b981' : '#6b7280') }}></span>
            {status}
          </div>
        </div>
      </div>

      <div className="main-content">
        <div className="upload-section">
          <h2>Upload Your Audio</h2>

          <div className="upload-area" onClick={() => document.getElementById('file-input')?.click()}>
            <input
              id="file-input"
              type="file"
              accept="audio/*,.mp3,.wav,.m4a,.aiff,.flac"
              style={{ display: "none" }}
              onChange={(e) => {
                const selectedFile = e.target.files?.[0];
                if (selectedFile) {
                  setFile(selectedFile);
                  setError("");
                  setPreviewUrl("");
                  setDownloadUrl("");
                  setUploadPct(0);
                  setProcessPct(0);
                  setShowComparison(false);
                }
              }}
            />
            <div className="upload-icon">🎵</div>
            <div className="upload-text">
              {file ? (
                <>
                  <div className="file-selected">✓ {file.name}</div>
                  <div className="file-info">{(file.size / 1024 / 1024).toFixed(1)} MB</div>
                </>
              ) : (
                <>
                  <div>Drop your audio file here or click to browse</div>
                  <div className="supported-formats">MP3, WAV, M4A, AIFF, FLAC supported</div>
                </>
              )}
            </div>
          </div>

          <button 
            className={`start-btn ${!file || isProcessing ? 'disabled' : ''}`} 
            onClick={startPreview} 
            disabled={!file || isProcessing}
          >
            {isProcessing ? (
              <>
                <span className="spinner"></span>
                Processing...
              </>
            ) : (
              !file ? "Select a file to start" : "🚀 Start Mastering"
            )}
          </button>
        </div>

        {/* Upload progress */}
        {uploadPct > 0 && (
          <div className="progress-bar">
            <div className="progress-track">
              <div className="progress-fill" style={{ width: `${uploadPct}%` }} />
            </div>
            <div className="progress-label">Upload: {Math.round(uploadPct)}%</div>
          </div>
        )}

        {/* Error line */}
        {error && (
          <div className="error-message">
            <span className="error-icon">⚠️</span>
            {error}
          </div>
        )}

        {/* Before/After Comparison */}
        {showComparison && originalAudioUrl && previewUrl && (
          <div className="comparison-section">
            <h2>Before & After Comparison</h2>
            <div className="audio-comparison">
              <div className="audio-player-container">
                <h3>Original</h3>
                <div className="player-wrapper">
                  <audio ref={originalAudioRef} src={originalAudioUrl} controls />
                  <button className="play-btn original" onClick={playOriginal}>
                    ▶️ Play Original
                  </button>
                </div>
                <div className="audio-info">Raw, unprocessed audio</div>
              </div>
              <div className="vs-divider">
                <span>VS</span>
              </div>
              <div className="audio-player-container">
                <h3>Mastered ✨</h3>
                <div className="player-wrapper">
                  <audio ref={masteredAudioRef} src={previewUrl} controls />
                  <button className="play-btn mastered" onClick={playMastered}>
                    ▶️ Play Mastered
                  </button>
                </div>
                <div className="audio-info">Professional mastered preview</div>
              </div>
            </div>
            <div className="preview-notice">
              <span>📝</span> This is a watermarked preview. Purchase to download the full-quality version.
            </div>
          </div>
        )}

        {/* Pricing Section */}
        {previewUrl && (
          <div className="pricing-section">
            <h2>Choose Your Plan</h2>
            <div className="pricing-cards">
              <div className={`pricing-card ${plan === "one_time" ? "selected" : ""}`}>
                <input
                  type="radio"
                  name="plan"
                  value="one_time"
                  checked={plan === "one_time"}
                  onChange={() => setPlan("one_time")}
                  id="one-time"
                />
                <label htmlFor="one-time">
                  <div className="plan-header">
                    <h3>Single Track</h3>
                    <div className="price">$4.99</div>
                  </div>
                  <ul className="plan-features">
                    <li>✓ One professional master</li>
                    <li>✓ High-quality MP3 download</li>
                    <li>✓ AI-powered processing</li>
                    <li>✓ Instant download</li>
                  </ul>
                </label>
              </div>
              
              <div className={`pricing-card ${plan === "subscription" ? "selected" : ""}`}>
                <input
                  type="radio"
                  name="plan"
                  value="subscription"
                  checked={plan === "subscription"}
                  onChange={() => setPlan("subscription")}
                  id="subscription"
                />
                <label htmlFor="subscription">
                  <div className="plan-header">
                    <h3>Pro Monthly</h3>
                    <div className="price">$19.99<span>/mo</span></div>
                  </div>
                  <ul className="plan-features">
                    <li>✓ Unlimited masters</li>
                    <li>✓ High-quality downloads</li>
                    <li>✓ Advanced AI processing</li>
                    <li>✓ Priority support</li>
                  </ul>
                  {plan === "subscription" && (
                    <input
                      type="email"
                      className="email-input"
                      placeholder="Enter your email address"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      required
                    />
                  )}
                </label>
              </div>
            </div>

            <div className="payment-actions">
              <button
                className="checkout-btn"
                onClick={onCheckout}
                disabled={!jobId || !canPay}
              >
                💳 {plan === "one_time" ? "Buy Single Track" : "Start Subscription"}
              </button>
              <button
                className="process-btn"
                onClick={onProcessFull}
                disabled={!file || !jobId}
              >
                🎵 Process Full Quality
              </button>
            </div>
          </div>
        )}

        {/* Processing progress */}
        {processPct > 0 && (
          <div className="progress-bar">
            <div className="progress-track">
              <div className="progress-fill" style={{ width: `${processPct}%` }} />
            </div>
            <div className="progress-label">Processing: {Math.round(processPct)}%</div>
          </div>
        )}

        {/* Payment badge */}
        {sessionId && (
          <div className="pill" style={{ marginTop: 10 }}>
            Payment session detected. You can process your full-quality download now.
          </div>
        )}

        {/* Download Section */}
        {downloadUrl && (
          <div className="download-section">
            <div className="success-message">
              <span className="success-icon">🎉</span>
              <h2>Your master is ready!</h2>
              <p>Professional quality, ready to share with the world.</p>
            </div>
            <a className="download-btn" href={downloadUrl}>
              <span>⬇️</span>
              Download Your Mastered Track
            </a>
            <div className="download-info">
              High-quality 320kbps MP3 • Professional mastering • Ready for streaming
            </div>
          </div>
        )}
        
        {/* Footer */}
        <div className="footer">
          <p>Powered by AI • Professional Results • Instant Processing</p>
          <a href="/api/health" target="_blank" rel="noreferrer" className="health-link">
            API Status
          </a>
        </div>
      </div>
    </div>
  );
}

