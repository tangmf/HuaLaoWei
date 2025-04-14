import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  TextInput,
  Pressable,
  Image,
  ScrollView,
} from "react-native";
import { Picker } from "@react-native-picker/picker";
import * as ImagePicker from "expo-image-picker";
import Navbar from "@/components/Navbar";
import Header from "@/components/Header";

export default function Create() {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [tags, setTags] = useState(["Add New Tag"]);
  const [selectedTag, setSelectedTag] = useState("Add New Tag");
  const [image, setImage] = useState(null); // Placeholder for image insertion

  // Request permissions for media library
  useEffect(() => {
    (async () => {
      const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
      if (status !== "granted") {
        alert("Sorry, we need camera roll permissions to make this work!");
      }
    })();
  }, []);

  // Function to pick an image
  const pickImage = async () => {
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      aspect: [4, 3], // Optional: Crop aspect ratio
      quality: 1, // Image quality (1 = highest)
    });

    if (!result.canceled) {
      setImage(result.assets[0].uri); // Set the selected image URI
    }
  };

  return (
    <View className="flex-1 bg-white">
      <Header title="Create Report" />

      {/* Manual Form Submission */}
      <ScrollView contentContainerStyle={{ padding: 20 }}>
        {/* Title */}
        <Text className="text-lg font-bold mb-2">Title</Text>
        <TextInput
          className="border border-gray-300 rounded-lg p-3 mb-5"
          placeholder="Enter title"
          value={title}
          onChangeText={setTitle}
        />

        {/* Image Insertion */}
        <Text className="text-lg font-bold mb-2">Image</Text>
        <Pressable
          className="h-40 border border-gray-300 rounded-lg flex items-center justify-center mb-5"
          onPress={pickImage}
        >
          {image ? (
            <Image source={{ uri: image }} className="w-full h-full rounded-lg" />
          ) : (
            <Text className="text-gray-400">Tap to add an image</Text>
          )}
        </Pressable>

        {/* Description */}
        <Text className="text-lg font-bold mb-2">Description</Text>
        <TextInput
          className="border border-gray-300 rounded-lg p-3 h-24 text-top mb-5"
          placeholder="Enter description"
          value={description}
          onChangeText={setDescription}
          multiline
        />

        {/* Tags */}
        <Text className="text-lg font-bold mb-2">Tags</Text>
        <View className="border border-gray-300 rounded-lg mb-5">
          <Picker
            selectedValue={selectedTag}
            onValueChange={(itemValue) => {
              if (itemValue === "Add New Tag") {
                const newTag = prompt("Enter new tag:");
                if (newTag) setTags((prev) => [...prev, newTag]);
              } else {
                setSelectedTag(itemValue);
              }
            }}
          >
            {tags.map((tag, index) => (
              <Picker.Item key={index} label={tag} value={tag} />
            ))}
          </Picker>
        </View>

        {/* Submit Button */}
        <Pressable
          className="bg-primary p-4 rounded-lg flex items-center"
          onPress={() => alert("Form submitted!")}
        >
          <Text className="text-white text-lg">Submit</Text>
        </Pressable>
      </ScrollView>

      <Navbar />
    </View>
  );
}