
document.addEventListener("DOMContentLoaded", function () {
    const menu = document.querySelector(".menu");
    const menuWrapper = document.querySelector(".hamburger-menu");
    const hamburgerIcon = document.querySelector(".hamburger-icon");
    const closeButton = document.querySelector(".close-btn");
  
    // メニュー開閉
    hamburgerIcon.addEventListener("click", function () {
      menu.classList.toggle("active");
      menuWrapper.classList.toggle("active");
    });
  
    // 閉じるボタンでメニューを閉じる
    closeButton.addEventListener("click", function () {
      menu.classList.remove("active");
      menuWrapper.classList.remove("active");
    });
  });