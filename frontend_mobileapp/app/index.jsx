import AsyncStorage from "@react-native-async-storage/async-storage";
import React, { useState } from "react";
import { View, Text, Pressable, Image, TextInput } from "react-native";
import Icon from "react-native-vector-icons/MaterialIcons";
import { useNavigation } from "@react-navigation/native";
import * as Crypto from "expo-crypto";
import Constants from "expo-constants";

export default function SignIn() {
  const navigation = useNavigation(); // Get the navigation object
  const [username, setUsername] = useState(""); // State for username
  const [password, setPassword] = useState(""); // State for password
  const [isPasswordVisible, setIsPasswordVisible] = useState(false); // State for toggling password visibility

  // Dynamically extract LAN IP from Expo
  const host = Constants.expoConfig?.hostUri?.split(":")[0];
  const API_BASE_URL = `http://${host}:${process.env.EXPO_PUBLIC_BACKEND_PORT}`;
  
  const validateForm = () => {
    let errorMessage = ""; // Initialize error message
    if (username.trim() === "") errorMessage = "Username is required"; // Check if username is empty
    else if (username.trim() === "") errorMessage = "Username is required"; // Check if username is empty
    else if (password.length < 8) errorMessage = "Password needs at least 8 characters"; // Initialize error message

    if (errorMessage !== "") {
      alert(errorMessage);
    }
    return errorMessage === "";
  }
  
  const hashPassword = async (password) => {
    return await Crypto.digestStringAsync(Crypto.CryptoDigestAlgorithm.SHA256, password);
  };

  const handleSignIn = async () => {
    if (!validateForm(password)) return;

    try {
      const password_hash = await hashPassword(password);

      console.log(`${API_BASE_URL}/v1/auth/signin`)
      const response = await fetch(`${API_BASE_URL}/v1/auth/signin`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password_hash }),
      });

      const text = await response.text();
      console.log("Raw response:", text);
      let data;
      try {
        data = JSON.parse(text);
      } catch (e) {
        console.error("Failed to parse JSON:", e);
        alert("Server error: " + text);
        return;
      }
      
      if (response.ok && data.access_token) {
        // Save token to AsyncStorage here if needed
        await AsyncStorage.setItem("token", data.access_token);
        
        navigation.navigate("home");
        setPassword("");
      } else {
        alert(data.message || "Invalid username or password");
        setPassword("");
      }
    } catch (error) {
      console.error("SignIn error:", error);
      alert("Network error. Please try again later.");
    }
  };

  return (
      <View className="flex-1 justify-center items-center px-6 bg-white">
        {/* Logo */}
        <Image
          source={require("@/assets/images/icon.png")}
          className="w-[100px] h-[100px] mb-8"
          resizeMode="contain"
        />

        {/* Title */}
        <Text className="text-3xl font-bold text-primary mb-2 text-center">
          Welcome to HuaLaoWei
        </Text>

        <Text className="text-base text-gray-600 mb-10 text-center">
          Your trusted platform for community reporting
        </Text>

        {/* Username Field */}
        <TextInput
          className="w-full max-w-md bg-gray-100 py-3 px-4 rounded-lg mb-4 border border-gray-300"
          placeholder="Username"
          value={username}
          onChangeText={setUsername}
        />

        {/* Password Field */}
        <View className="w-full max-w-md bg-gray-100 px-4 rounded-lg mb-4 border border-gray-300 flex-row items-center">
        <TextInput
          className="flex-1"
          placeholder="Password (Min 8 characters)"
          value={password}
          onChangeText={setPassword}
          secureTextEntry={!isPasswordVisible} // Toggle visibility
        />
        <Pressable onPress={() => setIsPasswordVisible(!isPasswordVisible)}>
          <Icon
            name={isPasswordVisible ? "visibility" : "visibility-off"} // Toggle icon
            size={20}
            color="gray"
          />
        </Pressable>
      </View>

        {/* Sign In Button */}
        <Pressable
          onPress={handleSignIn}
          className="w-full max-w-md bg-primary py-3 rounded-lg mb-4 flex-row justify-center items-center space-x-2 shadow-md shadow-black/20"
        >
          <Text className="text-white text-base font-semibold">
            Sign In
          </Text>
        </Pressable>

        {/* Sign Up Button */}
        <Pressable
          onPress={() => navigation.navigate("signup")}
          className="w-full max-w-md bg-white py-3 rounded-lg mb-4 border border-primary flex-row justify-center items-center space-x-2 shadow-sm"
        >
          <Text className="text-primary text-base font-semibold">
            Sign Up
          </Text>
        </Pressable>

        {/* Footer */}
        <Text className="text-sm text-gray-500 mt-10 text-center">
          By signing up, you agree to our{" "}{"\n"}
          <Text className="text-primary font-medium">Terms of Service</Text>{" "}
          and{" "}
          <Text className="text-primary font-medium">Privacy Policy</Text>.
        </Text>
      </View>
  );
}