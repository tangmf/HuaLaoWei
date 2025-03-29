import React, { useState, useEffect, useRef } from "react";
import { Text, View, Image, Pressable, ActivityIndicator, Animated, Dimensions, TextInput } from "react-native";
import MapView, { Marker, PROVIDER_DEFAULT } from "react-native-maps";
import * as Location from "expo-location";
import Navbar from "@/components/Navbar";
import Header from "@/components/Header";

const { height } = Dimensions.get("window");

export default function Home() {
  const [location, setLocation] = useState(null);
  const [heading, setHeading] = useState(0);
  const mapRef = useRef(null);
  const [hasZoomed, setHasZoomed] = useState(false);
  const [isPanelVisible, setIsPanelVisible] = useState(false);
  const slideAnim = useRef(new Animated.Value(height)).current;

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
            mapRef.current.animateToRegion({
              latitude: newLocation.coords.latitude,
              longitude: newLocation.coords.longitude,
              latitudeDelta: 0.005,
              longitudeDelta: 0.005,
            }, 1000);
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

  const togglePanel = () => {
    if (isPanelVisible) {
      Animated.timing(slideAnim, {
        toValue: height,
        duration: 300,
        useNativeDriver: false,
      }).start(() => setIsPanelVisible(false));
    } else {
      setIsPanelVisible(true);
      Animated.timing(slideAnim, {
        toValue: height - 300,
        duration: 300,
        useNativeDriver: false,
      }).start();
    }
  };

  const lockToMarker = () => {
    if (location && mapRef.current) {
      mapRef.current.animateToRegion({
        latitude: location.coords.latitude,
        longitude: location.coords.longitude,
        latitudeDelta: 0.005,
        longitudeDelta: 0.005,
      }, 1000);
    }
  };

  return (
    <View className="flex-1 bg-white">
      <Header title="Home" />

      <View className="flex-1 items-center justify-center">
        <View className="w-full bg-white p-3 border-b border-gray-300 z-10">
          <View className="flex-row items-center mb-2">
            <Text className="text-base font-bold text-gray-800 mr-2">Tags:</Text>
            <Pressable className="bg-blue-500 px-3 py-1 rounded">
              <Text className="text-white text-sm">Add</Text>
            </Pressable>
          </View>
          <View className="flex-row items-center mb-2">
            <Text className="text-base font-bold text-gray-800 mr-2">Severity:</Text>
            <Pressable className="bg-blue-500 px-3 py-1 rounded">
              <Text className="text-white text-sm">Add</Text>
            </Pressable>
          </View>
          <View className="flex-row items-center">
            <Text className="text-base font-bold text-gray-800 mr-2">Status:</Text>
            <Pressable className="bg-blue-500 px-3 py-1 rounded">
              <Text className="text-white text-sm">Add</Text>
            </Pressable>
          </View>
        </View>

        {location ? (
            <MapView
              ref={mapRef}
              style={{ width: "100%", height: "100%" }} 
              mapType="satellite"
              provider={PROVIDER_DEFAULT}
              initialRegion={{
                latitude: location.coords.latitude,
                longitude: location.coords.longitude,
                latitudeDelta: 0.005,
                longitudeDelta: 0.005,
              }}
            >
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

            <Marker
              coordinate={{
                latitude: location.coords.latitude + 0.001,
                longitude: location.coords.longitude + 0.001,
              }}
              title="Example Marker"
              description="This is an example marker with additional details."
              onPress={togglePanel}
            >
              <View className="w-5 h-5 bg-blue-500 rounded-full" />
            </Marker>
          </MapView>
        ) : (
          <View className="flex-1 justify-center items-center">
            <ActivityIndicator size="large" color="#0000ff" />
            <Text className="mt-2 text-base text-gray-700">Please wait...</Text>
          </View>
        )}
      </View>

      <Pressable
        onPress={lockToMarker}
        className="absolute bottom-20 right-5 bg-blue-500 px-4 py-2 rounded"
      >
        <Text className="text-white text-base">Lock</Text>
      </Pressable>

      <Animated.View
        style={{ top: slideAnim }}
        className="absolute left-0 right-0 h-[300px] bg-white rounded-t-2xl p-5 shadow shadow-black/20"
      >
        <Text className="text-base mb-2">Example Marker Details</Text>
        <Text className="text-base mb-2">Latitude: {location?.coords.latitude + 0.001}</Text>
        <Text className="text-base mb-2">Longitude: {location?.coords.longitude + 0.001}</Text>
        <Pressable
          className="mt-4 p-3 bg-red-500 rounded items-center"
          onPress={togglePanel}
        >
          <Text className="text-white text-base">Close</Text>
        </Pressable>
      </Animated.View>

      <Navbar />
    </View>
  );
}
