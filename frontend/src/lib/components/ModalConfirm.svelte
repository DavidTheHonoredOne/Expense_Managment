<script>
  import { fade, scale } from 'svelte/transition';
  
  export let isOpen = false;
  export let title = 'Confirmar';
  export let message = '¿Estás seguro?';
  export let onConfirm;
  export let onCancel;
</script>

{#if isOpen}
  <div class="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm" transition:fade>
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-2xl p-6 w-full max-w-sm border border-gray-200 dark:border-gray-700" in:scale={{start: 0.95}}>
      <h3 class="text-xl font-bold text-gray-900 dark:text-white mb-2">{title}</h3>
      <p class="text-gray-600 dark:text-gray-300 mb-6">{message}</p>
      <div class="flex justify-end gap-3">
        <button on:click={onCancel} class="px-4 py-2 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-200 rounded-lg font-medium transition-colors">
          Cancelar
        </button>
        <button on:click={onConfirm} class="px-4 py-2 bg-rose-600 hover:bg-rose-700 text-white rounded-lg font-medium shadow-md transition-colors">
          Confirmar
        </button>
      </div>
    </div>
  </div>
{/if}
