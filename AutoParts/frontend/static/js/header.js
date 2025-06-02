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
            // 😈 Maldad: ir primero al carrito y luego al perfil
            localStorage.setItem("redirectAfterCarrito", "/perfil");
            window.location.href = "/carrito/";
          } else {
            localStorage.removeItem("token");
            window.location.href = "/login";
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

  const carritoLink = document.getElementById("carrito-link");
  const carritoIcon = document.getElementById("carrito-icon");

  if (carritoLink) {
    carritoLink.addEventListener("click", (e) => verificarSesionYRedirigir(e, "/carrito/"));
  }

  if (carritoIcon) {
    carritoIcon.addEventListener("click", (e) => verificarSesionYRedirigir(e, "/carrito/"));
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

async function verificarSesionYRedirigir(event, destino) {
  event.preventDefault();

  let token = localStorage.getItem("token");

  if (!token) {
    try {
      const response = await fetch("/api/login/from-session/", {
        method: "GET",
        credentials: "include"
      });

      if (response.ok) {
        const data = await response.json();
        token = data.token;
        localStorage.setItem("token", token);
      } else {
        window.location.href = "/login";
        return;
      }
    } catch (error) {
      console.error("Error al obtener token desde sesión:", error);
      window.location.href = "/login";
      return;
    }
  }

  try {
    const validar = await fetch("/api/perfil/", {
      headers: { "Authorization": `Token ${token}` }
    });

    if (validar.ok) {
      window.location.href = destino;
    } else {
      localStorage.removeItem("token");
      window.location.href = "/login";
    }
  } catch (error) {
    console.error("Error al validar token:", error);
    window.location.href = "/login";
  }
}
