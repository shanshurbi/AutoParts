document.addEventListener("DOMContentLoaded", async function () {
    const token = localStorage.getItem("token");

    if (!token) {
      window.location.href = "{% url 'login' %}";
      return;
    }

    const response = await fetch("/api/perfil/", {
      headers: {
        "Authorization": "Token " + token
      }
    });

    if (!response.ok) {
      localStorage.removeItem("token");
      window.location.href = "{% url 'login' %}";
      return;
    }

    const data = await response.json();
    document.getElementById("username").textContent = data.usuario;
    document.getElementById("email").textContent = data.email;
  });

  document.getElementById('logout-btn').addEventListener('click', () => {
    localStorage.removeItem('token');
    window.location.href = "{% url 'home' %}";
  });