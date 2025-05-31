document.addEventListener("DOMContentLoaded", function () {
    const loginIcon = document.getElementById("login-icon");

    if (loginIcon) {
        loginIcon.addEventListener("click", async function (e) {
            e.preventDefault();

            const token = localStorage.getItem("token");

            if (token) {
                try {
                    const response = await fetch("/api/perfil/", {
                        headers: {
                            "Authorization": `Token ${token}`
                        }
                    });

                    if (response.ok) {
                        window.location.href = "/perfil";  // Usuario autenticado
                    } else {
                        localStorage.removeItem("token");
                        window.location.href = "/login";   // Token inválido
                    }
                } catch (error) {
                    console.error("Error al validar token:", error);
                    window.location.href = "/login";
                }
            } else {
                window.location.href = "/login";
            }
        });
    }
});

function actualizarContadorCarrito() {
    fetch('/carrito/')
        .then(response => response.text())
        .then(html => {
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const items = doc.querySelectorAll('.carrito-item').length;
            document.getElementById('cart-count').innerText = items;
        })
        .catch(error => {
            console.error('Error actualizando el contador del carrito:', error);
        });
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function getCSRFToken() {
    return getCookie("csrftoken");
}

function verificarSesionYRedirigir(event, destino) {
    event.preventDefault();
    const token = localStorage.getItem("token");

    if (token) {
        // Validar token con la API
        fetch("/api/perfil/", {
            headers: {
                "Authorization": `Token ${token}`
            }
        })
        .then(response => {
            if (response.ok) {
                window.location.href = destino;
            } else {
                localStorage.removeItem("token");
                window.location.href = "/login";
            }
        })
        .catch(() => {
            window.location.href = "/login";
        });
    } else {
        window.location.href = "/login";
    }
}

document.addEventListener("DOMContentLoaded", function () {
    const carritoLink = document.getElementById("carrito-link");
    const carritoIcon = document.getElementById("carrito-icon");

    if (carritoLink) {
        carritoLink.addEventListener("click", (e) => verificarSesionYRedirigir(e, "/carrito/"));
    }

    if (carritoIcon) {
        carritoIcon.addEventListener("click", (e) => verificarSesionYRedirigir(e, "/carrito/"));
    }
});