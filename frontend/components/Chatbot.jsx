import React, { useState, useRef, useEffect } from "react";
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
import { useNavigation } from "@react-navigation/native";

export default function Chatbot() {
  const [isChatOpen, setIsChatOpen] = useState(false); // State to toggle chat window
  const [messages, setMessages] = useState([
    { id: 1, text: "How may I help you?", sender: "bot" },
  ]); // Chat messages
  const [input, setInput] = useState(""); // User input
  const flatListRef = useRef(null); // Create a ref for the FlatList
  const navigation = useNavigation(); // Get the navigation object

  // Scroll to bottom when new message comes in
  useEffect(() => {
    if (flatListRef.current) {
      flatListRef.current.scrollToEnd({ animated: true });
    }
  }, [messages]); // Trigger whenever messages change

  const handleSend = () => {
    if (input.trim() === "") return;

    // Add user message
    setMessages((prevMessages) => [
      ...prevMessages,
      { id: prevMessages.length + 1, text: input, sender: "user" },
    ]);
    setInput(""); // Clear input

    // send message to the bot
    sendMessageToBot(input)
  };

  const openManualReport = () => {
    // Open manual report page
    setIsChatOpen(false); // Close chat window
    // Navigate to manual report page
    navigation.navigate("create");
    console.log("Opening manual report page...");
  }

  const handleAudioInput = () => {
    // Handle audio input (e.g., record audio and convert to text)
    console.log("Audio input feature is not implemented yet.");
    
  }

  const sendMessageToBot = (message) => {
    // Call API to send to bot
    let botResponse = "";

    if (message.toLowerCase().includes("report")) {
      // If the message contains "report", open the manual report page
      openManualReport();
      return;
    }

    try {
      // botResponse = await fetch("https://api.example.com/chatbot", {
      //   method: "POST",
      //   headers: {
      //     "Content-Type": "application/json",
      //   },
      //   body: JSON.stringify({ message }),
      // });
      // const data = await botResponse.json();

      // Test
      botResponse = "This is a test response from the bot."; // Replace with actual API response
    } catch (error) {
      console.error("Error sending message to bot:", error);
      botResponse = "Sorry, I couldn't process your request. Please try again. Error: " + error.message;
    } finally {
      setMessages((prevMessages) => [
        ...prevMessages,
        { id: prevMessages.length + 1, text: botResponse, sender: "bot" },
      ]);
    }
  }
    



  return (
    <View className="absolute bottom-20 right-0 z-10">
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
              ref={flatListRef}
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
                onPress={handleAudioInput}
                className="bg-primary rounded-full p-3 mr-2"
              >
                <Icon name="mic" size={20} color="white" />
              </Pressable>
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