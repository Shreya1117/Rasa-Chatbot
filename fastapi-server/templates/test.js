async function get_user_id () {
    let res = await fetch("/users/fetch_id").then((response) => response.json());
    let user_id = res['user_id'];
    localStorage.setItem("user_id", user_id);
    console.log(`After DOM load, set USER_ID ---> ${user_id}`);
    let inputElement = document.getElementById("input");
    inputElement.focus();
}


const textareaElement = document.getElementById("input");
textareaElement.addEventListener("keydown", function (e) {
    if (e.code === "Enter") {
        sendMessage();
}
});

async function sendMessage() {
    const inputElement = document.getElementById("input");
    const message = inputElement.value.trim();
    if (message === "") return;

    const user_id = localStorage.getItem('user_id');
    const messagesElement = document.getElementById("messages");
    const messageElement = document.createElement("div");
    messageElement.innerHTML = "<mark class='user-txt txt'>You</mark> " + message;
    messageElement.classList.add("message");
    messagesElement.appendChild(messageElement);
    messagesElement.scrollTop = messagesElement.scrollHeight;

    inputElement.value = "Waiting for response..."; // Waiting for response
    inputElement.disabled = true;

    const response = await fetch("/predict", {
    method: "POST",
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({"user_id": user_id, "user_message":  message})
});
    if (response.status === 500) {
        window.alert("Session Expired, Please reload to start a new session.");
        inputElement.value = "Sorry, your session has expired.";   // Session Expired
        return;
    }
    const res = (await response.json())["text"];

    setTimeout(function() {
        const replyElement = document.createElement("div");
        replyElement.innerHTML = "<mark class='chatbot-txt txt'>Chatbot</mark> " + res; // Echo back the message
        replyElement.classList.add("message");
        messagesElement.appendChild(replyElement);
        messagesElement.scrollTop = messagesElement.scrollHeight; // Scroll to bottom
    }, 1);

    inputElement.value = ""; // Clear the input
    inputElement.disabled = false;
    inputElement.focus();
}