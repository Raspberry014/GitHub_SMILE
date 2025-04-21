import { useLocalSearchParams, useRouter } from 'expo-router';
import { View, Text, FlatList, Image, TouchableOpacity, StyleSheet } from 'react-native';
import { usePlaces } from '../../../context/PlacesContext';

export default function PlacesByCategory() {
  const { category } = useLocalSearchParams();
  const { state, dispatch } = usePlaces();
  const router = useRouter();

  const filtered = state.places.filter((p) => p.category === category);

  const handleSelectPlace = (place) => {
    dispatch({ type: 'SELECT_PLACE', payload: place });
    router.push(`/places/${place.id}`);
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>{category}</Text>
      <FlatList
        data={filtered}
        keyExtractor={(item) => item.id.toString()}
        renderItem={({ item }) => (
          <TouchableOpacity style={styles.card} onPress={() => handleSelectPlace(item)}>
            <Image source={item.imageUrl} style={styles.image} />
            <View style={styles.info}>
              <Text style={styles.name}>{item.name}</Text>
              <Text style={styles.desc}>{item.description}</Text>
              <Text style={styles.rating}>Рейтинг: {item.rating}</Text>
            </View>
          </TouchableOpacity>
        )}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16 },
  title: { fontSize: 24, fontWeight: 'bold', marginBottom: 10 },
  card: {
    flexDirection: 'row',
    backgroundColor: '#eef',
    marginBottom: 12,
    borderRadius: 10,
    overflow: 'hidden',
  },
  image: { width: 100, height: 100 },
  info: { flex: 1, padding: 10 },
  name: { fontWeight: 'bold', fontSize: 18 },
  desc: { fontSize: 14, color: '#555' },
  rating: { marginTop: 6, fontStyle: 'italic' },
});
