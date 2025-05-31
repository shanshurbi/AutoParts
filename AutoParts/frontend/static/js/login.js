document.getElementById("login-form").addEventListener("submit", async function(e) {
      e.preventDefault();

      const email = document.querySelector('input[name="username"]').value;
      const password = document.querySelector('input[name="password"]').value;

      const response = await fetch("/api/login/", {
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
      console.log(data); 

      if (response.ok) {
        localStorage.setItem("token", data.token);
        window.location.href = "{% url 'home' %}";
      } else {
        alert(data.error || 'Error desconocido'); 
      }
    });