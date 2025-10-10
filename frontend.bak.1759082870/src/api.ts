// frontend/src/api.ts  (REPLACE ENTIRE FILE)
import axios from "axios";
const API = import.meta.env.VITE_API_URL || "http://localhost:8000";

export async function uploadForPreview(file: File) {
  const form = new FormData();
  form.append("file", file);
  const { data } = await axios.post(`${API}/preview`, form);
  return data as { job_id: string; preview_url: string };
}

export async function createCheckout(job_id: string) {
  const form = new FormData();
  form.append("job_id", job_id);
  const { data } = await axios.post(`${API}/checkout`, form);
  return data as { id: string; url: string };
}

export async function createSubscriptionCheckout(job_id: string, email: string) {
  const form = new FormData();
  form.append("job_id", job_id);
  form.append("email", email);
  const { data } = await axios.post(`${API}/checkout-subscription`, form);
  return data as { id: string; url: string };
}

export async function processFull(params: {
  job_id: string;
  file: File;
  session_id?: string | null;
  email?: string | null;
}) {
  const form = new FormData();
  form.append("job_id", params.job_id);
  form.append("file", params.file);
  if (params.session_id) form.append("session_id", params.session_id);
  if (params.email) form.append("email", params.email);
  const { data } = await axios.post(`${API}/process-full`, form);
  return data as { download_url: string };
}

