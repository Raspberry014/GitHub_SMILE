import * as FileSystem from 'expo-file-system';
import * as Sharing from 'expo-sharing';
import { getGames } from '../db/gameModel';

export const exportGamesToJson = async () => {
  try {
    const games = await getGames();
    const json = JSON.stringify(games, null, 2);

    const fileUri = FileSystem.documentDirectory + 'games_export.json';
    await FileSystem.writeAsStringAsync(fileUri, json, { encoding: FileSystem.EncodingType.UTF8 });

    if (await Sharing.isAvailableAsync()) {
      await Sharing.shareAsync(fileUri);
    } else {
      alert('Sharing API недоступен на этом устройстве');
    }
  } catch (error) {
    console.log('Ошибка экспорта:', error);
  }
};
