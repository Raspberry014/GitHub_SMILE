import React, { useState, useEffect } from 'react';
import { View, Text, Image, Button, StyleSheet, Modal, Pressable, TouchableOpacity } from 'react-native';

const games = [
  {
    title: "The Witcher 3: Wild Hunt",
    author: "CD Projekt",
    year: 2015,
    imageUrl: "https://upload.wikimedia.org/wikipedia/en/0/0c/Witcher_3_cover_art.jpg",
    description: "Эпическая RPG в открытом мире с охотником на монстров Геральтом."
  },
  {
    title: "Minecraft",
    author: "Mojang",
    year: 2011,
    imageUrl: "https://upload.wikimedia.org/wikipedia/en/5/51/Minecraft_cover.png",
    description: "Песочница с кубическим миром и бесконечными возможностями строительства."
  },
  {
    title: "Grand Theft Auto V",
    author: "Rockstar Games",
    year: 2013,
    imageUrl: "https://upload.wikimedia.org/wikipedia/en/a/a5/Grand_Theft_Auto_V.png",
    description: "Открытый мир, сюжет и хаос в Лос-Сантосе."
  },
  {
    title: "Elden Ring",
    author: "FromSoftware",
    year: 2022,
    imageUrl: "https://upload.wikimedia.org/wikipedia/en/b/b9/Elden_Ring_Box_art.jpg",
    description: "Фэнтези-RPG от автора Dark Souls и Джорджа Мартина."
  },
  {
    title: "God of War",
    author: "Santa Monica Studio",
    year: 2018,
    imageUrl: "https://upload.wikimedia.org/wikipedia/en/a/a7/God_of_War_4_cover.jpg",
    description: "Скандинавская мифология и отцовство в одной игре."
  }
];

export default function App() {
  const [index, setIndex] = useState(0);
  const [modalVisible, setModalVisible] = useState(false);

  const game = games[index];

  useEffect(() => {
    console.log("📋 Список игр:", games);
    console.log("🎮 Текущая игра:", game.title);
    console.log("📍 Индекс:", index);
  }, [index]);

  return (
    <View style={styles.container}>
      <TouchableOpacity onLongPress={() => {
        console.log("🧠 Долгое нажатие на игру:", game.title);
        setModalVisible(true);
      }}>
        <Image source={{ uri: game.imageUrl }} style={styles.image} />
      </TouchableOpacity>

      <Text style={styles.title}>{game.title}</Text>
      <Text style={styles.info}>Разработчик: {game.author}</Text>
      <Text style={styles.info}>Год выпуска: {game.year}</Text>

      <View style={styles.buttonContainer}>
        <Button
          title="Предыдущий"
          onPress={() => {
            console.log("⬅️ Предыдущий");
            setIndex(index - 1);
          }}
          disabled={index === 0}
        />
        <Button
          title="Следующий"
          onPress={() => {
            console.log("➡️ Следующий");
            setIndex(index + 1);
          }}
          disabled={index === games.length - 1}
        />
      </View>

      <Modal
        visible={modalVisible}
        transparent={true}
        animationType="slide"
        onRequestClose={() => {
          console.log("❌ Закрытие модального окна");
          setModalVisible(false);
        }}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalText}>{game.description}</Text>
            <Pressable
              style={styles.closeButton}
              onPress={() => {
                console.log("✅ Нажата кнопка 'Закрыть'");
                setModalVisible(false);
              }}
            >
              <Text style={{ color: '#fff' }}>Закрыть</Text>
            </Pressable>
          </View>
        </View>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    paddingTop: 60,
    alignItems: 'center',
    backgroundColor: '#f4f4f4',
    flex: 1
  },
  image: {
    width: 250,
    height: 350,
    borderRadius: 12,
    marginBottom: 20
  },
  title: {
    fontSize: 22,
    fontWeight: 'bold'
  },
  info: {
    fontSize: 16,
    marginVertical: 4
  },
  buttonContainer: {
    flexDirection: 'row',
    marginTop: 20,
    gap: 10
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'center',
    alignItems: 'center'
  },
  modalContent: {
    backgroundColor: '#fff',
    padding: 20,
    borderRadius: 10,
    width: '80%'
  },
  modalText: {
    fontSize: 16,
    marginBottom: 10
  },
  closeButton: {
    backgroundColor: '#007bff',
    padding: 10,
    alignItems: 'center',
    borderRadius: 6
  }
});
