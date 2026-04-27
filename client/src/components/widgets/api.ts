import { z } from "zod";

export type JobStatus = "pending" | "processing" | "completed" | "failed" | (string & {});

export type DocumentItem = {
  document_id: string;
  original_filename: string;
  stored_filename: string;
  status: JobStatus;
  collection_name: string;
  chroma_path: string;
  indexed_chunks: number;
  created_at: string;
  updated_at: string;
};

export type DocumentQuestionJobResponse = {
  job_id: string;
  document_id: string;
  question: string;
  status: JobStatus;
  started_at: string | null;
  finished_at: string | null;
  created_at: string;
  updated_at: string;
};

export type DocumentQuestionJobDetailResponse = {
  job_id: string;
  document_id: string;
  question: string;
  status: JobStatus;
  answer: string | null;
  error_message: string | null;
  started_at: string | null;
  finished_at: string | null;
  created_at: string;
  updated_at: string;
};

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

const jobStatusSchema = z.string();

const documentItemSchema = z.object({
  document_id: z.string(),
  original_filename: z.string(),
  stored_filename: z.string(),
  status: jobStatusSchema,
  collection_name: z.string(),
  chroma_path: z.string(),
  indexed_chunks: z.number().int(),
  created_at: z.string(),
  updated_at: z.string(),
});

const documentQuestionJobResponseSchema = z.object({
  job_id: z.string(),
  document_id: z.string(),
  question: z.string(),
  status: jobStatusSchema,
  started_at: z.string().nullable(),
  finished_at: z.string().nullable(),
  created_at: z.string(),
  updated_at: z.string(),
});

const documentQuestionJobDetailResponseSchema = z.object({
  job_id: z.string().uuid(),
  document_id: z.string().uuid(),
  question: z.string(),
  status: jobStatusSchema,
  answer: z.string().nullable(),
  error_message: z.string().nullable(),
  started_at: z.string().nullable(),
  finished_at: z.string().nullable(),
  created_at: z.string(),
  updated_at: z.string(),
});

async function parseJsonResponse<T>(response: Response, schema: z.ZodType<T>): Promise<T> {
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(errorText || `Request failed with ${response.status}`);
  }

  const data: unknown = await response.json();
  return schema.parse(data);
}

export async function fetchDocuments(): Promise<DocumentItem[]> {
  const response = await fetch(`${API_BASE_URL}/documents`);
  return parseJsonResponse(response, z.array(documentItemSchema));
}

export async function uploadDocument(file: File): Promise<DocumentItem> {
  const formData = new FormData();
  formData.set("file", file);

  const response = await fetch(`${API_BASE_URL}/documents/index`, {
    method: "POST",
    body: formData,
  });

  return parseJsonResponse(response, documentItemSchema);
}

export async function askDocumentQuestion(params: {
  documentId: string;
  question: string;
  nResults?: number;
}): Promise<DocumentQuestionJobResponse> {
  const response = await fetch(`${API_BASE_URL}/documents/${params.documentId}/ask`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      question: params.question,
      n_results: params.nResults,
    }),
  });

  return parseJsonResponse(response, documentQuestionJobResponseSchema);
}

export async function fetchAskJob(jobId: string): Promise<DocumentQuestionJobDetailResponse> {
  const response = await fetch(`${API_BASE_URL}/documents/ask-jobs/${jobId}`);
  return parseJsonResponse(response, documentQuestionJobDetailResponseSchema);
}
