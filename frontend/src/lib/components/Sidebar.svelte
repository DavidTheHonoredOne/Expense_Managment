<script>
  export let activeTab = 'dashboard';
  export let onTabChange;
  export let onLogout;
</script>

<aside class="w-64 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col h-full transition-colors duration-300">
  <div class="p-6">
    <h1 class="text-2xl font-bold text-emerald-600 dark:text-emerald-500"><i class="fas fa-wallet mr-2"></i>EMS App</h1>
  </div>
  <nav class="flex-1 px-4 space-y-2">
    <button 
      on:click={() => onTabChange('dashboard')} 
      class="w-full flex items-center px-4 py-3 rounded-lg transition {activeTab === 'dashboard' ? 'bg-emerald-600 text-white shadow-md shadow-emerald-500/30' : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 hover:text-emerald-600 dark:hover:text-emerald-400'}"
    >
      <i class="fas fa-chart-pie w-6"></i> Dashboard
    </button>
    <button 
      on:click={() => onTabChange('movimientos')} 
      class="w-full flex items-center px-4 py-3 rounded-lg transition {activeTab === 'movimientos' ? 'bg-emerald-600 text-white shadow-md shadow-emerald-500/30' : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 hover:text-emerald-600 dark:hover:text-emerald-400'}"
    >
      <i class="fas fa-list w-6"></i> Movimientos
    </button>
    <button 
      on:click={() => onTabChange('metas')} 
      class="w-full flex items-center px-4 py-3 rounded-lg transition {activeTab === 'metas' ? 'bg-emerald-600 text-white shadow-md shadow-emerald-500/30' : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 hover:text-emerald-600 dark:hover:text-emerald-400'}"
    >
      <i class="fas fa-bullseye w-6"></i> Metas
    </button>
    <button 
      on:click={() => onTabChange('perfil')} 
      class="w-full flex items-center px-4 py-3 rounded-lg transition {activeTab === 'perfil' ? 'bg-emerald-600 text-white shadow-md shadow-emerald-500/30' : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 hover:text-emerald-600 dark:hover:text-emerald-400'}"
    >
      <i class="fas fa-user w-6"></i> Perfil
    </button>
    <button 
      on:click={() => onTabChange('configuracion')} 
      class="w-full flex items-center px-4 py-3 rounded-lg transition {activeTab === 'configuracion' ? 'bg-emerald-600 text-white shadow-md shadow-emerald-500/30' : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 hover:text-emerald-600 dark:hover:text-emerald-400'}"
    >
      <i class="fas fa-cog w-6"></i> Configuración
    </button>
  </nav>
  
  <div class="p-4 border-t border-gray-200 dark:border-gray-700 space-y-4">
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-3">
        <div class="w-8 h-8 rounded-full bg-emerald-100 dark:bg-emerald-900 flex items-center justify-center font-bold text-emerald-700 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-700">JD</div>
        <div class="text-sm">
          <p class="font-medium text-gray-900 dark:text-white">Usuario</p>
          <p class="text-xs text-gray-500 dark:text-gray-400">En línea</p>
        </div>
      </div>
      <button on:click={onLogout} class="text-rose-500 hover:text-rose-600 dark:text-rose-400 dark:hover:text-white transition" title="Cerrar Sesión"><i class="fas fa-sign-out-alt"></i></button>
    </div>
  </div>
</aside>
