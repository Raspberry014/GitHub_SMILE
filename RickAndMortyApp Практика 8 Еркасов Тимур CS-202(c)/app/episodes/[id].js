import { useLocalSearchParams } from 'expo-router';
import { useEffect, useState } from 'react';
import { View, Text, ActivityIndicator, StyleSheet } from 'react-native';
import { fetchEpisodeById } from '../../api/rickAndMorty';

export default function EpisodeDetails() {
  const { id } = useLocalSearchParams();
  const [episode, setEpisode] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchEpisodeById(id).then((data) => {
      setEpisode(data);
      setLoading(false);
    });
  }, []);

  if (loading) return <ActivityIndicator size="large" />;
  if (!episode) return <Text>Эпизод не найден</Text>;

  return (
    <View style={styles.container}>
      <Text style={styles.name}>{episode.name}</Text>
      <Text>Код: {episode.episode}</Text>
      <Text>Дата выхода: {episode.air_date}</Text>
      <Text>Количество персонажей: {episode.characters.length}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20 },
  name: { fontSize: 22, fontWeight: 'bold', marginBottom: 10 },
});
