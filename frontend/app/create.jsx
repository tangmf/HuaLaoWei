import React, { useState, useRef, useEffect } from "react";
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
    <View style={{ flex: 1, backgroundColor: "white" }}>
      <Header title="Create Report" />

      {/* Manual Form Submission */}
      <ScrollView contentContainerStyle={{ padding: 20 }}>
        {/* Title */}
        <Text style={{ fontSize: 16, fontWeight: "bold", marginBottom: 10 }}>Title</Text>
        <TextInput
          style={{
            borderWidth: 1,
            borderColor: "#ccc",
            borderRadius: 10,
            padding: 10,
            marginBottom: 20,
          }}
          placeholder="Enter title"
          value={title}
          onChangeText={setTitle}
        />

        {/* Image Insertion */}
        <Text style={{ fontSize: 16, fontWeight: "bold", marginBottom: 10 }}>Image</Text>
        <Pressable
          style={{
            height: 150,
            borderWidth: 1,
            borderColor: "#ccc",
            borderRadius: 10,
            justifyContent: "center",
            alignItems: "center",
            marginBottom: 20,
          }}
          onPress={pickImage}
        >
          {image ? (
            <Image source={{ uri: image }} style={{ width: "100%", height: "100%", borderRadius: 10 }} />
          ) : (
            <Text style={{ color: "#aaa" }}>Tap to add an image</Text>
          )}
        </Pressable>

        {/* Description */}
        <Text style={{ fontSize: 16, fontWeight: "bold", marginBottom: 10 }}>Description</Text>
        <TextInput
          style={{
            borderWidth: 1,
            borderColor: "#ccc",
            borderRadius: 10,
            padding: 10,
            height: 100,
            textAlignVertical: "top",
            marginBottom: 20,
          }}
          placeholder="Enter description"
          value={description}
          onChangeText={setDescription}
          multiline
        />

        {/* Tags */}
        <Text style={{ fontSize: 16, fontWeight: "bold", marginBottom: 10 }}>Tags</Text>
        <View
          style={{
            borderWidth: 1,
            borderColor: "#ccc",
            borderRadius: 10,
            marginBottom: 20,
          }}
        >
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
          style={{
            backgroundColor: "#007bff",
            padding: 15,
            borderRadius: 10,
            alignItems: "center",
          }}
          onPress={() => alert("Form submitted!")}
        >
          <Text style={{ color: "white", fontSize: 16 }}>Submit</Text>
        </Pressable>
      </ScrollView>

      <Navbar />
    </View>
  );
}