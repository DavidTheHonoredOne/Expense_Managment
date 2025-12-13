<script>
  import { fly } from 'svelte/transition';
  import { notifications } from '../stores/notifications';

  const typeClasses = {
    info: 'bg-blue-500',
    success: 'bg-green-500',
    error: 'bg-red-500'
  };
</script>

<div class="fixed bottom-4 right-4 z-50 w-full max-w-sm pointer-events-none">
  {#each $notifications as notification (notification.id)}
    <div
      in:fly={{ y: 20, duration: 300 }}
      out:fly={{ y: 20, duration: 200, delay: 0 }}
      class="mt-2 p-4 rounded-lg shadow-lg text-white font-medium flex items-center gap-3 {typeClasses[notification.type]} transform translate-x-0"
    >
      <i class="fas {notification.type === 'success' ? 'fa-check-circle' : notification.type === 'error' ? 'fa-times-circle' : 'fa-info-circle'} text-xl"></i>
      <p>{notification.message}</p>
    </div>
  {/each}
</div>
