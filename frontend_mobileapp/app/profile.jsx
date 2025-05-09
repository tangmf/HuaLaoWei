import React, { useState } from "react";
import { View, Text, Image, FlatList, Pressable, Modal, TouchableOpacity } from "react-native";
import Icon from "react-native-vector-icons/MaterialIcons";
import Navbar from "@/components/Navbar";
import Header from "@/components/Header";

export default function Profile() {
  const [menuVisible, setMenuVisible] = useState(false); // State for the dropdown menu

  const user = {
    username: "John Tan",
    profilePicture: require("@/assets/images/profile-pic.png"),
    region: "Singapore",
    posts: [
      { id: 1, content: "Long Description to tell users about this issue.", timestamp: "2025-03-28 14:30" },
      { id: 2, content: "Long Description to tell users about this issue.", timestamp: "2025-03-28 14:30" },
      { id: 3, content: "Long Description to tell users about this issue.", timestamp: "2025-03-28 14:30" },
      { id: 4, content: "Long Description to tell users about this issue.", timestamp: "2025-03-28 14:30" },
    ],
  };

  const handleSettings = () => {
    console.log("Open Settings");
  };

  const toggleMenu = () => {
    setMenuVisible(!menuVisible);
  };

  return (
    <View className="flex-1 bg-white">
      <Header title="Profile" />

      {/* Top Section */}
      <View className="flex-row justify-between items-center px-5 py-3 bg-gray-100">
        <View className="flex-row items-center">
          <Image source={user.profilePicture} className="w-[60px] h-[60px] rounded-full mr-5" />
          <View>
            <Text className="text-xl font-bold text-gray-800">{user.username}</Text>
            <Text className="text-sm text-gray-600">Region: {user.region}</Text>
          </View>
        </View>
        
        {/* Hamburger Icon */}
        <Pressable onPress={toggleMenu}>
          <Icon name="menu" size={28}/>
        </Pressable>
      </View>


      <View className="flex-row justify-center mt-4">
  <View className="items-center mx-4">
    <Text className="text-lg font-bold text-black">{user.postCount || "4"}</Text>
    <Text className="text-sm text-black">Posts</Text>
  </View>
  <View className="items-center mx-4">
    <Text className="text-lg font-bold text-black">{user.likeCount || "0"}</Text>
    <Text className="text-sm text-black">Likes</Text>
  </View>
  <View className="items-center mx-4">
    <Text className="text-lg font-bold text-black">{user.commentCount || "0"}</Text>
    <Text className="text-sm text-black">Comments</Text>
  </View>
</View>
            
 
      {/* Dropdown Menu */}
      <Modal
        visible={menuVisible}
        transparent={true}
        animationType="fade"
        onRequestClose={() => setMenuVisible(false)}
      >
        <TouchableOpacity
          style={{ flex: 1, backgroundColor: "rgba(0, 0, 0, 0.5)" }}
          onPress={() => setMenuVisible(false)}
        >
          <View
            style={{
              position: "absolute",
              top: 70,
              right: 20,
              backgroundColor: "white",
              borderRadius: 8,
              padding: 10,
              shadowColor: "#000",
              shadowOffset: { width: 0, height: 2 },
              shadowOpacity: 0.25,
              shadowRadius: 4,
              elevation: 5,
            }}
          >
            <Pressable
              onPress={handleSettings}
              style={{ paddingVertical: 10, paddingHorizontal: 20 }}
            >
              <Text style={{ fontSize: 16, color: "#007bff" }}>Settings</Text>
            </Pressable>
            <Pressable
              onPress={() => console.log("Logout")}
              style={{ paddingVertical: 10, paddingHorizontal: 20 }}
            >
              <Text style={{ fontSize: 16, color: "#007bff" }}>Logout</Text>
            </Pressable>
          </View>
        </TouchableOpacity>
      </Modal>

      {/* Posts Section */}
      <View className="flex-1 px-5 mrt-5 m-5">
        <Text className="text-lg font-bold text-gray-800 mb-2">Your Posts</Text>
        <FlatList
          data={user.posts}
          keyExtractor={(item) => item.id.toString()}
          renderItem={({ item }) => (
            <View className="bg-white p-4 rounded-lg mb-4 shadow-md">
              {/* Post Title */}
              <Text className="text-lg font-bold text-gray-800 mb-2">
                Post #{item.id}
              </Text>

              {/* Post Image */}
              <Image
                source={require("@/assets/images/bgimg.png")} // Replace with actual post image if available
                className="w-full h-40 rounded-lg mb-2"
                resizeMode="cover"
              />

              {/* Post Description */}
              <Text className="text-base text-gray-700 mb-3">
                {item.content}
              </Text>

              {/* Timestamp */}
              <Text className="text-xs text-gray-500 mb-3">
                {item.timestamp}
              </Text>

              {/* Like and Comment Buttons */}
              <View className="flex-row justify-between items-center">
                <Pressable className="flex-row items-center">
                  <Icon name="thumb-up" size={20} color="#007bff" />
                  <Text className="ml-2 text-gray-800">Like</Text>
                </Pressable>
                <Pressable className="flex-row items-center">
                  <Icon name="comment" size={20} color="#007bff" />
                  <Text className="ml-2 text-gray-800">Comment</Text>
                </Pressable>
              </View>
            </View>
          )}
        />
      </View>

      <Navbar />
    </View>
  );
}