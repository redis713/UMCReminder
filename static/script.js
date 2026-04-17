var modal, modalMessage, modalForm, noA;

document.addEventListener("DOMContentLoaded", function () {
    modal = document.getElementById("modal");
    modalMessage = document.getElementById("modal-message");
    noBtn = document.getElementById("no-a");
    yesBtn = document.getElementById("yes-a")


    for_delete();
    for_complete();
    for_cancel();
});


function for_delete() {
    document.querySelectorAll(".btn-delete").forEach(btn => {
      btn.addEventListener("click", () => {
        if (btn.dataset.type == "user")
            modalMessage.textContent = "Точно удалить пользователя?"
        else
            modalMessage.textContent = "Точно удалить задачу?";
        yesBtn.href = btn.dataset.url;
        modal.style.display = "flex";
      });
    });
}


function for_complete() {
    document.querySelectorAll(".btn-complete").forEach(btn => {
      btn.addEventListener("click", () => {
        modalMessage.textContent = "Отметить задачу как выполненную?";
        yesBtn.href = btn.dataset.url;
        modal.style.display = "flex";
      });
    });
}


function for_cancel() {
    noBtn.addEventListener("click", () => {
      modal.style.display = "none";
    });
}
