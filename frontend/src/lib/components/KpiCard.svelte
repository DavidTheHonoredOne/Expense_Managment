<script>
  export let title;
  export let value;
  export let color = 'text-gray-900 dark:text-white';
  export let subtext = '';
</script>

<div class="bg-white dark:bg-gray-800 p-6 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm transition-colors duration-300">
  <p class="text-gray-500 dark:text-gray-400 text-sm mb-1">{title}</p>
  <h3 class="text-3xl font-bold {color}">{value}</h3>
  {#if subtext}
    <span class="text-xs text-gray-500 dark:text-gray-400">{@html subtext}</span>
  {/if}
</div>
