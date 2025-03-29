import React, { useState, useEffect, useRef } from "react";
import { Text, View, StyleSheet, ImageBackground, Pressable, Alert, ActivityIndicator } from "react-native";
import MapView, { Marker, PROVIDER_DEFAULT } from "react-native-maps";
import * as Location from "expo-location";
import backgroundimg from "@/assets/images/bgimg.png";
import { Link } from "expo-router";

export default function Index() {
  const [location, setLocation] = useState(null);
  const [heading, setHeading] = useState(0); // State to store the device's heading
  const mapRef = useRef(null); // Reference to the MapView
  const [hasZoomed, setHasZoomed] = useState(false); // State to track if the map has already zoomed

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

  return (
    <View style={styles.container}>
      {/* Main Content */}
      <View style={styles.content}>
        <ImageBackground source={backgroundimg} style={styles.image}>
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
            </MapView>
          ) : (
            // Loading Indicator
            <ActivityIndicator size="large" color="#0000ff" style={styles.loadingIndicator} />
          )}
        </ImageBackground>
      </View>

      {/* Bottom Navigation Bar */}
      <View style={styles.navbar}>
        <Link href="/explore" style={styles.link} asChild>
          <Pressable style={styles.navItem}>
            <Text style={styles.navText}>Home</Text>
          </Pressable>
        </Link>

        <Link href="/explore" style={styles.link} asChild>
          <Pressable style={styles.navItem}>
            <Text style={styles.navText}>Create</Text>
          </Pressable>
        </Link>

        <Link href="/explore" style={styles.link} asChild>
          <Pressable style={styles.navItem}>
            <Text style={styles.navText}>Profile</Text>
          </Pressable>
        </Link>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
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
    width: "90%",
    height: "50%",
    borderRadius: 10,
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
});