import React from "react";
import { View, Text, Pressable } from "react-native";
import { Link, useRouter } from "expo-router";

export default function Navbar() {
  const router = useRouter();
  const currentRoute = router.pathname;

  return (
    <View className="flex-row justify-around items-center h-[60px] bg-white border-t border-gray-300">
      <Link href="/home" asChild>
        <Pressable className="items-center p-1">
          <Text className={`text-base ${currentRoute === "/home" ? "text-blue-600 font-bold" : "text-gray-800"}`}>Home</Text>
        </Pressable>
      </Link>

      <Link href="/create" asChild>
        <Pressable className="items-center p-1">
          <Text className={`text-base ${currentRoute === "/create" ? "text-blue-600 font-bold" : "text-gray-800"}`}>Create</Text>
        </Pressable>
      </Link>

      <Link href="/manualsubmission" asChild>
        <Pressable className="items-center p-1">
          <Text className={`text-base ${currentRoute === "/manualsubmission" ? "text-blue-600 font-bold" : "text-gray-800"}`}>Manual Submission</Text>
        </Pressable>
      </Link>

      <Link href="/profile" asChild>
        <Pressable className="items-center p-1">
          <Text className={`text-base ${currentRoute === "/profile" ? "text-blue-600 font-bold" : "text-gray-800"}`}>Profile</Text>
        </Pressable>
      </Link>
    </View>
  );
}
