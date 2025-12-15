<script>
  import { createEventDispatcher } from 'svelte';
  import { fly, fade } from 'svelte/transition';
  import { notifications } from '../stores/notifications';

  const dispatch = createEventDispatcher();

  // Estado persistente en localStorage
  const ONBOARDING_STORAGE_KEY = 'ems_onboarding_state';
  
  let step = 1;
  let newAccount = {
    nombre_cuenta: '',
    saldo_inicial: ""
  };

  // Cargar estado persistente al inicializar
  function loadState() {
    try {
      const saved = localStorage.getItem(ONBOARDING_STORAGE_KEY);
      if (saved) {
        const state = JSON.parse(saved);
        step = state.step || 1;
        newAccount = state.newAccount || newAccount;
      }
    } catch (e) {
      console.warn('Error loading onboarding state:', e);
    }
  }

  // Guardar estado persistente
  function saveState() {
    try {
      localStorage.setItem(ONBOARDING_STORAGE_KEY, JSON.stringify({
        step,
        newAccount
      }));
    } catch (e) {
      console.warn('Error saving onboarding state:', e);
    }
  }

  // Limpiar estado al completar
  function clearState() {
    try {
      localStorage.removeItem(ONBOARDING_STORAGE_KEY);
    } catch (e) {
      console.warn('Error clearing onboarding state:', e);
    }
  }

  // Auto-guardar estado cuando cambie
  $: {
    if (typeof step !== 'undefined') {
      saveState();
    }
  }

  // Cargar estado al montar el componente
  loadState();

  // Validación de montos grandes
  const MAX_SALDO = 999999999; // 999 millones COP
  const MIN_SALDO = 1000; // 1000 COP

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

  function handleCreateAccount() {
    const saldo = newAccount.saldo_inicial.replace(/[^0-9]/g, '');
    const validation = validateSaldo(saldo);
    
    if (!validation.valid) {
      notifications.addNotification(validation.message, 'error');
      return;
    }

    if (!newAccount.nombre_cuenta.trim()) {
      notifications.addNotification('El nombre de la cuenta es requerido', 'error');
      return;
    }

    const saldoNumerico = parseInt(saldo, 10);
    
    dispatch('createAccount', { 
      ...newAccount, 
      saldo_inicial: saldoNumerico 
    });
    
    step = 3;
  }

  function handleGenerateCategories() {
    dispatch('generateCategories');
    step = 4;
  }

  function handleComplete() {
    clearState();
    dispatch("complete");
  }
</script>

<div class="fixed inset-0 bg-slate-900/90 backdrop-blur-md z-[60] flex items-center justify-center p-4" transition:fade>
  <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl p-8 w-full max-w-lg relative overflow-hidden">
    
    <!-- Progress Bar -->
    <div class="absolute top-0 left-0 h-2 bg-gray-200 dark:bg-gray-700 w-full">
        <div class="h-full bg-emerald-500 transition-all duration-500 ease-out" style="width: {(step / 4) * 100}%"></div>
    </div>

    {#if step === 1}
      <div in:fly={{ x: 100, duration: 300, delay: 100 }} class="text-center py-8">
        <div class="w-20 h-20 bg-emerald-100 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-500 rounded-full flex items-center justify-center mx-auto mb-6">
            <i class="fas fa-hand-sparkles text-3xl"></i>
        </div>
        <h2 class="text-3xl font-bold text-gray-900 dark:text-white mb-4">¡Bienvenido a EMS!</h2>
        <p class="text-gray-600 dark:text-gray-300 mb-8 text-lg">
          Tu gestor financiero personal. Vamos a configurar tu espacio en menos de 1 minuto.
        </p>
        <button on:click={() => step = 2} class="w-full bg-emerald-600 text-white font-bold py-4 rounded-xl text-lg shadow-lg shadow-emerald-500/30 hover:bg-emerald-500 hover:scale-[1.02] transition-all">
          Comenzar
        </button>
      </div>

    {:else if step === 2}
      <div in:fly={{ x: 100, duration: 300 }} class="py-4">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-2">Tu Primera Cuenta</h2>
        <p class="text-gray-500 dark:text-gray-400 mb-6">¿Dónde guardas tu dinero? (Ej: "Bancolombia", "Efectivo")</p>
        
        <div class="space-y-6">
          <div>
            <label for="account-name" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Nombre de la Cuenta</label>
            <div class="relative">
                <i class="fas fa-wallet absolute left-4 top-4 text-gray-400"></i>
                <input id="account-name" type="text" bind:value={newAccount.nombre_cuenta} class="w-full bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-xl pl-12 pr-4 py-3.5 text-gray-900 dark:text-white focus:ring-2 focus:ring-emerald-500 focus:outline-none transition-all" placeholder="Ej: Mi Billetera">
            </div>
          </div>
          <div>
            <label for="initial-balance" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Saldo Inicial 
              <span class="text-xs text-gray-500">
                (Min: ${MIN_SALDO.toLocaleString('es-CO')} - Max: ${MAX_SALDO.toLocaleString('es-CO')})
              </span>
            </label>
            <div class="relative">
                <i class="fas fa-dollar-sign absolute left-4 top-4 text-gray-400"></i>
                <input id="initial-balance" type="text" bind:value={newAccount.saldo_inicial} 
                       on:input={(e) => {
                           const input = /** @type {HTMLInputElement} */ (e.target);
                           let value = input.value.replace(/[^0-9]/g, '');
                           if (value) {
                             // Validar que no exceda el máximo
                             const numericValue = parseInt(value);
                             if (numericValue <= MAX_SALDO) {
                               newAccount.saldo_inicial = new Intl.NumberFormat('es-CO').format(numericValue);
                             }
                           } else {
                             newAccount.saldo_inicial = '';
                           }
                       }}
                       class="w-full bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-xl pl-12 pr-4 py-3.5 text-gray-900 dark:text-white focus:ring-2 focus:ring-emerald-500 focus:outline-none transition-all" placeholder="0">
            </div>
          </div>
        </div>

        <button on:click={handleCreateAccount} class="w-full mt-8 bg-emerald-600 text-white font-bold py-3.5 rounded-xl shadow-lg shadow-emerald-500/30 hover:bg-emerald-500 hover:scale-[1.02] transition-all flex items-center justify-center gap-2">
          <span>Crear Cuenta</span> <i class="fas fa-arrow-right"></i>
        </button>
      </div>

    {:else if step === 3}
      <div in:fly={{ x: 100, duration: 300 }} class="text-center py-6">
        <div class="w-16 h-16 bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-500 rounded-full flex items-center justify-center mx-auto mb-6">
            <i class="fas fa-tags text-2xl"></i>
        </div>
        <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-4">Categorías Rápidas</h2>
        <p class="text-gray-600 dark:text-gray-300 mb-8">
          ¿Quieres que creemos las categorías más comunes por ti? (Comida, Transporte, Ocio)
        </p>
        
        <div class="space-y-3">
            <button on:click={handleGenerateCategories} class="w-full bg-blue-600 text-white font-bold py-3.5 rounded-xl shadow-lg shadow-blue-500/30 hover:bg-blue-500 hover:scale-[1.02] transition-all">
              Sí, generar automáticamente
            </button>
            <button on:click={() => step = 4} class="w-full py-3.5 text-gray-500 dark:text-gray-400 font-medium hover:text-gray-900 dark:hover:text-white transition-colors">
              No, las crearé manualmente
            </button>
        </div>
      </div>

    {:else if step === 4}
      <div in:fly={{ x: 100, duration: 300 }} class="text-center py-6">
        <div class="w-20 h-20 bg-emerald-100 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-500 rounded-full flex items-center justify-center mx-auto mb-6">
            <i class="fas fa-check text-4xl"></i>
        </div>
        <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-4">¡Todo Listo!</h2>
        <p class="text-gray-600 dark:text-gray-300 mb-8">
          Tu cuenta ha sido creada. Ya puedes empezar a registrar tus gastos e ingresos.
        </p>
        <button on:click={handleComplete} class="w-full bg-emerald-600 text-white font-bold py-4 rounded-xl shadow-lg hover:bg-emerald-500 transition-all">
          Ir al Dashboard
        </button>
      </div>
    {/if}
  </div>
</div>
