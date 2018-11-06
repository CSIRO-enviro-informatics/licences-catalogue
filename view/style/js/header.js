jQuery.noConflict();

jQuery(document).ready(function ($) {
    window.bindHeader = function () {

        // Variables.
        $speed = 200;
        $responsiveWidth = 1050;
        $menuDropDown = $(".menu__dropdown");
        $menuDropDownControl = $(".menu__dropdown__control");
        $modalbackground = $(".modal__bg");
        $header = $("header");
        $headerNavWrapper = $(".header-nav__wrapper");
        $navMobileMenu = $(".nav__mobile--menu");
        $body = $("body");


        // Opens the dropdown menus.
        function openMenu(object) {
            if ($(document).width() > $responsiveWidth) {
                if (!object.closest(".menu__dropdown__control").hasClass("active")) {
                    // Closes all other open menus.
                    $menuDropDown.slideUp().closest(".menu__dropdown__control").removeClass("active");
                    // Open the menu being hovered.
                    object.closest(".menu__dropdown__control").addClass("active")
                           .find(".menu__dropdown").slideDown().attr("aria-hidden","false");
                }
            }
        }

        // Closes the draw if a user clicks the background.
        $modalbackground.click(function (e) {
            if (($(e.target).closest('.header').length == 0) && ($('.menu-open').length > 0)){
                $navMobileMenu.trigger( "click" );
                return false;
            }
        });

        // Opens the header drop down menus.
        if ($menuDropDownControl.length > 0) {
            $menuDropDownControl.find("a").hover(function () {
                openMenu($(this));
            });

            $menuDropDownControl.find("a").focus(function () {
                openMenu($(this));
            });

            // Opens the menu in responsive view.
            $(".menu__dropdown__control").find("a").unbind("click").click(function () {
               if ($(document).width() <= $responsiveWidth) {
                    if (!$(this).closest(".menu__dropdown__control").hasClass("mobile-dropdown-active")) {
                        // Slides the menu open.
                        $(this).closest(".menu__dropdown__control").addClass("mobile-dropdown-active")
                            .find(".menu__dropdown").slideDown($speed);

                    } else {
                        // Slides the menu closed.
                        $(this).closest(".menu__dropdown__control").removeClass("mobile-dropdown-active")
                            .find(".menu__dropdown").slideUp($speed);
                    }
                    return false;
                }
            });
        }

        // Closes the header drop down menus.
        $(".menu__dropdown__control").mouseleave(function () {
            if ($(document).width() > $responsiveWidth) {
                if ($(this).closest(".menu__dropdown__control").hasClass("active")) {
                    $(this).closest(".menu__dropdown__control").find(".menu__dropdown__link").removeClass("active");
                    $menuDropDown.hide().closest(".menu__dropdown__control").removeClass("active")
                        .find("ul").attr("aria-hidden", "true");

                }
            }
        });

        $header.find(".contextual-navigation").find("a").eq(0).unbind("click").click(function() {
            openMenu(object);
            return false;
        });

        // Opens/Closes the mobile draw.
        $navMobileMenu.unbind("click").click(function(){
            if($header.hasClass("menu-open")) {
                $header.removeClass("menu-open");
                $headerNavWrapper.hide("slide", { direction: "left" }, 200);
                $modalbackground.hide().removeClass('active');
                $body.removeClass('freeze');
                $navMobileMenu.removeClass("open").attr('aria-expanded','false').find('.sr-only').text("Open site navigation");
            } else {
                // Closes the search if it is open
                if($body.hasClass("search__active")) {
                    $(".nav__mobile--search").trigger("click");
                }
                $header.addClass("menu-open");
                $headerNavWrapper.show("slide", { direction: "left" }, 200);
                $modalbackground.show().addClass('active');
                $body.addClass('freeze');
                $(".header-nav__wrapper").find("ul").find("a").eq(0).focus();
                $navMobileMenu.addClass("open").attr('aria-expanded', 'true').find('.sr-only').text("Close site navigation");
            }

            return false;
        });

        // Closes the mobile draw if the window is resized.
        $(window).resize(function(){
            if($header.hasClass("menu-open")) {
                $header.removeClass("menu-open");
                $headerNavWrapper.hide("slide", { direction: "left" }, 200);
                $modalbackground.hide().removeClass('active');
                $body.removeClass('freeze');
                $navMobileMenu.removeClass("open");
            }
        });
    }
    bindHeader();
});
