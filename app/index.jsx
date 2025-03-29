import React from "react";
import { View, Text, Pressable, StyleSheet, Image, ImageBackground } from "react-native";
import * as WebBrowser from "expo-web-browser";
import { Link } from "expo-router"; // Import Link for navigation
import Background from "@/components/Background";

export default function SignIn() {
  const handleSignIn = async () => {
    // Replace with your Singpass login URL
    const singpassLoginUrl = "https://www.singpass.gov.sg/login"; // Example URL

    try {
      // Open the Singpass login page in a browser
      const result = await WebBrowser.openBrowserAsync(singpassLoginUrl);
      console.log("Login result:", result);
    } catch (error) {
      console.error("Error during Singpass login:", error);
    }
  };

  return (
    <Background>
      <View style={styles.container}>
        {/* Logo */}
        <Image
          source={require("@/assets/images/icon.png")} // Replace with your app's logo
          style={styles.logo}
        />

        {/* Title */}
        <Text style={styles.title}>Welcome to HuaLaoWei</Text>
        <Text style={styles.subtitle}>Sign in with Singpass to continue</Text>

        {/* Sign In Button */}
        <Pressable style={styles.signInButton} onPress={handleSignIn}>
          <Text style={styles.signInButtonText}>Sign in with Singpass</Text>
        </Pressable>

        {/* Go to Home Button */}
        <Link href="/home" style={styles.homeButton} asChild>
          <Pressable>
            <Text style={styles.homeButtonText}>Debug</Text>
          </Pressable>
        </Link>
      </View>
    </Background>
  );
}

const styles = StyleSheet.create({
  background: {
    flex: 1,
    resizeMode: "cover",
  },
  container: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: "rgba(255, 255, 255, 0.8)", // Semi-transparent overlay
    padding: 20,
  },
  logo: {
    width: 120,
    height: 120,
    marginBottom: 20,
    borderRadius: 60, // Circular logo
    borderWidth: 2,
    borderColor: "#007bff",
  },
  title: {
    fontSize: 28,
    fontWeight: "bold",
    color: "#333",
    marginBottom: 10,
    textAlign: "center",
  },
  subtitle: {
    fontSize: 16,
    color: "#666",
    marginBottom: 30,
    textAlign: "center",
  },
  signInButton: {
    backgroundColor: "#007bff",
    paddingVertical: 15,
    paddingHorizontal: 40,
    borderRadius: 25,
    alignItems: "center",
    marginBottom: 20,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 5,
    elevation: 5,
  },
  signInButtonText: {
    color: "#fff",
    fontSize: 18,
    fontWeight: "bold",
  },
  homeButton: {
    backgroundColor: "#28a745",
    paddingVertical: 15,
    paddingHorizontal: 40,
    borderRadius: 25,
    alignItems: "center",
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 5,
    elevation: 5,
  },
  homeButtonText: {
    color: "#fff",
    fontSize: 18,
    fontWeight: "bold",
  },
});