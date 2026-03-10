import { Platform } from "react-native";

const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL ?? "http://localhost:8000";

export interface AnalysisResult {
  id: string;
  ring_count: number;
  estimated_age: number;
  age_margin: number;
  confidence: number;
  notes: string;
  annotated_image_url: string | null;
  model_used: "gemini-3-flash" | "gemini-3.1-pro" | "yolo26";
  processing_time_ms: number;
}

/** Extract a human-readable message from any FastAPI error body. */
function extractErrorMessage(body: unknown): string {
  if (!body || typeof body !== "object") return "Analysis failed";
  const { detail } = body as Record<string, unknown>;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail) && detail.length > 0) {
    const first = detail[0];
    if (typeof first === "object" && first !== null) {
      return (first as Record<string, unknown>).msg as string ?? JSON.stringify(first);
    }
  }
  return "Analysis failed";
}

export async function analyzeImage(
  imageUri: string,
  mimeType: string = "image/jpeg"
): Promise<AnalysisResult> {
  const formData = new FormData();

  if (Platform.OS === "web") {
    // On web, expo-image-picker returns a blob: URL.
    // Fetch it to get the actual bytes, then create a proper File for multipart upload.
    const res = await fetch(imageUri);
    const blob = await res.blob();
    const resolvedType = blob.type || mimeType;
    formData.append("file", new File([blob], "photo.jpg", { type: resolvedType }));
  } else {
    // React Native: { uri, name, type } is handled by the native FormData polyfill.
    formData.append("file", {
      uri: imageUri,
      name: "photo.jpg",
      type: mimeType,
    } as unknown as Blob);
  }

  const response = await fetch(`${API_BASE_URL}/analyze`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(extractErrorMessage(body));
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
