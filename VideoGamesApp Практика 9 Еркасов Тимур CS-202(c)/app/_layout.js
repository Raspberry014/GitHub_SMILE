import { Tabs } from 'expo-router';
import { Provider as PaperProvider, useTheme } from 'react-native-paper';
import { useColorScheme } from 'react-native';
import { MD3DarkTheme, MD3LightTheme } from 'react-native-paper';
import { useEffect } from 'react';
import { initDb } from '../db/database';
  
export default function Layout() {
  const colorScheme = useColorScheme();
  const theme = colorScheme === 'dark' ? MD3DarkTheme : MD3LightTheme;

  useEffect(() => {
    initDb()
      .then(() => console.log('База данных инициализирована'))
      .catch((err) => console.log('Ошибка БД:', err));
  }, []);

  return (
    <PaperProvider theme={theme}>
      <Tabs>
        <Tabs.Screen name="games" options={{ title: 'Игры' }} />
        <Tabs.Screen name="genres" options={{ title: 'Жанры' }} />
      </Tabs>
    </PaperProvider>
  );
}
