import React, { useState, useEffect, useRef } from "react";
import { Text, View, StyleSheet, ImageBackground, Pressable, Alert, ActivityIndicator, Animated, Dimensions } from "react-native";
import MapView, { Marker, PROVIDER_DEFAULT } from "react-native-maps";
import * as Location from "expo-location";
import Navbar from "@/components/Navbar";
import Header from "@/components/Header";

const { height } = Dimensions.get("window");

export default function Index() {
  const [location, setLocation] = useState(null);
  const [heading, setHeading] = useState(0); // State to store the device's heading
  const mapRef = useRef(null); // Reference to the MapView
  const [hasZoomed, setHasZoomed] = useState(false); // State to track if the map has already zoomed
  const [isPanelVisible, setIsPanelVisible] = useState(false); // State to control sliding panel visibility
  const slideAnim = useRef(new Animated.Value(height)).current; // Animation for sliding panel

  useEffect(() => {
    let locationSubscription;
    let headingSubscription;

    (async () => {
      let { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== "granted") {
        Alert.alert("Permission Denied", "Location permission is required to use this feature.");
        return;
      }

      // Watch the user's location and update state
      locationSubscription = await Location.watchPositionAsync(
        {
          accuracy: Location.Accuracy.High,
          timeInterval: 1000, // Update every 1 second
          distanceInterval: 1, // Update when the user moves 1 meter
        },
        (newLocation) => {
          setLocation(newLocation);

          // Zoom into the marker only once
          if (!hasZoomed && mapRef.current) {
            mapRef.current.animateToRegion(
              {
                latitude: newLocation.coords.latitude,
                longitude: newLocation.coords.longitude,
                latitudeDelta: 0.005, // Zoom level
                longitudeDelta: 0.005, // Zoom level
              },
              1000 // Animation duration in milliseconds
            );
            setHasZoomed(true); // Mark as zoomed
          }
        }
      );

      // Watch the device's heading and update state
      headingSubscription = await Location.watchHeadingAsync((newHeading) => {
        setHeading(newHeading.trueHeading || 0); // Use true heading if available
      });
    })();

    // Cleanup the subscriptions when the component unmounts
    return () => {
      if (locationSubscription) {
        locationSubscription.remove();
      }
      if (headingSubscription) {
        headingSubscription.remove();
      }
    };
  }, [hasZoomed]);

  const togglePanel = () => {
    if (isPanelVisible) {
      // Slide panel down
      Animated.timing(slideAnim, {
        toValue: height,
        duration: 300,
        useNativeDriver: false,
      }).start(() => setIsPanelVisible(false));
    } else {
      // Slide panel up
      setIsPanelVisible(true);
      Animated.timing(slideAnim, {
        toValue: height - 300, // Adjust the height of the sliding panel
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
          latitudeDelta: 0.005, // Zoom level
          longitudeDelta: 0.005, // Zoom level
        },
        1000 // Animation duration in milliseconds
      );
    }
  };

  return (
    <View style={styles.container}>
      <Header title="Home" />
      {/* Main Content */}
      <View style={styles.content}>
        {/* Filtering Panel */}
<View style={styles.filterPanel}>
  <View style={styles.filterGroup}>
    <Text style={styles.filterLabel}>Tags:</Text>
    <Pressable style={styles.filterButton}>
      <Text style={styles.filterButtonText}>Add</Text>
    </Pressable>
  </View>

  <View style={styles.filterGroup}>
    <Text style={styles.filterLabel}>Severity:</Text>
    <Pressable style={styles.filterButton}>
      <Text style={styles.filterButtonText}>Add</Text>
    </Pressable>

  </View>

  <View style={styles.filterGroup}>
    <Text style={styles.filterLabel}>Status:</Text>
    <Pressable style={styles.filterButton}>
      <Text style={styles.filterButtonText}>Add</Text>
    </Pressable>
  </View>
</View>
          {/* Map Section */}
          {location ? (
            <MapView
              ref={mapRef} // Attach the map reference
              style={styles.map}
              mapType="satellite" // Set the map type to satellite
              provider={PROVIDER_DEFAULT} // Use the default provider to avoid Google branding
              initialRegion={{
                latitude: location.coords.latitude,
                longitude: location.coords.longitude,
                latitudeDelta: 0.005, // Initial zoom level
                longitudeDelta: 0.005, // Initial zoom level
              }}
            >
              {/* User's Current Location Marker */}
              <Marker
                coordinate={{
                  latitude: location.coords.latitude,
                  longitude: location.coords.longitude,
                }}
              >
                {/* Triangle Marker with Rotation */}
                <View
                  style={[
                    styles.triangleMarker,
                    { transform: [{ rotate: `${heading}deg` }] }, // Rotate based on heading
                  ]}
                />
              </Marker>

              {/* Example Marker */}
              <Marker
                coordinate={{
                  latitude: location.coords.latitude + 0.001, // Example marker slightly offset
                  longitude: location.coords.longitude + 0.001,
                }}
                title="Example Marker" // Title for the marker
  description="This is an example marker with additional details." // Description for the marker
                onPress={togglePanel} // Show sliding panel when clicked
              >
                <View style={styles.exampleMarker} />
              </Marker>
            </MapView>
          ) : (
            // Loading Indicator
            <View style={styles.loadingContainer}>
    <ActivityIndicator size="large" color="#0000ff" />
    <Text style={styles.loadingText}>Please wait...</Text>
  </View>
          )}

      </View>

{/* Lock Button */}
<Pressable style={styles.lockButton} onPress={lockToMarker}>
        <Text style={styles.lockButtonText}>Lock</Text>
      </Pressable>

      {/* Sliding Panel */}
      <Animated.View style={[styles.slidingPanel, { top: slideAnim }]}>
        <Text style={styles.panelText}>Example Marker Details</Text>
        <Text style={styles.panelText}>Latitude: {location?.coords.latitude + 0.001}</Text>
        <Text style={styles.panelText}>Longitude: {location?.coords.longitude + 0.001}</Text>
        <Pressable style={styles.closeButton} onPress={togglePanel}>
          <Text style={styles.closeButtonText}>Close</Text>
        </Pressable>
      </Animated.View>

      {/* Reusable Navbar */}
      <Navbar />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#fff",
  },
  image: {
    width: "100%",
    height: "100%",
    resizeMode: "cover",
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },
  content: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },
  map: {
    width: "100%",
    height: "70%",
    borderRadius: 10,
    bottom: 0,
    overflow: "hidden",
  },
  loadingIndicator: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },
  navbar: {
    flexDirection: "row",
    justifyContent: "space-around",
    alignItems: "center",
    height: 60,
    backgroundColor: "#fff",
    borderTopWidth: 1,
    borderTopColor: "#ccc",
  },
  navItem: {
    alignItems: "center",
  },
  navText: {
    fontSize: 16,
    color: "#333",
  },
  link: {
    padding: 4,
  },
  triangleMarker: {
    width: 0,
    height: 0,
    backgroundColor: "transparent",
    borderStyle: "solid",
    borderLeftWidth: 10,
    borderRightWidth: 10,
    borderBottomWidth: 20,
    borderLeftColor: "transparent",
    borderRightColor: "transparent",
    borderBottomColor: "red", // Change this color to customize the triangle
  },
  exampleMarker: {
    width: 20,
    height: 20,
    backgroundColor: "blue",
    borderRadius: 10,
  },
  slidingPanel: {
    position: "absolute",
    left: 0,
    right: 0,
    height: 300,
    backgroundColor: "#fff",
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    padding: 20,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: -2 },
    shadowOpacity: 0.2,
    shadowRadius: 5,
    elevation: 5,
  },
  panelText: {
    fontSize: 16,
    marginBottom: 10,
  },
  closeButton: {
    marginTop: 20,
    padding: 10,
    backgroundColor: "red",
    borderRadius: 5,
    alignItems: "center",
  },
  closeButtonText: {
    color: "#fff",
    fontSize: 16,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },
  loadingText: {
    marginTop: 10,
    fontSize: 16,
    color: "#333",
  },
  lockButton: {
    position: "absolute",
    bottom: 80,
    right: 20,
    backgroundColor: "blue",
    padding: 10,
    borderRadius: 5,
    alignItems: "center",
  },
  lockButtonText: {
    color: "#fff",
    fontSize: 16,
  },
  filterPanel: {
    width: "100%",
    backgroundColor: "#fff",
    padding: 10,
    borderBottomWidth: 1,
    borderBottomColor: "#ccc",
    elevation: 2,
    zIndex: 10, // Ensure it appears above the map
  },
  filterGroup: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 10,
  },
  filterLabel: {
    fontSize: 16,
    fontWeight: "bold",
    marginRight: 10,
    color: "#333",
  },
  filterButton: {
    backgroundColor: "#007bff",
    paddingVertical: 5,
    paddingHorizontal: 10,
    borderRadius: 5,
    marginRight: 10,
  },
  filterButtonText: {
    color: "#fff",
    fontSize: 14,
  },
});