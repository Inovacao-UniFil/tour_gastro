
document.addEventListener("DOMContentLoaded", function () {
    function aplicarMascaraTelefone(value) {
        return value.replace(/\D/g, "")
        .replace(/^(\d{2})(\d)/, "($1) $2")
        .replace(/(\d{5})(\d{1,4})$/, "$1-$2");
    }

    function validarEmail(email) {
        return /^(([^<>()[\]\.,;:\s@\"]+(\.[^<>()[\]\.,;:\s@\"]+)*)|(\".+\"))@(([^<>()[\]\.,;:\s@\"]+\.)+[^<>()[\]\.,;:\s@\"]{2,})$/i.test(email);
    }

    function validarComprovante(comprovante){
        return /^CONF\d{6}$/.test(comprovante);
    }

    function validateFormConsulta(){
        if(validarComprovante(comprovante.value)){
            submitButton.disabled = false;
            return true;
        }
        if(!validarEmail(email.value)){
            submitButton.disabled = true;
            return false;
        }
        if(telefone.value.length != 15){
            submitButton.disabled = true;
            return false;
        }
        submitButton.disabled = false;
        return true
    }

    let matricula = document.getElementById("matricula");
    //let telefone = document.getElementById("telefone");
    let email = document.getElementById("email");
    let matriculaFeedback = document.querySelector("#matriculaField .invalid-feedback");
    let comprovante = document.getElementById("comprovante");
    let has_selected_time = false;
    //let telefoneField = document.getElementById("telefoneField");
    let submitButton = document.getElementById("submitButton");
    
    

    telefone.addEventListener("input", function () {
        telefone.value = aplicarMascaraTelefone(telefone.value);
        if (telefone.value.length === 15) {
        telefone.classList.remove("is-invalid");
        telefone.classList.add("is-valid");
        } else {
        telefone.classList.remove("is-valid");
        telefone.classList.add("is-invalid");
        }
        validateFormConsulta()
    });
    
    email.addEventListener("input", function () {
        if (validarEmail(email.value)) {
        email.classList.remove("is-invalid");
        email.classList.add("is-valid");
        } else {
            email.classList.remove("is-valid");
            email.classList.add("is-invalid");
        }
        validateFormConsulta()
    });
    

    comprovante.addEventListener("input", function(){
        if(validateFormConsulta()){
            comprovante.classList.add("is-valid");
            comprovante.classList.remove("is-invalid");
        }else{
            comprovante.classList.remove("is-valid");
            comprovante.classList.add("is-invalid");
        }
    })

    document.getElementById("consultForm").addEventListener("submit", function (event) {
        if (!validateFormConsulta()) {
        event.preventDefault();
        }
    });

    document.getElementById("consultForm").addEventListener("submit", function (event) {
        event.preventDefault(); // Evita o envio padrão do formulário
        if(!validateFormConsulta()){ return }
        fetch("/consult", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            email: email.value,
            telefone: telefone.value,
            comprovante: comprovante.value,
        })
        })
        .then(response => response.json())
        .then(data => {
        console.log("Received Data:", data);
        window.location.href = data.url;
        })
        // Redireciona para a página de sucesso
    });

    });
