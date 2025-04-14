import React from "react";
import { Text, View, Dimensions, Animated, ScrollView, Image, Pressable } from "react-native";
import SlidingUpPanel from "rn-sliding-up-panel";
import { Ionicons, MaterialIcons } from "@expo/vector-icons";

const { height } = Dimensions.get("window");

class BottomSheet extends React.Component {
  static defaultProps = {
    draggableRange: { top: height / 2, bottom: 0 }, // Reduce the top height to 50% of the screen
  };

  _draggedValue = new Animated.Value(180);

  scrollViewRef = React.createRef(); // Create a ref for the ScrollView

  componentDidUpdate(prevProps) {
    // Check if the selectedTicket has changed
    if (prevProps.selectedTicket !== this.props.selectedTicket) {
      // Scroll to the top of the ScrollView
      this.scrollViewRef.current?.scrollTo({ y: 0, animated: true });
    }
  }

  render() {
    const { top, bottom } = this.props.draggableRange;
    const { selectedTicket } = this.props; // Access selectedTicket from props

    const backgoundOpacity = this._draggedValue.interpolate({
      inputRange: [bottom, bottom],
      outputRange: [1, 0],
      extrapolate: "clamp",
    });

    const iconTranslateY = this._draggedValue.interpolate({
      inputRange: [bottom, top],
      outputRange: [0, 10],
      extrapolate: "clamp",
    });

    const textTranslateY = this._draggedValue.interpolate({
      inputRange: [bottom, top],
      outputRange: [0, 8],
      extrapolate: "clamp",
    });

    const textTranslateX = this._draggedValue.interpolate({
      inputRange: [bottom, top],
      outputRange: [0, -112],
      extrapolate: "clamp",
    });

    const textScale = this._draggedValue.interpolate({
      inputRange: [bottom, top],
      outputRange: [1, 0.7],
      extrapolate: "clamp",
    });

    return (
      <View className="z-5 flex-1 bg-gray-100 items-center justify-center">
        <SlidingUpPanel
          ref={(c) => (this._panel = c)}
          draggableRange={this.props.draggableRange}
          animatedValue={this._draggedValue}
          height={height / 2 + 180} // Adjust the height to match the reduced top value
          friction={0.5}
        >
          <View className="flex-1 bg-white relative">
            <Animated.View
              className="absolute top-[-24px] left-[75px] w-[200px] h-[48px] bg-primary rounded-full z-4"
              style={{
                opacity: backgoundOpacity,
                transform: [{ translateY: iconTranslateY }],
              }}
            />
            <View className="h-[20px] bg-primary justify-end p-2">
              <Animated.View
                style={{
                  transform: [
                    { translateY: textTranslateY },
                    { translateX: textTranslateX },
                    { scale: textScale },
                  ],
                }}
              ></Animated.View>
            </View>
            <View className="z-5 flex-1 bg-gray-100">
{/* Scrollable content */}
<View style={{ height: "60%" }}> {/* Restrict the height to 50% of the panel */}
  <ScrollView
    ref={this.scrollViewRef} // Attach the ref to the ScrollView
    contentContainerStyle={{ padding: 20 }}
    showsVerticalScrollIndicator={true}
  >
    {/* Display selectedTicket details */}
    {selectedTicket ? (
      <View className="bg-white rounded-lg shadow-lg p-4">
        

        {/* Title and Details Section */}
        <View className="mb-4">
          <Text className="text-xl font-bold text-gray-800 mb-2">
            {selectedTicket.title || "N/A"}
          </Text>
          <Text className="text-gray-600 mb-1">
            Location: {selectedTicket.latitude + "," + selectedTicket.longitude || "N/A"}
          </Text>
          <Text className="text-gray-600 mb-1">
            Severity: {selectedTicket.severity || "N/A"}
          </Text>
          <Text className="text-gray-600 mb-1">
            Status: {selectedTicket.status || "N/A"}
          </Text>
          {/* Image Section */}
        <View className="mb-4">
          <Image
            source={
                selectedTicket.image
                  ? { uri: selectedTicket.image } // Remote image
                  : require("@/assets/images/bgimg.png") // Local fallback image
              }
            className="w-full h-40 rounded-lg"
            resizeMode="cover"
          />
        </View>
          <Text className="text-gray-600">
            Description: {selectedTicket.description || "N/A"}
          </Text>
        </View>
        {/* Action Buttons Section */}
      <View className="flex-row justify-between items-center">
        <Pressable className="flex-row items-center">
          <Ionicons name="heart-outline" size={24} color="red" />
          <Text className="ml-2 text-gray-800">Like</Text>
        </Pressable>
        <Pressable className="flex-row items-center">
          <Ionicons name="chatbubble-outline" size={24} color="blue" />
          <Text className="ml-2 text-gray-800">Comment</Text>
        </Pressable>
        <Pressable>
          <Ionicons name="ellipsis-vertical" size={24} color="gray" />
        </Pressable>
      </View>
      </View>
      
    ) : (
      <Text className="text-gray-500 text-center">No ticket selected</Text>
    )}
  </ScrollView>
</View>
            </View>
          </View>
        </SlidingUpPanel>
      </View>
    );
  }
}

export default BottomSheet;