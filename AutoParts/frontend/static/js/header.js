document.addEventListener("DOMContentLoaded", function () {
    const loginIcon = document.getElementById("login-icon");

    if (loginIcon) {
      loginIcon.addEventListener("click", function (e) {
        e.preventDefault(); 

        const token = localStorage.getItem("token");

        if (token) {
          
          window.location.href = "{% url 'perfil' %}";
        } else {
          
          window.location.href = "{% url 'login' %}";
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
            // ¿La cookie comienza con el nombre que buscamos?
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

// Ejecutar al cargar la página
document.addEventListener("DOMContentLoaded", actualizarContadorCarrito);