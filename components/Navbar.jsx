import React from "react";
import { View, Text, Pressable, StyleSheet } from "react-native";
import { Link, useRouter } from "expo-router";

export default function Navbar() {
  const router = useRouter();
  const currentRoute = router.pathname;

  return (
    <View style={styles.navbar}>
      <Link href="/" style={styles.link} asChild>
        <Pressable style={styles.navItem}>
          <Text style={[styles.navText, currentRoute === "/home" && styles.activeNavText]}>
            Home
          </Text>
        </Pressable>
      </Link>

      <Link href="/create" style={styles.link} asChild>
        <Pressable style={styles.navItem}>
          <Text style={[styles.navText, currentRoute === "/create" && styles.activeNavText]}>
            Create
          </Text>
        </Pressable>
      </Link>

      <Link href="/profile" style={styles.link} asChild>
        <Pressable style={styles.navItem}>
          <Text style={[styles.navText, currentRoute === "/profile" && styles.activeNavText]}>
            Profile
          </Text>
        </Pressable>
      </Link>
    </View>
  );
}

const styles = StyleSheet.create({
  navbar: {
    flexDirection: "row",
    justifyContent: "space-around",
    alignItems: "center",
    height: 60,
    backgroundColor: "#fff",
    borderTopWidth: 1,
    borderTopColor: "#ccc",
  },
  navItem: {
    alignItems: "center",
  },
  navText: {
    fontSize: 16,
    color: "#333",
  },
  activeNavText: {
    color: "blue", // Highlight color for the active page
    fontWeight: "bold",
  },
  link: {
    padding: 4,
  },
});