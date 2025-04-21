import { useLocalSearchParams } from 'expo-router';
import { useEffect, useState } from 'react';
import { View, Text, ActivityIndicator, StyleSheet } from 'react-native';
import { fetchLocationById } from '../../api/rickAndMorty';

export default function LocationDetails() {
  const { id } = useLocalSearchParams();
  const [location, setLocation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchLocationById(id)
      .then((data) => {
        setLocation(data);
      })
      .catch(() => setError('Ошибка загрузки'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <ActivityIndicator size="large" />;
  if (error) return <Text>{error}</Text>;
  if (!location) return <Text>Нет данных</Text>;

  return (
    <View style={styles.container}>
      <Text style={styles.name}>{location.name}</Text>
      <Text>Тип: {location.type}</Text>
      <Text>Измерение: {location.dimension}</Text>
      <Text>Кол-во жителей: {location.residents?.length ?? 0}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20 },
  name: { fontSize: 22, fontWeight: 'bold', marginBottom: 10 },
});
