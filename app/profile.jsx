import React from "react";
import { View, Text, Image, FlatList, StyleSheet } from "react-native";
import Navbar from "@/components/Navbar";

export default function Profile() {
  const user = {
    username: "John Doe",
    profilePicture: require("@/assets/images/profile-pic.png"), // Replace with your profile picture path
    region: "Singapore",
    posts: [
      { id: 1, content: "Reported a case of public nudity.", timestamp: "2025-03-28 14:30" },
      { id: 2, content: "Reported a case of public nudity.", timestamp: "2025-03-28 14:30" },
      { id: 3, content: "Reported a case of public nudity.", timestamp: "2025-03-28 14:30" },
      { id: 4, content: "Reported a case of public nudity.", timestamp: "2025-03-28 14:30" },
    ],
  };

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerText}>Profile</Text>
      </View>

      {/* Profile Info */}
      <View style={styles.profileContainer}>
        <Image source={user.profilePicture} style={styles.profilePicture} />
        <Text style={styles.username}>{user.username}</Text>
        <Text style={styles.region}>Region: {user.region}</Text>
      </View>

      {/* Posts */}
      <View style={styles.postsContainer}>
        <Text style={styles.postsHeader}>Your Posts</Text>
        <FlatList
          data={user.posts}
          keyExtractor={(item) => item.id.toString()}
          renderItem={({ item }) => (
            <View style={styles.postItem}>
              <Text style={styles.postContent}>{item.content}</Text>
              <Text style={styles.postTimestamp}>{item.timestamp}</Text>
            </View>
          )}
        />
      </View>

      {/* Navbar */}
      <Navbar />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#fff",
  },
  header: {
    height: 60,
    justifyContent: "center",
    alignItems: "center",
    borderBottomWidth: 1,
    borderBottomColor: "#ccc",
  },
  headerText: {
    fontSize: 20,
    fontWeight: "bold",
  },
  profileContainer: {
    alignItems: "center",
    marginVertical: 20,
  },
  profilePicture: {
    width: 100,
    height: 100,
    borderRadius: 50,
    marginBottom: 10,
  },
  username: {
    fontSize: 24,
    fontWeight: "bold",
    color: "#333",
  },
  region: {
    fontSize: 16,
    color: "#666",
    marginTop: 5,
  },
  postsContainer: {
    flex: 1,
    paddingHorizontal: 20,
  },
  postsHeader: {
    fontSize: 18,
    fontWeight: "bold",
    marginBottom: 10,
    color: "#333",
  },
  postItem: {
    backgroundColor: "#f9f9f9",
    padding: 15,
    borderRadius: 10,
    marginBottom: 10,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 5,
    elevation: 2,
  },
  postContent: {
    fontSize: 16,
    color: "#333",
  },
  postTimestamp: {
    fontSize: 12,
    color: "#999",
    marginTop: 5,
    textAlign: "right",
  },
});
