import { PixelifySans_400Regular, PixelifySans_700Bold } from '@expo-google-fonts/pixelify-sans';
import { useFonts } from 'expo-font';
import { DarkTheme, DefaultTheme, Stack, ThemeProvider } from 'expo-router';
import * as SplashScreen from 'expo-splash-screen';
import { useEffect } from 'react';
import { GestureHandlerRootView } from 'react-native-gesture-handler';

import { PixelFonts, WorldColors } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';
import { useTheme } from '@/hooks/use-theme';

// Keep the native splash up until the pixel font is ready, so text never swaps fonts.
SplashScreen.preventAutoHideAsync();

export default function RootLayout() {
  const colorScheme = useColorScheme();
  const colors = useTheme();
  const baseTheme = colorScheme === 'dark' ? DarkTheme : DefaultTheme;
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
    <ThemeProvider
      value={{
        ...baseTheme,
        colors: {
          ...baseTheme.colors,
          primary: colors.accent,
          background: colors.background,
          card: colors.backgroundElement,
          text: colors.text,
          border: colors.border,
        },
      }}>
      <GestureHandlerRootView style={{ flex: 1 }}>
        <Stack
          screenOptions={{
            headerShown: false,
            statusBarHidden: true,
            navigationBarHidden: true,
            contentStyle: { backgroundColor: WorldColors.space },
          }}
        />
      </GestureHandlerRootView>
    </ThemeProvider>
  );
}
