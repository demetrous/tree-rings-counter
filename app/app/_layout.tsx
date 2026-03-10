import "../global.css";
import { Stack } from "expo-router";
import { StatusBar } from "expo-status-bar";
import { useColorScheme } from "nativewind";
import { useEffect } from "react";
import { LogBox } from "react-native";

// Ignore known NativeWind v4 web warnings
LogBox.ignoreLogs([
  /shadow\*/,
  /pointerEvents/
]);

// Also suppress them from the browser console directly
if (typeof window !== 'undefined') {
  const originalConsoleError = console.error;
  console.error = (...args) => {
    // React Native Web sometimes passes the warning as the first arg, 
    // or as a format string with the warning in subsequent args
    const msg = args.join(' ');
    if (msg.includes('shadow*') || msg.includes('pointerEvents')) {
      return;
    }
    originalConsoleError(...args);
  };
}

export default function RootLayout() {
  const { colorScheme, setColorScheme } = useColorScheme();

  useEffect(() => {
    // Force dark mode for the entire app
    if (colorScheme !== "dark") {
      setColorScheme("dark");
    }
  }, [colorScheme, setColorScheme]);

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
