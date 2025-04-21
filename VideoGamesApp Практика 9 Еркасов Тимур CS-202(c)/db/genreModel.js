import db from './database';

export const getGenres = () => {
  return new Promise((resolve, reject) => {
    db.transaction(tx => {
      tx.executeSql(
        `SELECT * FROM genres`,
        [],
        (_, { rows }) => resolve(rows._array),
        (_, error) => reject(error)
      );
    });
  });
};

export const insertGenre = (name) => {
  return new Promise((resolve, reject) => {
    db.transaction(tx => {
      tx.executeSql(
        `INSERT INTO genres (name) VALUES (?)`,
        [name],
        (_, result) => resolve(result),
        (_, error) => reject(error)
      );
    });
  });
};

export const deleteGenre = (id) => {
  return new Promise((resolve, reject) => {
    db.transaction(tx => {
      tx.executeSql(
        `DELETE FROM genres WHERE id = ?`,
        [id],
        (_, result) => resolve(result),
        (_, error) => reject(error)
      );
    });
  });
};
