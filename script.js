const toggle = document.getElementById("themeToggle");
const body = document.body;

toggle.onclick = () => {
    body.classList.toggle("dark");
    body.classList.toggle("light");

    toggle.textContent = body.classList.contains("dark") ? "☀️" : "🌙";
};