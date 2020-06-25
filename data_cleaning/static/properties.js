$(document).ready(function(){
    $(".outlier-action").change(function(){
        var action = $(this).val()
        var column = $(this).data('column')
        var table = $(this).data('table')
        var url = '/properties/'
        url = url.concat(table)
        $.ajax({
            type: "POST",
            contentType: "application/json; charset=utf-8",
            url: url,
            data: JSON.stringify({settingname: "outlieraction", action: action, column: column})
          });
    })
    $(".outlier-range .min").change(function(){
        var min = $(this).val()
        var colname = $(this).data('column')
        var table = $(this).data('table')
        var datatype = $(this).data('type')
        var selector = '#range-'.concat(colname, '.max')
        var max = $(selector).val()
        if ((datatype == 'number' && min <= max) || (datatype=='date' && Date.parse(min) <= Date.parse(max))){
            $.data(this, 'previousvalue', $(this).val())
            var url = '/properties/'
            url = url.concat(table)
            $.ajax({
                type: "POST",
                contentType: "application/json; charset=utf-8",
                url: url,
                data: JSON.stringify({settingname: "outlierrange-min", min: min, column: colname, type: datatype})
              });
        }
        else {
            $(this).val($(this).data('previousvalue'))
        }
    })
    $(".outlier-range .max").change(function(){
        var max = $(this).val()
        var colname = $(this).data('column')
        var table = $(this).data('table')
        var datatype = $(this).data('type')
        var selector = '#range-'.concat(colname, '.min')
        var min = $(selector).val()
        if ((datatype == 'number' && min <= max) || (datatype=='date' && Date.parse(min) <= Date.parse(max))){
            $.data(this, 'previousvalue', $(this).val())
            var url = '/properties/'
            url = url.concat(table)
            $.ajax({
                type: "POST",
                contentType: "application/json; charset=utf-8",
                url: url,
                data: JSON.stringify({settingname: "outlierrange-max", max: max, column: colname, type: datatype})
              });
        }
        else{
            $(this).val($.data(this, 'previousvalue'))
        }
    })
    $(".null-action").change(function(){
        var action = $(this).val()
        var column = $(this).data('column')
        var table = $(this).data('table')
        var url = '/properties/'
        url = url.concat(table)
        $.ajax({
            type: "POST",
            contentType: "application/json; charset=utf-8",
            url: url,
            data: JSON.stringify({settingname: "nullaction", action: action, column: column})
          });
    })
    $(".futuredate-action").change(function(){
        var action = $(this).val()
        var column = $(this).data('column')
        var table = $(this).data('table')
        var url = '/properties/'
        url = url.concat(table)
        $.ajax({
            type: "POST",
            contentType: "application/json; charset=utf-8",
            url: url,
            data: JSON.stringify({settingname: "futuredateaction", action: action, column: column})
          });
    })
    $(".date-format").change(function(){
        var format = parseInt($(this).val())
        var column = $(this).data('column')
        var table = $(this).data('table')
        var url = '/properties/'
        url = url.concat(table)
        $.ajax({
            type: "POST",
            contentType: "application/json; charset=utf-8",
            url: url,
            data: JSON.stringify({settingname: "date-format", format: format, column: column})
          });
    })
})