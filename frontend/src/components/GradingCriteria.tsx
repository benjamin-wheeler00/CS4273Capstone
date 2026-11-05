"use client";

import { useEffect, useRef, useState } from "react";
import { Pencil } from "lucide-react";
import { getApiBaseUrl } from "@/lib/api";

// The API exposes only the stable question ID and its editable wording.
interface Criterion {
  id: string;
  text: string;
}

export default function GradingCriteria({ natureCodeId }: { natureCodeId: string }) {
  // Keep the saved list separate from the draft so Cancel never changes a criterion.
  const [criteria, setCriteria] = useState<Criterion[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState("");
  const [editing, setEditing] = useState<Criterion | null>(null);
  const [text, setText] = useState("");
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState("");
  // Incrementing this value lets Retry trigger a fresh load for the same protocol.
  const [attempt, setAttempt] = useState(0);
  // Native dialog controls provide modal focus handling; the textarea receives focus on open.
  const dialog = useRef<HTMLDialogElement>(null);
  const textarea = useRef<HTMLTextAreaElement>(null);
  const endpoint = `${getApiBaseUrl()}/api/grading-criteria/${encodeURIComponent(natureCodeId)}`;

  // Fetch the current master criteria when the protocol changes or the user retries.
  useEffect(() => {
    const controller = new AbortController();
    setLoading(true);
    setLoadError("");
    fetch(endpoint, { signal: controller.signal, cache: "no-store" })
      .then(async (response) => {
        if (!response.ok) throw new Error("Unable to load grading criteria.");
        return response.json() as Promise<Criterion[]>;
      })
      .then(setCriteria)
      .catch((error: unknown) => {
        if (!controller.signal.aborted) {
          setLoadError(error instanceof Error ? error.message : "Unable to load grading criteria.");
        }
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });
    // Stop an old request when this list is removed or another protocol is selected.
    return () => controller.abort();
  }, [endpoint, attempt]);

  // Synchronize the browser's modal with the selected criterion in React state.
  useEffect(() => {
    if (editing) {
      dialog.current?.showModal();
      textarea.current?.focus();
    } else {
      dialog.current?.close();
    }
  }, [editing]);

  async function confirm() {
    // Reject blank drafts and repeated submissions while a save is in progress.
    if (!editing || saving || !text.trim()) return;
    setSaving(true);
    setSaveError("");
    try {
      // Send only this criterion's wording; other question metadata stays on the server.
      const response = await fetch(`${endpoint}/${encodeURIComponent(editing.id)}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: text.trim() }),
      });
      const result = await response.json();
      if (!response.ok) throw new Error(result.error || "Unable to save criterion.");
      const updated = result as Criterion;
      // Update the displayed wording only after the backend confirms persistence.
      setCriteria((previous) => previous.map((item) => item.id === updated.id ? updated : item));
      setEditing(null);
    } catch (error) {
      // Preserve the draft and keep the popup open so the user can retry.
      setSaveError(error instanceof Error ? error.message : "Unable to save criterion.");
    } finally {
      setSaving(false);
    }
  }

  // Show loading or recovery controls before rendering the editable list.
  if (loading) return <p role="status">Loading grading criteria...</p>;
  if (loadError) return (
    <div role="alert">
      <p className="text-red-700">{loadError}</p>
      <button type="button" className="mt-2 underline" onClick={() => setAttempt((value) => value + 1)}>Retry</button>
    </div>
  );

  return (
    <div className="space-y-2">
      {/* Render each saved criterion with its own accessible pencil button. */}
      {criteria.length === 0 && <p>No grading criteria available.</p>}
      {criteria.map((criterion, index) => (
        <div key={criterion.id} className="flex items-start gap-3 rounded-md border border-gray-200 bg-gray-50 p-3 shadow-inner">
          <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-[#002d62] text-sm font-extrabold text-white">{index + 1}</span>
          <p className="grow whitespace-pre-wrap font-medium leading-relaxed text-gray-800">{criterion.text}</p>
          <button
            type="button"
            aria-label={`Edit criterion: ${criterion.text}`}
            title="Edit grading criterion"
            className="shrink-0 rounded p-2 text-gray-600 hover:bg-gray-200 focus-visible:outline-2 focus-visible:outline-blue-600"
            onClick={() => {
              // Start each edit from the saved text, discarding any previous draft.
              setText(criterion.text);
              setSaveError("");
              setEditing(criterion);
            }}
          >
            <Pencil size={16} aria-hidden="true" />
          </button>
        </div>
      ))}
      {/* Reuse one modal for the selected criterion instead of creating one per row. */}
      <dialog
        ref={dialog}
        aria-labelledby="criterion-dialog-title"
        aria-describedby="criterion-dialog-description"
        className="fixed inset-0 m-auto w-[calc(100%-2rem)] max-w-lg rounded-lg bg-white p-6 text-gray-900 shadow-2xl backdrop:bg-black/50"
        onCancel={(event) => {
          // Escape may dismiss a draft, but must not hide an in-progress save.
          if (saving) event.preventDefault();
          else setEditing(null);
        }}
        onClose={() => setEditing(null)}
      >
        <form onSubmit={(event) => {
          // Handle submission here to avoid a browser navigation or page reload.
          event.preventDefault();
          void confirm();
        }}>
          <h3 id="criterion-dialog-title" className="text-xl font-bold text-[#002d62]">Edit grading criterion</h3>
          <p id="criterion-dialog-description" className="my-3 text-sm text-gray-600">Changes apply to future grading and regrading for this protocol.</p>
          {/* The draft remains local until Confirm successfully saves it. */}
          <label htmlFor="criterion-text" className="mb-2 block font-medium">Criterion text</label>
          <textarea
            ref={textarea}
            id="criterion-text"
            rows={5}
            required
            value={text}
            disabled={saving}
            onChange={(event) => setText(event.target.value)}
            className="w-full rounded-md border border-gray-300 p-3 focus:outline-blue-600"
          />
          {saveError && <p role="alert" className="mt-2 text-sm text-red-700">{saveError}</p>}
          {/* Disable both actions during saving to keep the result unambiguous. */}
          <div className="mt-4 flex justify-end gap-3">
            <button type="button" disabled={saving} onClick={() => setEditing(null)} className="rounded-md border px-4 py-2 disabled:opacity-50">Cancel</button>
            <button type="submit" disabled={saving || !text.trim()} className="rounded-md bg-[#002d62] px-4 py-2 text-white disabled:opacity-50">{saving ? "Saving..." : "Confirm"}</button>
          </div>
        </form>
      </dialog>
    </div>
  );
}
