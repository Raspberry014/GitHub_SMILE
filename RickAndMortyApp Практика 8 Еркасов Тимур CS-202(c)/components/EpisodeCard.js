import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';

export default function EpisodeCard({ episode, onPress }) {
  return (
    <TouchableOpacity style={styles.card} onPress={onPress}>
      <Text style={styles.name}>{episode.name}</Text>
      <Text>Код: {episode.episode}</Text>
      <Text>Дата: {episode.air_date}</Text>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  card: {
    padding: 15,
    margin: 10,
    backgroundColor: '#ffeedd',
    borderRadius: 10,
  },
  name: {
    fontSize: 17,
    fontWeight: 'bold',
    marginBottom: 5,
  },
});
