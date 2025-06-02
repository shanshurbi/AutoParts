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
        limpiarSesionYRedirigir();
        return null;
      }
    } catch (error) {
      console.error("Error al recuperar token:", error);
      limpiarSesionYRedirigir();
      return null;
    }
  }

  return token;
}

function limpiarSesionYRedirigir() {
  localStorage.removeItem("token");
  sessionStorage.clear();
  window.location.href = "/login/";
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
      if (!response.ok) throw new Error("No se pudo eliminar el producto");
      return fetch("/api/carrito/", {
        headers: { "Authorization": "Token " + token }
      });
    })
    .then(response => response.json())
    .then(data => {
      actualizarTablaCarrito(data.carrito);
    })
    .catch(error => {
      console.error(error);
      alert("Error al eliminar el producto del carrito.");
    });
}

function cambiarCantidad(productoId, accion) {
  const token = localStorage.getItem("token");
  const csrftoken = getCookie("csrftoken");

  const url = `/carrito/${accion}/${productoId}/`;

  fetch(url, {
    method: "POST",
    headers: {
      "Authorization": "Token " + token,
      "X-CSRFToken": csrftoken
    }
  })
    .then(response => {
      if (!response.ok) throw new Error("No se pudo actualizar la cantidad");
      return fetch("/api/carrito/", {
        headers: { "Authorization": "Token " + token }
      });
    })
    .then(response => response.json())
    .then(data => {
      actualizarTablaCarrito(data.carrito);
    })
    .catch(error => {
      console.error(error);
      alert("Error al actualizar la cantidad del producto.");
    });
}

function actualizarTablaCarrito(items) {
  const tbody = document.querySelector("tbody");
  tbody.innerHTML = "";

  if (items.length === 0) {
    document.querySelector(".container").innerHTML = `<p>No tienes productos en tu carrito.</p>`;
    return;
  }

  let total = 0;

  items.forEach(item => {
    const subtotal = item.precio * item.cantidad;
    total += subtotal;

    const fila = document.createElement("tr");
    fila.innerHTML = `
      <td>${item.producto}</td>
      <td>${item.precio.toLocaleString("es-CL", { style: "currency", currency: "CLP" })}</td>
      <td>
        <div class="d-flex justify-content-center align-items-center">
          <button class="btn-cantidad restar px-2 me-2" onclick="cambiarCantidad(${item.producto_id}, 'disminuir')">
            <strong>-</strong>
          </button>
          <span class="mx-2 fw-bold">${item.cantidad}</span>
          <button class="btn-cantidad sumar px-2 ms-2" onclick="cambiarCantidad(${item.producto_id}, 'aumentar')">
            <strong>+</strong>
          </button>
        </div>
      </td>
      <td>${subtotal.toLocaleString("es-CL", { style: "currency", currency: "CLP" })}</td>
    `;

    tbody.appendChild(fila);
  });

  const totalRow = document.createElement("tr");
  totalRow.innerHTML = `
    <td colspan="3" class="text-end fw-bold">Total:</td>
    <td colspan="2" class="fw-bold" id="totalCompra">${total.toLocaleString("es-CL", { style: "currency", currency: "CLP" })}</td>
  `;
  tbody.appendChild(totalRow);

  // ⏺️ Guardar todo en localStorage
  localStorage.setItem("cart", JSON.stringify(items));
  localStorage.setItem("resumen", JSON.stringify({ total }));

  const emailUsuario = document.getElementById("userEmail")?.value;
  if (emailUsuario) {
    localStorage.setItem("cliente", JSON.stringify({ email: emailUsuario }));
  }
}

document.addEventListener("DOMContentLoaded", async function () {
  const token = await asegurarToken();

  if (!token) {
    localStorage.removeItem("carrito");
    window.location.href = "/login/";
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
    actualizarTablaCarrito(data.carrito);
  } catch (error) {
    console.error("Error al cargar el carrito:", error);
    limpiarSesionYRedirigir();
  }
});
document.addEventListener("DOMContentLoaded", function () {
  const btnPagar = document.getElementById("btnConfirmarPago");

  if (btnPagar) {
    btnPagar.addEventListener("click", async function () {
      const metodoSelect = document.getElementById("metodoPago");
      const metodo = metodoSelect ? metodoSelect.value : "";

      if (!metodo) {
        alert("Por favor selecciona un método de pago.");
        return;
      }

      const email = document.getElementById("userEmail")?.value || "";
      const totalTexto = document.getElementById("totalCompra")?.textContent || "";

      // Validar datos mínimos
      if (!email || !totalTexto) {
        alert("Información incompleta. Revisa tu carrito y datos.");
        return;
      }

      // Convertir texto "$12.345" a número entero
      const montoTotal = parseInt(totalTexto.replace(/\D/g, ""));

      try {
        const response = await fetch("/crear_pedido/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken"),
          },
          body: JSON.stringify({
            email: email,
            monto: montoTotal,
            metodo_pago: metodo
          })
        });

        if (!response.ok) throw new Error("Error al crear el pedido");

        const data = await response.json();
        if (data.order_id) {
          localStorage.setItem("order_id", data.order_id);
          window.location.href = `/pagar/${data.order_id}/`;
        } else {
          alert("No se pudo generar el pedido.");
        }
      } catch (error) {
        console.error("Error al procesar el pedido:", error);
        alert("Hubo un error al procesar tu pago.");
      }
    });
  }
});


