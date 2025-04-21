import { View, Text, Image, StyleSheet, TouchableOpacity } from 'react-native';

export default function CharacterCard({ character, onPress }) {
  return (
    <TouchableOpacity style={styles.card} onPress={onPress}>
      <Image source={{ uri: character.image }} style={styles.image} />
      <View style={styles.info}>
        <Text style={styles.name}>{character.name}</Text>
        <Text>Status: {character.status}</Text>
        <Text>Species: {character.species}</Text>
      </View>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  card: {
    flexDirection: 'row',
    margin: 10,
    backgroundColor: '#eee',
    borderRadius: 10,
    overflow: 'hidden',
  },
  image: {
    width: 100,
    height: 100,
  },
  info: {
    padding: 10,
    justifyContent: 'center',
  },
  name: {
    fontWeight: 'bold',
    fontSize: 16,
  },
});
