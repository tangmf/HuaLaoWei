import React from "react";
import { View, Text, Pressable } from "react-native";
import { Link, useSegments } from "expo-router";
import { Ionicons } from "@expo/vector-icons"; // Import icons from Expo

export default function Navbar() {
  const segments = useSegments(); // Get the current route segments
  const currentRoute = segments[0]; // Get the first segment (e.g., "home", "create", "profile")

  return (
    <View
      style={{
        flexDirection: "row",
        justifyContent: "space-around",
        alignItems: "center",
        height: 70,
        backgroundColor: "#007bff", // Blue background
        borderRadius: 20, // Rounded rectangle
        marginHorizontal: 20, // Padding from left and right
        marginBottom: 20, // Padding from the bottom
        paddingVertical: 10,
        shadowColor: "#000",
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.2,
        shadowRadius: 5,
        elevation: 5, // Shadow for Android
        zIndex: 10,
      }}
    >
      {/* Home Link */}
      <Link href="/home" asChild>
        <Pressable
          style={{
            alignItems: "center",
        
            padding: 10,
            borderRadius: 10,
          }}
        >
          <Ionicons
            name="home"
            size={24}
            color={currentRoute === "home" ? "white" : "#d1e7ff"} // Highlight active icon
          />
          <Text
            style={{
              fontSize: 12,
              color: currentRoute === "home" ? "white" : "#d1e7ff", // Highlight active text
              fontWeight: currentRoute === "home" ? "bold" : "normal",
            }}
          >
            Home
          </Text>
        </Pressable>
      </Link>

      {/* Create Link */}
      <Link href="/create" asChild>
        <Pressable
          style={{
            alignItems: "center",
            
            padding: 10,
            borderRadius: 10,
          }}
        >
          <Ionicons
            name="add-circle"
            size={24}
            color={currentRoute === "create" ? "white" : "#d1e7ff"} // Highlight active icon
          />
          <Text
            style={{
              fontSize: 12,
              color: currentRoute === "create" ? "white" : "#d1e7ff", // Highlight active text
              fontWeight: currentRoute === "create" ? "bold" : "normal",
            }}
          >
            Create
          </Text>
        </Pressable>
      </Link>

      {/* Profile Link */}
      <Link href="/profile" asChild>
        <Pressable
          style={{
            alignItems: "center",
            
            padding: 10,
            borderRadius: 10,
          }}
        >
          <Ionicons
            name="person"
            size={24}
            color={currentRoute === "profile" ? "white" : "#d1e7ff"} // Highlight active icon
          />
          <Text
            style={{
              fontSize: 12,
              color: currentRoute === "profile" ? "white" : "#d1e7ff", // Highlight active text
              fontWeight: currentRoute === "profile" ? "bold" : "normal",
            }}
          >
            Profile
          </Text>
        </Pressable>
      </Link>
    </View>
  );
}