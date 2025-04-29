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
import axios from 'axios';
import * as ImagePicker from "expo-image-picker";
import Navbar from "@/components/Navbar";
import Header from "@/components/Header";
import Icon from "react-native-vector-icons/MaterialIcons";
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
  const [isCategoryModalVisible, setIsCategoryModalVisible] = useState(false);
  const [isAISuggestionsVisible, setIsAISuggestionsVisible] = useState(false); // AI Suggestions Popup
  const [suggestions, setSuggestions] = useState({
    title: "",
    description: "",
    // suggestedCategories: AI generated categories (DOES NOT CHANGE in frontend)
    // This is so we know which categories were generated by the AI
    suggestedCategories: [],
    // suggestedCategoriesList: List of AI suggestions under AI Suggestions Modal. If user clicks on the AI Suggestion pill to add it,
    // it will go to suggestions.categories and be removed from the list.
    // If the user clicks on the categories pill to select it, it will remove from there and add back here.
    suggestedCategoriesList: [], 
    // Actual categories that will be put into "setCategories(suggestions.categories)" once user click confirm.
    // Temp storage in case user clicks cancel
    categories: [],
  }); // AI-generated suggestions
  const [loadingSuggestions, setLoadingSuggestions] = useState(false); // Loading state for AI suggestions

  const handleCategorySelection = (categoryKey, subCategoryLabel) => {
    const categoryText = `${categoryKey} - ${subCategoryLabel}`;
    setCategories((prev) => {
      if (prev.includes(categoryText)) {
        // If already selected, remove it
        return prev.filter((category) => category !== categoryText);
      } else {
        // If not selected, add it
        return [...prev, categoryText];
      }
    });
  };

  useEffect(() => {
    console.log("suggestions.suggestedCategoriesList: " + suggestions.suggestedCategoriesList.join("\n"))
    console.log("suggestions.categories: " + suggestions.categories.join("\n"))
    // console.log("===================")
    // console.log("\nsuggestions.categories: \n" + suggestions.categories.join("\n"))
    // // console.log("suggestions.suggestedCategories: \n" + suggestions.suggestedCategories.join("\n"))
    // console.log("-------------------\n")
    // console.log("\nsuggestions.suggestedCategoriesList: \n" + suggestions.suggestedCategoriesList.join("\n"))
    // console.log("===================\n")
    // // When categories change, update suggestions.suggestedCategoriesList so that the UI will refresh
    // // setSuggestions((prev) => (prev));
  }, [suggestions])
  
  const handleAddCategories = () => {
    // Close the modal after confirming the selection
    setIsCategoryModalVisible(false);
  };
  
  const handleRemoveCategory = (categoryText) => {
    setCategories((prev) => prev.filter((category) => category !== categoryText));
  };

  const fetchAISuggestions = async () => {
    if (!title || !description) {
      alert("Please fill in both title and description before using AI suggestions.");
      return;
    }

    setLoadingSuggestions(true);
    try {
      const formData = new FormData();
      formData.append("text", title + " " + description);

      if (lat && lon) {
        formData.append("coordinates", JSON.stringify({ "lat": lat, "lon": lon }));
      }

      if (image) {
        formData.append("image", {
          uri: image,
          name: "image.jpg",
          type: "image/jpeg",
        });
      }

      // const response = await fetch("https://your-api-url.com/generate-suggestions", {
      //   method: "POST",
      //   body: formData,
      //   headers: {
      //     "Content-Type": "multipart/form-data",
      //   },
      // });

      // const data = await response.json();

      // send POST api request to vlm model
      try {
        const { data } = await axios.post("http://localhost:8080/infer", formData, {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        })
        console.log("AI Suggestions: ", data);
      } catch (error) {
        console.error("Error fetching AI suggestions:", error);
      }


      // TODO
      let tempSuggestedCategoriesList = data.categories.filter(category => !categories.includes(category))

      setSuggestions({
        title: data.title || "",
        description: data.description || "",
        suggestedCategories: data.categories || [],
        suggestedCategoriesList: tempSuggestedCategoriesList || [],
        categories: Array.from(categories) || [],
      });
      setIsAISuggestionsVisible(true);
    } catch (error) {
      console.error("Error fetching AI suggestions:", error);
      alert("Failed to fetch AI suggestions. Please try again.");
    } finally {
      setLoadingSuggestions(false);
    }
  };

  const applySuggestions = () => {
    if (suggestions.title) setTitle(suggestions.title);
    if (suggestions.description) setDescription(suggestions.description);
    setCategories(suggestions.categories); // use the user selected categories not the suggested ones
    setIsAISuggestionsVisible(false);
  };

  const shortenText = (text, maxLength = 50) => {
    if (text.length > maxLength) {
      text = text.substring(0, maxLength) + "...";
    }

    return text;
  }
  
  const undoTitleSuggestion = () => {
    setSuggestions((prev) => ({ ...prev, title: title }));
  }
  
  const undoDescriptionSuggestion = () => {
    setSuggestions((prev) => ({ ...prev, description: description }));
  }

  return (
    <View className="flex-1 bg-white">
      <Header title="Create Report" />

      {/* Manual Form Submission */}
      <ScrollView contentContainerStyle={{ padding: 20 }}>
        {/* Image Insertion */}
        <Text className="text-lg font-bold mb-2">Image</Text>
        <Pressable
          className="h-40 border border-gray-300 rounded-lg flex items-center justify-center mb-2"
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
        
        <Pressable
          className="flex-row items-center mb-5"
          onPress={fetchAISuggestions}
        >
          <Icon name="auto-awesome" size={20} color="#8B0000" />
          <Text className="ml-2 font-bold text-gray-800" style={{ color: "#8B0000" }}>
            Click for AI Suggestions Based on Image
          </Text>
        </Pressable>

        {/* Title */}
        <Text className="text-lg font-bold mb-2">Title</Text>
        <TextInput
          className="border border-gray-300 rounded-lg p-3 mb-5"
          placeholder="Enter title"
          value={title}
          onChangeText={setTitle}
        />

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
            onPress={() => setIsCategoryModalVisible(true)}
          >
            <Text className="text-white text-sm">+ Edit Categories</Text>
          </Pressable>
        </View>

        {/* Submit Button */}
        <Pressable
          className="bg-primary p-4 rounded-lg flex items-center"
          onPress={() => alert(`Form submitted!\n\nTitle: ${title}\n\nDescription: ${description}\n\nCategories: ${categories.join(", ")}`)}
        >
          <Text className="text-white text-lg">Submit</Text>
        </Pressable>
      </ScrollView>

      {/* AI Suggestions Popup */}
      <Modal visible={isAISuggestionsVisible} transparent animationType="slide">
        <View className="flex-1 justify-center items-center bg-black bg-opacity-50">
          <View
            className="bg-white rounded-lg w-4/5"
            style={{ maxHeight: "80%", padding: 20 }}
          > 
          <ScrollView contentContainerStyle={{ paddingBottom: 20 }}>
            <Text className="text-lg font-bold mb-3">AI Suggestions</Text>
            {loadingSuggestions ? (
              <Text>Loading suggestions...</Text>
            ) : (
              <>
                {/* AI Suggested Title */}
                <Text className="text-md font-bold mb-2">Title</Text>
                <TextInput
                  className="border border-gray-300 rounded-lg p-3"
                  value={suggestions.title}
                  onChangeText={(text) =>
                    setSuggestions((prev) => ({ ...prev, title: text }))
                  }
                />
                <Pressable
                  className="flex-row items-center mb-5"
                  onPress={undoTitleSuggestion}
                >
                  <Icon name="history" size={30} color="#8B0000" />
                  <Text className="ml-1 font-bold text-gray-800" style={{ color: "#8B0000" }}>
                    Revert to "{shortenText(title, 100)}"
                  </Text>
                </Pressable>
                
                {/* AI Suggested Description */}
                <Text className="text-md font-bold mb-2">Description</Text>
                <TextInput
                  className="border border-gray-300 rounded-lg p-3"
                  value={suggestions.description}
                  onChangeText={(text) =>
                    setSuggestions((prev) => ({ ...prev, description: text }))
                  }
                  multiline
                />
                <Pressable
                  className="flex-row items-center mb-5"
                  onPress={undoDescriptionSuggestion}
                >
                  <Icon name="history" size={30} color="#8B0000" />
                  <Text className="ml-1 font-bold text-gray-800" style={{ color: "#8B0000" }}>
                    Revert to "{shortenText(description)}"
                  </Text>
                </Pressable>

                {/* AI Suggested Categories */}
                <Text className="text-md font-bold mb-2">Categories</Text>
                {/* Load original categories (from suggestions object) */}
                <View className="flex-row flex-wrap mb-5">
                  {suggestions.categories.map((category, index) => (
                    <Pressable
                      key={index}
                      className="bg-gray-200 rounded-full px-4 py-2 mr-2 mb-2"
                      onPress={
                        () => {
                          // Remove the category when clicked
                          setSuggestions((prev) => {
                            // console.log("prev.suggestedCategories.includes(prev.categories[index]): " + prev.suggestedCategories.includes(prev.categories[index]))
                            // console.log("!prev.suggestedCategoriesList.includes(prev.categories[index]): " + !prev.suggestedCategoriesList.includes(prev.categories[index]))
                            // console.log(prev.suggestedCategoriesList.concat(prev.categories[index]))
                            return {
                            ...prev,
                            // Only add back to suggested categories list if it was previously a suggested category and if not already exists
                            suggestedCategoriesList: (prev.suggestedCategories.includes(prev.categories[index]) && !prev.suggestedCategoriesList.includes(prev.categories[index])) 
                                                     ? prev.suggestedCategoriesList.concat(prev.categories[index]) 
                                                     : prev.suggestedCategoriesList,
                            categories: prev.categories.filter((_, i) => i !== index),
                            }})
                          }
                        }
                    >
                      <Text className="text-sm text-gray-700">{category} ✕</Text>
                    </Pressable>
                  ))}

                  {/* Load AI suggested categories */}
                  <View className="flex-row flex-wrap mb-5">
                  <Icon name="auto-awesome" size={20} color="#8B0000" />
                  <Text className="text-sm font-bold mb-2 ml-2" style={{ color: "#8B0000" }}>Click to Add AI Suggestions:</Text>
                    {suggestions.suggestedCategoriesList
                    // .filter((suggestion, s_index) => {
                      // for (let catI = 0; catI < categories.length; catI++) {
                      //   if (categories[catI] === suggestion) return false;
                      // }
                      // return true
                    // })
                    .map((category, index) => (
                      <Pressable
                        key={index}
                        className="flex-row items-center border-2 border-dashed border-gray bg-white-200 rounded-full px-4 py-2 mr-2 mb-2"
                        // style={{ borderColor: "#8B0000" }}
                        onPress={() => {
                          setSuggestions((prev) => {
                            console.log("Add to ai suggestions")
                            return ({
                            ...prev,
                            categories: prev.categories.concat(prev.suggestedCategoriesList[index]),
                            suggestedCategoriesList: prev.suggestedCategoriesList.filter((_, i) => i !== index),
                          })})
                        }}
                      >
                        <Text className="text-sm mr-2" >{category}</Text>
                        <Icon name="add-circle" size={20} />                    
                      </Pressable>
                    ))}
                  </View>
                  
                  {/* Edit Categories Pill */}
                  {/* <Pressable
                    className="bg-primary rounded-full px-4 py-2 mr-2 mb-2"
                    onPress={() => setIsCategoryModalVisible(true)}
                  >
                    <Text className="text-white text-sm">+ Edit Categories</Text>
                  </Pressable> */}
                </View>

                <Button title="Apply Suggestions" onPress={applySuggestions} />
                <View style={{ marginTop: 10 }}>
                  <Button
                    title="Cancel"
                    color="red"
                    onPress={() => setIsAISuggestionsVisible(false)}
                  />
                </View>
              </>
            )}
            </ScrollView>
          </View>
        </View>
      </Modal>

      {/* Modal for Adding Categories */}
      <Modal visible={isCategoryModalVisible} transparent animationType="slide">
        <View className="flex-1 justify-center items-center bg-black bg-opacity-50">
            <View
              className="bg-white rounded-lg w-4/5"
              style={{ maxHeight: "80%", padding: 20 }}
            >
            <ScrollView contentContainerStyle={{ paddingBottom: 20 }}>
            <Text className="text-lg font-bold mb-3">Select Categories</Text>
            <ScrollView style={{ maxHeight: 300 }}>
              {Object.keys(categoriesObject).map((categoryKey) => (
                <View key={categoryKey} className="mb-3">
                  <Text className="text-md font-bold mb-2">{categoryKey}</Text>
                  {categoriesObject[categoryKey].map((subCategory, index) => (
                    // Make one pressable for each subcategory
                    <Pressable
                      key={index}
                      className="flex-row items-center mb-2"
                      onPress={() =>
                        handleCategorySelection(categoryKey, subCategory.label)
                      }
                    >
                      <View
                        className={`w-5 h-5 border-2 rounded-full mr-3 ${
                          categories.includes(
                            `${categoryKey} - ${subCategory.label}`
                          )
                            ? "bg-primary border-primary"
                            : "border-gray-300"
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
              <Button
                title="Cancel"
                color="#8B0000"
                onPress={() => setIsCategoryModalVisible(false)}
              />
            </View>
            </ScrollView>
          </View>
        </View>
      </Modal>

      <Navbar />
    </View>
  );
}