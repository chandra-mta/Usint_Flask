//Functions with jQuery 1.12 dependence
jQuery.noConflict();
jQuery(document).ready(function(){
    // jQuery goes here;
    jQuery("#openDither").click(function(){
        jQuery("#ditherDiv").slideDown('fast');
    });
    jQuery("#closeDither").click(function(){
        jQuery("#ditherDiv").slideUp('fast');
    });
    jQuery("#openTime").click(function(){
        jQuery("#timeDiv").slideDown('fast');
    });
    jQuery("#closeTime").click(function(){
        jQuery("#timeDiv").slideUp('fast');
    });
    jQuery("#openRoll").click(function(){
        jQuery("#rollDiv").slideDown('fast');
    });
    jQuery("#closeRoll").click(function(){
        jQuery("#rollDiv").slideUp('fast');
    });
    
    jQuery("#openWindow").click(function(){
        console.log(jQuery(this));
        console.log(jQuery('#windowDiv'));
        jQuery("#windowDiv").slideDown('fast');
    });
    jQuery("#closeWindow").click(function(){
        console.log(jQuery(this));
        console.log(jQuery('#windowDiv'));
        jQuery("#windowDiv").slideUp('fast');
    });

    jQuery("#openACIS").click(function(){
        jQuery(".ACISDiv").slideDown('fast');
        jQuery(".HRCDiv").slideUp('fast');
    });
    jQuery("#openHRC").click(function(){
        jQuery(".HRCDiv").slideDown('fast');
        jQuery(".ACISDiv").slideUp('fast');
    });

    jQuery("#addTime").click(function(){
        addRank("template_time_ranks","time_ranks");
    });

    jQuery("#addRoll").click(function(){
        addRank("template_roll_ranks","roll_ranks");
    });

    jQuery("#addWindow").click(function(){
        addRank("template_window_ranks","window_ranks");
    });

    jQuery(".removeRow").click(function(){
        //ID for row removal is substring of clicked remove button id.
        var removeIDarr = jQuery(this).attr('id').split('-');
        //Selection of table and row number
        var removeID = removeIDarr[0] + "-" + removeIDarr[1];
        jQuery(`#${removeID}`).remove();
        //Rename all ranks in the table
        jQuery(`#${removeIDarr[0]} tbody`).find("tr").each(function(index){
            renameTableRow(jQuery(this),removeIDarr[0], index);
        });
    });
    
  });

function addRank(template_name, rank_list) {
    //Select set of rows in rank list table
    var rows = jQuery(`#${rank_list} tbody`).children("tr");
    var rowCount = rows.length;
    //Clone a new row from rank list template hidden in div
    var timeRowClone = jQuery(`#${template_name} table tr`).clone(true, true);
    renameTableRow(timeRowClone, rank_list, rowCount);
    jQuery(`#${rank_list} tbody`).append(timeRowClone);
};

function renameTableRow(row, rank_list, index){
    var rowID = `${rank_list}-${index}`;
    // Rename the row id
    row.attr({'id': rowID});
    // Change the displayed index
    row.children("th").text(`${index}`);
    // Rename and ReID the templated form input cells
    row.find("select, input").each(function(){
        //Find input type and use to construct new ID and Name
        var inputTypeArr = jQuery(this).attr('id').split('-');
        var inputType = inputTypeArr[inputTypeArr.length - 1];
        jQuery(this).attr({
            'id': `${rowID}-${inputType}`,
            'name': `${rowID}-${inputType}`
        });
    });
};