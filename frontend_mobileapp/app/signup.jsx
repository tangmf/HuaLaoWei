import React, { useEffect, useState } from "react";
import { View, Text, Pressable, Image, TextInput } from "react-native";
import Icon from "react-native-vector-icons/MaterialIcons";
import { useNavigation } from "@react-navigation/native";
import Constants from "expo-constants";
import * as Crypto from "expo-crypto";
import axios from "axios";

export default function SignUp() {
  const navigation = useNavigation(); // Get the navigation object
  const [username, setUsername] = useState(""); // State for username
  const [email, setEmail] = useState(""); // State for email
  const [password, setPassword] = useState(""); // State for password
  const [confirmPassword, setConfirmPassword] = useState(""); // State for password
  const [isPasswordVisible, setIsPasswordVisible] = useState(false); // State for toggling password visibility

  // Dynamically extract LAN IP from Expo
  const host = Constants.expoConfig?.hostUri?.split(":")[0];
  const API_BASE_URL = `http://${host}:${process.env.EXPO_PUBLIC_BACKEND_PORT}`;
  
  const validateForm = () => {
    let errorMessage = ""; // Initialize error message
    if (username.trim() === "") errorMessage = "Username is required"; // Check if username is empty
    else if (email.trim() === "") errorMessage = "Email is required";
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) errorMessage = "Invalid email format";
    else if (password !== confirmPassword) errorMessage = "Passwords do not match"; // Initialize error message
    else if (password.length < 8) errorMessage = "Password needs at least 8 characters"; // Initialize error message

    if (errorMessage !== "") {
      alert(errorMessage);
    }
    return errorMessage === "";
  }

  const hashPassword = async (password) => {
    return await Crypto.digestStringAsync(Crypto.CryptoDigestAlgorithm.SHA256, password);
  };

  const handleSignUp = async () => {
    if (!validateForm()) return;
    
    const password_hash = await hashPassword(password);

    const payload = {
      username,
      email,
      password_hash,
    };

    console.log(payload)

    try {
      console.log(`${API_BASE_URL}/v1/auth/signup`)
      const response = await fetch(`${API_BASE_URL}/v1/auth/signup`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await response.json();

      if (response.ok && data.access_token) {
        alert("Account created. You are now signed in.");
        navigation.navigate("home");
        setPassword("");
      } else {
        alert(data.message || "Signup failed");
      }
    } catch (error) {
      console.error("Signup error:", error);
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

        {/* Email Field */}
        <TextInput
          className="w-full max-w-md bg-gray-100 py-3 px-4 rounded-lg mb-4 border border-gray-300"
          placeholder="Email"
          value={email}
          onChangeText={setEmail}
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

        {/* Confirm Password Field */}
        <View className="w-full max-w-md bg-gray-100 px-4 rounded-lg mb-4 border border-gray-300 flex-row items-center">
          <TextInput
            className="flex-1"
            placeholder="Confirm Password"
            value={confirmPassword}
            onChangeText={setConfirmPassword}
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

        {/* Sign Up Button */}
        <Pressable
          onPress={handleSignUp}
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