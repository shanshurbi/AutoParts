
async function asegurarToken() {
  let token = localStorage.getItem("token");
  if (!token || token === "undefined" || token === "null" || token.trim() === "") {
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
        localStorage.removeItem("token");
        window.location.href = "/login/";
        return null;
      }
    } catch (error) {
      localStorage.removeItem("token");
      window.location.href = "/login/";
      return null;
    }
  }
  return token;
}

document.addEventListener("DOMContentLoaded", async () => {
  const token = await asegurarToken();
  if (!token) return;

  // 🔹 Cargar perfil (si es necesario)
  try {
    const response = await fetch("/api/perfil/", {
      headers: {
        "Authorization": "Token " + token
      }
    });

    if (!response.ok) {
      localStorage.removeItem("token");
      window.location.href = "/login/";
      return;
    }

    const data = await response.json();
    const usernameElem = document.getElementById("username");
    const emailElem = document.getElementById("email");

    if (usernameElem) usernameElem.textContent = data.usuario;
    if (emailElem) emailElem.textContent = data.email;
  } catch (error) {
    console.error("Error al obtener perfil:", error);
    localStorage.removeItem("token");
    window.location.href = "/login/";
  }

  // 🔹 Evento de logout
  const logoutBtn = document.getElementById('logout-btn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', async () => {
      try {
        await fetch('/logout/', { method: 'GET', credentials: 'include' });
      } catch (e) {
        console.warn("No se pudo cerrar sesión en el backend.");
      }
      localStorage.clear();
      window.location.href = "/";
    });
  }

  // 🔹 Cargar carrito
  try {
    const res = await fetch("/api/carrito/", {
      headers: { "Authorization": "Token " + token }
    });

    if (!res.ok) throw new Error("Error al obtener el carrito");

    const data = await res.json();
    const carrito = data.carrito;
    const tbody = document.getElementById("carrito-body");
    const mensajeVacio = document.getElementById("mensaje-vacio");

    tbody.innerHTML = "";

    if (carrito.length === 0) {
      mensajeVacio.style.display = "block";
      return;
    }

    mensajeVacio.style.display = "none";

    carrito.forEach(item => {
      const fila = document.createElement("tr");
      const subtotal = (item.precio * item.cantidad).toLocaleString("es-CL", {
        style: "currency",
        currency: "CLP"
      });
      fila.innerHTML = `
        <td>${item.producto}</td>
        <td>$${item.precio.toLocaleString("es-CL")}</td>
        <td>${item.cantidad}</td>
        <td>${subtotal}</td>
      `;
      tbody.appendChild(fila);
    });

  } catch (err) {
    console.error("❌ Error cargando carrito:", err);
  }
});

