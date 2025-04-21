import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';

export default function LocationCard({ location, onPress }) {
  return (
    <TouchableOpacity style={styles.card} onPress={onPress}>
      <Text style={styles.name}>{location.name}</Text>
      <Text>Тип: {location.type}</Text>
      <Text>Измерение: {location.dimension}</Text>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  card: {
    padding: 15,
    margin: 10,
    backgroundColor: '#ddeeff',
    borderRadius: 10,
  },
  name: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 5,
  },
});
