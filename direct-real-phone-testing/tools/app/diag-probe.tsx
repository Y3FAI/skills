import { View } from "react-native";
import { DIAG, useDiagTrail } from "./diag";

/**
 * The trail as one invisible accessibility element (testID "diag") the phone runner reads:
 * XCUITest reads its label on iOS, uiautomator its content-desc on Android.
 * Test builds only (EXPO_PUBLIC_DIAG=1); renders nothing otherwise.
 * Put <DiagProbe /> once in the root layout, after the navigator, so it is on every screen.
 */
export function DiagProbe() {
  if (!DIAG) return null;
  return <Probe />;
}

function Probe() {
  const trail = useDiagTrail();
  return (
    <View
      testID="diag"
      accessible
      accessibilityLabel={trail.join("\n") || "-"}
      pointerEvents="none"
      style={{ position: "absolute", top: 0, left: 0, width: 1, height: 1 }}
    />
  );
}
