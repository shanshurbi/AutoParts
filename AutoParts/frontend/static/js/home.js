 document.addEventListener("DOMContentLoaded", () => {

                function cargarProductos() {
                const params = new URLSearchParams(window.location.search);

                let url = "/api/productos/";

                fetch(url)
                    .then(res => res.json())
                    .then(productos => {
                    const container = document.getElementById("bestseller");
                    container.innerHTML = '';

                    productos.slice(0, 3).forEach(p => {
                        const card = `
                        <div class="col-lg-6 col-xl-4">
                            <div class="p-4 rounded bg-light">
                                <div class="row align-items-center">
                                    <div class="col-6">
                                        <img src="${p.imagen}" class="img-fluid rounded-circle w-100" alt="Pastillas de Freno">
                                    </div>
                                    <div class="col-6">
                                        <a href="#" class="h5">${p.nombre}</a>
                                        <div class="d-flex my-3">
                                            <i class="fas fa-star text-primary"></i>
                                            <i class="fas fa-star text-primary"></i>
                                            <i class="fas fa-star text-primary"></i>
                                            <i class="fas fa-star-half-alt text-primary"></i>
                                            <i class="fas fa-star"></i>
                                        </div>
                                        <h4 class="mb-3">$${p.precio}</h4>
                                        <a href="/producto/${p.id}" class="btn border border-secondary rounded-pill px-3 text-primary">
                                            <i class="fa fa-shopping-bag me-2 text-primary"></i> ver producto
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

                cargarProductos();
            });