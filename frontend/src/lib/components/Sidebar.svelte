<script>
  export let activeTab = 'dashboard';
  export let user = {};
  export let onTabChange;
  export let onLogout;
</script>

<aside class="w-64 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 hidden md:flex flex-col h-full transition-colors duration-300">
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
  
  <div class="p-4 border-t border-gray-200 dark:border-gray-700">
    <div class="bg-slate-100 dark:bg-slate-800/50 rounded-xl p-3 flex items-center gap-3 border border-slate-200 dark:border-slate-700 shadow-sm">
        <!-- Avatar -->
        <div class="w-10 h-10 rounded-full bg-gradient-to-br from-emerald-500 to-teal-600 text-white flex items-center justify-center font-bold shadow-sm">
            {(user.nombre || user.email || 'U')[0].toUpperCase()}
        </div>
        <!-- Info -->
        <div class="flex-1 min-w-0">
            <p class="font-semibold text-sm text-slate-800 dark:text-white truncate">{user.nombre || user.email || 'Usuario'}</p>
            <div class="flex items-center gap-1.5">
                <div class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
                <p class="text-xs text-slate-500 dark:text-slate-400">Pro</p>
            </div>
        </div>
        <!-- Action -->
        <button on:click={onLogout} class="text-slate-400 hover:text-rose-500 transition-colors p-1" title="Cerrar Sesión">
            <i class="fas fa-sign-out-alt"></i>
        </button>
    </div>
  </div>
</aside>
