// Função para o formulário de login
document.getElementById("login-form")?.addEventListener("submit", async (e) => {
    e.preventDefault();

    const username = document.getElementById("login-username").value;
    const password = document.getElementById("login-password").value;

    try {
        const response = await fetch("/login", {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: new URLSearchParams({
                username: username,
                password: password
            })
        });

        if (!response.ok) {
            throw new Error("Credenciais inválidas");
        }

        const data = await response.json();
        localStorage.setItem("token", data.access_token);
        window.location.href = "page-team.html";
    } catch (error) {
        alert(error.message);
    }
});

// Função para o formulário de cadastro
document.getElementById("register-form")?.addEventListener("submit", async (e) => {
    e.preventDefault();

    const username = document.getElementById("register-username").value;
    const email = document.getElementById("register-email").value;
    const password = document.getElementById("register-password").value;
    const confirmPassword = document.getElementById("register-password2").value;

    // Validação de senha
    if (password !== confirmPassword) {
        document.getElementById("error-message").textContent = "As senhas não coincidem.";
        return;
    }

    try {
        const response = await fetch("/register", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, email, password })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || "Erro ao registrar usuário");
        }

        const data = await response.json();
        alert("Usuário registrado com sucesso! Verifique seu e-mail para confirmar.");
        window.location.href = "page-login.html"; // Redireciona para a página de login
    } catch (error) {
        document.getElementById("error-message").textContent = error.message;
    }
});

// Função para verificar o token na página verify-email.html
document.addEventListener("DOMContentLoaded", async () => {
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get("token");

    if (!token) {
        document.getElementById("message").textContent = "Token não encontrado.";
        document.getElementById("details").textContent = "Por favor, verifique o link fornecido.";
        return;
    }

    try {
        const response = await fetch(`/verify-email?token=${token}`);
        const data = await response.json();

        if (data.detail) {
            document.getElementById("message").textContent = "Erro";
            document.getElementById("details").textContent = data.detail;
        } else {
            document.getElementById("message").textContent = "E-mail verificado!";
            document.getElementById("details").textContent = data.message;
            document.getElementById("redirect-link").classList.remove("d-none");
            document.getElementById("redirect-link").href = "/static/page-login.html";
        }
    } catch (error) {
        document.getElementById("message").textContent = "Erro";
        document.getElementById("details").textContent = "Ocorreu um erro ao verificar o token.";
    }
});
