import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  TextInput,
  Pressable,
  Image,
  ScrollView,
  Modal,
  Button,
} from "react-native";
import * as ImagePicker from "expo-image-picker";
import Navbar from "@/components/Navbar";
import Header from "@/components/Header";
import Chatbot from "@/components/Chatbot";

export default function Create() {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [categories, setCategories] = useState([]);
  const [image, setImage] = useState(null); // Placeholder for image insertion
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [newCategory, setNewCategory] = useState("");

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
  }

  const handleAddCategory = () => {
    if (newCategory.trim()) {
      setCategories((prev) => [...prev, newCategory.trim()]);
      setNewCategory("");
    }
    setIsModalVisible(false);
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

        {/* Categories */}
        <Text className="text-lg font-bold mb-2">Categories</Text>
        <View className="flex-row flex-wrap mb-5">
          {categories.map((category, index) => (
            <Pressable
              key={index}
              className="bg-gray-200 rounded-full px-4 py-2 mr-2 mb-2"
              onPress={() => {
                // Remove the category when clicked
                setCategories((prev) => prev.filter((_, i) => i !== index));
              }}
            >
              <Text className="text-sm text-gray-700">{category} ✕</Text>
            </Pressable>
          ))}
          {/* Add New Category Pill */}
          <Pressable
            className="bg-primary rounded-full px-4 py-2 mr-2 mb-2"
            onPress={() => setIsModalVisible(true)}
          >
            <Text className="text-white text-sm">+ Add New Category</Text>
          </Pressable>
        </View>

        {/* Submit Button */}
        <Pressable
          className="bg-primary p-4 rounded-lg flex items-center"
          onPress={() => alert("Form submitted!")}
        >
          <Text className="text-white text-lg">Submit</Text>
        </Pressable>
      </ScrollView>

      {/* Modal for Adding New Category */}
      <Modal visible={isModalVisible} transparent animationType="slide">
        <View className="flex-1 justify-center items-center bg-black bg-opacity-50">
          <View className="bg-white p-5 rounded-lg w-4/5">
            <Text className="text-lg font-bold mb-3">Add New Category</Text>
            <TextInput
              className="border border-gray-300 rounded-lg p-3 mb-5"
              placeholder="Enter New Category"
              value={newCategory}
              onChangeText={setNewCategory}
            />
            <Button
              title="Add Category"
              onPress={() => {
                if (newCategory.trim()) {
                  setCategories((prev) => [...prev, newCategory.trim()]);
                  setNewCategory("");
                  setIsModalVisible(false);
                }
              }}
            />
            {/* Add spacing between the buttons */}
            <View style={{ marginTop: 10 }}>
              <Button
                title="Cancel"
                color="red"
                onPress={() => setIsModalVisible(false)}
              />
            </View>
          </View>
        </View>
      </Modal>

      <Navbar />
    </View>
  );
}