$(function () {
    var $makecocktail;
    $makecocktail = $('.makecocktail');
    $makecocktail.on('submit', function (e) {
        e.preventDefault();
        var text = this.cocktail_id.value;
        console.log(text);
        $.ajax({
            url: 'make-cocktail',
            type: 'POST',
            data: {'cocktail_id': text},
            datatype: 'json',
            success: function (task_id) {
                if (task_id.task_id !== 'error') {

                    console.log(task_id);
                    var progressTimer,
                        progressbar = $("#progressbar"),
                        progressLabel = $(".progress-label"),
                        dialogButtons = [{
                            text: "Annuler le cocktail",
                            click: closeDownload
                        }],
                        dialog = $("#dialog").dialog({
                            autoOpen: false,
                            closeOnEscape: false,
                            resizable: false,
                            modal: true,
                            autocomplete: true,
                            buttons: dialogButtons,
                            open: function () {
                                progressTimer = setTimeout(progress, 2000);
                            },
                            close: function () {

                                $("#dialog").dialog('destroy');
                                $(".progress-label").remove();
                                $('#annulate').remove();
                            }

                        });

                    dialog.dialog("open");
                    progressbar.progressbar({
                        value: false,
                        change: function () {
                            progressLabel.text("Progression du cocktail: " + progressbar.progressbar("value") + "%");
                        },
                        complete: function () {
                            progressLabel.text("Complete!");
                            dialog.dialog("option", "buttons", [{
                                text: "Close",
                                click: closeDownload
                            }]);
                            $(".ui-dialog button").last().focus();
                        }
                    });

                    function progress() {
                        var val = progressbar.progressbar("value") || 0;
                        $.ajax({
                            url: 'make-cocktail',
                            type: 'POST',
                            data: {'task_id': task_id.task_id},
                            datatype: 'json', success: function (task_info) {
                                progressbar.progressbar("value", task_info.task_info)
                            }
                        });

                        if (val <= 99) {
                            progressTimer = setTimeout(progress, 400);
                        }
                    }

                    function closeDownload() {
                        clearTimeout(progressTimer);
                        progressbar.progressbar("value", false);
                        progressbar.progressbar("destroy");
                        $(this).append("<p id='annulate'>Cocktail annulé</p>");
                        $('.ui-dialog-buttonpane button:contains("Annuler le cocktail")').button().hide();


                    }


                }
                else {
                    dialog = $("#dialog").dialog({
                        autoOpen: false,
                        closeOnEscape: false,
                        resizable: false,
                        modal: true,
                        autocomplete: true,
                        open: function () {
                            $(this).append("<p id='error'>Impossible de faire le cocktail</p>");

                        },
                        close: function () {
                            $('#error').remove();
                            $("#dialog").dialog('destroy');
                        }

                    });
                    dialog.dialog("open");

                }
            }
        });
    });
});