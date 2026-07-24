const toggleBtn = document.getElementById("themeToggle");
const body = document.body;
const themeKey = "theme";

const applyTheme = (theme) => {
    body.classList.remove("light", "dark");
    body.classList.add(theme);
    localStorage.setItem(themeKey, theme);

    if (toggleBtn) {
        toggleBtn.innerText = theme === "light" ? "☀️" : "🌙";
    }
};

const savedTheme = localStorage.getItem(themeKey);
applyTheme(savedTheme === "light" ? "light" : "dark");

if (toggleBtn) {
    toggleBtn.addEventListener("click", () => {
        const nextTheme = body.classList.contains("dark") ? "light" : "dark";
        applyTheme(nextTheme);
    });
}

document.addEventListener("keydown", (event) => {
    const activeTag = document.activeElement.tagName;
    if (
        event.key.toLowerCase() === "l" &&
        !event.ctrlKey &&
        !event.metaKey &&
        !event.altKey &&
        !["INPUT", "TEXTAREA", "SELECT"].includes(activeTag)
    ) {
        const nextTheme = body.classList.contains("dark") ? "light" : "dark";
        applyTheme(nextTheme);
    }
});
