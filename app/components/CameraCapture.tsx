import { useState, useRef, useCallback } from "react";
import {
  View,
  Text,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
  Platform,
} from "react-native";
import { CameraView, CameraType, useCameraPermissions } from "expo-camera";
import * as ImagePicker from "expo-image-picker";
import { Ionicons } from "@expo/vector-icons";

interface CameraCaptureProps {
  onCapture: (uri: string) => void;
  isAnalyzing: boolean;
}

export default function CameraCapture({
  onCapture,
  isAnalyzing,
}: CameraCaptureProps) {
  const [facing] = useState<CameraType>("back");
  const [permission, requestPermission] = useCameraPermissions();
  const [showCamera, setShowCamera] = useState(false);
  const cameraRef = useRef<CameraView>(null);

  const handleTakePicture = useCallback(async () => {
    if (!cameraRef.current) return;
    try {
      const photo = await cameraRef.current.takePictureAsync({
        quality: 0.92,
        exif: false,
      });
      if (photo?.uri) {
        setShowCamera(false);
        onCapture(photo.uri);
      }
    } catch {
      Alert.alert("Error", "Failed to take picture. Please try again.");
    }
  }, [onCapture]);

  const handlePickFromGallery = useCallback(async () => {
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ["images"],
      quality: 0.92,
      allowsEditing: true,
      aspect: [1, 1],
    });
    if (!result.canceled && result.assets[0]) {
      onCapture(result.assets[0].uri);
    }
  }, [onCapture]);

  const handleOpenCamera = useCallback(async () => {
    if (Platform.OS === "web") {
      handlePickFromGallery();
      return;
    }
    if (!permission?.granted) {
      const { granted } = await requestPermission();
      if (!granted) {
        Alert.alert(
          "Camera Permission",
          "Camera access is needed to photograph tree cross-sections.",
          [{ text: "OK" }]
        );
        return;
      }
    }
    setShowCamera(true);
  }, [permission, requestPermission, handlePickFromGallery]);

  if (showCamera) {
    return (
      <View className="flex-1 bg-black">
        <CameraView
          ref={cameraRef}
          className="flex-1"
          facing={facing}
        >
          {/* Guidance overlay */}
          <View className="flex-1 items-center justify-center">
            {/* Circle guide */}
            <View className="w-72 h-72 rounded-full border-2 border-white/60 items-center justify-center">
              <View className="w-48 h-48 rounded-full border border-white/30" />
              <View className="absolute w-1 h-full border-l border-white/20" />
              <View className="absolute h-1 w-full border-t border-white/20" />
            </View>
            <Text className="text-white/80 mt-4 text-sm text-center px-8">
              Center the cut surface inside the circle
            </Text>
          </View>

          {/* Bottom controls */}
          <View className="pb-10 px-8 flex-row items-center justify-between">
            <TouchableOpacity
              onPress={() => setShowCamera(false)}
              className="w-12 h-12 items-center justify-center"
            >
              <Ionicons name="close" size={28} color="white" />
            </TouchableOpacity>

            <TouchableOpacity
              onPress={handleTakePicture}
              className="w-20 h-20 rounded-full border-4 border-white items-center justify-center"
              disabled={isAnalyzing}
            >
              <View className="w-16 h-16 rounded-full bg-white" />
            </TouchableOpacity>

            <TouchableOpacity
              onPress={() => {
                setShowCamera(false);
                handlePickFromGallery();
              }}
              className="w-12 h-12 items-center justify-center"
            >
              <Ionicons name="images-outline" size={28} color="white" />
            </TouchableOpacity>
          </View>
        </CameraView>
      </View>
    );
  }

  return (
    <View className="flex-1 items-center justify-center px-6 gap-6">
      {/* Hero illustration */}
      <View className="w-40 h-40 rounded-full bg-forest-800/60 border border-forest-500/40 items-center justify-center">
        <Ionicons name="leaf" size={72} color="#5fa05f" />
      </View>

      <Text className="text-white/90 text-center text-base px-4 leading-6">
        Point your camera at the{" "}
        <Text className="text-forest-400 font-semibold">cross-section</Text> of
        a freshly cut tree to estimate its age.
      </Text>

      {/* Tips */}
      <View className="w-full bg-forest-900/60 rounded-2xl p-4 gap-2 border border-forest-700/40">
        <Text className="text-forest-300 font-semibold text-sm mb-1">
          For best results:
        </Text>
        {[
          "Use bright, even lighting (avoid harsh shadows)",
          "Hold phone parallel to the cut surface",
          "Fill the frame with the cross-section",
          "Clean away dust or sawdust if possible",
        ].map((tip, i) => (
          <View key={i} className="flex-row items-start gap-2">
            <Text className="text-forest-500 text-xs mt-0.5">•</Text>
            <Text className="text-white/60 text-xs flex-1">{tip}</Text>
          </View>
        ))}
      </View>

      {isAnalyzing ? (
        <View className="w-full bg-forest-700/30 rounded-2xl p-5 items-center gap-3">
          <ActivityIndicator size="large" color="#5fa05f" />
          <Text className="text-forest-300 text-sm">Analyzing rings…</Text>
        </View>
      ) : (
        <View className="w-full gap-3">
          <TouchableOpacity
            onPress={handleOpenCamera}
            className="w-full bg-forest-600 rounded-2xl py-4 flex-row items-center justify-center gap-3"
          >
            <Ionicons name="camera" size={22} color="white" />
            <Text className="text-white font-semibold text-base">
              Take Photo
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            onPress={handlePickFromGallery}
            className="w-full bg-forest-900 border border-forest-600/50 rounded-2xl py-4 flex-row items-center justify-center gap-3"
          >
            <Ionicons name="images-outline" size={22} color="#5fa05f" />
            <Text className="text-forest-400 font-semibold text-base">
              Choose from Gallery
            </Text>
          </TouchableOpacity>
        </View>
      )}
    </View>
  );
}
