
document.addEventListener("DOMContentLoaded", function () {
    function aplicarMascaraCPF(value) {
        return value.replace(/\D/g, "")
        .replace(/(\d{3})(\d)/, "$1.$2")
        .replace(/(\d{3})(\d)/, "$1.$2")
        .replace(/(\d{3})(\d{1,2})$/, "$1-$2");
    }

    function aplicarMascaraTelefone(value) {
        return value.replace(/\D/g, "")
        .replace(/^(\d{2})(\d)/, "($1) $2")
        .replace(/(\d{5})(\d{1,4})$/, "$1-$2");
    }

    function validarNome(nome) {
        return !(nome == "");
    }

    function validarEmail(email) {
        return /^(([^<>()[\]\.,;:\s@\"]+(\.[^<>()[\]\.,;:\s@\"]+)*)|(\".+\"))@(([^<>()[\]\.,;:\s@\"]+\.)+[^<>()[\]\.,;:\s@\"]{2,})$/i.test(email);
    }

    function validarMatricula(matricula) {
        return /^251\d{6}$/.test(matricula);
    }

    function buscarDadosBD(cpf, matricula) {
        console.log(`Sending CPF: ${cpf}, Matricula: ${matricula}`);

        return fetch("/get_student_data", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            cpf: cpf,
            matricula: matricula
        })
        })
        .then(response => response.json())
        .then(data => {
        console.log("Received Data:", data);
        return data;
        })
        .catch(error => {
        console.error("Error:", error);
        return { error: "Erro ao buscar dados" };
        });
    }

    function buscarHorarios(dia) {
        console.log(`Sending Date: ${dia}`);
        
        return fetch("/get_valid_times", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            date: dia,
        })
        })
        .then(response => response.json())
        .then(data => {
        console.log("Received Data:", data);
        return data;
        })
        .catch(error => {
        console.error("Error:", error);
        return { error: "Erro ao buscar dados" };
        });
    }

    function validateForm(){
        if(!validarEmail(email.value)){
            submitButton.disabled = true;
            return false
        }
        if(!validarNome(nomeCompleto.value)){
            submitButton.disabled = true;
            return false
        }
        if(telefone.value.length != 15){
            submitButton.disabled = true;
            return false
        }
        if(has_selected_time == false){
            submitButton.disabled = true;
            return false
        }
        submitButton.disabled = false;
        return true
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
        if(!validarNome(nomeCompleto.value)){
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

    let cpf = document.getElementById("cpf");
    let matricula = document.getElementById("matricula");
    //let telefone = document.getElementById("telefone");
    let nomeCompleto = document.getElementById("nomeCompleto");
    let email = document.getElementById("email");
    let matriculaFeedback = document.querySelector("#matriculaField .invalid-feedback");
    let date = document.getElementById("date");
    let time = document.getElementById("time");
    let comprovante = document.getElementById("comprovante");
    let has_selected_time = false;
    //let telefoneField = document.getElementById("telefoneField");
    let submitButton = document.getElementById("submitButton");
    
    if(date.min < "2026-01-16"){
        date.min = "2026-01-16";
    }

    telefone.addEventListener("input", function () {
        telefone.value = aplicarMascaraTelefone(telefone.value);
        if (telefone.value.length === 15) {
        telefone.classList.remove("is-invalid");
        telefone.classList.add("is-valid");
        } else {
        telefone.classList.remove("is-valid");
        telefone.classList.add("is-invalid");
        }
        validateForm()
    });
    
    email.addEventListener("input", function () {
        if (validarEmail(email.value)) {
        email.classList.remove("is-invalid");
        email.classList.add("is-valid");
        if (telefone.value.length === 15) {
            if (validarNome(nomeCompleto.value)) {
                submitButton.disabled = false;
            }
        }
        } else {
            email.classList.remove("is-valid");
            email.classList.add("is-invalid");
        }
        validateForm()
    });
    
    nomeCompleto.addEventListener("input", function () {
        
        console.log("Nome")
        if (validarNome(nomeCompleto.value)) {
        nomeCompleto.classList.remove("is-invalid");
        nomeCompleto.classList.add("is-valid");
        if (telefone.value.length === 15) {
            if(validarEmail(email.value)){
                submitButton.disabled = false;
            }
        }
        } else {
            nomeCompleto.classList.remove("is-valid");
            nomeCompleto.classList.add("is-invalid");
        }
        validateForm()
    });
    

    date.addEventListener("change", async function(){
        var dia = date.value;
        console.log("Buscando datas");
        var horarios;
        horarios = await buscarHorarios(dia);
        var i;
        while(time.firstChild){
            time.removeChild(time.firstChild)
        }
        var new_option = document.createElement("option");
        new_option.value = "none";
        new_option.innerHTML = "Escolha um Horario";
        new_option.selected = true;
        new_option.disabled = false;
        time.appendChild(new_option)
        for(i=0;i<horarios.length;i++){
            element = horarios[i];
            new_option = document.createElement("option");
            new_option.value = element;
            new_option.innerHTML = element;
            time.appendChild(new_option)
        }
        has_selected_time = false;
        validateForm();
    })

    time.addEventListener("change", function(){
        has_selected_time = true;
        validateForm();
    })

    document.getElementById("dynamicForm").addEventListener("submit", function (event) {
        if (!validateForm()) {
        event.preventDefault();
        }
    });

    document.getElementById("dynamicForm").addEventListener("submit", function (event) {
        event.preventDefault(); // Evita o envio padrão do formulário
        if(!validateForm()){ return }
        submitButton.disabled = true;
        submitButton.innerHTML = '<table><td><div class="loader"></div></td><td><div>Enviando...</div></td></table>';
        nomeCompleto.disabled=true;
        email.disabled=true;
        telefone.disabled=true;
        date.disabled=true;
        time.disabled=true;
        fetch("/send_data", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            nome: nomeCompleto.value,
            email: email.value,
            telefone: telefone.value,
            date: date.value,
            time: time.value
        })
        })
        .then(response => response.json())
        .then(data => {
        console.log("Received Data:", data);
        window.location.href = data.url;
        })
        .catch(error => {
        matricula.classList.add("is-invalid");
        matriculaFeedback.textContent = data.error;
        });
        // Redireciona para a página de sucesso
    });

    document.getElementById("consultForm").addEventListener("submit", function (event) {
        if (!validateForm()) {
        event.preventDefault();
        }
    });

    document.getElementById("consultForm").addEventListener("submit", function (event) {
        event.preventDefault(); // Evita o envio padrão do formulário
        if(!validateForm()){ return }
        fetch("/consult", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            nome: nomeCompleto.value,
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
        .catch(error => {
        matricula.classList.add("is-invalid");
        matriculaFeedback.textContent = data.error;
        });
        // Redireciona para a página de sucesso
    });

    });
