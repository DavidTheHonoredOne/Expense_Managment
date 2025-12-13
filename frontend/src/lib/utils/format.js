export function formatMoney(amount) {
    // Asegurar que el valor sea numérico
    const numericAmount = typeof amount === 'number' ? amount : parseFloat(amount) || 0;

    // Formatear con puntos de miles SIEMPRE, incluso para valores pequeños
    return new Intl.NumberFormat('es-CO', {
        style: 'currency',
        currency: 'COP',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0,
        // Asegurar formato consistente
        useGrouping: true // Esto fuerza los separadores de miles
    }).format(numericAmount);
}
