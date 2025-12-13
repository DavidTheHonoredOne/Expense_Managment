<script>
  import { api } from '../api';
  import { onMount } from 'svelte';
  import { notifications } from '../stores/notifications';

  export let user = {};

  let nombre = '';
  let email = '';
  let current_password = '';
  let new_password = '';
  let confirm_password = '';
  let showPassword = false;
  let avatarUrl = '';

  onMount(() => {
    if (user) {
        nombre = user.nombre || '';
        email = user.email || '';
        updateAvatar(nombre);
    }
  });

  $: if (nombre) {
      updateAvatar(nombre);
  }

  function updateAvatar(name) {
      avatarUrl = `https://ui-avatars.com/api/?name=${encodeURIComponent(name)}&background=10b981&color=fff&size=128`;
  }

  async function handleUpdateProfile() {
      try {
          await api.updateProfile({ nombre, email });
          notifications.addNotification('Perfil actualizado correctamente', 'success');
      } catch (e) {
          notifications.addNotification('Error al actualizar perfil: ' + e.message, 'error');
      }
  }

  async function handleChangePassword() {
      if (new_password !== confirm_password) {
          notifications.addNotification('Las contraseñas nuevas no coinciden', 'error');
          return;
      }
      try {
          await api.changePassword({ current_password, new_password });
          notifications.addNotification('Contraseña actualizada correctamente', 'success');
          current_password = '';
          new_password = '';
          confirm_password = '';
      } catch (e) {
          notifications.addNotification('Error al cambiar contraseña: ' + e.message, 'error');
      }
  }
</script>

<div class="space-y-8 animate-fade-in">
  <div class="bg-white dark:bg-gray-800 p-8 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm transition-colors duration-300">
    <h3 class="text-2xl font-bold text-gray-900 dark:text-white mb-6 border-b border-gray-200 dark:border-gray-700 pb-2">Mi Perfil</h3>
    
    <div class="flex flex-col md:flex-row gap-8 items-start">
        <!-- Avatar -->
        <div class="flex flex-col items-center gap-4">
            <img src={avatarUrl} alt="Avatar" class="w-32 h-32 rounded-full border-4 border-emerald-100 dark:border-emerald-900 shadow-lg">
            <span class="px-3 py-1 bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400 rounded-full text-xs font-bold uppercase tracking-wider">Usuario Activo</span>
        </div>

        <!-- Form Datos -->
        <div class="flex-1 w-full space-y-4">
            <h4 class="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-2"><i class="fas fa-user-edit mr-2 text-emerald-500"></i>Datos Personales</h4>
            <form on:submit|preventDefault={handleUpdateProfile} class="space-y-4">
                <div>
                    <label for="nombre" class="block text-sm text-gray-600 dark:text-gray-400 mb-1">Nombre Completo</label>
                    <input id="nombre" type="text" bind:value={nombre} class="w-full bg-gray-50 dark:bg-gray-900 border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2 text-gray-900 dark:text-white focus:border-emerald-500 focus:outline-none transition-colors" required>
                </div>
                <div>
                    <label for="email-profile" class="block text-sm text-gray-600 dark:text-gray-400 mb-1">Correo Electrónico</label>
                    <input id="email-profile" type="email" bind:value={email} class="w-full bg-gray-50 dark:bg-gray-900 border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2 text-gray-900 dark:text-white focus:border-emerald-500 focus:outline-none transition-colors" required>
                </div>
                <div class="pt-2">
                    <button type="submit" class="bg-emerald-600 hover:bg-emerald-500 text-white px-6 py-2 rounded-lg font-medium shadow-md shadow-emerald-500/20 transition-all hover:scale-[1.02]">
                        Guardar Cambios
                    </button>
                </div>
            </form>
        </div>
    </div>
  </div>

  <div class="bg-white dark:bg-gray-800 p-8 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm transition-colors duration-300">
    <h3 class="text-xl font-bold text-gray-900 dark:text-white mb-6 border-b border-gray-200 dark:border-gray-700 pb-2"><i class="fas fa-shield-alt mr-2 text-rose-500"></i>Seguridad</h3>
    
    <form on:submit|preventDefault={handleChangePassword} class="max-w-md space-y-4">
        <div>
            <label for="current_password" class="block text-sm text-gray-600 dark:text-gray-400 mb-1">Contraseña Actual</label>
            <div class="relative">
                <input id="current_password" type="password" bind:value={current_password} class="w-full bg-gray-50 dark:bg-gray-900 border border-gray-300 dark:border-gray-600 rounded-lg pl-4 pr-10 py-2 text-gray-900 dark:text-white focus:border-emerald-500 focus:outline-none transition-colors" required>
                <i class="fas fa-lock absolute right-3 top-3 text-gray-400"></i>
            </div>
        </div>
        <div>
            <label for="new_password" class="block text-sm text-gray-600 dark:text-gray-400 mb-1">Nueva Contraseña</label>
            <div class="relative">
                <input id="new_password" type={showPassword ? 'text' : 'password'} bind:value={new_password} class="w-full bg-gray-50 dark:bg-gray-900 border border-gray-300 dark:border-gray-600 rounded-lg pl-4 pr-10 py-2 text-gray-900 dark:text-white focus:border-emerald-500 focus:outline-none transition-colors" required>
                <button type="button" on:click={() => showPassword = !showPassword} class="absolute right-3 top-3 text-gray-400 hover:text-gray-600 focus:outline-none" aria-label="Mostrar contraseña">
                    <i class="fas {showPassword ? 'fa-eye-slash' : 'fa-eye'}"></i>
                </button>
            </div>
        </div>
        <div>
            <label for="confirm_password" class="block text-sm text-gray-600 dark:text-gray-400 mb-1">Confirmar Nueva Contraseña</label>
            <div class="relative">
                <input id="confirm_password" type={showPassword ? 'text' : 'password'} bind:value={confirm_password} class="w-full bg-gray-50 dark:bg-gray-900 border border-gray-300 dark:border-gray-600 rounded-lg pl-4 pr-10 py-2 text-gray-900 dark:text-white focus:border-emerald-500 focus:outline-none transition-colors" required>
            </div>
        </div>
        <div class="pt-2">
            <button type="submit" class="bg-gray-700 hover:bg-gray-600 dark:bg-gray-700 dark:hover:bg-gray-600 text-white px-6 py-2 rounded-lg font-medium shadow-md transition-all hover:scale-[1.02]">
                Cambiar Contraseña
            </button>
        </div>
    </form>

    <!-- Botón de Cerrar Sesión -->
    <div class="mt-8">
        <button on:click={() => { localStorage.removeItem('access_token'); window.location.reload(); }} class="w-full mt-8 bg-rose-50 text-rose-600 border border-rose-200 hover:bg-rose-100 font-bold py-3 rounded-xl flex items-center justify-center gap-2 transition-colors">
            <i class="fas fa-sign-out-alt"></i>
            Cerrar Sesión
        </button>
    </div>
  </div>
</div>
