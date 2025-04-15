import React, { useState, useEffect, useRef } from "react";
import { Text, View, ActivityIndicator, Animated, Dimensions, Pressable, Image, TextInput } from "react-native";
import MapView, { Marker, Callout } from "react-native-maps";
import * as Location from "expo-location";
import Navbar from "@/components/Navbar";
import Chatbot from "@/components/Chatbot";
import BottomSheet from "@/components/BottomSheet";
import { Ionicons, MaterialIcons } from "@expo/vector-icons"; // Import icons from Expo

const { height } = Dimensions.get("window");

export default function Home() {
  const [location, setLocation] = useState(null);
  const [heading, setHeading] = useState(0);
  const [tickets, setTickets] = useState([]); // State to store tickets
  const [selectedTicket, setSelectedTicket] = useState(null); // State for the currently viewed ticket
  const mapRef = useRef(null);
  const [hasZoomed, setHasZoomed] = useState(false);
  const [isPanelVisible, setIsPanelVisible] = useState(false);
  const slideAnim = useRef(new Animated.Value(height)).current;
  const [isFilterPanelVisible, setIsFilterPanelVisible] = useState(true);
  const filterAnim = useRef(new Animated.Value(-height * 2)).current; // Start off-screen

  // Fetch tickets from the database
  useEffect(() => {
    const fetchTickets = async () => {
      try {
        const response = await fetch("https://your-api-url.com/api/tickets"); // Replace with your API URL
        const data = await response.json();

        if (data && Array.isArray(data) && data.length > 0) {
          setTickets(data); // Set tickets if data is valid
        } else {
          console.warn("No tickets found or data is invalid.");
          setTickets([]); // Fallback to an empty array if data is null or invalid
        }
      } catch (error) {
        console.error("Error fetching tickets:", error);

        // Create fallback tickets
        const fallbackTicket1 = {
          id: 1,
          title: "Public Disturbance",
          description: "There is a public disturbance.",
          latitude: 1.4521,
          longitude: 103.8198,
          severity: "High",
        };
        const fallbackTicket2 = {
          id: 2,
          title: "Public Disturbance",
          description: "There is a public disturbance.",
          latitude: 1.3421,
          longitude: 103.8298,
          severity: "Medium",
        };
        const fallbackTicket3 = {
          id: 3,
          title: "Public Disturbance",
          description: "There is a public disturbance.",
          latitude: 1.4441,
          longitude: 103.8048,
          severity: "Medium",
        };

        setTickets([fallbackTicket1, fallbackTicket2, fallbackTicket3]);
      }
    };

    fetchTickets();
  }, []);

  // Get user location and heading
  useEffect(() => {
    let locationSubscription;
    let headingSubscription;

    (async () => {
      let { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== "granted") {
        alert("Location permission denied");
        return;
      }

      locationSubscription = await Location.watchPositionAsync(
        {
          accuracy: Location.Accuracy.High,
          timeInterval: 1000,
          distanceInterval: 1,
        },
        (newLocation) => {
          setLocation(newLocation);
          if (!hasZoomed && mapRef.current) {
            mapRef.current.animateToRegion(
              {
                latitude: newLocation.coords.latitude,
                longitude: newLocation.coords.longitude,
                latitudeDelta: 0.005,
                longitudeDelta: 0.005,
              },
              1000
            );
            setHasZoomed(true);
          }
        }
      );

      headingSubscription = await Location.watchHeadingAsync((newHeading) => {
        setHeading(newHeading.trueHeading || 0);
      });
    })();

    return () => {
      if (locationSubscription) locationSubscription.remove();
      if (headingSubscription) headingSubscription.remove();
    };
  }, [hasZoomed]);

  const togglePanel = (ticket) => {
    if (isPanelVisible) {
      // If the panel is already visible, just update the selected ticket
      setSelectedTicket(ticket);
    } else {
      // If the panel is not visible, open it and set the selected ticket
      setSelectedTicket(ticket);
      setIsPanelVisible(true);
      Animated.timing(slideAnim, {
        toValue: height - 300, // Slide the panel up
        duration: 300,
        useNativeDriver: false,
      }).start();
    }
  };

  const lockToMarker = () => {
    if (location && mapRef.current) {
      mapRef.current.animateToRegion(
        {
          latitude: location.coords.latitude,
          longitude: location.coords.longitude,
          latitudeDelta: 0.005,
          longitudeDelta: 0.005,
        },
        1000
      );
    }
  };

  // Toggle the filter panel
  const toggleFilterPanel = () => {
    if (isFilterPanelVisible) {
      // Slide out
      Animated.timing(filterAnim, {
        toValue: -height * 0.85, // Move off-screen
        duration: 300,
        useNativeDriver: false,
      }).start(() => setIsFilterPanelVisible(false));
    } else {
      // Slide in
      setIsFilterPanelVisible(true);
      Animated.timing(filterAnim, {
        toValue: -height * 2, // Move into view
        duration: 300,
        useNativeDriver: false,
      }).start();
    }
  };

  return (
    <View className="flex-1 bg-white">
      
      
      {/* Filter Button */}
      <Pressable
        onPress={toggleFilterPanel}
       className ="absolute top-10 right-5 bg-primary p-2 rounded-full z-10"
      >
        <Ionicons name="filter" size={24} color="white" />
      </Pressable>
      
<Pressable
        onPress={lockToMarker}
        style={{
          position: "absolute",
    bottom: 160, // Distance from the top of the screen
    right: 20, // Distance from the right of the screen
    paddingVertical: 10,
    paddingHorizontal: 15,
    borderRadius: 100,
    zIndex: 3, // Ensure the button is above other elements
        }}
      className="bg-primary rounded-full p-2"
        

      >
        <Ionicons name="locate-outline" size={24} color="white" />
      </Pressable>


      
      <View className="flex-1 items-center justify-center">
        
        {location ? (
          <MapView
            ref={mapRef}
            style={{ width: "100%", height: "100%", position: "absolute", bottom: 0}}
            mapType="standard"
            initialRegion={{
              latitude: location.coords.latitude,
              longitude: location.coords.longitude,
              latitudeDelta: 0.005,
              longitudeDelta: 0.005,
            }}
          >
            {/* Display user location */}
            <Marker
              coordinate={{
                latitude: location.coords.latitude,
                longitude: location.coords.longitude,
              }}
            >
              <View
                style={{ transform: [{ rotate: `${heading}deg` }] }}>
                <Ionicons name="navigate" size={32} color="red" />
              </View>
            </Marker>

            {/* Display tickets from the database */}
            {tickets.map((ticket) => (
    <Marker
      key={ticket.id}
      coordinate={{
                  latitude: ticket.latitude,
                  longitude: ticket.longitude,
      }}
                title={ticket.title}
                description={ticket.description}
      pinColor={ticket.severity === "High" ? "red" : "orange"} // Color based on severity
      onPress={() => togglePanel(ticket)} // Pass the ticket to the panel
              >

            <Ionicons name="warning" size={32} color="orange" />

                </Marker>
            ))}
            
          </MapView>
        ) : (
          <View className="flex-1 justify-center items-center">
            <ActivityIndicator size="large" color="#0000ff" />
            <Text className="mt-2 text-base text-gray-700">Please wait...</Text>
          </View>
        )}
        
      </View>
      <View  className="top-0 left-0 right-0 bottom-0">
        <View>
        
      
        </View>
        
        {/* Filter Panel */}
        <Animated.View
  style={{
    position: "absolute",
    top: filterAnim, // Animate the top position
    left: 0,
    width: "100%",
    height: height * 0.5, // 50% of the screen height
    backgroundColor: "rgba(0, 0, 0, 0.7)", // Translucent background
    padding: 20,
    zIndex: 5,
  }}
>
  <Text style={{ fontSize: 14, fontWeight: "bold", color: "white" }}>
    Filter
  </Text>

  <View
    style={{
      flexDirection: "row",
      alignItems: "center",
      backgroundColor: "white",
      borderRadius: 8,
      paddingHorizontal: 10,
      margin: 10,
      height: 40,
      width: 250
    }}>
    <Ionicons name="search" size={20} color="gray" />
    <TextInput
      placeholder="Search..."
      placeholderTextColor="gray"
      style={{
        flex: 1,
        marginLeft: 10,
        fontSize: 12,
        color: "black",
      }}
    />
  </View>

  {/* Severity Section */}
  <View style={{ marginTop: 10 }}>
    <Text style={{ fontSize: 12, color: "white", marginBottom: 5 }}>
      <Ionicons name="warning" size={12} color="yellow" /> Severity
    </Text>
    <View style={{ flexDirection: "row" }}>
      <Pressable
        style={{
          backgroundColor: "red",
          padding: 5, // Reduced padding
          borderRadius: 3, // Reduced border radius
          marginRight: 5, // Reduced margin
        }}
      >
        <Text style={{ color: "white", fontSize: 12 }}>High</Text>
      </Pressable>
      <Pressable
        style={{
          backgroundColor: "orange",
          padding: 5, // Reduced padding
          borderRadius: 3, // Reduced border radius
          marginRight: 5, // Reduced margin
        }}
      >
        <Text style={{ color: "white", fontSize: 12 }}>Medium</Text>
      </Pressable>
      <Pressable
        style={{
          backgroundColor: "green",
          padding: 5, // Reduced padding
          borderRadius: 3, // Reduced border radius
        }}
      >
        <Text style={{ color: "white", fontSize: 12 }}>Low</Text>
      </Pressable>
    </View>
  </View>

  {/* Status Section */}
  <View style={{ marginTop: 10 }}>
    <Text style={{ fontSize: 12, color: "white", marginBottom: 5 }}>
      <Ionicons name="checkmark-circle" size={12} color="lightgreen" /> Status
    </Text>
    <View style={{ flexDirection: "row" }}>
      <Pressable
        style={{
          backgroundColor: "#007bff",
          padding: 5, // Reduced padding
          borderRadius: 3, // Reduced border radius
          marginRight: 5, // Reduced margin
        }}
      >
        <Text style={{ color: "white", fontSize: 12 }}>Pending</Text>
      </Pressable>
      <Pressable
        style={{
          backgroundColor: "#6c757d",
          padding: 5, // Reduced padding
          borderRadius: 3, // Reduced border radius
        }}
      >
        <Text style={{ color: "white", fontSize: 12 }}>Resolved</Text>
      </Pressable>
    </View>
  </View>

  {/* Tags Section */}
  <View style={{ marginTop: 10 }}>
    <Text style={{ fontSize: 12, color: "white", marginBottom: 5 }}>
      <MaterialIcons name="label" size={12} color="lightblue" /> Tags
    </Text>
    <View style={{ flexDirection: "row", flexWrap: "wrap" }}>
      <Pressable
        style={{
          backgroundColor: "#17a2b8",
          padding: 5, // Reduced padding
          borderRadius: 3, // Reduced border radius
          marginRight: 5, // Reduced margin
          marginBottom: 5, // Reduced margin
        }}
      >
        <Text style={{ color: "white", fontSize: 12 }}>Traffic</Text>
      </Pressable>
      <Pressable
        style={{
          backgroundColor: "#ffc107",
          padding: 5, // Reduced padding
          borderRadius: 3, // Reduced border radius
          marginRight: 5, // Reduced margin
          marginBottom: 5, // Reduced margin
        }}
      >
        <Text style={{ color: "white", fontSize: 12 }}>Noise</Text>
      </Pressable>
      <Pressable
        style={{
          backgroundColor: "#28a745",
          padding: 5, // Reduced padding
          borderRadius: 3, // Reduced border radius
          marginRight: 5, // Reduced margin
          marginBottom: 5, // Reduced margin
        }}
      >
        <Text style={{ color: "white", fontSize: 12 }}>Environment</Text>
      </Pressable>
    </View>
  </View>
</Animated.View>
<BottomSheet selectedTicket ={selectedTicket} >
        </BottomSheet>
      </View>
      <Navbar />
    </View>
    
  );
}