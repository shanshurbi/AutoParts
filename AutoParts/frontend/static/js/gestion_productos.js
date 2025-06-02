
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
      cookie = cookie.trim();
      if (cookie.startsWith(name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

const csrftoken = getCookie('csrftoken');
const token = localStorage.getItem("token");
if (!token) {
  window.location.href = "/login/";
}

function formatearCLP(valor) {
  return `$${valor.toLocaleString('es-CL')}`;
}

function cargarProductos() {
  fetch(URL_PRODUCTOS_API, {
    headers: {
      "Authorization": "Token " + token
    }
  })
    .then(res => res.json())
    .then(productos => {
      const tbody = document.getElementById("productos-lista");
      tbody.innerHTML = '';
      productos.forEach(p => {
        const fila = `
          <tr>
            <td>${p.nombre}</td>
            <td>${p.descripcion}</td>
            <td>${formatearCLP(p.precio)}</td>
            <td>${formatearCLP(p.precio_mayorista)}</td>
            <td>${p.stock}</td>
            <td><img src="${p.imagen || ''}" alt="${p.nombre}" style="max-height: 50px;"></td>
            <td>
              <button class="btn btn-sm btn-warning me-1" onclick="mostrarFormularioModificar(${p.id})">Modificar</button>
              <button class="btn btn-sm btn-danger" onclick="eliminarProducto(${p.id})">Eliminar</button>
            </td>
          </tr>
        `;
        tbody.innerHTML += fila;
      });
    })
    .catch(err => console.error("Error cargando productos:", err));
}

function mostrarFormularioModificar(id) {
  fetch(`/api/productos/${id}/`, {
    headers: {
      "Authorization": "Token " + token
    }
  })
    .then(res => res.json())
    .then(p => {
      const form = document.getElementById('form-producto');
      form.dataset.editId = id;  

      form.nombre.value = p.nombre;
      form.precio.value = p.precio;
      form.precio_mayorista.value = p.precio_mayorista;
      form.descripcion.value = p.descripcion;
      form.stock.value = p.stock;
      form.categoria.value = p.categoria; 
    })
    .catch(console.error);
}

function limpiarFormulario() {
  const form = document.getElementById('form-producto');
  form.reset();
  delete form.dataset.editId;
}

document.getElementById('form-producto').addEventListener('submit', function (e) {
  e.preventDefault();

  const form = e.target;
  const editId = form.dataset.editId;
  const url = editId ? `/api/productos/${editId}/` : '/api/productos/';
  const method = editId ? 'PUT' : 'POST';

  const formData = new FormData(form);

  fetch(url, {
    method,
    headers: {
      'X-CSRFToken': csrftoken,
      'Authorization': 'Token ' + token
    },
    body: formData,
  })
  .then(res => {
    if (!res.ok) {
      return res.json().then(errorData => {
        console.error("Errores del servidor:", errorData);
        alert('Error al guardar producto: ' + JSON.stringify(errorData));
        throw new Error('Error en la petición');
      });
    }
    return res.json();
  })
  .then(data => {
    alert(editId ? 'Producto modificado' : 'Producto agregado');
    limpiarFormulario();
    cargarProductos();
  })
  .catch(err => {
    console.error(err);
    alert('Error al guardar producto');
  });
});

function eliminarProducto(id) {
  if (!confirm('¿Seguro que quieres eliminar este producto?')) return;

  fetch(`/api/productos/${id}/`, {
    method: 'DELETE',
    headers: {
      'X-CSRFToken': csrftoken,
      'Authorization': 'Token ' + token
    }
  })
  .then(res => {
    if (res.ok) {
      alert('Producto eliminado');
      cargarProductos();
    } else {
      alert('Error al eliminar producto');
    }
  })
  .catch(console.error);
}

document.addEventListener('DOMContentLoaded', cargarProductos);
