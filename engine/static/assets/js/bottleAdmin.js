 $(function () {
     $(".empty").click(function () {
                this_empty = $(this);
                if ($(this_empty).is(':checked')) {
                    console.log("checked");
                    console.log($(this_empty).attr('name'));
                    empty_object = $(this_empty).attr('name');
                    $.ajax({
                        statusCode: {
                            500: function () {
                                $(this_empty).prop('checked', false);
                            }
                        },
                        url: 'bottle-modify-parameter',
                        type: 'POST',
                        data: {'empty': true, 'solenoidValve': empty_object},
                        datatype: 'json',
                        success: function (empty) {
                            if (empty.empty !== 'ok') {
                                $(this_empty).prop('checked', false);
                            }
                        }
                    });
                }
                else {
                    console.log("unchecked");
                    console.log($(this_empty).attr('name'));
                    empty_object = $(this_empty).attr('name');
                    $.ajax({
                        statusCode: {
                            500: function () {
                                $(this_empty).prop('checked', true);
                            }
                        },
                        url: 'bottle-modify-parameter',
                        type: 'POST',
                        data: {'empty': false, 'solenoidValve': empty_object},
                        datatype: 'json',
                        success: function (empty) {
                            if (empty.empty !== 'ok') {
                                $(this_empty).prop('checked', true);
                            }
                        }
                    });
                }

            });

  $(document).on('input', '.step', function() {
      this_step = $(this);
      empty_object = $(this_step).attr('name');
      $.ajax({
          url: 'bottle-modify-parameter',
          type: 'POST',
          data: {'step': this_step.val(), 'solenoidValve': empty_object},
          datatype: 'json',
          success: function (empty) {
              if (empty.empty !== 'ok') {
                  console.log('error')
              }
          }
      });
  });
 });