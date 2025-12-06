<script>
  export let cuentas = [];
  export let categorias = [];
  export let onDeleteCuenta;
  export let onDeleteCategoria;
  export let onOpenModalCuenta;
  export let onOpenModalCategoria;
</script>

<div class="space-y-8 animate-fade-in">
  <!-- Cuentas Section -->
  <div class="bg-white dark:bg-gray-800 p-6 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm transition-colors duration-300">
    <div class="flex justify-between items-center mb-6">
      <h3 class="text-xl font-bold text-gray-900 dark:text-white">Gestionar Cuentas</h3>
      <button on:click={onOpenModalCuenta} class="bg-emerald-600 hover:bg-emerald-500 text-white px-4 py-2 rounded-lg font-medium text-sm transition shadow-lg shadow-emerald-500/20">
        <i class="fas fa-plus mr-2"></i> Nueva Cuenta
      </button>
    </div>
    
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {#each cuentas as cuenta}
        <div class="bg-gray-50 dark:bg-gray-900 p-4 rounded-lg border border-gray-200 dark:border-gray-700 flex justify-between items-center group hover:border-emerald-500 dark:hover:border-emerald-500 transition">
          <div>
            <p class="font-bold text-gray-900 dark:text-white">{cuenta.nombre_cuenta}</p>
            <p class="text-xs text-gray-500 dark:text-gray-400">{cuenta.tipo || 'General'}</p>
          </div>
          <button on:click={() => onDeleteCuenta(cuenta.cuenta_id)} class="text-rose-500 dark:text-rose-400 hover:text-rose-700 dark:hover:text-rose-300 p-2" aria-label="Eliminar Cuenta" title="Eliminar">
            <i class="fas fa-trash"></i>
          </button>
        </div>
      {:else}
        <p class="text-gray-500 dark:text-gray-400 col-span-full text-center py-4">No hay cuentas registradas.</p>
      {/each}
    </div>
  </div>

  <!-- Categorias Section -->
  <div class="bg-white dark:bg-gray-800 p-6 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm transition-colors duration-300">
    <div class="flex justify-between items-center mb-6">
      <h3 class="text-xl font-bold text-gray-900 dark:text-white">Gestionar Categorías</h3>
      <button on:click={onOpenModalCategoria} class="bg-teal-600 hover:bg-teal-500 text-white px-4 py-2 rounded-lg font-medium text-sm transition shadow-lg shadow-teal-500/20">
        <i class="fas fa-plus mr-2"></i> Nueva Categoría
      </button>
    </div>
    
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {#each categorias as cat}
        <div class="bg-gray-50 dark:bg-gray-900 p-4 rounded-lg border border-gray-200 dark:border-gray-700 flex justify-between items-center group hover:border-teal-500 dark:hover:border-teal-500 transition">
          <div class="flex items-center gap-2">
            <span class="w-2 h-2 rounded-full {cat.tipo === 'Ingreso' ? 'bg-teal-500' : 'bg-rose-500'}"></span>
            <p class="font-medium text-gray-900 dark:text-white">{cat.nombre_categoria}</p>
          </div>
          <button on:click={() => onDeleteCategoria(cat.categoria_id)} class="text-rose-500 dark:text-rose-400 hover:text-rose-700 dark:hover:text-rose-300 p-2" aria-label="Eliminar Categoría" title="Eliminar">
            <i class="fas fa-trash"></i>
          </button>
        </div>
      {:else}
        <p class="text-gray-500 dark:text-gray-400 col-span-full text-center py-4">No hay categorías registradas.</p>
      {/each}
    </div>
  </div>
</div>
