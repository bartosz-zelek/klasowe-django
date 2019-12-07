String.prototype.escapeDiacritics = function() {
    return this.replace(/ą/g, 'a').replace(/Ą/g, 'A') //zmiana polskich znaków
        .replace(/ć/g, 'c').replace(/Ć/g, 'C')
        .replace(/ę/g, 'e').replace(/Ę/g, 'E')
        .replace(/ł/g, 'l').replace(/Ł/g, 'L')
        .replace(/ń/g, 'n').replace(/Ń/g, 'N')
        .replace(/ó/g, 'o').replace(/Ó/g, 'O')
        .replace(/ś/g, 's').replace(/Ś/g, 'S')
        .replace(/ż/g, 'z').replace(/Ż/g, 'Z')
        .replace(/ź/g, 'z').replace(/Ź/g, 'Z');
}

function showError(text) {
    return document.querySelector('#error').innerHTML = text;
}

function generateRandomPassword() {
    const chars = '0123456789abcdefghiklmnopqrstuvwxyz';
    let pass = '';
    for (let i = 0; i < 6; i++) {
        let rand = Math.floor((Math.random() * 35));
        pass += chars.charAt(rand);
    }
    return pass;
}
let adminExist = false; //pierwszy dodany użytkownik to administrator i nie ma możliwości usunięcia go
var realCodeClass = '';
document.querySelector('#addClass').addEventListener('submit', (e) => {
    e.preventDefault();
    document.querySelector('#error').innerHTML = '';
    let name = document.querySelector('#name').value;
    let surname = document.querySelector('#surname').value;
    let validationOK = true;
    if (name != '' && surname != '' && !name.includes(' ') && !surname.includes(' ') && name.length <= 30 && surname.length <= 30 && isNaN(name) && isNaN(surname)) { //poprawność imienia i nazwiska, nan - not a number
        var realName = '';
        realName += name[0].toUpperCase();
        for (let i = 1; i < name.length; i++) {
            realName += name[i].toLowerCase();
        }
        var realSurname = '';
        realSurname += surname[0].toUpperCase();
        for (let i = 1; i < surname.length; i++) {
            realSurname += surname[i].toLowerCase();
        }
    } else {
        showError('<br>Pola nie mogą zawierać spacji oraz znaków specjalnych. Max. długość: 30 znaków.');
        validationOK = false;
    }
    if (adminExist == false) { //jednorazowo przy wstawianiu admina i kodu klasy
        let codeClass = document.querySelector('#codeClass').value.escapeDiacritics();
        if (isNaN(codeClass) && codeClass.length <= 5 && !codeClass.includes(' ') && codeClass != '') { //poprawność kodu klasy
            realCodeClass += codeClass.toLowerCase();
        } else {
            showError('<br>Niepoprawny kod klasy lub rocznik.');
            validationOK = false;
        }
        if (adminExist == false && validationOK == true) { //walidacja kodu klasy przepiegła pomyślnie
            document.querySelector('#classValues').style.display = 'none';
            document.querySelector('#title').innerHTML = 'Dodaj płatników do klasy';
            document.querySelector('#info').innerHTML = '';
            document.querySelector('#addClass').className = 'border border-primary rounded w-25 p-3';
            document.querySelector('#makeClass').style.display = "inline-block";
            adminExist = true;
        }
    }

    if (validationOK == true) { //jeżeli walidacja przebiegła pomyślnie
        adminExist = true;
        let inputs = document.querySelectorAll('input');
        inputs.forEach((el) => { //wyczyszczenie inputów
            if (el.type == 'text')
                el.value = '';
        });
        document.querySelector('#name').focus();
        let usersList = document.querySelector('#usersList');
        let li = document.createElement('li');
        li.className = 'user';
        li.appendChild(document.createTextNode(`${realName} ${realSurname}`));
        //
        if (usersList.firstElementChild != null) {
            let inputDelete = document.createElement('input');
            inputDelete.className = "btn btn-danger btn-sm float-right delete mr-2";
            inputDelete.setAttribute('type', 'button');
            inputDelete.setAttribute('value', 'X');
            inputDelete.setAttribute('style', 'margin-left: -10%');
            li.appendChild(inputDelete);
        }
        //
        usersList.appendChild(li);
        usersList.firstElementChild.style.color = 'red';
        usersList.firstElementChild.style.marginTop = '20px';

    }
});
document.querySelector('#makeClass').addEventListener('click', () => {
    if (confirm('Czy na pewno dodałeś wszystkie osoby i chcesz stworzyć klase?')) {
        const users = document.querySelectorAll('#usersList .user');
        let objUsers = [];
        users.forEach((e) => {
            let nameSurname = e.textContent.split(' ');
            objUsers.push({
                name: nameSurname[0],
                surname: nameSurname[1],
            }, );
        });
        let xhr = new XMLHttpRequest();
        xhr.open('POST', "/add-class/", true);
        let csrftoken = document.querySelector("input[name='csrfmiddlewaretoken']").value;
        xhr.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
        xhr.setRequestHeader('X-CSRFToken', csrftoken);
        xhr.onload = function() {
            if (this.status == 200 && this.responseText != 'False') {
                document.querySelector('.container').innerHTML = '<div class="alert alert-warning mt-5"><span class="error">Uwaga!</span> PDF z loginami i hasłami generowany jest tylko raz. Jeżeli pobieranie nie rozpoczęło się kliknij tu: <a style="color: blue; text-decoration: underline; cursor: pointer"id="download">POBIERZ</a></div>';
                let validatedUsers = JSON.parse(this.responseText);
                let usersPDF = new jsPDF();
                let i = 10;
                validatedUsers.forEach((e) => {
                    usersPDF.text(`${e.name.escapeDiacritics()} ${e.surname.escapeDiacritics()}       Login: ${e.login}       Haslo: ${e.password}`, 10, i);
                    i += 10;
                });

                function download() {
                    usersPDF.save('users.pdf');
                }
                download();
                document.querySelector('#download').addEventListener('click', () => {
                    download();
                });
            }
            else{
                document.querySelector('.container').innerHTML = '<div class="alert alert-danger mt-5">Tworzenie klasy nie powiodło się. Nie modyfikuj skryptu. Jeżeli błąd powtarza się skontaktuj się z administratorem.</div>'
            }
        }
        xhr.send("objUsers=" + JSON.stringify(objUsers) + '&codeClass=' + realCodeClass);
    }
});
document.querySelector('#usersList').addEventListener('click', (e) => {
    if (e.target.classList.contains('delete')) {
        e.target.parentElement.remove();
    }
});