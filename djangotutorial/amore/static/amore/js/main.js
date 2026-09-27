/*
 * Amore Di Ramos - JavaScript del lado del cliente
 * -------------------------------------------------
 * 1) Filtro en vivo del catálogo de productos (sin recargar la página).
 * 2) Confirmación antes de eliminar un producto.
 *
 * No reemplaza ninguna validación de backend: Django sigue validando
 * y protegiendo las rutas de creación/edición/eliminación en el servidor.
 * Esto solo mejora la experiencia de uso en el navegador.
 */

document.addEventListener("DOMContentLoaded", function () {
    inicializarFiltroProductos();
    inicializarConfirmacionEliminar();
});

function inicializarFiltroProductos() {
    const input = document.getElementById("filtro-productos");
    const grid = document.getElementById("grid-productos");
    if (!input || !grid) return;

    const tarjetas = Array.from(grid.querySelectorAll(".producto-tile"));
    const mensajeSinResultados = document.getElementById("sin-resultados-filtro");

    input.addEventListener("input", function () {
        const termino = input.value.trim().toLowerCase();
        let visibles = 0;

        tarjetas.forEach(function (tarjeta) {
            const nombre = tarjeta.dataset.nombre || "";
            const tipo = tarjeta.dataset.tipo || "";
            const coincide = nombre.includes(termino) || tipo.includes(termino);
            tarjeta.classList.toggle("oculto-por-filtro", !coincide);
            if (coincide) visibles += 1;
        });

        if (mensajeSinResultados) {
            mensajeSinResultados.style.display = visibles === 0 ? "block" : "none";
        }
    });
}

function inicializarConfirmacionEliminar() {
    const formulariosEliminar = document.querySelectorAll(".form-eliminar-producto");
    formulariosEliminar.forEach(function (form) {
        form.addEventListener("submit", function (evento) {
            const confirmado = window.confirm(
                "¿Seguro que quieres eliminar este producto? Esta acción no se puede deshacer."
            );
            if (!confirmado) {
                evento.preventDefault();
            }
        });
    });
}
