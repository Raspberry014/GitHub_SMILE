import { usePlaces } from '../../../context/PlacesContext';
import { useLocalSearchParams } from 'expo-router';
import { View, Text, Image, StyleSheet, ScrollView } from 'react-native';

export default function PlaceDetails() {
  const { state } = usePlaces();
  const { id } = useLocalSearchParams();

  const place = state.places.find((p) => p.id === parseInt(id));

  if (!place) {
    return <Text style={styles.notFound}>Место не найдено</Text>;
  }

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Image source={place.imageUrl} style={styles.image} />
      <Text style={styles.name}>{place.name}</Text>
      <Text style={styles.category}>{place.category}</Text>
      <Text style={styles.desc}>{place.description}</Text>
      <Text style={styles.rating}>Рейтинг: {place.rating}</Text>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { padding: 16, alignItems: 'center' },
  image: { width: '100%', height: 250, borderRadius: 10, marginBottom: 20 },
  name: { fontSize: 24, fontWeight: 'bold', marginBottom: 5 },
  category: { fontSize: 16, fontStyle: 'italic', marginBottom: 10 },
  desc: { fontSize: 16, marginBottom: 10, textAlign: 'center' },
  rating: { fontSize: 16, color: '#666' },
  notFound: { padding: 16, fontSize: 18, color: 'red' },
});
