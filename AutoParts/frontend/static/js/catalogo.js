document.addEventListener("DOMContentLoaded", () => {
            const selectOrden = document.getElementById("ordenar-select");

            function cargarProductos() {
            const params = new URLSearchParams(window.location.search);
            const categoria = params.get("categoria");
            const orden = params.get("orden");

            if (selectOrden && orden) {
                selectOrden.value = orden;
            }

            let url = "/api/productos/";
            if (categoria || orden) {
                url += "?";
                if (categoria) url += `categoria=${categoria}&`;
                if (orden) url += `orden=${orden}`;
            }

            fetch(url)
                .then(res => res.json())
                .then(productos => {
                const container = document.getElementById("productos-container");
                container.innerHTML = '';

                productos.forEach(p => {
                    console.log("Productp:", p);
                    const card = `
                    <div class="col-md-6 col-lg-6 col-xl-4">
                        <a href="/producto/${p.id}" class="text-decoration-none">
                        <div class="rounded position-relative fruite-item">
                            <div class="fruite-img">
                            <img src="${p.imagen}" class="img-fluid w-100 rounded-top" alt="${p.nombre}">
                            </div>
                            <div class="text-white bg-secondary px-3 py-1 rounded position-absolute" style="top: 10px; left: 10px;">${p.nombre_categoria}</div>
                            <div class="p-4 border border-secondary border-top-0 rounded-bottom">
                            <h4>${p.nombre}</h4>
                            <p>${p.descripcion}</p>
                            <div class="d-flex justify-content-between flex-lg-wrap">
                                <p class="text-dark fs-5 fw-bold mb-0">$${p.precio}</p>
                                <button onclick="agregarAlCarrito(${p.id})" class="btn border border-secondary rounded-pill px-3 text-primary">
                                <i class="fa fa-shopping-bag me-2 text-primary"></i> Añadir al carro
                                </button>
                            </div>
                            </div>
                        </div>
                        </a>
                    </div>`;
                    container.innerHTML += card;
                });
                })
                .catch(err => console.error("Error cargando productos:", err));
            }

            if (selectOrden) {
            selectOrden.addEventListener("change", () => {
                const orden = selectOrden.value;
                const params = new URLSearchParams(window.location.search);

                if (orden) {
                params.set("orden", orden);
                } else {
                params.delete("orden");
                }

                const nuevaUrl = `${window.location.pathname}?${params.toString()}`;
                window.history.replaceState({}, '', nuevaUrl);
                cargarProductos();
            });
            }

            cargarProductos();
        });
        function agregarAlCarrito(productoId) {
            fetch('/carrito/agregar/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Token ' + localStorage.getItem('token')
                },
                body: JSON.stringify({ producto_id: productoId })
            })
            .then(response => response.json())
            .then(data => {
                if (data.error === 'No autenticado') {
                    window.location.href = '/login/';
                } else if (data.error) {
                    alert(data.error);
                } else {
                    alert('Producto agregado al carrito');
                    actualizarContadorCarrito();
                }
            })
            .catch(err => {
                console.error("Error:", err);
                alert('Error al agregar producto');
            });
        }
        function mostrarNotificacion(mensaje, tipo = 'success') {
        const notif = document.createElement('div');
        notif.className = `alert alert-${tipo === 'error' ? 'danger' : 'success'} fixed-top m-3`;
        notif.style.zIndex = 9999;
        notif.innerText = mensaje;
        document.body.appendChild(notif);

        setTimeout(() => {
            notif.remove();
        }, 3000);
        }
        function actualizarContadorCarrito() {
        fetch('/carrito/contador/')
        .then(res => res.json())
        .then(data => {
            const contador = document.getElementById('carrito-contador');
            if (contador) {
                contador.innerText = data.cantidad;
            }
        });
        }