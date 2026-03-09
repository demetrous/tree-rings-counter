const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL ?? "http://localhost:8000";

export interface AnalysisResult {
  id: string;
  ring_count: number;
  estimated_age: number;
  age_margin: number;
  confidence: number;
  notes: string;
  annotated_image_url: string | null;
  model_used: "gemini-2.5-flash" | "gpt-4o" | "yolo26";
  processing_time_ms: number;
}

export interface AnalysisError {
  detail: string;
}

export async function analyzeImage(
  imageUri: string,
  mimeType: string = "image/jpeg"
): Promise<AnalysisResult> {
  const formData = new FormData();
  formData.append("file", {
    uri: imageUri,
    name: "photo.jpg",
    type: mimeType,
  } as unknown as Blob);

  const response = await fetch(`${API_BASE_URL}/analyze`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const err: AnalysisError = await response.json();
    throw new Error(err.detail ?? "Analysis failed");
  }

  return response.json() as Promise<AnalysisResult>;
}

export async function healthCheck(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/health`, { method: "GET" });
    return response.ok;
  } catch {
    return false;
  }
}
