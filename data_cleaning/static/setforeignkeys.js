$(document).ready(function(){
    $(".foreignkey.checkbox").change(function(){
        var checked_value = $(this).is(':checked')
        var url = "/setforeignkey"
        $.ajax({
            type: "POST",
            contentType: "application/json; charset=utf-8",
            url: url,
            data: JSON.stringify({id: $(this).val(), checked: checked_value})
          });
    })
})