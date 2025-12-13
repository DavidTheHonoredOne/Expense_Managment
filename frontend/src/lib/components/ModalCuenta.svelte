<script>
  import { notifications } from "../stores/notifications";
  export let isOpen = false;
  export let onClose;
  export let onSave;

  let nombre_cuenta = "";
  let saldo_inicial = "";
  let tipo = "Banco";

  $: if (!isOpen) {
    nombre_cuenta = "";
    saldo_inicial = "";
    tipo = "Banco";
  }

  const handleSubmit = () => {
    if (!nombre_cuenta) {
        notifications.addNotification("Nombre requerido", "error");
        return;
    }
    onSave({ 
        nombre_cuenta, 
        saldo_inicial: parseFloat(saldo_inicial) || 0,
        tipo
    });
  };
</script>

{#if isOpen}
  <div class="fixed inset-0 bg-black/80 z-50 flex items-center justify-center backdrop-blur-sm animate-fade-in">
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-2xl border border-gray-200 dark:border-gray-700 w-full max-w-md p-6 relative">
      <button on:click={onClose} class="absolute top-4 right-4 text-gray-400 hover:text-gray-900 dark:hover:text-white" aria-label="Cerrar">
        <i class="fas fa-times text-xl"></i>
      </button>
      <h3 class="text-xl font-bold mb-6 text-gray-900 dark:text-white border-b border-gray-200 dark:border-gray-700 pb-2">Nueva Cuenta</h3>
      <form on:submit|preventDefault={handleSubmit} class="space-y-4">
        <div>
          <label for="acc-name" class="block text-sm text-gray-600 dark:text-gray-400 mb-1">Nombre</label>
          <input 
            id="acc-name"
            type="text" 
            bind:value={nombre_cuenta} 
            class="w-full bg-gray-50 dark:bg-gray-900 border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2 text-gray-900 dark:text-white focus:border-emerald-500 focus:outline-none" 
            placeholder="Ej: Bancolombia"
            required
          >
        </div>
        
        <div>
          <label for="acc-balance" class="block text-sm text-gray-600 dark:text-gray-400 mb-1">Saldo Inicial ($)</label>
          <input 
            id="acc-balance"
            type="number" 
            min="0" 
            step="0.01"
            bind:value={saldo_inicial} 
            on:input={(e) => { const input = /** @type {HTMLInputElement} */ (e.target); saldo_inicial = Math.abs(parseFloat(input.value)).toString(); }}
            on:keydown={(e) => { if (e.keyCode === 69 || e.keyCode === 189) e.preventDefault(); }}
            class="w-full bg-gray-50 dark:bg-gray-900 border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2 text-gray-900 dark:text-white focus:border-emerald-500 focus:outline-none" 
            placeholder="0.00"
          >
        </div>

        <div>
          <label for="acc-type" class="block text-sm text-gray-600 dark:text-gray-400 mb-1">Tipo</label>
          <select 
            id="acc-type"
            bind:value={tipo}
            class="w-full bg-gray-50 dark:bg-gray-900 border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2 text-gray-900 dark:text-white focus:border-emerald-500 focus:outline-none"
          >
            <option value="Banco">Banco</option>
            <option value="Efectivo">Efectivo</option>
            <option value="Digital">Digital</option>
          </select>
        </div>

        <button 
            type="submit" 
            class="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-bold py-3 rounded-lg mt-4 shadow-lg shadow-emerald-500/20 transition-all hover:scale-[1.02]"
        >
            Crear Cuenta
        </button>
      </form>
    </div>
  </div>
{/if}
