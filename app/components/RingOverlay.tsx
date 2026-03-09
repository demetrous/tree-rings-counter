import { View, Text } from "react-native";
import Svg, { Circle, Line, Text as SvgText } from "react-native-svg";

interface RingOverlayProps {
  ringCount: number;
  size?: number;
}

/**
 * Renders a stylized SVG cross-section with concentric rings
 * proportional to the detected ring count.
 */
export default function RingOverlay({ ringCount, size = 240 }: RingOverlayProps) {
  const cx = size / 2;
  const cy = size / 2;
  const maxRadius = (size / 2) * 0.92;

  // Generate ring radii with slight randomness for natural look
  const rings = Array.from({ length: ringCount }, (_, i) => {
    const normalized = (i + 1) / ringCount;
    // Non-linear spacing — inner rings are closer together (juvenile growth)
    const radius = maxRadius * Math.pow(normalized, 0.75);
    return radius;
  });

  // Color gradient: early rings = lighter, outer rings = darker
  const getRingColor = (index: number): string => {
    const ratio = index / Math.max(ringCount - 1, 1);
    const light = Math.round(200 - ratio * 100);
    return `rgb(${light}, ${Math.round(light * 0.72)}, ${Math.round(light * 0.45)})`;
  };

  return (
    <View className="items-center">
      <Svg width={size} height={size}>
        {/* Background fill */}
        <Circle cx={cx} cy={cy} r={maxRadius} fill="#3d2817" />

        {/* Rings */}
        {rings.map((r, i) => (
          <Circle
            key={i}
            cx={cx}
            cy={cy}
            r={r}
            fill="none"
            stroke={getRingColor(i)}
            strokeWidth={ringCount > 80 ? 0.8 : ringCount > 40 ? 1.2 : 1.8}
            opacity={0.85}
          />
        ))}

        {/* Pith (center dot) */}
        <Circle cx={cx} cy={cy} r={3} fill="#d4b48a" opacity={0.9} />

        {/* Cardinal lines through center */}
        <Line
          x1={cx} y1={cy - maxRadius}
          x2={cx} y2={cy + maxRadius}
          stroke="white" strokeWidth={0.5} opacity={0.15}
        />
        <Line
          x1={cx - maxRadius} y1={cy}
          x2={cx + maxRadius} y2={cy}
          stroke="white" strokeWidth={0.5} opacity={0.15}
        />

        {/* Ring count label */}
        <SvgText
          x={cx}
          y={size - 10}
          textAnchor="middle"
          fill="white"
          fontSize={10}
          opacity={0.5}
        >
          {ringCount} rings
        </SvgText>
      </Svg>
    </View>
  );
}
