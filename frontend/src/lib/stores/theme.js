import { writable } from 'svelte/store';

function createThemeStore() {
  const isBrowser = typeof window !== 'undefined';

  // Determine initial theme
  let savedTheme = isBrowser ? localStorage.getItem('theme') : 'light';
  if (!savedTheme) {
    const systemPrefersDark = isBrowser ? window.matchMedia('(prefers-color-scheme: dark)').matches : false;
    savedTheme = systemPrefersDark ? 'dark' : 'light';
  }

  const { subscribe, set, update } = writable(savedTheme);

  return {
    subscribe,
    toggle: () => update(currentTheme => {
      const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
      if (isBrowser) {
        localStorage.setItem('theme', newTheme);
      }
      return newTheme;
    }),
    init: () => {
      if (isBrowser) set(localStorage.getItem('theme') || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'));
    }
  };
}

export const theme = createThemeStore();
