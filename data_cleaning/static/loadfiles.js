$(document).ready(function(){
    $("#submit-import").click(function(){
        var input = document.getElementById("fileInput")
        if (!input){
            // submission without a file being loaded
            return
        }
        else{
            // Get the files being loaded
            var loaded_files = []
            $("#imported-files li").each(function(i){
                loaded_files.push($(this).text())
            })
            // If file not already loaded, add it to loaded files
            for (var i = 0; i < input.files.length; i++){
                var filename = input.files[i].path
                if (! loaded_files.includes(filename)){
                    $("#imported-files").append(`<li>${filename}</li>`)
                }
            }
        }
    })
    $("#process-tables").click(function(){
        // Get the files being loaded
        var loaded_files = []
        $("#imported-files li").each(function(i){
            loaded_files.push($(this).text())
        })
        
        /*
            TODO: send ajax request here and redirect (set window location) to returned URL
        */
        $.ajax({
            type: "POST",
            contentType: "application/json; charset=utf-8",
            url: '/',
            data: JSON.stringify({files: loaded_files}),
            success: function(data, status){
                window.location.href = data
            }
        });
    })
})
