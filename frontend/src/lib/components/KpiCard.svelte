<script>
  export let title;
  export let value;
  export let color = 'text-gray-900 dark:text-white';
  export let subtext = '';

  // Clean value to check if it's negative
  function isNegativeValue(val) {
    if (!val) return false;
    // Remove any currency symbols or formatting
    const cleaned = val.toString().replace(/[^-\d.]/g, '');
    const numeric = parseFloat(cleaned);
    return !isNaN(numeric) && numeric < 0;
  }
</script>

<div class="bg-white dark:bg-gray-800 p-6 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm transition-colors duration-300">
  <p class="text-gray-500 dark:text-gray-400 text-sm mb-1">{title}</p>
  <div class="flex items-center gap-2">
    {#if isNegativeValue(value)}
      <span class="text-rose-600 dark:text-rose-500 text-xl">⚠️</span>
    {/if}
    <h3 class="text-3xl font-bold {isNegativeValue(value) ? 'text-rose-600 dark:text-rose-500' : color}">{value}</h3>
  </div>
  {#if subtext}
    <span class="text-xs text-gray-500 dark:text-gray-400">{@html subtext}</span>
  {/if}
</div>
