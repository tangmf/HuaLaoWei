import React, { useState, useEffect, useRef } from "react";
import { Text, View, ActivityIndicator, Animated, Dimensions, Pressable, Image } from "react-native";
import MapView, { Marker } from "react-native-maps";
import * as Location from "expo-location";
import Navbar from "@/components/Navbar";
import Header from "@/components/Header";
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
          description: "Naked men.",
          latitude: 1.3521,
          longitude: 103.8198,
          severity: "High",
        };
        const fallbackTicket2 = {
          id: 2,
          title: "Public Disturbance",
          description: "Naked men.",
          latitude: 1.3421,
          longitude: 103.8298,
          severity: "Medium",
        };

        setTickets([fallbackTicket1, fallbackTicket2]);
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
        toValue: -height * 0.8, // Move off-screen
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
       className ="absolute top-10 right-5 bg-blue-500 p-2 rounded-full z-10"
      >
        <Ionicons name="filter" size={24} color="white" />
      </Pressable>
      
<Pressable
        onPress={lockToMarker}
        style={{
          position: "absolute",
    bottom: 150, // Distance from the top of the screen
    right: 20, // Distance from the right of the screen
    backgroundColor: "#007bff", // Blue background
    paddingVertical: 10,
    paddingHorizontal: 15,
    borderRadius: 100,
    zIndex: 3, // Ensure the button is above other elements
        }}
        

      >
        <Ionicons name="locate-outline" size={24} color="white" />
      </Pressable>


      
      <View className="flex-1 items-center justify-center">
        
        {location ? (
          <MapView
            ref={mapRef}
            style={{ width: "100%", height: "100%", position: "absolute", bottom: 0}}
            mapType="satellite"
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
                className="w-0 h-0 border-l-[10px] border-r-[10px] border-b-[20px] border-l-transparent border-r-transparent border-b-red-500"
                style={{ transform: [{ rotate: `${heading}deg` }] }}
              />
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
              />
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
        <Text style={{ fontSize: 18, fontWeight: "bold", color: "white" }}>
          Filter
        </Text>

        {/* Severity Section */}
        <View style={{ marginTop: 20 }}>
          <Text style={{ fontSize: 16, color: "white", marginBottom: 10 }}>
            <Ionicons name="warning" size={16} color="yellow" /> Severity
          </Text>
          <View style={{ flexDirection: "row" }}>
            <Pressable
              style={{
                backgroundColor: "red",
                padding: 10,
                borderRadius: 5,
                marginRight: 10,
              }}
            >
              <Text style={{ color: "white" }}>High</Text>
            </Pressable>
            <Pressable
              style={{
                backgroundColor: "orange",
                padding: 10,
                borderRadius: 5,
                marginRight: 10,
              }}
            >
              <Text style={{ color: "white" }}>Medium</Text>
            </Pressable>
            <Pressable
              style={{
                backgroundColor: "green",
                padding: 10,
                borderRadius: 5,
              }}W
            >
              <Text style={{ color: "white" }}>Low</Text>
            </Pressable>
          </View>
        </View>

        {/* Status Section */}
        <View style={{ marginTop: 20 }}>
          <Text style={{ fontSize: 16, color: "white", marginBottom: 10 }}>
            <Ionicons name="checkmark-circle" size={16} color="lightgreen" />{" "}
            Status
          </Text>
          <View style={{ flexDirection: "row" }}>
            <Pressable
              style={{
                backgroundColor: "#007bff",
                padding: 10,
                borderRadius: 5,
                marginRight: 10,
              }}
            >
              <Text style={{ color: "white" }}>Pending</Text>
            </Pressable>
            <Pressable
              style={{
                backgroundColor: "#6c757d",
                padding: 10,
                borderRadius: 5,
              }}
            >
              <Text style={{ color: "white" }}>Resolved</Text>
            </Pressable>
          </View>
        </View>

        {/* Tags Section */}
        <View style={{ marginTop: 20 }}>
          <Text style={{ fontSize: 16, color: "white", marginBottom: 10 }}>
            <MaterialIcons name="label" size={16} color="lightblue" /> Tags
          </Text>
          <View style={{ flexDirection: "row", flexWrap: "wrap" }}>
            <Pressable
              style={{
                backgroundColor: "#17a2b8",
                padding: 10,
                borderRadius: 5,
                marginRight: 10,
                marginBottom: 10,
              }}
            >
              <Text style={{ color: "white" }}>Traffic</Text>
            </Pressable>
            <Pressable
              style={{
                backgroundColor: "#ffc107",
                padding: 10,
                borderRadius: 5,
                marginRight: 10,
                marginBottom: 10,
              }}
            >
              <Text style={{ color: "white" }}>Noise</Text>
            </Pressable>
            <Pressable
              style={{
                backgroundColor: "#28a745",
                padding: 10,
                borderRadius: 5,
                marginRight: 10,
                marginBottom: 10,
              }}
            >
              <Text style={{ color: "white" }}>Environment</Text>
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