import { useEffect, useState } from 'react';
import { View, Text, TextInput, Button, FlatList, StyleSheet, Alert } from 'react-native';
import { getGenres, insertGenre, deleteGenre } from '../../db/genreModel';

export default function GenreScreen() {
  const [genres, setGenres] = useState([]);
  const [newGenre, setNewGenre] = useState('');

  const loadGenres = async () => {
    try {
      const data = await getGenres();
      setGenres(data);
    } catch (err) {
      console.log('Ошибка при загрузке жанров:', err);
    }
  };

  const handleAddGenre = async () => {
    if (!newGenre.trim()) return;
    await insertGenre(newGenre.trim());
    setNewGenre('');
    loadGenres();
  };

  const handleDelete = (id) => {
    Alert.alert('Удаление', 'Удалить жанр?', [
      { text: 'Отмена' },
      {
        text: 'Удалить',
        onPress: async () => {
          await deleteGenre(id);
          loadGenres();
        },
      },
    ]);
  };

  useEffect(() => {
    loadGenres();
  }, []);

  return (
    <View style={styles.container}>
      <TextInput
        placeholder="Новый жанр"
        value={newGenre}
        onChangeText={setNewGenre}
        style={styles.input}
      />
      <Button title="Добавить" onPress={handleAddGenre} />

      <FlatList
        data={genres}
        keyExtractor={(item) => item.id.toString()}
        renderItem={({ item }) => (
          <View style={styles.genreItem}>
            <Text style={styles.name}>{item.name}</Text>
            <Button title="Удалить" onPress={() => handleDelete(item.id)} />
          </View>
        )}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { padding: 16 },
  input: {
    borderBottomWidth: 1,
    marginBottom: 12,
    padding: 8,
    backgroundColor: '#f0f0f0',
  },
  genreItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginVertical: 8,
    padding: 10,
    backgroundColor: '#eee',
    borderRadius: 6,
  },
  name: {
    fontSize: 16,
  },
});
