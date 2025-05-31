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
                if (!container) return;

                container.innerHTML = '';

                productos.forEach(p => {
                    const card = `
                        <div class="col-md-6 col-lg-6 col-xl-4">
                            <div class="rounded position-relative fruite-item">
                                <div class="fruite-img">
                                    <img src="img/fruite-item-5.jpg" class="img-fluid w-100 rounded-top" alt="${p.nombre}">
                                </div>
                                <div class="text-white bg-secondary px-3 py-1 rounded position-absolute" style="top: 10px; left: 10px;">${p.categoria}</div>
                                <div class="p-4 border border-secondary border-top-0 rounded-bottom">
                                    <h4>${p.nombre}</h4>
                                    <p>${p.descripcion}</p>
                                    <div class="d-flex justify-content-between flex-lg-wrap">
                                        <p class="text-dark fs-5 fw-bold mb-0">$${p.precio}</p>
                                        <a href="#" onclick="agregarAlCarrito({{ producto.id }})" class="btn border border-secondary rounded-pill px-3 text-primary">
                                            <i class="fa fa-shopping-bag me-2 text-primary"></i> Añadir al carro
                                        </a>
                                    </div>
                                </div>
                            </div>
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
        document.querySelectorAll('.agregar-carrito-btn').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const productoId = this.getAttribute('data-producto-id');
            agregarAlCarrito(productoId);
        });
        });
        function agregarAlCarrito(productoId) {
        fetch('/carrito/agregar/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': '{{ csrf_token }}'
            },
            body: JSON.stringify({ producto_id: productoId }),
            credentials: 'include'
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