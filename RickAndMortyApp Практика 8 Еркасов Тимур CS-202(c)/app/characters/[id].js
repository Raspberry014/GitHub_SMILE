import { useLocalSearchParams } from 'expo-router';
import { useEffect, useState } from 'react';
import { View, Text, Image, ActivityIndicator, StyleSheet } from 'react-native';
import { fetchCharacterById } from '../../api/rickAndMorty';

export default function CharacterDetails() {
  const { id } = useLocalSearchParams();
  const [character, setCharacter] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCharacterById(id).then((data) => {
      setCharacter(data);
      setLoading(false);
    });
  }, []);

  if (loading) return <ActivityIndicator size="large" />;
  if (!character) return <Text>Персонаж не найден</Text>;

  return (
    <View style={styles.container}>
      <Image source={{ uri: character.image }} style={styles.image} />
      <Text style={styles.name}>{character.name}</Text>
      <Text>Status: {character.status}</Text>
      <Text>Species: {character.species}</Text>
      <Text>Gender: {character.gender}</Text>
      <Text>Origin: {character.origin.name}</Text>
      <Text>Location: {character.location.name}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, alignItems: 'center', padding: 20 },
  image: { width: 200, height: 200, borderRadius: 100, marginBottom: 20 },
  name: { fontSize: 24, fontWeight: 'bold', marginBottom: 10 },
});
