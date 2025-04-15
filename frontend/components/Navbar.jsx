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
        height: 50, // Reduced height
        borderRadius: 15, // Adjusted border radius
        marginHorizontal: 15, // Reduced horizontal margin
        marginBottom: 15, // Reduced bottom margin
        paddingVertical: 5, // Reduced padding
        shadowColor: "#000",
        shadowOffset: { width: 0, height: 1 }, // Reduced shadow offset
        shadowOpacity: 0.15, // Reduced shadow opacity
        shadowRadius: 3, // Reduced shadow radius
        elevation: 3, // Reduced elevation for Android
        zIndex: 9,
      }}
      className="bg-primary"
    >
      {/* Home Link */}
      <Link href="/home" asChild>
        <Pressable
          style={{
            alignItems: "center",
            padding: 5, // Reduced padding
            borderRadius: 8, // Adjusted border radius
          }}
        >
          <Ionicons
            name="home"
            size={20} // Reduced icon size
            color={currentRoute === "home" ? "white" : "#d1e7ff"} // Highlight active icon
          />
          <Text
            style={{
              fontSize: 10, // Reduced font size
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
            padding: 5, // Reduced padding
            borderRadius: 8, // Adjusted border radius
          }}
        >
          <Ionicons
            name="add-circle"
            size={20} // Reduced icon size
            color={currentRoute === "create" ? "white" : "#d1e7ff"} // Highlight active icon
          />
          <Text
            style={{
              fontSize: 10, // Reduced font size
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
            padding: 5, // Reduced padding
            borderRadius: 8, // Adjusted border radius
          }}
        >
          <Ionicons
            name="person"
            size={20} // Reduced icon size
            color={currentRoute === "profile" ? "white" : "#d1e7ff"} // Highlight active icon
          />
          <Text
            style={{
              fontSize: 10, // Reduced font size
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