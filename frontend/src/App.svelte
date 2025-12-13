<script>
  import { onMount } from 'svelte';
  import { fly } from 'svelte/transition';
  import { api } from './lib/api';
  import { theme } from './lib/stores/theme';
  import { formatMoney } from './lib/utils/format';
  
  import Sidebar from './lib/components/Sidebar.svelte';
  import KpiCard from './lib/components/KpiCard.svelte';
  import TransactionTable from './lib/components/TransactionTable.svelte';
  import ModalMovimiento from './lib/components/ModalMovimiento.svelte';
  import ModalCuenta from './lib/components/ModalCuenta.svelte';
  import ModalCategoria from './lib/components/ModalCategoria.svelte';
  import ModalMeta from './lib/components/ModalMeta.svelte';
  import ModalAbonoMeta from './lib/components/ModalAbonoMeta.svelte';
  import Configuracion from './lib/components/Configuracion.svelte';
  import Perfil from './lib/components/Perfil.svelte';
  
  import Chart from 'chart.js/auto';

  let isAuthenticated = false;
  let activeTab = 'dashboard';
  
  // Modals
  let isModalOpen = false;
  let isModalCuentaOpen = false;
  let isModalCategoriaOpen = false;
  let isModalMetaOpen = false;
  let isModalAbonoMetaOpen = false;

  // Edit Mode & State
  let editingTransaction = null;
  let abonoMetaTarget = null;
  let editingMeta = null;

  // Data
  let kpis = { saldo: 0, ingresos: 0, gastos: 0 };
  let transactions = [];
  let cuentas = [];
  let categorias = [];
  let metas = [];
  let user = {};

  // Auth Form
  let email = '';
  let password = '';
  let isRegistering = false;
  let authError = '';
  let name = ''; // For registration
  let isLoading = false; // For login UX
  
  $: darkMode = $theme;

  $: {
      if (typeof document !== 'undefined') {
        if ($theme) {
            document.documentElement.classList.add('dark');
        } else {
            document.documentElement.classList.remove('dark');
        }
      }
  }

  // Charts
  let donutChartInstance = null;
  let barChartInstance = null;
  let donutCanvas;
  let barCanvas;

  onMount(async () => {
    theme.init(); // Initialize theme preference

    const token = localStorage.getItem('access_token');
    if (token) {
      isAuthenticated = true;
      try {
        user = await api.getProfile();
        await loadData();
      } catch (error) {
        if (error.status === 401) {
          handleLogout();
        }
      }
    }
  });

  async function loadData() {
    try {
      // Load foundational data (always needed for modals)
      const [cuentasRes, catsRes] = await Promise.all([
        api.getCuentas().catch(err => []),
        api.getCategorias().catch(err => [])
      ]);
      cuentas = cuentasRes;
      categorias = catsRes;

      if (activeTab === 'dashboard') {
        const dashboard = await api.getDashboard().catch(err => ({ total_ingresos: 0, total_gastos: 0, saldo_total: 0 }));
        kpis = {
            saldo: dashboard.saldo_total,
            ingresos: dashboard.total_ingresos,
            gastos: dashboard.total_gastos
        };
        await loadChartsData();
      } else if (activeTab === 'movimientos') {
        transactions = await api.getMovimientos().catch(err => []);
        transactions = transactions.map(t => ({
            ...t,
            nombre_cuenta: t.nombre_cuenta || cuentas.find(c => c.cuenta_id === t.cuenta_id)?.nombre_cuenta,
            nombre_categoria: t.nombre_categoria || categorias.find(c => c.categoria_id === t.categoria_id)?.nombre_categoria
        }));
      } else if (activeTab === 'metas') {
        metas = await api.getMetas().catch(err => []);
      } 
      // Configuracion uses 'cuentas' and 'categorias' which are already loaded
    } catch (error) {
      console.error('Error loading data', error);
      if (error.status === 401 || (error.message && error.message.includes('401'))) handleLogout();
    }
  }

  async function loadChartsData() {
    const movs = await api.getMovimientos().catch(err => []);
    
    // Process for Donut (Gastos por Categoria)
    const gastos = movs.filter(m => m.tipo.toLowerCase() === 'gasto'); 
    const gastosPorCat = {};
    gastos.forEach(g => {
        const catName = g.nombre_categoria || categorias.find(c => c.categoria_id === g.categoria_id)?.nombre_categoria || 'Otros';
        gastosPorCat[catName] = (gastosPorCat[catName] || 0) + parseFloat(g.monto);
    });

    // Process for Bar (Balance Mensual)
    const monthlyData = {};
    movs.forEach(m => {
        if (!m.fecha) return;
        const date = new Date(m.fecha);
        const key = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`; // YYYY-MM
        if (!monthlyData[key]) monthlyData[key] = { ingresos: 0, gastos: 0 };
        
        const tipo = m.tipo?.toLowerCase();
        if (tipo === 'ingreso') {
            monthlyData[key].ingresos += parseFloat(m.monto);
        } else if (tipo === 'gasto') {
            monthlyData[key].gastos += parseFloat(m.monto);
        }
    });

    // Sort by date and take last 6 months
    const sortedKeys = Object.keys(monthlyData).sort().slice(-6);
    const chartLabels = sortedKeys.map(key => {
        const [year, month] = key.split('-');
        const date = new Date(parseInt(year), parseInt(month) - 1);
        return date.toLocaleDateString('es-CO', { month: 'short', year: 'numeric' });
    });
    const ingresosData = sortedKeys.map(key => monthlyData[key].ingresos);
    const gastosData = sortedKeys.map(key => monthlyData[key].gastos);

    // Render Charts
    requestAnimationFrame(() => {
        if (activeTab === 'dashboard' && donutCanvas && barCanvas) {
            renderCharts(gastosPorCat, chartLabels, ingresosData, gastosData);
        }
    });
  }

  function renderCharts(gastosPorCat, barLabels, barIngresos, barGastos) {
    if (donutChartInstance) donutChartInstance.destroy();
    if (barChartInstance) barChartInstance.destroy();

    const isDark = document.documentElement.classList.contains('dark');
    const textColors = isDark ? '#e5e7eb' : '#1f2937';
    const gridColors = isDark ? '#374151' : '#e5e7eb';

    // Donut
    donutChartInstance = new Chart(donutCanvas, {
        type: 'doughnut',
        data: {
            labels: Object.keys(gastosPorCat),
            datasets: [{
                data: Object.values(gastosPorCat),
                backgroundColor: ['#10b981', '#14b8a6', '#f43f5e', '#6366f1', '#f59e0b', '#8b5cf6'],
                borderWidth: 0
            }]
        },
        options: { 
            responsive: true,
            maintainAspectRatio: false,
            plugins: { 
                legend: { position: 'right', labels: { color: textColors } } 
            } 
        }
    });

    // Bar Chart
    barChartInstance = new Chart(barCanvas, {
        type: 'bar',
        data: {
            labels: barLabels && barLabels.length > 0 ? barLabels : ['Sin datos'],
            datasets: [
                { label: 'Ingresos', data: barIngresos && barIngresos.length > 0 ? barIngresos : [0], backgroundColor: '#14b8a6' },
                { label: 'Gastos', data: barGastos && barGastos.length > 0 ? barGastos : [0], backgroundColor: '#f43f5e' }
            ]
        },
        options: { 
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { labels: { color: textColors } } }, 
            scales: { 
                y: { ticks: { color: textColors }, grid: { color: gridColors } }, 
                x: { ticks: { color: textColors }, grid: { display: false } } 
            } 
        }
    });
  }

  async function handleLogin() {
    isLoading = true;
    try {
      authError = '';
      if (isRegistering) {
        await api.register({ nombre: name, email, contraseña: password });
        isRegistering = false;
        alert('Registro exitoso. Por favor inicia sesión.');
      } else {
        const res = await api.login(email, password);
        localStorage.setItem('access_token', res.access_token);
        isAuthenticated = true;
        user = await api.getProfile();
        await loadData();
      }
    } catch (e) {
      authError = e.message || 'Error de autenticación';
    } finally {
        isLoading = false;
    }
  }

  function handleLogout() {
    localStorage.removeItem('access_token');
    isAuthenticated = false;
    email = '';
    password = '';
    user = {};
  }

  function handleTabChange(tab) {
    activeTab = tab;
    loadData();
  }

  async function handleSaveMovimiento(data) {
    try {
      if (editingTransaction) {
        await api.updateMovimiento(editingTransaction.movimiento_id, data);
      } else {
        await api.createMovimiento(data);
      }
      isModalOpen = false;
      editingTransaction = null;
      loadData();
    } catch (e) {
      alert('Error al guardar: ' + e.message);
    }
  }

  function handleEditMovimiento(transaction) {
    editingTransaction = transaction;
    isModalOpen = true;
  }

  function handleOpenNewMovimiento() {
    editingTransaction = null;
    isModalOpen = true;
  }

  async function handleSaveCuenta(data) {
    try {
      await api.createCuenta(data);
      isModalCuentaOpen = false;
      loadData();
    } catch (e) {
      alert('Error al crear cuenta: ' + e.message);
    }
  }

  async function handleDeleteCuenta(id) {
    if(!confirm('¿Estás seguro de eliminar esta cuenta?')) return;
    try {
      await api.deleteCuenta(id);
      loadData();
    } catch (e) {
      alert('Error al eliminar: ' + e.message);
    }
  }

  async function handleSaveCategoria(data) {
    try {
      await api.createCategoria(data);
      isModalCategoriaOpen = false;
      loadData();
    } catch (e) {
      alert('Error al crear categoría: ' + e.message);
    }
  }

  async function handleDeleteCategoria(id) {
    if(!confirm('¿Estás seguro de eliminar esta categoría?')) return;
    try {
      await api.deleteCategoria(id);
      loadData();
    } catch (e) {
      alert('Error al eliminar: ' + e.message);
    }
  }

  async function handleSaveMeta(data, meta_id) {
    try {
        if (meta_id) {
            await api.updateMeta(meta_id, data);
        } else {
            await api.createMeta(data);
        }
        isModalMetaOpen = false;
        editingMeta = null;
        loadData();
    } catch (e) {
        alert('Error al guardar meta: ' + e.message);
    }
  }
  
  function handleEditMeta(meta) {
      editingMeta = meta;
      isModalMetaOpen = true;
  }

  async function handleDeleteMeta(metaId) {
      if (confirm('¿Estás seguro de eliminar esta meta?')) {
          try {
              await api.deleteMeta(metaId);
              loadData();
          } catch (e) {
              alert('Error al eliminar meta: ' + e.message);
          }
      }
  }

  function handleOpenAbonoMeta(meta) {
      abonoMetaTarget = meta;
      isModalAbonoMetaOpen = true;
  }

  async function handleSaveAbonoMeta(metaId, payload) {
      try {
          await api.abonarMeta(metaId, payload);
          isModalAbonoMetaOpen = false;
          abonoMetaTarget = null;
          loadData();
      } catch (e) {
          alert('Error al abonar: ' + e.message);
      }
  }
</script>

{#if !isAuthenticated}
  <div class="w-screen h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 transition-colors duration-300 relative overflow-hidden">
    <!-- Background Image with Overlay -->
    <div class="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1579621970563-ebec7560eb3e?q=80&w=2500&auto=format&fit=crop')] bg-cover bg-center opacity-20"></div>
    
    <div class="bg-white dark:bg-gray-800 p-8 rounded-2xl shadow-2xl border border-gray-200 dark:border-gray-700 w-full max-w-md relative z-10 animate-fade-in backdrop-blur-sm bg-opacity-95 dark:bg-opacity-95">
      <div class="text-center mb-8">
        <div class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-emerald-100 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-500 mb-4 shadow-sm">
          <i class="fas fa-wallet text-3xl"></i>
        </div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Bienvenido a EMS</h1>
        <p class="text-gray-500 dark:text-gray-400 text-sm mt-2">Gestiona tus finanzas con inteligencia.</p>
      </div>

      <div class="flex bg-gray-100 dark:bg-gray-900/50 rounded-lg p-1 mb-6">
          <button on:click={() => isRegistering = false} class="flex-1 py-2 text-sm font-medium rounded-md transition { !isRegistering ? 'bg-white dark:bg-emerald-600 text-gray-900 dark:text-white shadow' : 'text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white' }">Iniciar Sesión</button>
          <button on:click={() => isRegistering = true} class="flex-1 py-2 text-sm font-medium rounded-md transition { isRegistering ? 'bg-white dark:bg-emerald-600 text-gray-900 dark:text-white shadow' : 'text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white' }">Registrarse</button>
      </div>

      <form on:submit|preventDefault={handleLogin} class="space-y-4">
          {#if isRegistering}
          <div>
              <label for="register-name" class="block text-sm text-gray-600 dark:text-gray-400 mb-1">Nombre Completo</label>
              <div class="relative">
                  <i class="fas fa-user absolute left-3 top-3 text-gray-400 dark:text-gray-500"></i>
                  <input id="register-name" type="text" bind:value={name} class="w-full bg-gray-50 dark:bg-gray-900 border border-gray-300 dark:border-gray-600 rounded-lg pl-10 pr-4 py-2 text-gray-900 dark:text-white focus:border-emerald-500 focus:outline-none transition-colors" placeholder="Tu Nombre" required>
              </div>
          </div>
          {/if}
          <div>
          <label for="email" class="block text-sm text-gray-600 dark:text-gray-400 mb-1">Correo Electrónico</label>
          <div class="relative">
              <i class="fas fa-envelope absolute left-3 top-3 text-gray-400 dark:text-gray-500"></i>
              <input id="email" type="email" bind:value={email} class="w-full bg-gray-50 dark:bg-gray-900 border border-gray-300 dark:border-gray-600 rounded-lg pl-10 pr-4 py-2 text-gray-900 dark:text-white focus:border-emerald-500 focus:outline-none transition-colors" placeholder="ejemplo@correo.com" required>
          </div>
          </div>
          <div>
          <label for="password" class="block text-sm text-gray-600 dark:text-gray-400 mb-1">Contraseña</label>
          <div class="relative">
              <i class="fas fa-lock absolute left-3 top-3 text-gray-400 dark:text-gray-500"></i>
              <input id="password" type="password" bind:value={password} class="w-full bg-gray-50 dark:bg-gray-900 border border-gray-300 dark:border-gray-600 rounded-lg pl-10 pr-4 py-2 text-gray-900 dark:text-white focus:border-emerald-500 focus:outline-none transition-colors" placeholder="••••••••" required>
          </div>
          </div>
          
          {#if authError}
              <p class="text-rose-500 text-sm text-center">{authError}</p>
          {/if}

          <button type="submit" disabled={isLoading} class="w-full {isRegistering ? 'bg-emerald-600 hover:bg-emerald-500' : 'bg-emerald-600 hover:bg-emerald-500'} text-white font-bold py-3 rounded-lg shadow-lg transition transform hover:scale-[1.02] disabled:opacity-50">
            {#if isLoading}
                <i class="fas fa-spinner fa-spin mr-2"></i> Conectando...
            {:else}
                {isRegistering ? 'Crear Cuenta' : 'Ingresar'}
            {/if}
          </button>
      </form>

    </div>
  </div>
{:else}
  <div class="flex h-screen overflow-hidden bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-white transition-colors duration-300">
    <Sidebar 
        {activeTab} 
        darkMode={$theme}
        onTabChange={handleTabChange} 
        onLogout={handleLogout} 
        toggleDarkMode={theme.toggle}
    />
    
    <main class="flex-1 overflow-y-auto p-8 relative scrollbar-thin scrollbar-thumb-gray-300 dark:scrollbar-thumb-gray-700">
      <header class="flex justify-between items-center mb-8" in:fly={{ y: -20, duration: 500 }}>
        <h2 class="text-3xl font-bold text-gray-800 dark:text-white">
            {activeTab === 'dashboard' ? 'Resumen Financiero' : 
             activeTab === 'movimientos' ? 'Historial de Movimientos' : 
             activeTab === 'metas' ? 'Metas de Ahorro' : 
             activeTab === 'perfil' ? 'Mi Perfil' : 'Configuración'}
        </h2>
        
        {#if activeTab === 'movimientos'}
        <button on:click={handleOpenNewMovimiento} class="bg-emerald-600 hover:bg-emerald-500 text-white px-6 py-2 rounded-lg font-medium shadow-lg shadow-emerald-500/30 flex items-center gap-2 transition hover:scale-105">
            <i class="fas fa-plus"></i> Nuevo Movimiento
        </button>
        {:else if activeTab === 'metas'}
        <button on:click={() => { editingMeta = null; isModalMetaOpen = true; }} class="bg-purple-600 hover:bg-purple-500 text-white px-6 py-2 rounded-lg font-medium shadow-lg shadow-purple-500/30 flex items-center gap-2 transition hover:scale-105">
            <i class="fas fa-plus"></i> Nueva Meta
        </button>
        {/if}
      </header>

      {#if activeTab === 'dashboard'}
        <div class="space-y-6" in:fly={{ y: 20, duration: 500, delay: 100 }}>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                <KpiCard title="Saldo Actual" value={formatMoney(kpis.saldo)} />
                <KpiCard title="Ingresos (Total)" value={formatMoney(kpis.ingresos)} color="text-teal-500 dark:text-teal-400" />
                <KpiCard title="Gastos (Total)" value={formatMoney(kpis.gastos)} color="text-rose-500 dark:text-rose-400" />
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div class="bg-white dark:bg-gray-800 p-6 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm transition-colors duration-300">
                    <h4 class="font-bold mb-4 text-gray-800 dark:text-white">Top Gastos por Categoría</h4>
                    <div class="h-64 flex items-center justify-center">
                        <canvas bind:this={donutCanvas}></canvas>
                    </div>
                </div>
                <div class="bg-white dark:bg-gray-800 p-6 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm transition-colors duration-300">
                    <h4 class="font-bold mb-4 text-gray-800 dark:text-white">Balance Mensual</h4>
                    <div class="h-64">
                        <canvas bind:this={barCanvas}></canvas>
                    </div>
                </div>
            </div>
        </div>
      {:else if activeTab === 'movimientos'}
        <div class="space-y-6" in:fly={{ y: 20, duration: 500 }}>
            <div class="flex gap-4 bg-white dark:bg-gray-800 p-4 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm transition-colors duration-300">
                <div class="flex-1 relative">
                    <i class="fas fa-search absolute left-3 top-3 text-gray-400 dark:text-gray-500"></i>
                    <input type="text" placeholder="Buscar..." class="w-full bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-white rounded-lg pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-700 focus:border-emerald-500 focus:outline-none transition-colors" />
                </div>
            </div>
            <TransactionTable 
                transactions={transactions} 
                onEdit={handleEditMovimiento} 
                onDelete={(id) => api.deleteMovimiento(id).then(loadData)} 
            />
        </div>
      {:else if activeTab === 'metas'}
        <div class="space-y-6" in:fly={{ y: 20, duration: 500 }}>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                {#each metas as meta}
                <div class="bg-white dark:bg-gray-800 p-6 rounded-xl border border-gray-200 dark:border-gray-700 relative overflow-hidden group hover:border-purple-500 transition shadow-sm">
                    <div class="absolute top-0 left-0 w-1 h-full bg-purple-500"></div>
                    <div class="flex justify-between items-start mb-4">
                        <div>
                            <span class="bg-purple-100 dark:bg-purple-500/20 text-purple-600 dark:text-purple-400 px-2 py-1 rounded text-xs font-bold uppercase">Meta</span>
                            <h4 class="text-xl font-bold text-gray-900 dark:text-white mt-1 truncate max-w-[200px]" title={meta.nombre_meta}>{meta.nombre_meta}</h4>
                        </div>
                        <div class="text-right">
                            <p class="text-xs text-gray-500 dark:text-gray-400">Objetivo</p>
                            <p class="font-bold text-gray-900 dark:text-white truncate max-w-[100px]" title={formatMoney(meta.monto_objetivo)}>{formatMoney(meta.monto_objetivo)}</p>
                        </div>
                    </div>
                    <div class="mb-2 flex justify-between text-sm">
                        <span class="text-gray-500 dark:text-gray-400">Progreso ({((meta.monto_actual / meta.monto_objetivo) * 100).toFixed(0)}%)</span>
                        <span class="text-gray-900 dark:text-white font-bold truncate max-w-[100px]">{formatMoney(meta.monto_actual)}</span>
                    </div>
                    <div class="w-full bg-gray-200 dark:bg-gray-700 h-3 rounded-full mb-4">
                        <div class="bg-gradient-to-r from-purple-600 to-blue-500 h-3 rounded-full transition-all duration-1000" style="width: {Math.min(100, (meta.monto_actual / meta.monto_objetivo) * 100)}%"></div>
                    </div>
                    
                    <div class="flex gap-2 mt-4">
                        <button on:click={() => handleOpenAbonoMeta(meta)} class="flex-1 bg-gray-100 dark:bg-gray-700 hover:bg-emerald-600 dark:hover:bg-emerald-600 hover:text-white text-gray-700 dark:text-gray-300 font-medium py-2 rounded-lg transition-colors flex items-center justify-center gap-2">
                            <i class="fas fa-plus-circle"></i> Abonar
                        </button>

                        <button on:click={() => handleEditMeta(meta)} class="w-10 bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 hover:bg-blue-600 hover:text-white rounded-lg transition-colors flex items-center justify-center" title="Editar Meta">
                            <i class="fas fa-pen"></i>
                        </button>

                        <button on:click={() => handleDeleteMeta(meta.meta_id)} class="w-10 bg-rose-100 dark:bg-rose-900/30 text-rose-600 dark:text-rose-400 hover:bg-rose-600 hover:text-white rounded-lg transition-colors flex items-center justify-center" title="Eliminar Meta">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
                {:else}
                    <div class="col-span-2 text-center py-12 text-gray-500 dark:text-gray-400">
                        <i class="fas fa-bullseye text-4xl mb-4 text-gray-300 dark:text-gray-600"></i>
                        <p>No hay metas registradas. ¡Crea una nueva para empezar a ahorrar!</p>
                    </div>
                {/each}
            </div>
        </div>
      {:else if activeTab === 'perfil'}
        <div in:fly={{ y: 20, duration: 500 }}>
            <Perfil {user} />
        </div>
      {:else if activeTab === 'configuracion'}
        <Configuracion 
            {cuentas} 
            {categorias} 
            onDeleteCuenta={handleDeleteCuenta}
            onDeleteCategoria={handleDeleteCategoria}
            onOpenModalCuenta={() => isModalCuentaOpen = true}
            onOpenModalCategoria={() => isModalCategoriaOpen = true}
        />
      {/if}
    </main>
  </div>

  <ModalMovimiento 
    isOpen={isModalOpen} 
    onClose={() => isModalOpen = false} 
    onSave={handleSaveMovimiento}
    {cuentas}
    {categorias}
    {editingTransaction}
  />

  <ModalCuenta
    isOpen={isModalCuentaOpen}
    onClose={() => isModalCuentaOpen = false}
    onSave={handleSaveCuenta}
  />

  <ModalCategoria
    isOpen={isModalCategoriaOpen}
    onClose={() => isModalCategoriaOpen = false}
    onSave={handleSaveCategoria}
  />
  
  <ModalMeta
    isOpen={isModalMetaOpen}
    onClose={() => { isModalMetaOpen = false; editingMeta = null; }}
    onSave={handleSaveMeta}
    editingMeta={editingMeta}
  />

  <ModalAbonoMeta
    isOpen={isModalAbonoMetaOpen}
    onClose={() => isModalAbonoMetaOpen = false}
    onSave={handleSaveAbonoMeta}
    meta={abonoMetaTarget}
    cuentas={cuentas} 
  />
{/if}
