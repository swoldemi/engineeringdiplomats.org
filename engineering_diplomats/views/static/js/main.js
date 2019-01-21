// Hamburger menu for mobile
(function () {
    var burger = document.querySelector(".burger");
    var menu = $("#" + burger.dataset.target);
    burger.addEventListener("click", function () {
        if (menu.is(":visible")) {
            menu.hide(100);
        } else {
            menu.show(100);
        }
        burger.classList.toggle("is-active");
        menu.toggleClass("is-active");
    });

    // Expander for answer submissions
    var answer_expander = $(".answer-expander");
    answer_expander.click(function () {
        var answer_container = $($(this).parent().get(0)).find("form");
        if (answer_container.is(":visible")) {
            answer_container.hide(100);
        } else {
            answer_container.show(100);
            answer_container.css("display", "grid");
        }
    });
})();