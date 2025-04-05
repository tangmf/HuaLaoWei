import React, { useState } from "react";
import { View, Text, TextInput, Pressable, Image, FlatList } from "react-native";
// import DropDownPicker from 'react-native-dropdown-picker';
import {Picker} from '@react-native-picker/picker';
import GetLocation from 'react-native-get-location'
import Navbar from "@/components/Navbar";
import Header from "@/components/Header";

const issueCatItemsObj = {
	"Illegal Parking":[
		{label:"Road", value:"Road"},
		{label:"HDB/URA Car Park", value:"HDB/URA Car Park"},
		{label:"Motorcycle at Void Deck", value:"Motorcycle at Void Deck"}
	],
	"Facilities in HDB Estates":[
		{label:"Lightning Maintenance", value:"Lightning Maintenance"},
		{label:"Common Area Maintenance", value:"Common Area Maintenance"},
		{label:"HDB Car Park Maintenance", value:"HDB Car Park Maintenance"},
		{label:"Playground & Fitness Facilities Maintenance", value:"Playground & Fitness Facilities Maintenance"},
		{label:"Bulky Waste in Common Areas", value:"Bulky Waste in Common Areas"}
	],
	"Roads & Footprints":[
		{label:"Damaged Road Signs", value:"Damaged Road Signs"},
		{label:"Faulty Streetlight", value:"Faulty Streetlight"},
		{label:"Covered Linkway Maintenance", value:"Covered Linkway Maintenance"},
		{label:"Road Maintenance", value:"Road Maintenance"},
		{label:"Footpath Maintenance", value:"Footpath Maintenance"}
	],
	"Cleanliness":[
		{label:"Dirty Public Areas", value:"Dirty Public Areas"},
		{label:"Overflowing Litter Bin", value:"Overflowing Litter Bin"},
		{label:"High-rise Littering", value:"High-rise Littering"},
		{label:"Bulky Waste in HDB Common Areas", value:"Bulky Waste in HDB Common Areas"}
	],
	"Pests":[
		{label:"Cockroaches in Food Establishment", value:"Cockroaches in Food Establishment"},
		{label:"Mosquitoes", value:"Mosquitoes"},
		{label:"Rodents in Common Areas", value:"Rodents in Common Areas"},
		{label:"Rodents in Food Establishment", value:"Rodents in Food Establishment"},
		{label:"Bees & Hornets", value:"Bees & Hornets"}
	],
	"Animals & Bird":[
		{label:"Dead Animal", value:"Dead Animal"},
		{label:"Injured Animal", value:"Injured Animal"},
		{label:"Bird Issues", value:"Bird Issues"},
		{label:"Cat Issues", value:"Cat Issues"},
		{label:"Dog Issues", value:"Dog Issues"},
		{label:"Other Animal Issues", value:"Other Animal Issues"}
	],
	"Smoking":[
		{label:"Food Premises", value:"Food Premises"},
		{label:"Parks & Park Connectors", value:"Parks & Park Connectors"},
		{label:"Other Public Areas", value:"Other Public Areas"}
	],
	"Parks & Greenery":[
		{label:"Fallen Tree/Branch", value:"Fallen Tree/Branch"},
		{label:"Overgrown Grass", value:"Overgrown Grass"},
		{label:"Park Lighting Maintenance", value:"Park Lighting Maintenance"},
		{label:"Park Facilities Maintenance", value:"Park Facilities Maintenance"},
		{label:"Other Parks and Greenery Issues", value:"Other Parks and Greenery Issues"}
	],
	"Drains & Sewers":[
		{label:"Choked Drain/Stagnant Water", value:"Choked Drain/Stagnant Water"},
		{label:"Damaged Drain", value:"Damaged Drain"},
		{label:"Flooding", value:"Flooding"},
		{label:"Sewer Choke/Overflow", value:"Sewer Choke/Overflow"},
		{label:"Sewage Smell", value:"Sewage Smell"}
	],
	"Drinking Water":[
		{label:"No Water", value:"No Water"},
		{label:"Water Leak", value:"Water Leak"},
		{label:"Water Pressure", value:"Water Pressure"},
		{label:"Water Quality", value:"Water Quality"}
	],
	"Construction Sites":[
		{label:"Construction Noise", value:"Construction Noise"}
	],
	"Abandoned Trolleys":[
		{label:"Cold Storage", value:"Cold Storage"},
		{label:"Giant", value:"Giant"},
		{label:"Mustafa", value:"Mustafa"},
		{label:"FairPrice", value:"FairPrice"},
		{label:"ShengSong", value:"ShengSong"},
		{label:"Ikea", value:"Ikea"}
	],
	"Shared Bicycles":[
		{label:"Anywheel", value:"Anywheel"},
		{label:"HelloRide", value:"HelloRide"},
		{label:"Others", value:"Others"}
	],
	"Others":[
		{label:"Others", value:"Others"}
	]
}

export default function ManualSubmission() {
  const [input, setInput] = useState("");
  const [issueCat, setIssueCat] = useState(Object.keys(issueCatItemsObj)[0]);
  const issueCatPickerItemList = [] // List of Picker.Items
  // Get the list of Picker.Items for each issue category
  Object.keys(issueCatItemsObj).forEach(itemCat => {
      issueCatPickerItemList.push(<Picker.Item label={itemCat} value={itemCat} />)
  });

  const [issueSubcat, setIssueSubcat] = useState("");
  const [issueSubcatPickerItemsList, setIssueSubcatPickerItemsList] = useState(generateIssueSubcatItemsList(issueCat)); // List of Picker.Items
  function generateIssueSubcatItemsList(issueCat) {
    // When issue category is changed, the sub category list will also change
    // This function will change the issue sub categories list based on the issue category
    let subcats = issueCatItemsObj[issueCat]
    if (subcats === undefined) return [];
    let subcatItemsList = [];
    subcats.forEach(subcat => {
      subcatItemsList.push(<Picker.Item label={subcat.label} value={subcat.value} />)
    });
    return subcatItemsList
  }

  const [severity, setSeverity] = useState("");
  const [municipalContact, setMunicipalContact] = useState("");
  const [tags, setTags] = useState([]);
  const [location, setLocation] = useState("");
  
  function getCurrentLocation() {
    console.log(GetLocation)
    GetLocation.getCurrentPosition({
        enableHighAccuracy: true,
        timeout: 60000,
    })
    .then(location => {
        console.log(location)
        setLocation(location);
    })
    .catch(error => {
        const { code, message } = error;
        console.warn(code, message);
    })
  }

  const submitForm = () => {
    return "";
  }
  

  return (
    <View className="flex-1 bg-white">
      <Header title="Manual Submission" />

      <View>
        <Text>Upload Photo</Text>
      </View>

      <View>
        <Text>Severity</Text>
        
        {/* <DropDownPicker
          className="border border-gray-300 rounded-full px-4 mr-2 bg-white"
          open={severityOpen}
          value={severity}
          items={severityItems}
          setOpen={setSeverityOpen}
          setValue={setSeverity}
          setItems={setSeverityItems}
        /> */}

        <Picker
          selectedValue={severity}
          onValueChange={(itemValue, itemIndex) =>
            setSeverity(itemValue)
          }>
          <Picker.Item label="Low" value="Low" />
          <Picker.Item label="Medium" value="Medium" />
          <Picker.Item label="High" value="High" />
        </Picker>
      </View>

      <View>
        <Text>Issue Category</Text>
        {/* <TextInput
          className="border border-gray-300 rounded-full px-4 mr-2 bg-white"
          placeholder="Type here ..."
          value={issueCat}
          onChangeText={setIssueCat}
        /> */}
        <Picker
          selectedValue={issueCat}
          onValueChange={(newIssueCat, itemIndex) => {
              setIssueCat(newIssueCat);
              setIssueSubcatPickerItemsList(generateIssueSubcatItemsList(newIssueCat)); // Change subcat list
              setIssueSubcat(""); // Reset subcat selection
            }
          }>
          {issueCatPickerItemList}
        </Picker>
      </View>

      <View>
        <Text>Issue Sub-Category</Text>
        <Picker
          selectedValue={issueSubcat}
          onValueChange={(newIssueSubcat, itemIndex) => {
              setIssueCat(newIssueSubcat);
            }
          }>
          {issueSubcatPickerItemsList}
        </Picker>
      </View>

      <View>
        <Text>Municipal Contact</Text>
        <TextInput
          className="border border-gray-300 rounded-full px-4 mr-2 bg-white"
          placeholder="Type here ..."
          value={municipalContact}
          onChangeText={setMunicipalContact}
        />
      </View>


      <View>
        <Text>Location</Text>
        <TextInput
          className="border border-gray-300 rounded-full px-4 mr-2 bg-white"
          placeholder="Type here ..."
          value={location}
          onChangeText={setLocation}
        />
        <Pressable onPress={getCurrentLocation} className="h-10 bg-blue-500 rounded-full justify-center items-center">
          <Text className="text-white text-lg">Use Current Location</Text>
        </Pressable>
      </View>

      <View className="flex-row items-center mb-2">
        <Text className="text-base font-bold text-gray-800 mr-2">Tags:</Text>
        <Pressable className="bg-blue-500 px-3 py-1 rounded">
          <Text className="text-white text-sm">Add</Text>
        </Pressable>
      </View>


      <Pressable onPress={submitForm} className="h-10 bg-blue-500 rounded-full justify-center items-center">
        <Text className="text-white text-lg">Submit Form</Text>
      </Pressable>

      <Navbar />
    </View>
  );
}
