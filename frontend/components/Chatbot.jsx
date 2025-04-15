import React, { useState } from "react";
import {
  View,
  Text,
  TextInput,
  Pressable,
  Modal,
  FlatList,
  Image,
} from "react-native";
import Icon from "react-native-vector-icons/MaterialIcons";

export default function Chatbot() {
  const [isChatOpen, setIsChatOpen] = useState(false); // State to toggle chat window
  const [messages, setMessages] = useState([
    { id: 1, text: "How may I help you?", sender: "bot" },
  ]); // Chat messages
  const [input, setInput] = useState(""); // User input

  const handleSend = () => {
    if (input.trim() === "") return;

    // Add user message
    setMessages((prevMessages) => [
      ...prevMessages,
      { id: prevMessages.length + 1, text: input, sender: "user" },
    ]);
    setInput(""); // Clear input
  };

  return (
    <View className="absolute bottom-20 right-5 z-10">
      {/* Chatbot Icon */}
      <Pressable
        onPress={() => setIsChatOpen(true)}
        className="bg-primary rounded-full p-3 shadow-md shadow-black/25"
      >
        <Image
          source={require("@/assets/images/bot-icon.png")} // Replace with your chatbot icon
          className="w-12 h-12"
          resizeMode="contain"
        />
      </Pressable>

      {/* Chat Window */}
      <Modal
        visible={isChatOpen}
        transparent={true}
        animationType="slide"
        onRequestClose={() => setIsChatOpen(false)}
      >
        <View className="flex-1 bg-black/50 justify-end">
          <View className="bg-white rounded-t-2xl p-4 max-h-[70%]">
            {/* Chat Header */}
            <View className="flex-row justify-between items-center mb-3">
              <Text className="text-lg font-bold text-primary">Chatbot</Text>
              <Pressable onPress={() => setIsChatOpen(false)}>
                <Icon name="close" size={24} color="#8B0000" />
              </Pressable>
            </View>

            {/* Chat Messages */}
            <FlatList
              data={messages}
              keyExtractor={(item) => item.id.toString()}
              renderItem={({ item }) => (
                <View
                  className={`${
                    item.sender === "bot"
                      ? "self-start bg-gray-200"
                      : "self-end bg-primary"
                  } rounded-lg p-3 mb-2 max-w-[70%]`}
                >
                  <Text
                    className={`${
                      item.sender === "bot" ? "text-black" : "text-white"
                    } text-sm`}
                  >
                    {item.text}
                  </Text>
                </View>
              )}
            />

            {/* Input Field */}
            <View className="flex-row items-center mt-3 border-t border-gray-300 pt-3">
              <TextInput
                value={input}
                onChangeText={setInput}
                placeholder="Type a message..."
                className="flex-1 bg-gray-100 rounded-full px-4 py-2 text-sm border border-gray-300 mr-3"
              />
              <Pressable
                onPress={handleSend}
                className="bg-primary rounded-full p-3"
              >
                <Icon name="send" size={20} color="white" />
              </Pressable>
            </View>
          </View>
        </View>
      </Modal>
    </View>
  );
}