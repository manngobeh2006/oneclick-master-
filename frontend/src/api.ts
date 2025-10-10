// frontend/src/api.ts — uses XHR to get upload progress events
export type ProgressFn = (percent: number) => void;
const API_BASE = "/api";

function postFormXHR<T>(path: string, form: FormData, onProgress?: ProgressFn): Promise<T> {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open("POST", `${API_BASE}${path}`);
    xhr.upload.onprogress = (e) => {
      if (onProgress && e.lengthComputable) {
        onProgress(Math.max(1, Math.round((e.loaded / e.total) * 100))); // 1..100
      }
    };
    xhr.onreadystatechange = () => {
      if (xhr.readyState === 4) {
        if (xhr.status >= 200 && xhr.status < 300) {
          try {
            resolve(JSON.parse(xhr.responseText));
          } catch {
            reject(new Error("Invalid JSON from server"));
          }
        } else {
          reject(new Error(`HTTP ${xhr.status}: ${xhr.responseText}`));
        }
      }
    };
    xhr.onerror = () => reject(new Error("Network error"));
    xhr.send(form);
  });
}

export async function uploadForPreview(file: File, onProgress?: ProgressFn) {
  const form = new FormData();
  form.append("file", file);
  return postFormXHR<{ job_id: string; preview_url: string }>("/preview", form, onProgress);
}

export async function createCheckout(job_id: string) {
  const form = new FormData();
  form.append("job_id", job_id);
  return postFormXHR<{ id: string; url: string }>("/checkout", form);
}

export async function createSubscriptionCheckout(job_id: string, email: string) {
  const form = new FormData();
  form.append("job_id", job_id);
  form.append("email", email);
  return postFormXHR<{ id: string; url: string }>("/checkout-subscription", form);
}

export async function processFull(params: {
  job_id: string;
  file: File;
  session_id?: string | null;
  email?: string | null;
}, onProgress?: ProgressFn) {
  const form = new FormData();
  form.append("job_id", params.job_id);
  form.append("file", params.file);
  if (params.session_id) form.append("session_id", params.session_id);
  if (params.email) form.append("email", params.email);
  return postFormXHR<{ download_url: string }>("/process-full", form, onProgress);
}

