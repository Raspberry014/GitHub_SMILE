import { useEffect, useState } from 'react';
import { View, Text, FlatList, Button, StyleSheet, ActivityIndicator, TouchableOpacity } from 'react-native';
import { getGames, deleteGame } from '../../db/gameModel';
import { useRouter } from 'expo-router';
import { exportGamesToJson } from '../../utils/exportToJson';


export default function GameListScreen() {
  const [games, setGames] = useState([]);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  const loadGames = async () => {
    setLoading(true);
    try {
      const data = await getGames();
      setGames(data);
    } catch (err) {
      console.log('Ошибка загрузки игр:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    await deleteGame(id);
    loadGames();
  };

  useEffect(() => {
    const unsubscribe = router.addListener('focus', loadGames); // обновление при возвращении на экран
    loadGames();
    return unsubscribe;
  }, []);

  const renderItem = ({ item }) => (
    <TouchableOpacity style={styles.card} onPress={() => router.push(`/games/${item.id}`)}>
      <Text style={styles.title}>{item.title}</Text>
      <Text>{item.platform} • {item.releaseYear}</Text>
      <Text>Жанр: {item.genreName || 'Без жанра'}</Text>
      <Button title="Удалить" onPress={() => handleDelete(item.id)} />
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      <Button title="Экспортировать в JSON" onPress={exportGamesToJson} />
      <Button title="Добавить игру" onPress={() => router.push('/games/new')} />
      {loading ? (
        <ActivityIndicator size="large" />
      ) : (
        <FlatList
          data={games}
          keyExtractor={(item) => item.id.toString()}
          renderItem={renderItem}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 10 },
  card: {
    backgroundColor: '#eef',
    marginVertical: 8,
    padding: 12,
    borderRadius: 8,
  },
  title: { fontSize: 18, fontWeight: 'bold' },
});
