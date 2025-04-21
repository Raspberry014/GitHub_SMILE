import { useState, useEffect } from 'react';
import { View, TextInput, FlatList, ActivityIndicator, Text, StyleSheet } from 'react-native';
import { fetchCharacters } from '../../api/rickAndMorty';
import CharacterCard from '../../components/CharacterCard';
import { useRouter } from 'expo-router';

export default function CharactersScreen() {
  const [characters, setCharacters] = useState([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const router = useRouter();

  const loadData = async (query = '') => {
    setLoading(true);
    setError('');
    try {
      const data = await fetchCharacters(query);
      setCharacters(data);
    } catch (err) {
      setError(err.message);
    }
    setLoading(false);
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleSearch = (text) => {
    setSearch(text);
    loadData(text);
  };

  return (
    <View style={styles.container}>
      <TextInput
        placeholder="Поиск персонажей..."
        value={search}
        onChangeText={handleSearch}
        style={styles.input}
      />
      {loading ? (
        <ActivityIndicator size="large" />
      ) : error ? (
        <Text>{error}</Text>
      ) : (
        <FlatList
          data={characters}
          keyExtractor={(item) => item.id.toString()}
          renderItem={({ item }) => (
            <CharacterCard character={item} onPress={() => router.push(`/characters/${item.id}`)} />
          )}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 10,
  },
  input: {
    backgroundColor: '#f0f0f0',
    padding: 10,
    borderRadius: 10,
    marginBottom: 10,
  },
});
