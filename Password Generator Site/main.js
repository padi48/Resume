let chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
let password = document.getElementById("password");
let pw = "";
let button = document.getElementById("gbutton");
let s = document.getElementById("strength");
let copybutton = document.getElementById("cbutton");
let special = document.getElementById("special");
let allcaps = document.getElementById("allcaps");


function makepw() {
    pw = "";
    pwlength = 0;

    if (s.value == "0"){
        pwlength = 6;
    } 
    else if (s.value == "1") {
        pwlength = 8;
    } 
    else {
        pwlength = 10;
    }

    for (var i = 0; i < pwlength; i++) {
        pw += chars.charAt(Math.floor(Math.random() * chars.length));
    }

    password.innerHTML = pw;
    
    return pw

}

function copypw() {
    navigator.clipboard.writeText(pw);
}

button.onclick = makepw;
copybutton.onclick = copypw;
