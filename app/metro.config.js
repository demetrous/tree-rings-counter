const { getDefaultConfig } = require("expo/metro-config");
const { withNativeWind } = require("nativewind/metro");

const config = getDefaultConfig(__dirname);

// npm on Windows creates empty-package.json lock directories like
// node_modules/.abort-controller-HfMIbxb0/ which cause Metro's Package.read()
// to crash with "Unexpected end of JSON input". Block them while preserving .bin.
config.resolver.blockList = [
  ...(config.resolver.blockList ? [config.resolver.blockList].flat() : []),
  /node_modules[\\/]\.(?!bin)[^\\/]+[\\/]/,
];

module.exports = withNativeWind(config, { input: "./global.css" });
