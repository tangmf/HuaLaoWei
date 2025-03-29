import React from "react";
import { Text, View, StyleSheet, TouchableOpacity, ImageBackground, Pressable} from "react-native";
import backgroundimg from "@/assets/images/bgimg.png";
import {Link} from "expo-router";


export default function Index() {
  return (
    <View style={styles.container}>
      {/* Main Content */}
      <View style={styles.content}>
        <ImageBackground
        source = {backgroundimg}
        style = {styles.image}>
          <Text>Edit app/index.tsx to edit this screen.</Text>
        </ImageBackground>
        
      </View>

      {/* Bottom Navigation Bar */}
      <View style={styles.navbar}>

        <Link href = "/index"
        style = {styles.link} asChild>
          <Pressable style={styles.navItem}>
            <Text style={styles.navText}>Home</Text>
          </Pressable>
        </Link>

        <Link href = "/index"
        style = {styles.link} asChild>
          <Pressable style={styles.navItem}>
            <Text style={styles.navText}>Create</Text>
          </Pressable>
        </Link>

        <Link href = "/index"
        style = {styles.link} asChild>
          <Pressable style={styles.navItem}>
            <Text style={styles.navText}>Profile</Text>
          </Pressable>
        </Link>


        {/*
        <TouchableOpacity style={styles.navItem}>
          <Text style={styles.navText}>Home</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.navItem}>
          <Text style={styles.navText}>Create</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.navItem}>
          <Text style={styles.navText}>Profile</Text>
        </TouchableOpacity>
        */}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  image: {
    width: '100%',
    height: '100%',
    resizemode: "cover",
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },
  content: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },
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
  link:{
    padding: 4,
  },
  button:{
    backgroundColor: "#007AFF",
    padding: 10,
    borderRadius: 5,
    marginTop: 20,
  },
  buttonText:{
    color: "#fff",
    fontSize: 16,
  },
});
