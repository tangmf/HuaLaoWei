import React from "react";
import { ImageBackground, StyleSheet, View } from "react-native";

const Background = ({ children }) => {
  return (
    <ImageBackground
      source={require("@/assets/images/bgimg.png")} // Replace with your background image path
      style={styles.background}
    >
      <View style={styles.overlay}>
        {children}
      </View>
    </ImageBackground>
  );
};

const styles = StyleSheet.create({
  background: {
    flex: 1,
    resizeMode: "cover",
  },
  overlay: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },
});

export default Background;