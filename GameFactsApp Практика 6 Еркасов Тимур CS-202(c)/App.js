import * as React from 'react';
import { FlatList, Image } from 'react-native';
import { Provider as PaperProvider, DefaultTheme, DarkTheme, Card, Title, Paragraph, useTheme } from 'react-native-paper';
import { useColorScheme, View, Text } from 'react-native';

const facts = [
  {
    id: '1',
    title: 'The Legend of Zelda: Ocarina of Time',
    image: 'https://upload.wikimedia.org/wikipedia/en/5/57/The_Legend_of_Zelda_Ocarina_of_Time.jpg',
    description: 'Первая 3D-игра в серии, вышедшая в 1998 году и получившая рекордные оценки.',
    date: '1998-11-21'
  },
  {
    id: '2',
    title: 'Half-Life 2',
    image: 'https://upload.wikimedia.org/wikipedia/en/2/25/Half-Life_2_cover.jpg',
    description: 'Valve представила революционный игровой движок Source с реалистичной физикой.',
    date: '2004-11-16'
  },
  {
    id: '3',
    title: 'The Witcher 3: Wild Hunt',
    image: 'https://upload.wikimedia.org/wikipedia/en/0/0c/Witcher_3_cover_art.jpg',
    description: 'Открытый мир, потрясающий сюжет и сотни часов контента от CD Projekt RED.',
    date: '2015-05-19'
  },
  {
    id: '4',
    title: 'Minecraft',
    image: 'https://upload.wikimedia.org/wikipedia/en/5/51/Minecraft_cover.png',
    description: 'Игра, которая позволяет строить и выживать, завоевала миллионы игроков по всему миру.',
    date: '2011-11-18'
  },
  {
    id: '5',
    title: 'Elden Ring',
    image: 'https://upload.wikimedia.org/wikipedia/en/b/b9/Elden_Ring_Box_art.jpg',
    description: 'Совместный проект FromSoftware и Джорджа Мартина, ставший хитом 2022 года.',
    date: '2022-02-25'
  }
];

const GameCard = ({ item }) => {
  const { colors } = useTheme();

  return (
    <Card style={{ margin: 10, backgroundColor: colors.surface }}>
      <Card.Content>
        <Text style={{ fontSize: 12, color: colors.primary }}>📅 {item.date}</Text>
        <Title>{item.title}</Title>
      </Card.Content>
      <Card.Cover source={{ uri: item.image }} />
      <Card.Content>
        <Paragraph style={{ marginTop: 5 }}>{item.description}</Paragraph>
      </Card.Content>
    </Card>
  );
};

export default function App() {
  const scheme = useColorScheme(); // 'light' | 'dark'
  const theme = scheme === 'dark' ? DarkTheme : DefaultTheme;

  return (
    <PaperProvider theme={theme}>
      <FlatList
        data={facts}
        keyExtractor={item => item.id}
        renderItem={({ item }) => <GameCard item={item} />}
      />
    </PaperProvider>
  );
}
