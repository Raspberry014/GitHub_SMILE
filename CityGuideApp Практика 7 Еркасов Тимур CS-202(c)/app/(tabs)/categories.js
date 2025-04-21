import { View, Text, FlatList, TouchableOpacity, StyleSheet } from 'react-native';
import { usePlaces } from '../../context/PlacesContext';
import { useRouter } from 'expo-router';

export default function CategoriesScreen() {
  const { state, dispatch } = usePlaces();
  const router = useRouter();

  const handleSelectCategory = (category) => {
    dispatch({ type: 'SELECT_CATEGORY', payload: category });
    router.push(`/places/${category}`);
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Категории</Text>
      <FlatList
        data={state.categories}
        keyExtractor={(item) => item}
        renderItem={({ item }) => (
          <TouchableOpacity style={styles.card} onPress={() => handleSelectCategory(item)}>
            <Text style={styles.cardText}>{item}</Text>
          </TouchableOpacity>
        )}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16 },
  title: { fontSize: 24, fontWeight: 'bold', marginBottom: 12 },
  card: {
    backgroundColor: '#ccddff',
    padding: 20,
    marginBottom: 12,
    borderRadius: 8,
  },
  cardText: { fontSize: 18 },
});
