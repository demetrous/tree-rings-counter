import { useLocalSearchParams, useRouter } from "expo-router";
import {
  View,
  Text,
  Image,
  ScrollView,
  TouchableOpacity,
  Share,
  Alert,
} from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { SafeAreaView } from "react-native-safe-area-context";
import RingOverlay from "@/components/RingOverlay";
import ResultCard from "@/components/ResultCard";
import type { AnalysisResult } from "@/services/api";

export default function ResultScreen() {
  const { resultJson, imageUri } = useLocalSearchParams<{
    id: string;
    resultJson: string;
    imageUri: string;
  }>();
  const router = useRouter();

  let result: AnalysisResult | null = null;
  try {
    result = JSON.parse(resultJson ?? "null");
  } catch {
    result = null;
  }

  if (!result) {
    return (
      <View className="flex-1 bg-forest-950 items-center justify-center gap-4 px-8">
        <Ionicons name="alert-circle-outline" size={48} color="#5fa05f" />
        <Text className="text-white text-center text-base">
          Result data is unavailable.
        </Text>
        <TouchableOpacity
          onPress={() => router.back()}
          className="bg-forest-700 rounded-xl px-6 py-3"
        >
          <Text className="text-white font-semibold">Go Back</Text>
        </TouchableOpacity>
      </View>
    );
  }

  const handleShare = async () => {
    try {
      await Share.share({
        message: `🌲 Tree age estimate: ~${result!.estimated_age} years (± ${result!.age_margin} yrs), based on ${result!.ring_count} visible rings. Analyzed with Tree Rings Counter app.`,
      });
    } catch {
      Alert.alert("Share failed", "Could not share the result.");
    }
  };

  return (
    <SafeAreaView className="flex-1 bg-forest-950" edges={["bottom"]}>
      <ScrollView
        className="flex-1"
        contentContainerClassName="pb-12 items-center"
        showsVerticalScrollIndicator={false}
      >
        <View className="w-full max-w-3xl px-4 pt-6 gap-8">
          {/* Result card (Top) */}
          <View className="gap-4">
            <ResultCard result={result} />

            {/* Action buttons */}
            <View className="flex-row gap-3 mt-2">
              <TouchableOpacity
                onPress={() => router.back()}
                className="flex-1 bg-forest-900 border border-forest-700/40 rounded-2xl py-4 flex-row items-center justify-center gap-2"
              >
                <Ionicons name="camera-outline" size={20} color="#5fa05f" />
                <Text className="text-forest-400 font-semibold">New Photo</Text>
              </TouchableOpacity>

              <TouchableOpacity
                onPress={handleShare}
                className="flex-1 bg-forest-600 rounded-2xl py-4 flex-row items-center justify-center gap-2"
              >
                <Ionicons name="share-outline" size={20} color="white" />
                <Text className="text-white font-semibold">Share</Text>
              </TouchableOpacity>
            </View>
          </View>

          {/* Ring visualization */}
          <View className="items-center">
            <View className="bg-forest-900/50 rounded-full p-4 border border-forest-700/30">
              <RingOverlay ringCount={result.ring_count} size={160} />
            </View>
          </View>

          {/* Photo (Bottom) */}
          <View className="w-full rounded-2xl overflow-hidden bg-black/20 border border-forest-800/50">
            {imageUri ? (
              <Image
                source={{ uri: imageUri }}
                className="w-full aspect-square sm:aspect-video"
                resizeMode="contain"
              />
            ) : null}
          </View>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}
