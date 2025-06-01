const API_BASE = window.location.origin; // http://localhost:8000

  document.getElementById("login-form").addEventListener("submit", async function(e) {
    e.preventDefault();

    const email = document.querySelector('input[name="username"]').value;
    const password = document.querySelector('input[name="password"]').value;

    const response = await fetch(`${API_BASE}/api/login/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": "{{ csrf_token }}"
      },
      body: JSON.stringify({
        usuario: email,
        contraseña: password
      })
    });

    const data = await response.json();

    if (response.ok) {
      localStorage.setItem("token", data.token);
      window.location.href = "/";
    } else {
      alert(data.error || 'Error desconocido');
    }
  });