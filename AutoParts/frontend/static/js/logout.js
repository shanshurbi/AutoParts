document.getElementById('logout-btn').addEventListener('click', async () => {
  try {
    await fetch('/logout/', {
      method: 'GET',
      credentials: 'include'
    });
  } catch (error) {
    console.error("Error cerrando sesión en el backend:", error);
  }

  localStorage.clear();
  window.location.href = "/";
});
