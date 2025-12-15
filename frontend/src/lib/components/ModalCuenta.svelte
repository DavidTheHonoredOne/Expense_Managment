<script>
  import { notifications } from "../stores/notifications";
  export let isOpen = false;
  export let onClose;
  export let onSave;

  let nombre_cuenta = "";
  let saldo_inicial = "";
  let tipo = "Banco";
  let isSubmitting = false;

  // Límites de validación
  const MAX_SALDO = 999999999; // 999 millones COP
  const MIN_SALDO = 1000; // 1000 COP

  $: if (!isOpen) {
    nombre_cuenta = "";
    saldo_inicial = "";
    tipo = "Banco";
    isSubmitting = false;
  }

  function validateSaldo(saldo) {
    if (!saldo) return { valid: false, message: 'El saldo es requerido' };
    
    const numericSaldo = parseFloat(saldo.toString().replace(/[^0-9]/g, ''));
    
    if (isNaN(numericSaldo)) {
      return { valid: false, message: 'El saldo debe ser un número válido' };
    }
    
    if (numericSaldo < MIN_SALDO) {
      return { valid: false, message: `El saldo mínimo es $${MIN_SALDO.toLocaleString('es-CO')} COP` };
    }
    
    if (numericSaldo > MAX_SALDO) {
      return { valid: false, message: `El saldo máximo es $${MAX_SALDO.toLocaleString('es-CO')} COP` };
    }
    
    return { valid: true };
  }

  const handleSubmit = async () => {
    if (!nombre_cuenta) {
        notifications.addNotification("Nombre requerido", "error");
        return;
    }
    
    const validation = validateSaldo(saldo_inicial);
    if (!validation.valid) {
        notifications.addNotification(validation.message, "error");
        return;
    }
    
    isSubmitting = true;
    try {
      const saldoNumerico = parseFloat(saldo_inicial.replace(/[^0-9]/g, ''));
      await onSave({ 
          nombre_cuenta, 
          saldo_inicial: saldoNumerico,
          tipo
      });
    } catch (e) {
      isSubmitting = false;
    }
  };

  // Formatear entrada de saldo en tiempo real
  function handleSaldoInput(event) {
    const input = /** @type {HTMLInputElement} */ (event.target);
    let value = input.value.replace(/[^0-9]/g, '');
    
    if (value) {
      const numericValue = parseInt(value);
      // Validar que no exceda el máximo
      if (numericValue <= MAX_SALDO) {
        saldo_inicial = new Intl.NumberFormat('es-CO').format(numericValue);
      }
    } else {
      saldo_inicial = '';
    }
  }
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
          <label for="acc-balance" class="block text-sm text-gray-600 dark:text-gray-400 mb-1">
            Saldo Inicial ($)
            <span class="text-xs text-gray-500 block">
              (Min: ${MIN_SALDO.toLocaleString('es-CO')} - Max: ${MAX_SALDO.toLocaleString('es-CO')})
            </span>
          </label>
          <input 
            id="acc-balance"
            type="text" 
            bind:value={saldo_inicial} 
            on:input={handleSaldoInput}
            class="w-full bg-gray-50 dark:bg-gray-900 border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2 text-gray-900 dark:text-white focus:border-emerald-500 focus:outline-none" 
            placeholder="0"
            required
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
            disabled={isSubmitting}
            class="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-bold py-3 rounded-lg mt-4 shadow-lg shadow-emerald-500/20 transition-all hover:scale-[1.02] disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
        >
            {#if isSubmitting}
                <i class="fas fa-spinner fa-spin mr-2"></i>
                Guardando...
            {:else}
                Crear Cuenta
            {/if}
        </button>
      </form>
    </div>
  </div>
{/if}
