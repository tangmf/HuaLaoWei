import * as WebBrowser from "expo-web-browser";
import React, { useEffect, useState } from "react";
import { View, Text, Pressable, Image, TextInput } from "react-native";
import Icon from "react-native-vector-icons/MaterialIcons";
import { useNavigation } from "@react-navigation/native";
import axios from "axios";

export default function SignUp() {
  const navigation = useNavigation(); // Get the navigation object
  const [username, setUsername] = useState(""); // State for username
  const [email, setEmail] = useState(""); // State for email
  const [password, setPassword] = useState(""); // State for password
  const [confirmPassword, setConfirmPassword] = useState(""); // State for password
  const [isPasswordVisible, setIsPasswordVisible] = useState(false); // State for toggling password visibility
  
  const validateForm = () => {
    let errorMessage = ""; // Initialize error message
    if (username.trim() === "") errorMessage = "Username is required"; // Check if username is empty
    else if (username.trim() === "") errorMessage = "Username is required"; // Check if username is empty
    else if (email.trim() === "") errorMessage = "Email is required";
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) errorMessage = "Invalid email format";
    else if (password !== confirmPassword) errorMessage = "Passwords do not match"; // Initialize error message
    else if (password.length < 8) errorMessage = "Password needs at least 8 characters"; // Initialize error message

    if (errorMessage !== "") {
      alert(errorMessage);
    }
    return errorMessage === "";
  }

  const handleSignUp = async () => {
    if (!validateForm()) return; // Validate the form before proceeding

    // Prepare the user data
    const formData = {
      username,
      email,
      password, // Send the plain password (hashing should be done on the backend for security)
    };
    console.log("2")
  
    try {
      console.log("3")
      // Make the POST request to the signup endpoint
      const { data } = await axios.post("http://localhost:5000/user", formData, {
        headers: {
          "Content-Type": "application/json", // Specify JSON content type
        },
      });
  
      // Handle the response
      console.log("User created successfully:", data);
      alert("Signup successful! Welcome to HuaLaoWei.");
      navigation.navigate("home"); // Navigate to the SignIn screen after successful signup
    } catch (error) {
      // Handle errors
      console.error("Error creating user:", error);
      alert("Error creating user. Please try again. Error: " + error.message);
    }
  }

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
          By signing up, you agree to our{" "}
          <Text className="text-primary font-medium">Terms of Service</Text>{" "}
          and{" "}
          <Text className="text-primary font-medium">Privacy Policy</Text>.
        </Text>
      </View>
  );
}