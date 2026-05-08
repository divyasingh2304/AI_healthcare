function validateForm() {
    const mobile = document.getElementById("mobile").value;
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    const confirmPassword = document.getElementById("confirm_password").value;
    const errorMsg = document.getElementById("error-msg");

    errorMsg.innerText = "";

    // Mobile validation
    if (!/^[0-9]{10}$/.test(mobile)) {
        errorMsg.innerText = "Mobile number must be 10 digits.";
        return false;
    }

    // Gmail validation
    if (!email.endsWith("@gmail.com")) {
        errorMsg.innerText = "Only Gmail IDs are allowed.";
        return false;
    }

    // Password match
    if (password !== confirmPassword) {
        errorMsg.innerText = "Passwords do not match.";
        return false;
    }

    return true;
}

function checkStrength() {
    const password = document.getElementById("password").value;
    const strengthText = document.getElementById("strength-text");

    if (password.length < 6) {
        strengthText.innerText = "Weak Password";
        strengthText.style.color = "red";
    }
    else if (password.match(/[A-Z]/) && password.match(/[0-9]/)) {
        strengthText.innerText = "Strong Password";
        strengthText.style.color = "green";
    }
    else {
        strengthText.innerText = "Medium Password";
        strengthText.style.color = "orange";
    }
}

function togglePassword(id) {
    const input = document.getElementById(id);
    input.type = input.type === "password" ? "text" : "password";
}
