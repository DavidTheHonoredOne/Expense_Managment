<script>
  import { createEventDispatcher } from 'svelte';
  import { notifications } from '../stores/notifications';

  const dispatch = createEventDispatcher();

  let step = 1;
  let newAccount = {
    nombre_cuenta: '',
    saldo_inicial: null
  };

  function handleCreateAccount() {
    if (newAccount.nombre_cuenta && newAccount.saldo_inicial > 0) {
      dispatch('createAccount', newAccount);
      step = 3;
    } else {
      notifications.addNotification('Por favor, ingresa un nombre y un saldo inicial mayor a cero.', 'error');
    }
  }

  function handleGenerateCategories() {
    dispatch('generateCategories');
  }
</script>

<div class="fixed inset-0 bg-gray-900 bg-opacity-75 z-50 flex items-center justify-center">
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl p-8 w-full max-w-md">
    {#if step === 1}
      <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-4">¡Bienvenido a EMS!</h2>
      <p class="text-gray-600 dark:text-gray-300 mb-6">
        Parece que es tu primera vez aquí. Sigue estos sencillos pasos para configurar tu espacio financiero.
      </p>
      <button on:click={() => step = 2} class="w-full bg-emerald-600 text-white font-bold py-2 px-4 rounded-lg hover:bg-emerald-700 transition">
        Comenzar Configuración
      </button>
    {:else if step === 2}
      <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-4">Crea tu Primera Cuenta</h2>
      <p class="text-gray-600 dark:text-gray-300 mb-6">
        Necesitas al menos una cuenta para registrar tus movimientos. Puede ser tu cuenta de ahorros, cartera, etc.
      </p>
      <div class="space-y-4">
        <div>
          <label for="account-name" class="block text-sm font-medium text-gray-700 dark:text-gray-300">Nombre de la Cuenta</label>
          <input type="text" id="account-name" bind:value={newAccount.nombre_cuenta} class="mt-1 block w-full px-3 py-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-emerald-500 focus:border-emerald-500 sm:text-sm text-gray-900 dark:text-white" placeholder="Ej: Cartera">
        </div>
        <div>
          <label for="initial-balance" class="block text-sm font-medium text-gray-700 dark:text-gray-300">Saldo Inicial</label>
          <input type="number" id="initial-balance" bind:value={newAccount.saldo_inicial} class="mt-1 block w-full px-3 py-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-emerald-500 focus:border-emerald-500 sm:text-sm text-gray-900 dark:text-white" placeholder="0.00">
        </div>
      </div>
      <button on:click={handleCreateAccount} class="w-full mt-6 bg-emerald-600 text-white font-bold py-2 px-4 rounded-lg hover:bg-emerald-700 transition">
        Crear Cuenta y Continuar
      </button>
    {:else if step === 3}
      <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-4">Categorías Básicas</h2>
      <p class="text-gray-600 dark:text-gray-300 mb-6">
        Para facilitar el registro de tus gastos, podemos generar algunas categorías comunes por ti.
      </p>
      <button on:click={handleGenerateCategories} class="w-full bg-emerald-600 text-white font-bold py-2 px-4 rounded-lg hover:bg-emerald-700 transition">
        Generar Categorías (Comida, Transporte, Ocio)
      </button>
      <button on:click={() => dispatch("finish")} class="w-full mt-4 text-sm text-gray-500 dark:text-gray-400 hover:underline">
        Lo haré más tarde
      </button>
    {/if}
  </div>
</div>
