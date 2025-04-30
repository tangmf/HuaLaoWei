import * as WebBrowser from "expo-web-browser";
import React, { useState } from "react";
import { View, Text, Pressable, Image, TextInput } from "react-native";
import Icon from "react-native-vector-icons/MaterialIcons";
import { useNavigation } from "@react-navigation/native";

export default function SignIn() {
  const navigation = useNavigation(); // Get the navigation object
  const [username, setUsername] = useState(""); // State for username
  const [password, setPassword] = useState(""); // State for password
  const [isPasswordVisible, setIsPasswordVisible] = useState(false); // State for toggling password visibility
  
  const validatePassword = (password) => {
    let errorMessage = ""; // Initialize error message
    if (password.length < 8) errorMessage = "Password needs at least 8 characters"; // Initialize error message

    if (errorMessage !== "") {
      alert(errorMessage);
    }
    return errorMessage === "";
  }

  const handleSignIn = () => {
    if (!validatePassword(password)) return;
    // Send API

    // If password is correct, login
    if (true) {
      // Save user data to AsyncStorage or any state management library

      // Change frontend
      navigation.navigate("home");
      setPassword("")
    } else {
      alert("Invalid username or password"); // Show error message
      setPassword("")
    }
  };

  const handleSignUp = () => {
    if (!validatePassword(password)) return;
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