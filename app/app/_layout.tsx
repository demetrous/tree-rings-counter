import "../global.css";
import { Stack } from "expo-router";
import { StatusBar } from "expo-status-bar";
import { Platform, StyleSheet } from "react-native";

// Fix for NativeWind dark mode error on web
if (Platform.OS === "web") {
  try {
    // @ts-ignore - internal API
    if (typeof StyleSheet.setFlag === "function") {
      StyleSheet.setFlag("darkMode", "class");
    }
  } catch (e) {
    // Ignore if not available
  }
}

export default function RootLayout() {
  return (
    <>
      <StatusBar style="light" />
      <Stack
        screenOptions={{
          headerStyle: { backgroundColor: "#1a2e1a" },
          headerTintColor: "#fff",
          headerTitleStyle: { fontWeight: "bold" },
          contentStyle: { backgroundColor: "#0d1f0f" },
        }}
      >
        <Stack.Screen
          name="index"
          options={{ title: "Tree Rings Counter", headerShown: false }}
        />
        <Stack.Screen
          name="result/[id]"
          options={{ title: "Analysis Result", headerBackTitle: "Back" }}
        />
      </Stack>
    </>
  );
}
