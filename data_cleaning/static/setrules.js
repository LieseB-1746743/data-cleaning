$(document).ready(function(){
    $("#waiting-div").css({"display": "none!important"})
    $("#main-container").show()
    $(".clustercolumns").change(function(){
        var tablename = $('#tablename').text()
        var checked_value = $(this).is(':checked')
        var url = "/setclustercolumns/"
        url = url.concat(tablename)
        $.ajax({
            type: "POST",
            contentType: "application/json; charset=utf-8",
            url: url,
            data: JSON.stringify({column: $(this).val(), checked: checked_value})
          });
    })
    $(".denialconstraint").change(function(){
        var tablename = $('#tablename').text()
        var checked_value = $(this).is(':checked')
        var url = "/setdenialconstraint/"
        url = url.concat(tablename)
        $.ajax({
            type: "POST",
            contentType: "application/json; charset=utf-8",
            url: url,
            data: JSON.stringify({id: $(this).val(), checked: checked_value})
          });
    })
    $("#addUniqueConstraint").click(function(){
        // get all checked checkboxes
        var tablename = $('#tablename').text()
        var url = "/uniqueconstraint/"
        url = url.concat(tablename)
        var columns = []
        $.each($("#uniqueConstraintForm input[name='column']:checked"), function(){
            columns.push($(this).val())
        })
        if (columns.length > 0){
            // Send new constraint to backend
            $.ajax({
                type: "POST",
                contentType: "application/json; charset=utf-8",
                url: url,
                data: JSON.stringify({data: columns, action: "add"}),
                success: function(newID) {
                    // append to list
                    $("#uniqueConstraintForm input[name='column']:checked").each(function(){
                        this.checked = false
                    })
                    $("#uniqueConstraints").append(`<li id='${newID.toString()}'>${columns}<button class='deleteUniqueConstraint btn' value='${newID.toString()}'><i class='fas fa-trash-alt'></i></button></li>`)
                    $("#noUniqueConstraints").hide()
                }
              });
          }
    })
    $("#uniqueConstraints").on('click', '.deleteUniqueConstraint', function(){
        var id = $(this).val()
        var tablename = $('#tablename').text()
        var url = "/uniqueconstraint/"
        url = url.concat(tablename)
        $.ajax({
            type: "POST",
            contentType: "application/json; charset=utf-8",
            url: url,
            data: JSON.stringify({id: id, action: "delete"}),
            success: function() {
                var selector = "#".concat(id)
                $(selector).remove()
                if ($('.deleteUniqueConstraint').length == 0){
                    $("#noUniqueConstraints").show()
                }
            }
          });
    })
    $("#clean").click(function(){
        var table_to_clean = $(this).data("table")
        var url = "/clean/"
        url = url.concat(table_to_clean)
        $("#clean").prop('disabled', true)
        $.ajax({
            type: "GET",
            url: url,
            success: function() {
                $("#clean").prop('disabled', false)
                var text = "Successfully cleaned table ".concat(table_to_clean)
                $("#success-cleaned-message").text(text)
                $("#clean-success").fadeIn()
            },
            error: function(){
                $("#clean").prop('disabled', false)
                var text = "An error occurred while cleaning table ".concat(table_to_clean, ", watch the console for more details.")
                $("#error-cleaned-message").text(text)
                $("#clean-error").fadeIn()
            }
        });
    })
    $('#select-all').click(function(){
        $(".functional-dependency:checkbox").each(function(i, obj){
            $(this).prop("checked", true);
            var tablename = $('#tablename').text()
            var checked_value = $(this).is(':checked')
            var url = "/setfunctionaldependency/"
            url = url.concat(tablename)
            $.ajax({
                type: "POST",
                contentType: "application/json; charset=utf-8",
                async: false,
                url: url,
                data: JSON.stringify({id: $(this).val(), checked: checked_value})
              });
        })
    })
    $('#unselect-all').click(function(){
        $(".functional-dependency:checkbox").each(function(i, obj){
            $(this).prop("checked", false);
            var tablename = $('#tablename').text()
            var checked_value = $(this).is(':checked')
            var url = "/setfunctionaldependency/"
            url = url.concat(tablename)
            $.ajax({
                type: "POST",
                contentType: "application/json; charset=utf-8",
                async: false,
                url: url,
                data: JSON.stringify({id: $(this).val(), checked: checked_value})
              });
        })
    })
    $(".functional-dependency").change(function(){
        var tablename = $('#tablename').text()
        var checked_value = $(this).is(':checked')
        var url = "/setfunctionaldependency/"
        url = url.concat(tablename)
        $.ajax({
            type: "POST",
            contentType: "application/json; charset=utf-8",
            url: url,
            data: JSON.stringify({id: $(this).val(), checked: checked_value})
          });
    })
})
