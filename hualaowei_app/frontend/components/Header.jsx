import React from "react";
import { View, Text } from "react-native";

export default function Header({ title }) {
  return (
    <View className="h-[60px] justify-center items-center border-b border-gray-300">
      <Text className="text-lg font-bold">{title}</Text>
    </View>
  );
}