import React from "react";
import { ImageBackground, View } from "react-native";

export default function Background({ children }) {
  return (
    <ImageBackground
      source={require("@/assets/images/bgimg.png")}
      className="flex-1"
      resizeMode="cover"
    >
      <View className="flex-1 justify-center items-center">
        {children}
      </View>
    </ImageBackground>
  );
}
