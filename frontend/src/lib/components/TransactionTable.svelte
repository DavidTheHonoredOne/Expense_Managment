<script>
  export let transactions = [];
  export let onEdit;
  export let onDelete;

  const formatDate = (dateStr) => {
    if(!dateStr) return '';
    const date = new Date(dateStr);
    return date.toLocaleDateString('es-CO', { day: '2-digit', month: 'short', year: 'numeric' });
  };
  
  const formatCurrency = (amount) => {
      return new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP' }).format(amount);
  };

  const downloadCSV = () => {
    let csv = "Fecha,Categoría,Descripción,Cuenta,Monto,Tipo\n";

    transactions.forEach(t => {
      const fecha = formatDate(t.fecha);
      const categoria = t.nombre_categoria || 'General';
      const descripcion = t.descripcion || '';
      const cuenta = t.nombre_cuenta || '';
      const monto = t.monto;
      const tipo = t.tipo || 'gasto';

      csv += `"${fecha}","${categoria}","${descripcion}","${cuenta}",${monto},"${tipo}"\n`;
    });

    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', 'movimientos.csv');
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };
</script>

<div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm overflow-x-auto">
  <div class="flex justify-between items-center p-4 border-b border-gray-200 dark:border-gray-700">
    <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Movimientos</h3>
    <button on:click={downloadCSV} class="text-gray-500 border border-gray-300 hover:bg-gray-50 dark:text-gray-400 dark:border-gray-600 dark:hover:bg-gray-700 px-3 py-1 rounded-md text-sm transition-colors">
      <i class="fas fa-download mr-1"></i> Exportar CSV
    </button>
  </div>
  <table class="w-full text-left text-sm text-gray-500 dark:text-gray-400">
    <thead class="bg-gray-50 dark:bg-gray-700 text-gray-700 dark:text-gray-200 uppercase text-xs">
      <tr>
        <th class="px-6 py-3">Fecha</th>
        <th class="px-6 py-3">Categoría</th>
        <th class="px-6 py-3 hidden md:table-cell">Descripción</th>
        <th class="px-6 py-3 hidden md:table-cell">Cuenta</th>
        <th class="px-6 py-3 text-right">Monto</th>
        <th class="px-6 py-3 text-center">Acciones</th>
      </tr>
    </thead>
    <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
      {#each transactions as t}
        <tr class="hover:bg-gray-50 dark:hover:bg-gray-700/50 transition">
          <td class="px-6 py-4">{formatDate(t.fecha)}</td>
          <td class="px-6 py-4">
            <span class="bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 px-2 py-1 rounded text-xs">
               {t.nombre_categoria || 'General'}
            </span>
          </td>
          <td class="px-6 py-4 text-gray-900 dark:text-white hidden md:table-cell">{t.descripcion || ''}</td>
          <td class="px-6 py-4 hidden md:table-cell">{t.nombre_cuenta || ''}</td>
          <td class="px-6 py-4 text-right font-bold {t.tipo && t.tipo.toLowerCase() === 'ingreso' ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-400'}">
            {t.tipo && t.tipo.toLowerCase() === 'ingreso' ? '+' : '-'} {formatCurrency(t.monto)}
          </td>
          <td class="px-6 py-4 text-center">
            <button on:click={() => onEdit(t)} class="text-emerald-600 dark:text-emerald-400 hover:text-emerald-700 dark:hover:text-white mx-1 transition" aria-label="Editar" title="Editar"><i class="fas fa-pencil"></i></button>
            <button on:click={() => onDelete(t.movimiento_id)} class="text-rose-500 dark:text-rose-400 hover:text-rose-700 dark:hover:text-white mx-1 transition" aria-label="Eliminar" title="Eliminar"><i class="fas fa-trash"></i></button>
          </td>
        </tr>
      {:else}
        <tr>
          <td colspan="6" class="text-center py-8 text-gray-500 dark:text-gray-400">No hay movimientos recientes.</td>
        </tr>
      {/each}
    </tbody>
  </table>
</div>
