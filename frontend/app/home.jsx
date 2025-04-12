import React, { useState, useEffect, useRef } from "react";
import { Text, View, ActivityIndicator, Animated, Dimensions, Pressable, Image } from "react-native";
import MapView, { Marker } from "react-native-maps";
import * as Location from "expo-location";
import Navbar from "@/components/Navbar";
import Header from "@/components/Header";
import BottomSheet from "@/components/BottomSheet";

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
  const [isFilterPanelVisible, setIsFilterPanelVisible] = useState(false);

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

  return (
    <View className="flex-1 bg-white">
      
      <Header title="Home" />
      <Pressable
  onPress={() => setIsFilterPanelVisible(!isFilterPanelVisible)}
  style={{
    position: "absolute",
    top: 70, // Distance from the top of the screen
    right: 20, // Distance from the right of the screen
    backgroundColor: "#007bff", // Blue background
    paddingVertical: 10,
    paddingHorizontal: 15,
    borderRadius: 10,
    zIndex: 10, // Ensure the button is above other elements
  }}
>
  <Text style={{ color: "white", fontSize: 16 }}>Filter</Text>
</Pressable>
<Pressable
        onPress={lockToMarker}
        style={{
          position: "absolute",
    bottom: 100, // Distance from the top of the screen
    right: 20, // Distance from the right of the screen
    backgroundColor: "#007bff", // Blue background
    paddingVertical: 10,
    paddingHorizontal: 15,
    borderRadius: 10,
    zIndex: 10, // Ensure the button is above other elements
        }}
      >
        <Image source={require("@/assets/images/lock.png")} style={{width: 40, height: 40 }} />
      </Pressable>


      {/* Filtering Panel */}
{isFilterPanelVisible && (
        <Animated.View
          style={{
            top: 0,
            right: 0,
            height: "30%",
            backgroundColor: "white",
            shadowColor: "#000",
            shadowOffset: { width: -2, height: 0 },
            shadowOpacity: 0.2,
            shadowRadius: 5,
            elevation: 5,
            padding: 20,
          }}
        >
          <Text style={{ fontSize: 18, fontWeight: "bold", marginBottom: 10 }}>
            Filter Options
          </Text>
          {/* Add filtering options here */}

          <Text>Severity:</Text>
          <View style={{ flexDirection: "row", marginTop: 10 }}>
            <Pressable
              onPress={() => setTickets(tickets.filter(ticket => ticket.severity === "High"))}
              style={{
                backgroundColor: "red",
                padding: 10,
                borderRadius: 5,
                marginRight: 10,
              }}
            >
              
              </Pressable>
              </View>


              <Text>Status:</Text>
          <View style={{ flexDirection: "row", marginTop: 10 }}>
            <Pressable
              onPress={() => setTickets(tickets.filter(ticket => ticket.severity === "High"))}
              style={{
                backgroundColor: "red",
                padding: 10,
                borderRadius: 5,
                marginRight: 10,
              }}
            >
              
              </Pressable>
              </View>
         
          

        </Animated.View>
      )}
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
        

<BottomSheet selectedTicket ={selectedTicket} >
        </BottomSheet>
      </View>
      <Navbar />
    </View>
    
  );
}