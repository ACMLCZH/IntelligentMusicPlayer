function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
const csrftoken = getCookie("csrftoken");

async function submitForm_sign_in() {
  console.log("Button clicked!");
  event.preventDefault();
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;

  const data = {
    type: "sign_in",
    username: username,
    password: password,
  };
  //   发送POST请求;
  // await sleep(10);
  fetch("/sign_in_sign_up_reset_request", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrftoken,
    },
    body: JSON.stringify(data),
  })
    .then((response) => {
      if (!response.ok)
        throw new Error(`HTTP error! Status: ${response.status}`);
      console.log("Fetch response status:", response.status);
      return response.json();
    })
    .then((data) => {
      document.getElementById("response").innerText = data.response;
      setTimeout(function () {
        document.getElementById("response").innerText = "";
        if (data.redirect) {
          window.location.href = data.redirect_url;
        }
      }, 2000);
    })
    .catch((error) => {
      console.error("Fetch error:", error);
    });
  // .catch((error) => console.error("Error:", error));
}

async function submitForm_sign_up() {
  console.log("Button clicked!");
  event.preventDefault();
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;
  const confirm_password = document.getElementById("confirm_password").value;

  const data = {
    type: "sign_up",
    username: username,
    password: password,
    confirm_password: confirm_password,
  };
  // await sleep(10);
  fetch("/sign_in_sign_up_reset_request", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrftoken,
    },
    body: JSON.stringify(data),
  })
    .then((response) => {
      if (!response.ok)
        throw new Error(`HTTP error! Status: ${response.status}`);
      console.log("Fetch response status:", response.status);
      return response.json();
    })
    .then((data) => {
      document.getElementById("response").innerText = data.response;
      setTimeout(function () {
        document.getElementById("response").innerText = "";
        if (data.redirect) {
          window.location.href = data.redirect_url;
        }
      }, 2000);
    })
    .catch((error) => {
      console.error("Fetch error:", error);
    });
}

async function submitForm_reset() {
  console.log("Button clicked!");
  event.preventDefault();
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;
  const confirm_password = document.getElementById("confirm_password").value;

  const data = {
    type: "reset",
    username: username,
    password: password,
    confirm_password: confirm_password,
  };
  fetch("/sign_in_sign_up_reset_request", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrftoken,
    },
    body: JSON.stringify(data),
  })
    .then((response) => {
      if (!response.ok)
        throw new Error(`HTTP error! Status: ${response.status}`);
      console.log("Fetch response status:", response.status);
      return response.json();
    })
    .then((data) => {
      document.getElementById("response").innerText = data.response;
      setTimeout(function () {
        document.getElementById("response").innerText = "";
        if (data.redirect) {
          window.location.href = data.redirect_url;
        }
      }, 2000);
    })
    .catch((error) => {
      console.error("Fetch error:", error);
    });
}
