import React, { useState } from "react";
import { View, Text, TextInput, Pressable, Image, FlatList } from "react-native";
import Navbar from "@/components/Navbar";
import Header from "@/components/Header";

export default function Create() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "Hi! I’m HuaLaoWei bot! How may I assist you?\n\n1. Report a new case\n2. Check on status of previously reported case(s)\n3. Get notified on what’s happening nearby\n4. Other questions\n\nKey in 1, 2, 3, or 4 to proceed.",
      isBot: true,
      timestamp: new Date().toLocaleTimeString(),
    },
  ]);

  const userProfilePicture = require("@/assets/images/profile-pic.png");

  const handleSend = () => {
    if (input.trim() === "") return;

    const userMessage = {
      id: messages.length + 1,
      text: input,
      isBot: false,
      timestamp: new Date().toLocaleTimeString(),
    };

    setMessages((prev) => [...prev, userMessage]);

    setTimeout(() => {
      let botResponse = "I'm sorry, I didn't understand that.";
      if (input === "1") botResponse = "Please provide details about the new case.";
      else if (input === "2") botResponse = "Checking the status of your previously reported cases...";
      else if (input === "3") botResponse = "Here are the latest updates happening nearby.";
      else if (input === "4") botResponse = "Feel free to ask any other questions.";

      const botMessage = {
        id: messages.length + 2,
        text: botResponse,
        isBot: true,
        timestamp: new Date().toLocaleTimeString(),
      };

      setMessages((prev) => [...prev, botMessage]);
    }, 1000);

    setInput("");
  };

  return (
    <View className="flex-1 bg-white">
      <Header title="Chatbot" />

      <FlatList
        data={messages}
        keyExtractor={(item) => item.id.toString()}
        renderItem={({ item }) => (
          <View
            className={`my-1 p-3 rounded-xl max-w-[80%] flex-wrap flex-row items-start space-x-2 ${
              item.isBot ? "bg-gray-200 self-start" : "bg-blue-500 self-end"
            }`}
          >
            <Image
              source={item.isBot ? require("@/assets/images/bot-icon.png") : userProfilePicture}
              className="w-7 h-7 mt-1"
            />
            <View>
              <Text className="text-sm text-black whitespace-pre-line">{item.text}</Text>
              <Text className="text-[10px] text-gray-600 mt-1">{item.timestamp}</Text>
            </View>
          </View>
        )}
        contentContainerStyle={{ padding: 10 }}
      />

      <View className="flex-row items-center p-3 border-t border-gray-300 bg-gray-100">
        <TextInput
          className="flex-1 h-10 border border-gray-300 rounded-full px-4 mr-2 bg-white"
          placeholder="Type here ..."
          value={input}
          onChangeText={setInput}
        />
        <Pressable onPress={handleSend} className="w-10 h-10 bg-blue-500 rounded-full justify-center items-center">
          <Text className="text-white text-lg">↑</Text>
        </Pressable>
      </View>

      <Navbar />
    </View>
  );
}
