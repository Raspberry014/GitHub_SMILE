import { useState, useEffect } from 'react';
import { View, Text, TextInput, Button, StyleSheet, Image, ScrollView, Alert } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { insertGame } from '../../db/gameModel';
import { getGenres } from '../../db/genreModel';
import { useRouter } from 'expo-router';

export default function NewGameScreen() {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [releaseYear, setReleaseYear] = useState('');
  const [platform, setPlatform] = useState('');
  const [imageUri, setImageUri] = useState('');
  const [genres, setGenres] = useState([]);
  const [genreId, setGenreId] = useState(null);
  const router = useRouter();

  useEffect(() => {
    getGenres().then(setGenres);
  }, []);

  const pickImage = async () => {
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      quality: 0.7,
    });

    if (!result.canceled) {
      setImageUri(result.assets[0].uri);
    }
  };

  const handleSave = async () => {
    if (!title || !releaseYear || !platform) {
      Alert.alert('Ошибка', 'Заполните обязательные поля');
      return;
    }

    const game = {
      title,
      description,
      releaseYear: parseInt(releaseYear),
      platform,
      imageUri,
      genreId,
    };

    try {
      await insertGame(game);
      router.replace('/games'); // назад к списку
    } catch (err) {
      Alert.alert('Ошибка при сохранении', err.message);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <TextInput
        placeholder="Название"
        value={title}
        onChangeText={setTitle}
        style={styles.input}
      />
      <TextInput
        placeholder="Описание"
        value={description}
        onChangeText={setDescription}
        style={styles.input}
        multiline
      />
      <TextInput
        placeholder="Год выпуска"
        value={releaseYear}
        onChangeText={setReleaseYear}
        keyboardType="numeric"
        style={styles.input}
      />
      <TextInput
        placeholder="Платформа (PC, PS5...)"
        value={platform}
        onChangeText={setPlatform}
        style={styles.input}
      />

      <Text style={styles.label}>Жанр:</Text>
      {genres.map((genre) => (
        <Button
          key={genre.id}
          title={`${genre.name} ${genreId === genre.id ? '✓' : ''}`}
          onPress={() => setGenreId(genre.id)}
        />
      ))}

      <Button title="Выбрать изображение" onPress={pickImage} />
      {imageUri ? <Image source={{ uri: imageUri }} style={styles.image} /> : null}

      <Button title="Сохранить игру" onPress={handleSave} />
    </ScrollView>
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
  label: {
    fontWeight: 'bold',
    marginVertical: 10,
  },
  image: {
    width: '100%',
    height: 200,
    marginTop: 10,
    marginBottom: 20,
  },
});
