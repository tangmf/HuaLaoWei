import React from "react";
import { View, Text, Pressable, Image } from "react-native";
import * as WebBrowser from "expo-web-browser";
import { Link } from "expo-router";
import Background from "@/components/Background";

export default function SignIn() {
  const handleSignIn = async () => {
    // Code here to handle sign-in with Huawei cloud
  };

  return (
    <Background>
      <View className="flex-1 justify-center items-center px-6">

        {/* Logo */}
        <Image
          source={require("@/assets/images/icon.png")}
          className="w-[100px] h-[100px] mb-8"
          resizeMode="contain"
        />

        {/* Title */}
        <Text className="text-2xl font-semibold text-[#31727c] mb-1 text-center">
          HuaLaoWei
        </Text>

        <Text className="text-sm text-gray-600 mb-10 text-center">
          Sign in to continue
        </Text>

        {/* Debug / Primary Button */}
        <Link href="/home" asChild>
          <Pressable
            className="w-full max-w-md bg-[#31727c] py-3 rounded-lg mb-4 flex-row justify-center items-center space-x-2 shadow-sm shadow-black/10"
          >
            <Text className="text-white text-base font-medium">
              Debug
            </Text>
          </Pressable>
        </Link>

        {/* Login with Singpass */}
        <Pressable
          onPress={handleSignIn}
          className="w-full max-w-md bg-white py-3 rounded-lg mb-4 border border-[#1ea9c0] flex-row justify-center items-center space-x-2"
        >
          <Text className="text-[#1ea9c0] text-base font-medium">
            Login with Singpass
          </Text>
        </Pressable>

        {/* Optional: Add this if you want a tertiary link later */}
        {/* <Pressable onPress={() => {}} className="mt-2">
          <Text className="text-[#b62f3e] text-sm font-medium">
            Log in using passcode
          </Text>
        </Pressable> */}

      </View>
    </Background>
  );
}
