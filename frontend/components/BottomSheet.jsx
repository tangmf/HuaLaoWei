import React from "react";
import { Text, View, Dimensions, Animated, ScrollView } from "react-native";

import SlidingUpPanel from "rn-sliding-up-panel";

const { height } = Dimensions.get("window");

const styles = {
  container: {
    flex: 1,
    backgroundColor: "#f8f9fa",
    alignItems: "center",
    justifyContent: "center"
  },
  panel: {
    flex: 1,
    backgroundColor: "white",
    position: "relative"
  },
  panelHeader: {
    height: 20,
    backgroundColor: "red",
    justifyContent: "flex-end",
    padding: 10,
  },
  icon: {
    alignItems: "center",
    justifyContent: "center",
    position: "absolute",
    top: -24,
    right: 18,
    width: 48,
    height: 48,
    zIndex: 1
  },
  iconBg: {
    backgroundColor: "red",
    position: "absolute",
    top: -24,
    right: 18,
    width: 48,
    height: 48,
    borderRadius: 24,
    zIndex: 1
  }
};

class BottomSheet extends React.Component {
    static defaultProps = {
      draggableRange: { top: height / 2, bottom: 0 }, // Reduce the top height to 50% of the screen
    };
  
    _draggedValue = new Animated.Value(180);
  
    render() {
      const { top, bottom } = this.props.draggableRange;
      const { selectedTicket } = this.props; // Access selectedTicket from props
  
      const backgoundOpacity = this._draggedValue.interpolate({
        inputRange: [bottom, top],
        outputRange: [1, 0],
        extrapolate: "clamp",
      });
  
      const iconTranslateY = this._draggedValue.interpolate({
        inputRange: [bottom, top],
        outputRange: [0, 56],
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
        <View style={styles.container}>
          <SlidingUpPanel
            ref={(c) => (this._panel = c)}
            draggableRange={this.props.draggableRange}
            animatedValue={this._draggedValue}
            snappingPoints={[360]}
            height={height / 2 + 180} // Adjust the height to match the reduced top value
            friction={0.5}
          >
            <View style={styles.panel}>
              <Animated.View
                style={[
                  styles.iconBg,
                  {
                    opacity: backgoundOpacity,
                    transform: [{ translateY: iconTranslateY }],
                  },
                ]}
              />
              <View style={styles.panelHeader}>
                <Animated.View
                  style={{
                    transform: [
                      { translateY: textTranslateY },
                      { translateX: textTranslateX },
                      { scale: textScale },
                    ],
                  }}
                >

                </Animated.View>
              </View>
              <View style={styles.container}>
                {/* Scrollable content */}
              <ScrollView contentContainerStyle={{ padding: 20 }}>
                {/* Display selectedTicket details */}
                {selectedTicket ? (
                  <>
                    <Text>Title: {selectedTicket.title || "N/A"}</Text>
                    <Text>Latitude: {selectedTicket.latitude || "N/A"}</Text>
                    <Text>Longitude: {selectedTicket.longitude || "N/A"}</Text>
                    <Text>Severity: {selectedTicket.severity || "N/A"}</Text>
                    <Text>Status: {selectedTicket.status || "N/A"}</Text>
                    <Text>Description: {selectedTicket.description || "N/A"}</Text>
                  </>
                ) : (
                  <Text>No ticket selected</Text>
                )}
              </ScrollView>
              </View>
            </View>
          </SlidingUpPanel>
        </View>
      );
    }
  }
  
  export default BottomSheet;
