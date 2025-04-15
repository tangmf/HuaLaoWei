import * as WebBrowser from "expo-web-browser";
import React from "react";
import { View, Text, Pressable, Image } from "react-native";
import { Link } from "expo-router";

export default function SignIn() {
  const handleSignIn = async () => {
    // Code here to handle sign-in with Huawei cloud
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

        {/* Sign In Button */}
        <Link href="/home" asChild>
          <Pressable
            className="w-full max-w-md bg-primary py-3 rounded-lg mb-4 flex-row justify-center items-center space-x-2 shadow-md shadow-black/20"
          >
            <Text className="text-white text-base font-semibold">
              Sign In
            </Text>
          </Pressable>
        </Link>

        {/* Sign Up Button */}
        <Pressable
          onPress={handleSignIn}
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