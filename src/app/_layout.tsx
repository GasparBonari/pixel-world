import { PixelifySans_400Regular, PixelifySans_700Bold } from '@expo-google-fonts/pixelify-sans';
import { useFonts } from 'expo-font';
import { DarkTheme, Stack, ThemeProvider } from 'expo-router';
import * as SplashScreen from 'expo-splash-screen';
import { useEffect } from 'react';
import { GestureHandlerRootView } from 'react-native-gesture-handler';

import { Palette, PixelFonts, WorldColors } from '@/constants/theme';
import { NoticeProvider } from '@/ui';

// Keep the native splash up until the pixel font is ready, so text never swaps fonts.
SplashScreen.preventAutoHideAsync();

export default function RootLayout() {
  const [fontsLoaded, fontError] = useFonts({
    [PixelFonts.regular]: PixelifySans_400Regular,
    [PixelFonts.bold]: PixelifySans_700Bold,
  });
  useEffect(() => {
    if (fontsLoaded || fontError) SplashScreen.hideAsync();
  }, [fontsLoaded, fontError]);
  // A failed font load falls back to system text rather than blocking the app.
  if (!fontsLoaded && !fontError) return null;

  return (
    // One game look in light and dark system modes: night-navy frame, parchment content.
    <ThemeProvider
      value={{
        ...DarkTheme,
        colors: {
          ...DarkTheme.colors,
          primary: Palette.gold,
          background: Palette.space,
          card: Palette.navyDeep,
          text: Palette.snow,
          border: Palette.navyEdge,
        },
      }}>
      <GestureHandlerRootView style={{ flex: 1 }}>
        <NoticeProvider>
          <Stack
            screenOptions={{
              headerShown: false,
              statusBarHidden: true,
              navigationBarHidden: true,
              contentStyle: { backgroundColor: WorldColors.space },
            }}
          />
        </NoticeProvider>
      </GestureHandlerRootView>
    </ThemeProvider>
  );
}
