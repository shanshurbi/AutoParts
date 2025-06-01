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
                            <div class="col-md-6 col-lg-4 loaded">
                                <div class="card h-100 card-hover bg-bestseller border-0 rounded shadow-sm">
                                    <img src="${p.imagen}" class="card-img-top img-fluid rounded-top" alt="${p.nombre}" style="max-height: 250px; object-fit: cover; border-bottom: 4px solid #C1121F;">
                                    <div class="card-body text-center">
                                        <h5 class="card-title text-azul fw-bold">${p.nombre}</h5>
                                        <div class="d-flex justify-content-center my-2">
                                            <i class="fas fa-star"></i>
                                            <i class="fas fa-star"></i>
                                            <i class="fas fa-star"></i>
                                            <i class="fas fa-star"></i>
                                            <i class="fas fa-star text-muted"></i>
                                        </div>
                                        <h4 class="mb-3 text-dark fw-semibold">$${p.precio}</h4>
                                        <a href="/producto/${p.id}" class="btn-bestseller">Ver producto <i class="fas fa-arrow-right ms-1"></i></a>
                                    </div>
                                </div>
                            </div>
                        `;
                        document.getElementById("bestseller").innerHTML += card;
                    });
                    })
                    .catch(err => console.error("Error cargando productos:", err));
                }

                cargarProductos();
            });