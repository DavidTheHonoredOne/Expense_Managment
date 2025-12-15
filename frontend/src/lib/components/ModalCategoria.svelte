<script>
  import { notifications } from "../stores/notifications";
  export let isOpen = false;
  export let onClose;
  export let onSave;

  let nombre_categoria = "";
  let tipo = "Gasto";
  let isSubmitting = false;

  $: if (!isOpen) {
    nombre_categoria = "";
    tipo = "Gasto";
  }

  const handleSubmit = async () => {
    if (!nombre_categoria) {
        notifications.addNotification("Nombre requerido", "error");
        return;
    }
    isSubmitting = true;
    try {
      await onSave({ nombre_categoria, tipo });
    } catch (e) {
      isSubmitting = false;
    }
  };
</script>

{#if isOpen}
  <div class="fixed inset-0 bg-black/80 z-50 flex items-center justify-center backdrop-blur-sm animate-fade-in">
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-2xl border border-gray-200 dark:border-gray-700 w-full max-w-md p-6 relative">
      <button on:click={onClose} class="absolute top-4 right-4 text-gray-400 hover:text-gray-900 dark:hover:text-white" aria-label="Cerrar">
        <i class="fas fa-times text-xl"></i>
      </button>
      <h3 class="text-xl font-bold mb-6 text-gray-900 dark:text-white border-b border-gray-200 dark:border-gray-700 pb-2">Nueva Categoría</h3>
      <form on:submit|preventDefault={handleSubmit} class="space-y-4">
        <div>
          <label for="cat-name" class="block text-sm text-gray-600 dark:text-gray-400 mb-1">Nombre</label>
          <input 
            id="cat-name"
            type="text" 
            bind:value={nombre_categoria} 
            class="w-full bg-gray-50 dark:bg-gray-900 border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2 text-gray-900 dark:text-white focus:border-emerald-500 focus:outline-none" 
            placeholder="Ej: Comida"
            required
          >
        </div>
        
        <div>
          <span class="block text-sm text-gray-600 dark:text-gray-400 mb-2">Tipo</span>
          <div class="grid grid-cols-2 gap-2 p-1 bg-gray-100 dark:bg-gray-900 rounded-lg">
            <button 
                type="button" 
                class="py-2 rounded-md font-medium text-sm transition {tipo === "Gasto" ? "bg-rose-500 text-white shadow" : "text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"}"
                on:click={() => tipo = "Gasto"}
            >
                Gasto
            </button>
            <button 
                type="button" 
                class="py-2 rounded-md font-medium text-sm transition {tipo === "Ingreso" ? "bg-teal-500 text-white shadow" : "text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"}"
                on:click={() => tipo = "Ingreso"}
            >
                Ingreso
            </button>
          </div>
        </div>

        <button 
            type="submit" 
            disabled={isSubmitting}
            class="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-bold py-3 rounded-lg mt-4 shadow-lg shadow-emerald-500/20 transition-all hover:scale-[1.02] disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
        >
            {#if isSubmitting}
                <i class="fas fa-spinner fa-spin mr-2"></i>
                Guardando...
            {:else}
                Crear Categoría
            {/if}
        </button>
      </form>
    </div>
  </div>
{/if}
