import { useLocalSearchParams, useRouter } from 'expo-router';
import { useEffect, useState } from 'react';
import { View, Text, Image, Button, ActivityIndicator, StyleSheet, Alert, ScrollView } from 'react-native';
import db from '../../db/database';
import { deleteGame } from '../../db/gameModel';

export default function GameDetails() {
  const { id } = useLocalSearchParams();
  const router = useRouter();
  const [game, setGame] = useState(null);
  const [loading, setLoading] = useState(true);

  const loadGame = () => {
    db.transaction(tx => {
      tx.executeSql(
        `SELECT games.*, genres.name AS genreName FROM games
         LEFT JOIN genres ON games.genreId = genres.id WHERE games.id = ?`,
        [id],
        (_, { rows }) => {
          setGame(rows._array[0]);
          setLoading(false);
        },
        (_, error) => {
          console.log(error);
          setLoading(false);
        }
      );
    });
  };

  useEffect(() => {
    loadGame();
  }, []);

  const handleDelete = async () => {
    Alert.alert('Удаление', 'Вы уверены?', [
      { text: 'Отмена' },
      {
        text: 'Удалить',
        onPress: async () => {
          await deleteGame(id);
          router.replace('/games');
        },
      },
    ]);
  };

  if (loading) return <ActivityIndicator size="large" />;
  if (!game) return <Text>Игра не найдена</Text>;

  return (
    <ScrollView style={styles.container}>
      {game.imageUri ? <Image source={{ uri: game.imageUri }} style={styles.image} /> : null}
      <Text style={styles.title}>{game.title}</Text>
      <Text>Платформа: {game.platform}</Text>
      <Text>Год: {game.releaseYear}</Text>
      <Text>Жанр: {game.genreName || '—'}</Text>
      <Text style={styles.description}>{game.description}</Text>

      <Button title="Удалить игру" color="red" onPress={handleDelete} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { padding: 20 },
  image: { width: '100%', height: 200, marginBottom: 20 },
  title: { fontSize: 22, fontWeight: 'bold', marginBottom: 10 },
  description: { marginTop: 10, fontStyle: 'italic' },
});
