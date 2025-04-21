import React from 'react';
import { View, Text, Image, StyleSheet, ScrollView } from 'react-native';

export default function App() {
  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Image
        source={require('./assets/123.png')} // вставьте ссылку на своё фото
        style={styles.avatar}
      />
      <Text style={styles.name}>Тимур Еркасов</Text>
      <Text style={styles.group}>Группа: CS-202(c)</Text>
      <Text style={styles.email}>Email: timur@example.com</Text>
      <Text style={styles.sectionTitle}>О себе:</Text>
      <Text style={styles.description}>
        Люблю программирование, компьютерные игры, путешествия и книги. 
        Цитата: "Учись так, будто тебе предстоит жить вечно."
      </Text>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
    paddingVertical: 50,
    paddingHorizontal: 20,
    backgroundColor: '#f2f2f2',
  },
  avatar: {
    width: 150,
    height: 150,
    borderRadius: 75,
    marginBottom: 20,
    borderWidth: 2,
    borderColor: '#333',
  },
  name: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  group: {
    fontSize: 18,
    marginBottom: 5,
  },
  email: {
    fontSize: 16,
    color: '#555',
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  description: {
    fontSize: 16,
    textAlign: 'center',
    lineHeight: 22,
  },
});
