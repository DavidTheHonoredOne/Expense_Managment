<script>
  import { notifications } from "../stores/notifications";
  export let isOpen = false;
  export let onClose;
  export let onSave;
  /** @type {any} */
  export let editingMeta = null;

  let nombre_meta = "";
  let monto_objetivo = "";
  let displayMontoObjetivo = "";
  let fecha_fin = new Date().toISOString().split("T")[0];
  let isSubmitting = false; // Prevenir múltiples clicks

  // FIX(UX): Implement input masking for COP currency (Sprint 4)
  function formatCurrency(value) {
    if (!value && value !== 0) return "";
    const numericValue = value.toString().replace(/\D/g, '');
    if (numericValue === "") return "";

    // Formatear SIEMPRE con puntos de miles, incluso para valores pequeños (ej: 1000 -> 1.000)
    const formatted = new Intl.NumberFormat('es-ES', {
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
      useGrouping: true // Fuerza los separadores de miles
    }).format(parseInt(numericValue) || 0);

    return formatted;
  }

  $: if (isOpen) {
    if (editingMeta) {
        nombre_meta = editingMeta.nombre_meta;
        monto_objetivo = editingMeta.monto_objetivo;
        displayMontoObjetivo = formatCurrency(editingMeta.monto_objetivo?.toString() || "");
        fecha_fin = new Date(editingMeta.fecha_fin).toISOString().split("T")[0];
    } else {
        nombre_meta = "";
        monto_objetivo = "";
        displayMontoObjetivo = "";
        fecha_fin = new Date().toISOString().split("T")[0];
    }
  } else {
      isSubmitting = false; // Resetear siempre al cerrar
  }

  const handleSubmit = async () => {
    if (!nombre_meta || !monto_objetivo || !fecha_fin) {
        notifications.addNotification("Por favor complete los campos obligatorios", "error");
        return;
    }

    isSubmitting = true;

    const payload = {
        nombre_meta,
        monto_objetivo: parseFloat(monto_objetivo),
        fecha_fin
    };
    
    try {
        await onSave(payload, editingMeta ? editingMeta.meta_id : null);
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
      <h3 class="text-xl font-bold mb-6 text-gray-900 dark:text-white border-b border-gray-200 dark:border-gray-700 pb-2">{editingMeta ? "Editar Meta" : "Nueva Meta de Ahorro"}</h3>
      <form on:submit|preventDefault={handleSubmit} class="space-y-4">
        <div>
          <label for="nombre_meta" class="block text-sm text-gray-600 dark:text-gray-400 mb-1">Nombre de la Meta</label>
          <input 
            id="nombre_meta"
            type="text" 
            bind:value={nombre_meta} 
            class="w-full bg-gray-50 dark:bg-gray-900 border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2 text-gray-900 dark:text-white focus:border-blue-500 focus:outline-none" 
            placeholder="Ej: Viaje a Japón"
            required
          >
        </div>
        
        <div>
          <label for="monto_objetivo" class="block text-sm text-gray-600 dark:text-gray-400 mb-1">Monto Objetivo ($)</label>
          <!-- NOTE: Separating visual value from raw value to prevent formatting bugs -->
          <input
            id="monto_objetivo"
            type="text"
            bind:value={displayMontoObjetivo}
            on:input={(e) => {
              const input = /** @type {HTMLInputElement} */ (e.target);
              const rawValue = input.value.replace(/\D/g, '');
              monto_objetivo = rawValue ? rawValue : "";
              displayMontoObjetivo = formatCurrency(rawValue);
            }}
            on:keydown={(e) => { if (e.keyCode === 69 || e.keyCode === 189) e.preventDefault(); }}
            class="w-full bg-gray-50 dark:bg-gray-900 border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2 text-gray-900 dark:text-white focus:border-blue-500 focus:outline-none text-lg font-bold"
            placeholder="0.00"
            required
          >
        </div>

        <div>
          <label for="fecha_fin" class="block text-sm text-gray-600 dark:text-gray-400 mb-1">Fecha Límite</label>
          <input 
            id="fecha_fin"
            type="date" 
            bind:value={fecha_fin} 
            class="w-full bg-gray-50 dark:bg-gray-900 border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2 text-gray-900 dark:text-white focus:border-blue-500 text-sm"
            required
          >
        </div>

        <button
            type="submit"
            disabled={isSubmitting}
            class="w-full bg-blue-600 hover:bg-blue-500 text-white font-bold py-3 rounded-lg mt-4 shadow-lg shadow-blue-500/20 transition-all hover:scale-[1.02] disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
        >
            {#if isSubmitting}
                <i class="fas fa-spinner fa-spin mr-2"></i>
                Guardando...
            {:else}
                {editingMeta ? "Guardar Cambios" : "Crear Meta"}
            {/if}
        </button>
      </form>
    </div>
  </div>
{/if}
