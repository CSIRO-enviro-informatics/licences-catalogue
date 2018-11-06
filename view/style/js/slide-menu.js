jQuery.noConflict();
jQuery(document).ready(function ($) {
    window.bindFilter = function () {
        // Opens the responsive nav bar
        $(".btn--navbar-toggle").click(function () {
            $(".sliding-nav").slideToggle("slow", function () {
                // Animation complete.
            });

        });

        // Opens the news filter
        $(".filter--btn__news").click(function () {
            if ($(".btn--filter--clear").is(":visible")) {
                // slides the menu down
                $(".filter--news").slideToggle("slow", function () {

                });

            } else {
                // slides the menu across
                $(".filter--news").toggle('slide', {
                    direction: 'right'
                }, 200);
                if($("body").hasClass("filter-active")) {
                    $.scrollLock( false );
                } else {
                    setTimeout(
                      function()
                      {
                        $.scrollLock( true );
                      },200
                  );
                }
                $(".modal__bg").toggle().toggleClass('active');
                $("body").toggleClass("filter-active");

            }

            $(this).toggleClass( "filter-btn--active");

            return false;
        });

        $(".modal__bg").click(function (e) {
            if (($(e.target).closest('.filter').length == 0) && ($('.filter-active').length > 0)){
                $( ".filter--btn__news" ).trigger( "click" );
                return false;
            }
        });

        /**** Makes sure that if the 'any' option is selected none of the other options are also selected,
        and when an option other than 'any' is selected the 'any' option is automatically unselected ****/
        $(".filter__section").find(".checkbox").click(function () {
            $field = $(this);
            $box = $field.find("input");
            $list = $field.closest(".filter__section").find('ul');
            if($list.hasClass("filter-platforms"))
            {
                if ($box.val() == "Select all") {
                    $list.find(".checkbox").addClass("isChecked");
                    $list.find('input:checkbox').attr('checked', true);
                    $field.addClass("isChecked");
                    $box.attr('checked', false);
                    $box.closest("label").find("span").text("Clear selection");
                    $box.val("Clear selection");
                }
                else if ($box.val() == "Clear selection") {
                    $list.find(".checkbox").removeClass("isChecked");
                    $list.find('input:checkbox').attr('checked', false);
                    $field.removeClass("isChecked");
                    $box.attr('checked', false);
                    $box.closest("label").find("span").text("Select all");
                    $box.val("Select all");
                }
                else
                {
                    if ($field.hasClass('isChecked')) {
                        $field.removeClass("isChecked");
                        $box.attr("checked", false);
                        var scount = $list.find('input:checkbox[checked="checked"]').length;
                        var stcount = $list.find('input:checkbox').length;
                        if (scount <= stcount - 1)
                        {
                            $list.find(".checkbox").eq(0).removeClass("isChecked");
                            $list.find(".checkbox").eq(0).find("span").text("Select all");
                            $list.find('input:checkbox').eq(0).attr('checked', false);
                            $list.find('input:checkbox').eq(0).val("Select all");
                        }
                    } else {
                        $field.addClass("isChecked");
                        $box.attr("checked", true);
                        var xcount = $list.find('input:checkbox[checked="checked"]').length;
                        var tcount = $list.find('input:checkbox').length;
                        if (xcount == tcount -1) {
                            $list.find(".checkbox").eq(0).addClass("isChecked");
                            $list.find(".checkbox").eq(0).find("span").text("Clear selection");
                            $list.find('input:checkbox').eq(0).attr('checked', true);
                            $list.find('input:checkbox').eq(0).val("Clear selection");
                        }
                    }
                }
                return false;
            }
            if ($list.hasClass("filter-dates"))
            {
                $list.find(".checkbox").removeClass("isChecked");
                $list.find('input:checkbox').attr('checked', false);
                $field.addClass("isChecked");
                $box.attr('checked', true);
                return false;
            }
            if ($box.val() == "on") {
                // the All box was checked
                $list.find(".checkbox").removeClass("isChecked");
                $list.find('input:checkbox').attr('checked', false);
                $field.addClass("isChecked");
                $box.attr('checked', true);
            }
            else {
                if ($field.hasClass("isChecked")) {
                    $field.removeClass("isChecked");
                    $box.attr('checked', false);
                } else {
                    $list.find(".checkbox").eq(0).removeClass("isChecked");
                    $list.find('input:checkbox').eq(0).attr('checked', false);
                    console.log($field);
                    $field.addClass("isChecked");
                    $box.attr('checked', true);
                }
                $checked = $box.attr('checked');
                if ($checked != "checked") {
                    var count = $list.find('input:checkbox[checked="checked"]').length;
                    if (count == 0) {
                        // all others were unchecked
                        $list.find(".checkbox").eq(0).addClass("isChecked");
                        $list.find('input:checkbox').eq(0).attr('checked', true);
                    }
                }
            }
            return false;
        });
    }
});
