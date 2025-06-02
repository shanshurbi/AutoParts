document.addEventListener("DOMContentLoaded", async function () {
  const token = localStorage.getItem("token");

  if (!token) {
    return window.location.href = "/login/";
  }

  try {
    const response = await fetch("/api/perfil/", {
      headers: {
        "Authorization": "Token " + token
      }
    });

    if (!response.ok) {
      localStorage.removeItem("token");
      return window.location.href = "/perfil/";
    }

    const data = await response.json();

    // Asegurarse de que los elementos existen antes de intentar llenarlos
    const usernameElem = document.getElementById("username");
    const emailElem = document.getElementById("email");

    if (usernameElem) usernameElem.textContent = data.usuario;
    if (emailElem) emailElem.textContent = data.email;

  } catch (error) {
    console.error("Error al obtener perfil:", error);
    localStorage.removeItem("token");
    window.location.href = "/login/";
  }

  // Evento para cerrar sesión
  const logoutBtn = document.getElementById('logout-btn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', async () => {
      try {
        await fetch('/logout/', {
          method: 'GET',
          credentials: 'include'
        });
      } catch (e) {
        console.warn("No se pudo cerrar sesión en el backend.");
      }

      localStorage.clear(); // Limpieza total
      window.location.href = "/";
    });
  }
});
