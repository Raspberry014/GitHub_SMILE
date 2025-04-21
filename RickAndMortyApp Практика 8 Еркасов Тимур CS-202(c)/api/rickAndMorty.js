const BASE_URL = 'https://rickandmortyapi.com/api';

export async function fetchCharacters(name = '') {
  try {
    const response = await fetch(`${BASE_URL}/character/?name=${name}`);
    const json = await response.json();
    return json.results || [];
  } catch (error) {
    throw new Error('Ошибка загрузки персонажей');
  }
}

export async function fetchCharacterById(id) {
  try {
    const response = await fetch(`${BASE_URL}/character/${id}`);
    const json = await response.json();
    return json;
  } catch (error) {
    throw new Error('Ошибка загрузки персонажа');
  }
}

export async function fetchLocations() {
    try {
      const response = await fetch('https://rickandmortyapi.com/api/location');
      const json = await response.json();
      return json.results || [];
    } catch (error) {
      throw new Error('Ошибка загрузки локаций');
    }
  }
  
  export async function fetchLocationById(id) {
    try {
      const response = await fetch(`https://rickandmortyapi.com/api/location/${id}`);
      const json = await response.json();
      return json;
    } catch (error) {
      throw new Error('Ошибка загрузки локации');
    }
  }
  
  export async function fetchEpisodes() {
    try {
      const response = await fetch('https://rickandmortyapi.com/api/episode');
      const json = await response.json();
      return json.results || [];
    } catch (error) {
      throw new Error('Ошибка загрузки эпизодов');
    }
  }
  
  export async function fetchEpisodeById(id) {
    try {
      const response = await fetch(`https://rickandmortyapi.com/api/episode/${id}`);
      const json = await response.json();
      return json;
    } catch (error) {
      throw new Error('Ошибка загрузки эпизода');
    }
  }
  