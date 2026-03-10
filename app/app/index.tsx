import { useState, useCallback } from "react";
import { View, Text, Alert, SafeAreaView, StatusBar } from "react-native";
import { useRouter } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import CameraCapture from "@/components/CameraCapture";
import { analyzeImage } from "@/services/api";

export default function HomeScreen() {
  const router = useRouter();
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const handleCapture = useCallback(
    async (uri: string) => {
      setIsAnalyzing(true);
      try {
        const result = await analyzeImage(uri);
        router.push({
          pathname: "/result/[id]",
          params: {
            id: result.id,
            resultJson: JSON.stringify(result),
            imageUri: uri,
          },
        });
      } catch (err) {
        const message =
          err instanceof Error ? err.message : "An unexpected error occurred.";
        Alert.alert("Analysis Failed", message, [{ text: "Try Again" }]);
      } finally {
        setIsAnalyzing(false);
      }
    },
    [router]
  );

  return (
    <View className="flex-1 bg-forest-950 items-center">
      <SafeAreaView className="flex-1 w-full max-w-3xl">
        {/* Header */}
        <View className="px-5 pt-4 pb-3 flex-row items-center gap-3">
          <View className="w-9 h-9 rounded-full bg-forest-700/50 items-center justify-center">
            <Ionicons name="leaf" size={18} color="#5fa05f" />
          </View>
          <View>
            <Text className="text-white font-bold text-lg leading-5">
              Tree Rings Counter
            </Text>
            <Text className="text-white/40 text-xs">
              AI-powered age estimation
            </Text>
          </View>
        </View>

        {/* Camera / upload UI */}
        <CameraCapture onCapture={handleCapture} isAnalyzing={isAnalyzing} />
      </SafeAreaView>
    </View>
  );
}
