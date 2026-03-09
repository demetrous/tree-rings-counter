import "../global.css";
import { Stack } from "expo-router";
import { StatusBar } from "expo-status-bar";

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
