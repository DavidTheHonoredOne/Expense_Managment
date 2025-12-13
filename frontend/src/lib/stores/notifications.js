import { writable } from 'svelte/store';

function createNotificationStore() {
  const { subscribe, update } = writable([]);
  let id = 0;

  function addNotification(message, type = 'info', timeout = 3000) {
    const newNotification = { id: id++, message, type };
    update(notifications => [...notifications, newNotification]);

    setTimeout(() => {
      removeNotification(newNotification.id);
    }, timeout);
  }

  function removeNotification(id) {
    update(notifications => notifications.filter(n => n.id !== id));
  }

  return { subscribe, addNotification, removeNotification };
}

export const notifications = createNotificationStore();
