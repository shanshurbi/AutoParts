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

document.getElementById("register-form").addEventListener("submit", async function(e) {
  e.preventDefault();

  const mensajeError = document.getElementById("mensaje-error");
  mensajeError.style.display = "none";
  mensajeError.textContent = "";

  const username = document.querySelector('input[name="username"]').value.trim();
  const email = document.querySelector('input[name="email"]').value.trim();
  const password = document.querySelector('input[name="password"]').value;
  const passwordConfirm = document.querySelector('input[name="password_confirm"]').value;

  if (password !== passwordConfirm) {
    mensajeError.textContent = "Las contraseñas no coinciden.";
    mensajeError.style.display = "block";
    return;
  }

  const hasUppercase = /[A-Z]/.test(password);
  const hasSymbol = /[!@#$%^&*(),.?":{}|<>]/.test(password);

  if (!hasUppercase || !hasSymbol) {
    mensajeError.textContent = "La contraseña debe contener al menos una letra mayúscula y un símbolo.";
    mensajeError.style.display = "block";
    return;
  }

  const csrftoken = getCookie('csrftoken');

  const response = await fetch("/api/registro/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrftoken
    },
    body: JSON.stringify({
      usuario: username,
      email: email,
      contraseña: password,
      contraseña_confirm: passwordConfirm
    })
  });

  const data = await response.json();

  if (response.ok) {
    localStorage.setItem("token", data.token);
    window.location.href = "/"; // O la URL de tu página de inicio
  } else {
    mensajeError.textContent = data.error || "Error desconocido";
    mensajeError.style.display = "block";
  }
});