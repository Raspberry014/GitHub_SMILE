import * as SQLite from 'expo-sqlite';

const db = SQLite.openDatabase('games.db');

export const initDb = () => {
  return new Promise((resolve, reject) => {
    db.transaction(tx => {
      // Таблица жанров
      tx.executeSql(
        `CREATE TABLE IF NOT EXISTS genres (
          id INTEGER PRIMARY KEY NOT NULL,
          name TEXT NOT NULL
        );`
      );

      // Таблица видеоигр
      tx.executeSql(
        `CREATE TABLE IF NOT EXISTS games (
          id INTEGER PRIMARY KEY NOT NULL,
          title TEXT NOT NULL,
          description TEXT,
          releaseYear INTEGER,
          platform TEXT,
          imageUri TEXT,
          genreId INTEGER,
          FOREIGN KEY (genreId) REFERENCES genres(id)
        );`,
        [],
        () => resolve(),
        (_, error) => reject(error)
      );
    });
  });
};

export default db;
