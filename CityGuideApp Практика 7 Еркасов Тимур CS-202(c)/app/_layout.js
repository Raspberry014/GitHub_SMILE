import { Stack } from 'expo-router';
import { PlacesProvider } from '../context/PlacesContext';

export default function RootLayout() {
  return (
    <PlacesProvider>
      <Stack screenOptions={{ headerShown: false }} />
    </PlacesProvider>
  );
}
