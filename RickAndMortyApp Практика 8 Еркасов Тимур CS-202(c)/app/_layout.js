import { Tabs } from 'expo-router';

export default function Layout() {
  return (
    <Tabs>
      <Tabs.Screen name="characters" options={{ title: 'Персонажи' }} />
      <Tabs.Screen name="locations" options={{ title: 'Локации' }} />
      <Tabs.Screen name="episodes" options={{ title: 'Эпизоды' }} />
    </Tabs>
  );
}
