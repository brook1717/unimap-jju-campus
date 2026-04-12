// @capacitor/cli will be installed in Week 4 during mobile packaging.
// Run: npm install @capacitor/core @capacitor/cli

interface CapacitorConfig {
  appId: string;
  appName: string;
  webDir: string;
  bundledWebRuntime?: boolean;
  server?: { androidScheme: string };
}

const config: CapacitorConfig = {
  appId: 'et.edu.jju.unimap',
  appName: 'UniMap JJU',
  webDir: 'dist',
  bundledWebRuntime: false,
  server: {
    androidScheme: 'https',
  },
};

export default config;
