import React, { useState } from "react";
import { View, Text, TextInput, Pressable, StyleSheet, Image, FlatList } from "react-native";
import Navbar from "@/components/Navbar";

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

  const userProfilePicture = require("@/assets/images/profile-pic.png"); // Replace with your user profile picture path

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

    setInput(""); // Clear input field
  };

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerText}>HuaLaoWei Bot</Text>
      </View>

      {/* Chat Area */}
      <FlatList
        data={messages}
        keyExtractor={(item) => item.id.toString()}
        renderItem={({ item }) => (
          <View
            style={[
              styles.messageBubble,
              item.isBot ? styles.botBubble : styles.userBubble,
            ]}
          >
            {item.isBot ? (
              <Image
                source={require("@/assets/images/bot-icon.png")} // Replace with your bot icon path
                style={styles.botIcon}
              />
            ) : (
              <Image
                source={userProfilePicture} // User profile picture
                style={styles.userIcon}
              />
            )}
            <View>
              <Text style={styles.messageText}>{item.text}</Text>
              <Text style={styles.timestamp}>{item.timestamp}</Text>
            </View>
          </View>
        )}
        contentContainerStyle={styles.chatContainer}
      />

      {/* Input Area */}
      <View style={styles.inputContainer}>
        <TextInput
          style={styles.input}
          placeholder="Type here ..."
          value={input}
          onChangeText={setInput}
        />
        <Pressable style={styles.sendButton} onPress={handleSend}>
          <Text style={styles.sendButtonText}>↑</Text>
        </Pressable>
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
  chatContainer: {
    padding: 10,
  },
  messageBubble: {
    marginVertical: 5,
    padding: 10,
    borderRadius: 10,
    maxWidth: "80%",
    flexWrap: "wrap",
    flexDirection: "row", // Align icon and text in a row
    alignItems: "center",
  },
  botBubble: {
    backgroundColor: "#f0f0f0",
    alignSelf: "flex-start",
  },
  userBubble: {
    backgroundColor: "#007bff",
    alignSelf: "flex-end",
  },
  messageText: {
    color: "#000",
  },
  timestamp: {
    fontSize: 10,
    color: "#666",
    marginTop: 5,
  },
  botIcon: {
    width: 30,
    height: 30,
    marginRight: 10,
  },
  userIcon: {
    width: 30,
    height: 30,
    marginRight: 10,
    borderRadius: 15, // Make the user icon circular
  },
  inputContainer: {
    flexDirection: "row",
    alignItems: "center",
    padding: 10,
    borderTopWidth: 1,
    borderTopColor: "#ccc",
    backgroundColor: "#f8f8f8", // Solid background color
  },
  input: {
    flex: 1,
    height: 40,
    borderWidth: 1,
    borderColor: "#ccc",
    borderRadius: 20,
    paddingHorizontal: 10,
    marginRight: 10,
  },
  sendButton: {
    backgroundColor: "#007bff",
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: "center",
    alignItems: "center",
  },
  sendButtonText: {
    color: "#fff",
    fontSize: 18,
  },
});
