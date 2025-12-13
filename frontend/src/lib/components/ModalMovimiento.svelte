<script>
  import { notifications } from "../stores/notifications";
  export let isOpen = false;
  export let onClose;
  export let onSave;
  export let cuentas = [];
  export let categorias = [];
  /** @type {any} */
  export let editingTransaction = null;

  $: isMetaTransaction = editingTransaction && 
       (editingTransaction.descripcion?.toLowerCase().includes('abono a meta') || 
        editingTransaction.nombre_categoria?.toLowerCase().includes('meta'));

  let form = {
    tipo: "gasto",
    monto: null,
    cuenta_id: 0,
    categoria_id: 0,
    fecha: new Date().toISOString().split("T")[0],
    descripcion: ""
  };

  $: if (isOpen) {
    if (editingTransaction) {
        form = {
            tipo: editingTransaction.tipo,
            monto: editingTransaction.monto,
            cuenta_id: editingTransaction.cuenta_id,
            categoria_id: editingTransaction.categoria_id,
            fecha: editingTransaction.fecha ? new Date(editingTransaction.fecha).toISOString().split("T")[0] : new Date().toISOString().split("T")[0],
            descripcion: editingTransaction.descripcion
        };
    } else {
        // Keep current state if user is typing, or reset if it was a fresh open
    }
  }

  $: if (!isOpen) {
    // Reset form when closed
    form = {
        tipo: "gasto",
        monto: null,
        cuenta_id: 0,
        categoria_id: 0,
        fecha: new Date().toISOString().split("T")[0],
        descripcion: ""
    };
  }

  const handleSubmit = () => {
    if (!form.cuenta_id || !form.categoria_id || !form.monto) {
        notifications.addNotification("Por favor complete los campos obligatorios", "error");
        return;
    }

    const payload = {
        tipo: form.tipo,
        monto: Number(form.monto),
        cuenta_id: Number(form.cuenta_id),
        categoria_id: Number(form.categoria_id),
        fecha: form.fecha, 
        descripcion: form.descripcion
    };
    
    onSave(payload);
  };
</script>

{#if isOpen}
  <div class="fixed inset-0 bg-black/80 z-50 flex items-center justify-center backdrop-blur-sm animate-fade-in">
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-2xl border border-gray-200 dark:border-gray-700 w-full max-w-md p-6 relative">
      <button on:click={onClose} class="absolute top-4 right-4 text-gray-400 hover:text-gray-900 dark:hover:text-white" aria-label="Cerrar">
        <i class="fas fa-times text-xl"></i>
      </button>
      <h3 class="text-xl font-bold mb-6 text-gray-900 dark:text-white border-b border-gray-200 dark:border-gray-700 pb-2">{editingTransaction ? "Editar Movimiento" : "Registrar Movimiento"}</h3>
      <form on:submit|preventDefault={handleSubmit} class="space-y-4">
        <div>
          <span class="block text-sm text-gray-600 dark:text-gray-400 mb-2">Tipo de Movimiento</span>
          <div class="grid grid-cols-2 gap-2 p-1 bg-gray-100 dark:bg-gray-900 rounded-lg">
            <button 
                type="button" 
                class="py-2 rounded-md font-medium text-sm transition {form.tipo === "gasto" ? "bg-rose-500 text-white shadow" : "text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"}"
                on:click={() => form.tipo = "gasto"}
                disabled={isMetaTransaction}
            >
                Gasto
            </button>
            <button 
                type="button" 
                class="py-2 rounded-md font-medium text-sm transition {form.tipo === "ingreso" ? "bg-teal-500 text-white shadow" : "text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"}"
                on:click={() => form.tipo = "ingreso"}
                disabled={isMetaTransaction}
            >
                Ingreso
            </button>
          </div>
        </div>
        
        <div>
          <label for="monto" class="block text-sm text-gray-600 dark:text-gray-400 mb-1">Monto ($)</label>
          <input 
            id="monto"
            type="number" 
            min="0" 
            step="0.01"
            bind:value={form.monto} 
            on:input={(e) => { const input = /** @type {HTMLInputElement} */ (e.target); form.monto = Math.abs(parseFloat(input.value)); }}
            on:keydown={(e) => { if (e.keyCode === 69 || e.keyCode === 189) e.preventDefault(); }}
            class="w-full bg-gray-50 dark:bg-gray-900 border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2 text-gray-900 dark:text-white focus:border-emerald-500 focus:outline-none text-lg font-bold" 
            placeholder="0.00"
            required
          >
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label for="cuenta" class="block text-sm text-gray-600 dark:text-gray-400 mb-1">Cuenta <span class="text-rose-500">*</span></label>
            <select 
                id="cuenta"
                bind:value={form.cuenta_id} 
                class="w-full bg-gray-50 dark:bg-gray-900 border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-gray-900 dark:text-white focus:border-emerald-500"
                required
            >
              <option value={0} disabled>Seleccionar...</option>
              {#each cuentas as c}
                <option value={c.cuenta_id}>{c.nombre_cuenta}</option>
              {/each}
            </select>
            
          </div>
          <div>
            <label for="categoria" class="block text-sm text-gray-600 dark:text-gray-400 mb-1">Categoría <span class="text-rose-500">*</span></label>
            <select 
                id="categoria"
                bind:value={form.categoria_id} 
                class="w-full bg-gray-50 dark:bg-gray-900 border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-gray-900 dark:text-white focus:border-emerald-500"
                required
            >
              <option value={0} disabled>Seleccionar...</option>
              {#each categorias as cat}
                <option value={cat.categoria_id}>{cat.nombre_categoria}</option>
              {/each}
            </select>
            
          </div>
        </div>

        <div>
          <label for="fecha" class="block text-sm text-gray-600 dark:text-gray-400 mb-1">Fecha</label>
          <input 
            id="fecha"
            type="date" 
            bind:value={form.fecha} 
            class="w-full bg-gray-50 dark:bg-gray-900 border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2 text-gray-900 dark:text-white focus:border-emerald-500 text-sm"
          >
        </div>

        <div>
          <label for="descripcion" class="block text-sm text-gray-600 dark:text-gray-400 mb-1">Descripción</label>
          <input 
            id="descripcion"
            type="text" 
            bind:value={form.descripcion} 
            class="w-full bg-gray-50 dark:bg-gray-900 border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2 text-gray-900 dark:text-white focus:border-emerald-500 text-sm" 
            placeholder="Ej: Almuerzo con el equipo"
          >
        </div>

        <button 
            type="submit" 
            class="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-bold py-3 rounded-lg mt-4 shadow-lg shadow-emerald-500/20"
        >
            {editingTransaction ? "Actualizar Transacción" : "Guardar Transacción"}
        </button>
      </form>
    </div>
  </div>
{/if}
