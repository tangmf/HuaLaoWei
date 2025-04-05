import React from "react";
import { View, Text, Image, FlatList, Pressable } from "react-native";
import Icon from "react-native-vector-icons/MaterialIcons";
import Navbar from "@/components/Navbar";
import Header from "@/components/Header";

export default function Profile() {
  const user = {
    username: "John Doe",
    profilePicture: require("@/assets/images/profile-pic.png"),
    region: "Singapore",
    posts: [
      { id: 1, content: "Reported a case of public nudity.", timestamp: "2025-03-28 14:30" },
      { id: 2, content: "Reported a case of public nudity.", timestamp: "2025-03-28 14:30" },
      { id: 3, content: "Reported a case of public nudity.", timestamp: "2025-03-28 14:30" },
      { id: 4, content: "Reported a case of public nudity.", timestamp: "2025-03-28 14:30" },
    ],
  };

  const handleSettings = () => {
    console.log("Open Settings");
  };

  return (
    <View className="flex-1 bg-white">
      <Header title="Profile" />

      <View className="items-center my-5">
        <Image source={user.profilePicture} className="w-[100px] h-[100px] rounded-full mb-2" />
        <Text className="text-2xl font-bold text-gray-800 mb-1">{user.username}</Text>
        <Text className="text-base text-gray-600 mb-2">Region: {user.region}</Text>
        <Pressable onPress={handleSettings} className="p-2">
          <Icon name="settings" size={24} color="#007bff" />
        </Pressable>
      </View>

      <View className="flex-1 px-5">
        <Text className="text-lg font-bold text-gray-800 mb-2">Your Posts</Text>
        <FlatList
          data={user.posts}
          keyExtractor={(item) => item.id.toString()}
          renderItem={({ item }) => (
            <View className="bg-gray-100 p-4 rounded-lg mb-2 shadow-sm">
              <Text className="text-base text-gray-800">{item.content}</Text>
              <Text className="text-xs text-gray-500 mt-1 text-right">{item.timestamp}</Text>
            </View>
          )}
        />
      </View>

      <Navbar />
    </View>
  );
}