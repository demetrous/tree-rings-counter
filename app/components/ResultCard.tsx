import { View, Text } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import type { AnalysisResult } from "@/services/api";

interface ResultCardProps {
  result: AnalysisResult;
}

function ConfidenceBadge({ confidence }: { confidence: number }) {
  const pct = Math.round(confidence * 100);
  const color =
    pct >= 80
      ? "bg-forest-700/60 text-forest-300"
      : pct >= 55
      ? "bg-yellow-900/60 text-yellow-300"
      : "bg-red-900/60 text-red-300";

  return (
    <View className={`rounded-full px-3 py-1 ${color.split(" ")[0]}`}>
      <Text className={`text-xs font-semibold ${color.split(" ")[1]}`}>
        {pct}% confidence
      </Text>
    </View>
  );
}

function StatItem({
  label,
  value,
  icon,
}: {
  label: string;
  value: string;
  icon: React.ComponentProps<typeof Ionicons>["name"];
}) {
  return (
    <View className="flex-1 bg-forest-900/60 rounded-xl p-3 items-center gap-1 border border-forest-700/30">
      <Ionicons name={icon} size={18} color="#5fa05f" />
      <Text className="text-white font-bold text-lg">{value}</Text>
      <Text className="text-white/50 text-xs">{label}</Text>
    </View>
  );
}

export default function ResultCard({ result }: ResultCardProps) {
  const modelLabel =
    result.model_used === "gemini-2.5-flash"
      ? "Gemini 2.5 Flash"
      : result.model_used === "gemini-2.5-pro"
      ? "Gemini 2.5 Pro"
      : "YOLO26";

  return (
    <View className="gap-4">
      {/* Age headline */}
      <View className="bg-forest-800/50 rounded-2xl p-6 items-center gap-2 border border-forest-600/30">
        <Text className="text-white/60 text-sm uppercase tracking-widest">
          Estimated Age
        </Text>
        <Text className="text-white text-6xl font-bold">
          {result.estimated_age}
        </Text>
        <Text className="text-forest-400 text-base">
          ± {result.age_margin} years
        </Text>
        <ConfidenceBadge confidence={result.confidence} />
      </View>

      {/* Stats row */}
      <View className="flex-row gap-3">
        <StatItem
          label="Rings"
          value={String(result.ring_count)}
          icon="radio-button-off-outline"
        />
        <StatItem
          label="Processing"
          value={`${(result.processing_time_ms / 1000).toFixed(1)}s`}
          icon="time-outline"
        />
        <StatItem
          label="Model"
          value={modelLabel}
          icon="hardware-chip-outline"
        />
      </View>

      {/* Notes from AI */}
      {result.notes ? (
        <View className="bg-forest-900/40 rounded-xl p-4 gap-2 border border-forest-700/20">
          <View className="flex-row items-center gap-2">
            <Ionicons name="information-circle-outline" size={16} color="#5fa05f" />
            <Text className="text-forest-400 text-xs font-semibold uppercase tracking-wide">
              Notes
            </Text>
          </View>
          <Text className="text-white/70 text-sm leading-5">{result.notes}</Text>
        </View>
      ) : null}

      {/* Disclaimer */}
      <Text className="text-white/30 text-xs text-center leading-4">
        Ring counting accuracy depends on image quality and species.
        Results are estimates, not certified measurements.
      </Text>
    </View>
  );
}
