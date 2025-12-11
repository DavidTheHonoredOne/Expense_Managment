import { writable } from 'svelte/store';

function createThemeStore() {
    const isBrowser = typeof window !== 'undefined';
    // Check localStorage or system preference
    const storedTheme = isBrowser ? localStorage.getItem('theme') : null;
    const systemPrefersDark = isBrowser ? window.matchMedia('(prefers-color-scheme: dark)').matches : false;
    
    const initialTheme = storedTheme === 'dark' || (!storedTheme && systemPrefersDark);

    const { subscribe, set, update } = writable(initialTheme);

    return {
        subscribe,
        toggle: () => update(isDark => {
            const newTheme = !isDark;
            if (isBrowser) {
                if (newTheme) {
                    document.documentElement.classList.add('dark');
                    localStorage.setItem('theme', 'dark');
                } else {
                    document.documentElement.classList.remove('dark');
                    localStorage.setItem('theme', 'light');
                }
            }
            return newTheme;
        }),
        init: () => {
            if (isBrowser) {
                if (initialTheme) {
                    document.documentElement.classList.add('dark');
                } else {
                    document.documentElement.classList.remove('dark');
                }
            }
        }
    };
}

export const theme = createThemeStore();
