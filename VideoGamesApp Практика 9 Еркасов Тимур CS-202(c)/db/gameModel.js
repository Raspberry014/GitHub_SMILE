import db from './database';

export const getGames = () => {
  return new Promise((resolve, reject) => {
    db.transaction(tx => {
      tx.executeSql(
        `SELECT games.*, genres.name as genreName FROM games LEFT JOIN genres ON games.genreId = genres.id`,
        [],
        (_, { rows }) => resolve(rows._array),
        (_, error) => reject(error)
      );
    });
  });
};

export const insertGame = (game) => {
  const { title, description, releaseYear, platform, imageUri, genreId } = game;
  return new Promise((resolve, reject) => {
    db.transaction(tx => {
      tx.executeSql(
        `INSERT INTO games (title, description, releaseYear, platform, imageUri, genreId) VALUES (?, ?, ?, ?, ?, ?)`,
        [title, description, releaseYear, platform, imageUri, genreId],
        (_, result) => resolve(result),
        (_, error) => reject(error)
      );
    });
  });
};

export const deleteGame = (id) => {
  return new Promise((resolve, reject) => {
    db.transaction(tx => {
      tx.executeSql(
        `DELETE FROM games WHERE id = ?`,
        [id],
        (_, result) => resolve(result),
        (_, error) => reject(error)
      );
    });
  });
};
