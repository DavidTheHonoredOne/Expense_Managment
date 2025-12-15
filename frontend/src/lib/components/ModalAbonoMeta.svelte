<script>
  import { notifications } from "../stores/notifications";
  export let isOpen = false;
  export let onClose;
  export let onSave;
  /** @type {any} */
  export let meta = null;
  export let cuentas = []; // New prop for accounts

  let monto = null;
  let cuenta_id = 0; // New state for selected account
  let isSubmitting = false;

  $: if (!isOpen) {
    monto = "";
    cuenta_id = 0; // Reset account selection
    isSubmitting = false;
  }

  const handleSubmit = async () => {
    if (!meta) {
        notifications.addNotification("Error: No se ha seleccionado una meta.", "error");
        return;
    }
    if (!monto || monto.trim() === "") {
        notifications.addNotification("Por favor ingrese un monto válido", "error");
        return;
    }
    if (!cuenta_id || cuenta_id === 0) {
        notifications.addNotification("Por favor seleccione una cuenta de origen.", "error");
        return;
    }
    isSubmitting = true;
    try {
      // CORRECCIÓN: usar parseInt y manejar correctamente los puntos separadores de miles
      const montoNumerico = parseInt(monto.replace(/\./g, '').replace(/[^0-9]/g, ''), 10);
      if (isNaN(montoNumerico) || montoNumerico <= 0) {
        notifications.addNotification("Por favor ingrese un monto válido", "error");
        isSubmitting = false;
        return;
      }
      await onSave(meta.meta_id, { monto: montoNumerico, cuenta_id: Number(cuenta_id) });
    } catch (e) {
      isSubmitting = false;
    }
  };
</script>

{#if isOpen}
  <div class="fixed inset-0 bg-black/80 z-50 flex items-center justify-center backdrop-blur-sm animate-fade-in">
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-2xl border border-gray-200 dark:border-gray-700 w-full max-w-sm p-6 relative">
      <button on:click={onClose} class="absolute top-4 right-4 text-gray-400 hover:text-gray-900 dark:hover:text-white" aria-label="Cerrar">
        <i class="fas fa-times text-xl"></i>
      </button>
      <h3 class="text-xl font-bold mb-4 text-gray-900 dark:text-white border-b border-gray-200 dark:border-gray-700 pb-2">Abonar a Meta</h3>
      
      {#if meta}
        <p class="text-sm text-gray-500 dark:text-gray-400 mb-4">Abonando a: <span class="font-bold text-gray-800 dark:text-gray-200">{meta.nombre_meta}</span></p>
      {/if}

      <form on:submit|preventDefault={handleSubmit} class="space-y-4">
        <div>
          <label for="abono-monto" class="block text-sm text-gray-600 dark:text-gray-400 mb-1">Monto ($)</label>
          <input 
            id="abono-monto"
            type="text" 
            bind:value={monto} 
            on:input={(e) => {
                const input = /** @type {HTMLInputElement} */ (e.target);
                let value = input.value.replace(/[^0-9]/g, '');
                if (value) {
                    monto = new Intl.NumberFormat('es-CO').format(parseInt(value));
                } else {
                    monto = '';
                }
            }}
            class="w-full bg-gray-50 dark:bg-gray-900 border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2 text-gray-900 dark:text-white focus:border-emerald-500 focus:outline-none text-lg font-bold" 
            placeholder="0"
            required
          >
        </div>

        <div>
            <label for="abono-cuenta" class="block text-sm text-gray-600 dark:text-gray-400 mb-1">Cuenta de Origen</label>
            <select 
                id="abono-cuenta"
                bind:value={cuenta_id}
                class="w-full bg-gray-50 dark:bg-gray-900 border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-gray-900 dark:text-white focus:border-emerald-500"
                required
            >
                <option value={0} disabled>Seleccionar cuenta...</option>
                {#each cuentas as c}
                    <option value={c.cuenta_id}>{c.nombre_cuenta} ({c.saldo_actual})</option>
                {/each}
            </select>
        </div>

        <button 
            type="submit" 
            disabled={isSubmitting}
            class="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-bold py-3 rounded-lg mt-4 shadow-lg shadow-emerald-500/20 transition-all hover:scale-[1.02] disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
        >
            {#if isSubmitting}
                <i class="fas fa-spinner fa-spin mr-2"></i>
                Procesando...
            {:else}
                Confirmar Abono
            {/if}
        </button>
      </form>
    </div>
  </div>
{/if}
