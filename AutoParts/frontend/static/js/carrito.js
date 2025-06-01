  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      const cookies = document.cookie.split(";");
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.startsWith(name + "=")) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  function eliminarDelCarrito(productoId) {
    const token = localStorage.getItem("token");
    const csrftoken = getCookie("csrftoken");

    fetch(`/carrito/remover/${productoId}/`, {
      method: "POST",
      headers: {
        "Authorization": "Token " + token,
        "X-CSRFToken": csrftoken,
      },
    })
    .then(response => {
      if (!response.ok) {
        throw new Error("No se pudo eliminar el producto");
      }

      location.reload();
    })
    .catch(error => {
      console.error(error);
      alert("Error al eliminar el producto del carrito.");
    });
  }

  document.addEventListener("DOMContentLoaded", async function () {
    const token = localStorage.getItem("token");

    if (!token) {
      window.location.href = "{% url 'login' %}";
      return;
    }

    try {
      const response = await fetch("/api/carrito/", {
        headers: {
          "Authorization": "Token " + token
        }
      });

      if (!response.ok) {
        throw new Error("Token inválido o expirado");
      }

      const data = await response.json();
      const carritoItems = data.carrito;

      const tbody = document.querySelector("tbody");
      tbody.innerHTML = "";

      if (carritoItems.length === 0) {
        document.querySelector(".container").innerHTML = `
          <p>No tienes productos en tu carrito.</p>
        `;
        return;
      }

      carritoItems.forEach(item => {
        const fila = document.createElement("tr");
        fila.innerHTML = `
          <td>${item.producto}</td>
          <td>$${item.precio}</td>
          <td>${item.cantidad}</td>
          <td>$${(item.precio * item.cantidad).toFixed(2)}</td>
          <td>
            <button onclick="eliminarDelCarrito(${item.producto_id})" class="btn btn-danger btn-sm">Eliminar</button>
          </td>
        `;
        tbody.appendChild(fila);
      });

    } catch (error) {
      localStorage.removeItem("token");
      window.location.href = "{% url 'login' %}";
    }
  });