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
import { Audio } from "expo-av";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { v4 as uuidv4 } from "uuid";
import Constants from "expo-constants";
import { useAuth } from "@/hooks/useAuth";

export default function Chatbot() {
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [recording, setRecording] = useState(null);
  const [isRecording, setIsRecording] = useState(false);
  const [messages, setMessages] = useState([
    { id: 1, text: "How may I help you?", sender: "bot" },
  ]);
  const [input, setInput] = useState("");
  const flatListRef = useRef(null);
  const navigation = useNavigation();
  const [sessionId, setSessionId] = useState(null);

  const { token, userId } = useAuth();
  const host = Constants.expoConfig?.hostUri?.split(":")[0];
  const API_BASE_URL = `http://${host}:${process.env.EXPO_PUBLIC_BACKEND_PORT}`;

  useEffect(() => {
    const loadSession = async () => {
      let stored = await AsyncStorage.getItem("chatbot_session_id");
      if (!stored) {
        stored = uuidv4();
        await AsyncStorage.setItem("chatbot_session_id", stored);
      }
      setSessionId(stored);
    };
    loadSession();
  }, []);

  useEffect(() => {
    if (flatListRef.current) {
      flatListRef.current.scrollToEnd({ animated: true });
    }
  }, [messages]);

  const handleSend = () => {
    if (input.trim() === "" || !userId) return;
    setMessages((prev) => [...prev, { id: prev.length + 1, text: input, sender: "user" }]);
    sendMessageToBot(input);
    setInput("");
  };

  const sendMessageToBot = async (message) => {
    let botResponse = "Sorry, I could not process your request.";
    try {
      const formData = new FormData();
      formData.append("text", message);
      formData.append("user_id", String(userId));
      formData.append("session_id", sessionId);

      const res = await fetch(`${API_BASE_URL}/v1/ai_models/chatbot/text`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      });

      const json = await res.json();
      botResponse = json.response || botResponse;
    } catch (err) {
      console.error("Chatbot error:", err);
    } finally {
      setMessages((prev) => [...prev, { id: prev.length + 1, text: botResponse, sender: "bot" }]);
    }
  };

  const handleAudioInput = async () => {
    if (isRecording) return handleStopRecording();
    try {
      const { status } = await Audio.requestPermissionsAsync();
      if (status !== "granted") return;

      const rec = new Audio.Recording();
      await rec.prepareToRecordAsync(Audio.RECORDING_OPTIONS_PRESET_HIGH_QUALITY);
      await rec.startAsync();
      setRecording(rec);
      setIsRecording(true);
    } catch (err) {
      console.error("Audio input error:", err);
    }
  };

  const handleStopRecording = async () => {
    let botResponse = "Sorry, audio could not be processed.";
    try {
      await recording.stopAndUnloadAsync();
      setIsRecording(false);

      const uri = recording.getURI();
      const formData = new FormData();
      formData.append("audio", {
        uri,
        name: "voice-message.m4a",
        type: "audio/m4a",
      });
      formData.append("user_id", String(userId));
      formData.append("session_id", sessionId);

      const res = await fetch(`${API_BASE_URL}/v1/ai_models/chatbot/audio`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      });

      const json = await res.json();
      botResponse = json.response || botResponse;
    } catch (err) {
      console.error("Stop recording error:", err);
    } finally {
      setRecording(null);
      setMessages((prev) => [...prev, { id: prev.length + 1, text: botResponse, sender: "bot" }]);
    }
  };

  return (
    <View className="absolute bottom-20 right-0 z-10">
      <Pressable onPress={() => setIsChatOpen(true)} className="bg-primary rounded-full p-3 shadow-md shadow-black/25">
        <Image source={require("@/assets/images/bot-icon.png")} className="w-12 h-12" resizeMode="contain" />
      </Pressable>

      <Modal visible={isChatOpen} transparent animationType="slide" onRequestClose={() => setIsChatOpen(false)}>
        <View className="flex-1 bg-black/50 justify-end">
          <View className="bg-white rounded-t-2xl p-4 max-h-[70%]">
            <View className="flex-row justify-between items-center mb-3">
              <Text className="text-lg font-bold text-primary">Chatbot</Text>
              <Pressable onPress={() => setIsChatOpen(false)}>
                <Icon name="close" size={24} color="#8B0000" />
              </Pressable>
            </View>
            <FlatList
              ref={flatListRef}
              data={messages}
              keyExtractor={(item) => item.id.toString()}
              renderItem={({ item }) => (
                <View className={`${item.sender === "bot" ? "self-start bg-gray-200" : "self-end bg-primary"} rounded-lg p-3 mb-2 max-w-[70%]`}>
                  <Text className={`${item.sender === "bot" ? "text-black" : "text-white"} text-sm`}>{item.text}</Text>
                </View>
              )}
            />
            <View className="flex-row items-center mt-3 border-t border-gray-300 pt-3">
              <TextInput
                value={input}
                editable={!isRecording}
                onChangeText={setInput}
                placeholder="Type a message..."
                className="flex-1 bg-gray-100 rounded-full px-4 py-2 text-sm border border-gray-300 mr-3"
              />
              <Pressable onPress={handleAudioInput} className="bg-primary rounded-full p-3 mr-2">
                <Icon name={isRecording ? "stop" : "mic"} size={20} color="white" />
              </Pressable>
              <Pressable onPress={handleSend} className="bg-primary rounded-full p-3">
                <Icon name="send" size={20} color="white" />
              </Pressable>
            </View>
          </View>
        </View>
      </Modal>
    </View>
  );
}
