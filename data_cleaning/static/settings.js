$(document).ready(function(){
    $("#OutlierAction").change(function(){
        var action = $(this).val()
        $.ajax({
            type: "POST",
            contentType: "application/json; charset=utf-8",
            url: '/settings',
            data: JSON.stringify({settingname: "outlieraction", action: action})
          });
    })
    $("#DuplicateAction").change(function(){
        var action = $(this).val()
        $.ajax({
            type: "POST",
            contentType: "application/json; charset=utf-8",
            url: '/settings',
            data: JSON.stringify({settingname: "duplicateaction", action: action})
          });
    })
    $("#NullAction").change(function(){
        var action = $(this).val()
        $.ajax({
            type: "POST",
            contentType: "application/json; charset=utf-8",
            url: '/settings',
            data: JSON.stringify({settingname: "nullaction", action: action})
          });
    })
    $("#FutureDateAction").change(function(){
        var action = $(this).val()
        $.ajax({
            type: "POST",
            contentType: "application/json; charset=utf-8",
            url: '/settings',
            data: JSON.stringify({settingname: "futuredateaction", action: action})
          });
    })
    $("#DateFormat").change(function(){
        var format = parseInt($(this).val())
        $.ajax({
            type: "POST",
            contentType: "application/json; charset=utf-8",
            url: '/settings',
            data: JSON.stringify({settingname: "dateformat", format: format})
          });
    })
    $("#ForeignKeyAction").change(function(){
        var action = $(this).val()
        $.ajax({
            type: "POST",
            contentType: "application/json; charset=utf-8",
            url: '/settings',
            data: JSON.stringify({settingname: "foreignkeyaction", action: action})
          });
    })
    $("#DenialConstraintAction").change(function(){
        var action = $(this).val()
        $.ajax({
            type: "POST",
            contentType: "application/json; charset=utf-8",
            url: '/settings',
            data: JSON.stringify({settingname: "denialconstraintaction", action: action})
          });
    })
    $("#FunctionalDependencyAction").change(function(){
        var action = $(this).val()
        $.ajax({
            type: "POST",
            contentType: "application/json; charset=utf-8",
            url: '/settings',
            data: JSON.stringify({settingname: "functionaldependencyaction", action: action})
          });
    })
})