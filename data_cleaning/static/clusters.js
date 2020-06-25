$(document).ready(function(){
    $(".cluster-filter").change(function(){
        var filter = $(this).val()
        var column = $(this).data("column")
        var selector = ".cluster-"
        selector = selector.concat(column)
        $.each($(selector), function(){
            var percentage = parseFloat($(this).data("percentage"))
            if (percentage > filter){
                $(this).hide()
            }
            else{
                $(this).show()
            }
        })
    })
    $("#start-clustering").click(function(){
        var table = $(this).data("table")
        var url = "/cluster/"
        url = url.concat(table)
        $("#main-container").hide()
        $("#waiting-div").show()
        $.ajax({
            type: "GET",
            url: url,
            success: function(data, status){
                window.location.href = window.location.href
            },
            error: function(data, status){
                window.location.href = window.location.href
            }
          });
    })
    $(".cluster-select").change(function(){
        var selected = $(this).is(":checked")
        var cluster_id = parseInt($(this).val())
        var column = $(this).data("column")
        var table = $(this).data("table")
        var url = "/setclusterselect/"
        url = url.concat(table, "/", column)
        $.ajax({
            type: "POST",
            contentType: "application/json; charset=utf-8",
            url: url,
            data: JSON.stringify({id: cluster_id, checked: selected})
          });
    })
    $(".new-cluster-value").change(function(){
        var column = $(this).data("column")
        var table = $(this).data("table")
        var url = "/setclusterreplaceby/"
        url = url.concat(table, "/", column)
        var new_value = $(this).val()
        var cluster_id = $(this).data("id")
        $.ajax({
            type: "POST",
            contentType: "application/json; charset=utf-8",
            url: url,
            data: JSON.stringify({id: cluster_id, replaceby: new_value})
          });
    })
    $(".split-cluster").click(function(){
        var column = $(this).data("column")
        var table = $(this).data("table")
        var url = "/splitcluster/"
        url = url.concat(table, "/", column)
        var clusterid = $(this).data("clusterid")
        var selector = ".clusteritem-".concat(clusterid.toString())
        var strings_new_cluster = []
        var selected_items = $(selector.concat(" input[type=checkbox]:checked"))
        var all_items = $(selector.concat(" input[type=checkbox]"))
        if (selected_items.length > 0 && selected_items.length < all_items.length){
            $(selector).each(function(index, element){
                var input = jQuery(this).find("input")
                var labels = jQuery(this).find("label")
                if (input.length > 0 && input[0].checked && labels.length > 0){
                    $(this).remove()
                    var string = labels[0].attributes[2].value
                    strings_new_cluster.push(string)
                }
            })
            if (strings_new_cluster.length > 0){
                $.ajax({
                    type: "POST",
                    contentType: "application/json; charset=utf-8",
                    url: url,
                    data: JSON.stringify({clusterid: clusterid, strings: strings_new_cluster}),
                    success: function(data, status){
                        var rowselector = "#".concat(column, "-cluster-row-", clusterid)
                        var row = $(rowselector)
                        var part1 = `
                            <tr id="${column}-cluster-row-${data['id']}" class="cluster-${column}" data-percentage="${data['max_occurrences_percentage']}">
                                <td>
                                <input value="${data['id']}" type="checkbox" class="cluster-select" data-column="${column}" data-table="${table}" checked>
                                </td>     
                                <td>`


                        for (var i = 0; i < data["content"].length; i++){
                            var item = data["content"][i]  // dict with keys value and duplicates
                            var value = item["value"]
                            var duplicates = item["duplicates"]
                            part1 = part1.concat(`
                                <div class="clusteritem-${data['id']}">
                                    <input type="checkbox" id="${value}" data-clusterid="${data['id']}"/>
                                    <label for="${value}" style="margin-bottom: 0px;" data-value="${value}">${value} (${duplicates} rows)</label>
                                    <br/>
                                </div>
                            `)
                        }

                        var last_part = `
                                <button type="button" data-toggle="tooltip" data-placement="right" title="Move selected strings to a seperate cluster" class="btn btn-sm btn-link split-cluster" data-clusterid="${data['id']}" data-column="${column}" data-table="${table}">Split</button>
                                </td>
                                <td><input type="text" value="${data['replaceby']}" data-id="${data['id']}" data-column="${column}" data-table="${table}" class="form-control form-control-sm new-cluster-value"></td>
                            </tr>
                            `

                        var html_content = part1.concat(last_part)
                        row.after(html_content);
                    }
                  });
            }
        }
    })
})
