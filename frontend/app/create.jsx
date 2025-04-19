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

const categoriesObject = {
  "Illegal Parking": [
    { label: "Road", value: "Road" },
    { label: "HDB/URA Car Park", value: "HDB/URA Car Park" },
    { label: "Motorcycle at Void Deck", value: "Motorcycle at Void Deck" },
  ],
  "Facilities in HDB Estates": [
    { label: "Lightning Maintenance", value: "Lightning Maintenance" },
    { label: "Common Area Maintenance", value: "Common Area Maintenance" },
    { label: "HDB Car Park Maintenance", value: "HDB Car Park Maintenance" },
    { label: "Playground & Fitness Facilities Maintenance", value: "Playground & Fitness Facilities Maintenance" },
    { label: "Bulky Waste in Common Areas", value: "Bulky Waste in Common Areas" },
  ],
  "Roads & Footprints": [
    { label: "Damaged Road Signs", value: "Damaged Road Signs" },
    { label: "Faulty Streetlight", value: "Faulty Streetlight" },
    { label: "Covered Linkway Maintenance", value: "Covered Linkway Maintenance" },
    { label: "Road Maintenance", value: "Road Maintenance" },
    { label: "Footpath Maintenance", value: "Footpath Maintenance" },
  ],
  "Cleanliness": [
    { label: "Dirty Public Areas", value: "Dirty Public Areas" },
    { label: "Overflowing Litter Bin", value: "Overflowing Litter Bin" },
    { label: "High-rise Littering", value: "High-rise Littering" },
    { label: "Bulky Waste in HDB Common Areas", value: "Bulky Waste in HDB Common Areas" },
  ],
  "Pests": [
    { label: "Cockroaches in Food Establishment", value: "Cockroaches in Food Establishment" },
    { label: "Mosquitoes", value: "Mosquitoes" },
    { label: "Rodents in Common Areas", value: "Rodents in Common Areas" },
    { label: "Rodents in Food Establishment", value: "Rodents in Food Establishment" },
    { label: "Bees & Hornets", value: "Bees & Hornets" },
  ],
  "Animals & Bird": [
    { label: "Dead Animal", value: "Dead Animal" },
    { label: "Injured Animal", value: "Injured Animal" },
    { label: "Bird Issues", value: "Bird Issues" },
    { label: "Cat Issues", value: "Cat Issues" },
    { label: "Dog Issues", value: "Dog Issues" },
    { label: "Other Animal Issues", value: "Other Animal Issues" },
  ],
  "Smoking": [
    { label: "Food Premises", value: "Food Premises" },
    { label: "Parks & Park Connectors", value: "Parks & Park Connectors" },
    { label: "Other Public Areas", value: "Other Public Areas" },
  ],
  "Parks & Greenery": [
    { label: "Fallen Tree/Branch", value: "Fallen Tree/Branch" },
    { label: "Overgrown Grass", value: "Overgrown Grass" },
    { label: "Park Lighting Maintenance", value: "Park Lighting Maintenance" },
    { label: "Park Facilities Maintenance", value: "Park Facilities Maintenance" },
    { label: "Other Parks and Greenery Issues", value: "Other Parks and Greenery Issues" },
  ],
  "Drains & Sewers": [
    { label: "Choked Drain/Stagnant Water", value: "Choked Drain/Stagnant Water" },
    { label: "Damaged Drain", value: "Damaged Drain" },
    { label: "Flooding", value: "Flooding" },
    { label: "Sewer Choke/Overflow", value: "Sewer Choke/Overflow" },
    { label: "Sewage Smell", value: "Sewage Smell" },
  ],
  "Drinking Water": [
    { label: "No Water", value: "No Water" },
    { label: "Water Leak", value: "Water Leak" },
    { label: "Water Pressure", value: "Water Pressure" },
    { label: "Water Quality", value: "Water Quality" },
  ],
  "Construction Sites": [
    { label: "Construction Noise", value: "Construction Noise" },
  ],
  "Abandoned Trolleys": [
    { label: "Cold Storage", value: "Cold Storage" },
    { label: "Giant", value: "Giant" },
    { label: "Mustafa", value: "Mustafa" },
    { label: "FairPrice", value: "FairPrice" },
    { label: "ShengSong", value: "ShengSong" },
    { label: "Ikea", value: "Ikea" },
  ],
  "Shared Bicycles": [
    { label: "Anywheel", value: "Anywheel" },
    { label: "HelloRide", value: "HelloRide" },
    { label: "Others", value: "Others" },
  ],
  "Others": [
    { label: "Others", value: "Others" },
  ],
};

export default function Create() {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [categories, setCategories] = useState([]); // Selected categories
  const [image, setImage] = useState(null);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [categoriesState, setCategoriesState] = useState(categoriesObject); // State for categoriesObject

  const handleCategorySelection = (categoryKey, subCategoryIndex) => {
    setCategoriesState((prev) => {
      const updated = { ...prev };
      updated[categoryKey][subCategoryIndex].selected = !updated[categoryKey][subCategoryIndex].selected;
      return updated;
    });
  };
  
  const handleAddCategories = () => {
    const selectedCategories = [];
    Object.keys(categoriesState).forEach((categoryKey) => {
      categoriesState[categoryKey].forEach((subCategory) => {
        if (subCategory.selected) {
          selectedCategories.push(`${categoryKey} - ${subCategory.label}`);
        }
      });
    });
    setCategories(selectedCategories);
    setIsModalVisible(false);
  };
  
  const handleRemoveCategory = (categoryText) => {
    const [categoryKey, subCategoryLabel] = categoryText.split(" - ");
    setCategories((prev) => prev.filter((category) => category !== categoryText));
    setCategoriesState((prev) => {
      const updated = { ...prev };
      const subCategoryIndex = updated[categoryKey].findIndex(
        (subCategory) => subCategory.label === subCategoryLabel
      );
      if (subCategoryIndex !== -1) {
        updated[categoryKey][subCategoryIndex].selected = false;
      }
      return updated;
    });
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
          onPress={async () => {
            const result = await ImagePicker.launchImageLibraryAsync({
              mediaTypes: ImagePicker.MediaTypeOptions.Images,
              allowsEditing: true,
              aspect: [4, 3],
              quality: 1,
            });
            if (!result.canceled) {
              setImage(result.assets[0].uri);
            }
          }}
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
              onPress={
                // Remove the category when clicked
                () => handleRemoveCategory(category)
              }
            >
              <Text className="text-sm text-gray-700">{category} ✕</Text>
            </Pressable>
          ))}
          {/* Edit Categories Pill */}
          <Pressable
            className="bg-primary rounded-full px-4 py-2 mr-2 mb-2"
            onPress={() => setIsModalVisible(true)}
          >
            <Text className="text-white text-sm">+ Edit Categories</Text>
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

      {/* Modal for Adding Categories */}
      <Modal visible={isModalVisible} transparent animationType="slide">
        <View className="flex-1 justify-center items-center bg-black bg-opacity-50">
          <View className="bg-white p-5 rounded-lg w-4/5 max-h-[80%]">
            <Text className="text-lg font-bold mb-3">Select Categories</Text>
            <ScrollView style={{ maxHeight: 300 }}>
              {Object.keys(categoriesState).map((categoryKey) => (
                <View key={categoryKey} className="mb-3">
                  <Text className="text-md font-bold mb-2">{categoryKey}</Text>
                  {categoriesState[categoryKey].map((subCategory, index) => (
                    <Pressable
                      key={index}
                      className="flex-row items-center mb-2"
                      onPress={() => handleCategorySelection(categoryKey, index)}
                    >
                      <View
                        className={`w-5 h-5 border-2 rounded-full mr-3 ${
                          subCategory.selected ? "bg-primary border-primary" : "border-gray-300"
                        }`}
                      />
                      <Text className="text-sm">{subCategory.label}</Text>
                    </Pressable>
                  ))}
                </View>
              ))}
            </ScrollView>
            <Button title="Add Selected Categories" onPress={handleAddCategories} />
            <View style={{ marginTop: 10 }}>
              <Button title="Cancel" color="red" onPress={() => setIsModalVisible(false)} />
            </View>
          </View>
        </View>
      </Modal>

      <Navbar />
    </View>
  );
}