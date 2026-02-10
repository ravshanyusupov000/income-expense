function getCsrfToken() {
  const el = document.querySelector('meta[name="csrf-token"]');
  return el ? el.getAttribute("content") : "";
}


async function sendSupport() {
  const subject = document.querySelector("#support-subject").value.trim();
  const message = document.querySelector("#support-message").value.trim();
  const phoneInput = form.querySelector('input[name="phone"]');
  const phoneError = document.getElementById("phoneError");
  const res = await fetch("{% url 'finance:support_quick_create' %}", {

    function validatePhone(){
      const v = (phoneInput.value || "").trim();
      const ok = /^\+998\d{9}$/.test(v);

      if(!ok){
        phoneError.classList.remove("d-none");
        return false;
      }
      phoneError.classList.add("d-none");
      return true;
    }

    phoneInput.addEventListener("input", () => {
      phoneInput.value = phoneInput.value.replace(/(?!^\+)[^\d]/g, "");
      validatePhone();
    });


  const res = await fetch("/api/support/", {
    method: "POST",
    credentials: "same-origin",
    headers: {
      "X-CSRFToken": getCsrfToken(),
      "X-Requested-With": "XMLHttpRequest",
      "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
    },
    body: new URLSearchParams({ subject, message }).toString(),
  });

  const text = await res.text();
  console.log("Support response:", res.status, text);

  if (!res.ok) throw new Error(text);

  const data = JSON.parse(text);
  if (data.ok) {
    alert("Send");
  } else {
    alert(data.error || "{% trans 'error' %}");
  }
}

document.querySelector("#support-send").addEventListener("click", () => {
  sendSupport().catch((e) => {
    alert("{% trans 'Network error' %}");
    console.log(e);
  });
});
