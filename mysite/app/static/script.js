const existingTabs = new Set(["PROVERS", "VCs", "RESULT"])
const existingTabContent = new Set(["proversContent", "vcsContent", "resultContent"])

function framaOutputHandler(id) {
    var element = document.getElementById(id)

}

function tabsHandler(tabId, toUnhide, codeId = 0) {
    existingTabContent.forEach(element => {
        document.getElementById(element).style.display = "none";
    });

    existingTabs.forEach(element => {
        document.getElementById(element).className = "";
    })

    document.getElementById(toUnhide).style.display = "block";
    document.getElementById(tabId).className = "active";

    if (tabId == "RESULT" && codeId != "None") {
        document.getElementById("actualResultContent").innerHTML = ""
        document.getElementById("loading").style.display = "block";
        $.ajax({
            url: "/resultAction/",
            data: { pk: codeId },
            dataType: "json",
            success: function(data) {
                document.getElementById("loading").style.display = "none";
                document.getElementById("actualResultContent").innerHTML = data.result;
            }
        });
    }
}

function codeHandler(codeId) {
    if (codeId == "pepe") {
        document.getElementById("code").innerHTML = "";
        document.getElementById("pepe").style.display = "block"
    } else {
        $.ajax({
            url: "/showFile/",
            data: { pk: codeId },
            dataType: "json",
            success: function(data) {
                document.getElementById("pepe").style.display = "none";
                var code = "";
                Array.from(data.code).forEach(line => {
                    code += '<span style="background:var(--linenum)">' + line[1] + '  </span>  ' + line[0];
                });
                document.getElementById("code").innerHTML = code;
            }
        });
    }
}

function menuHandler(navName) {
    switch (navName) {
        case "delete":
            document.getElementById("mainpage").style.display = "none";
            document.getElementById("delfile").style.display = "block";
            break;
        case "run":
            break;
        default:
            break;
    }
}

function fileHandler(type) {
    $.ajax({
        url: "/makeFiles/",
        data: {},
        dataType: "json",
        success: function(data) {
            if (type == 'main')
                document.getElementById('files').innerHTML = mainFiles(data);
            else {
                document.getElementById('deleteFiles').innerHTML = deleteFiles(data);
                Array.from(data.directories).forEach(directory => {
                    document.getElementById('deldir_' + directory[0][0]).addEventListener('click', function() { deleteHandler(directory[0][0], 'dir') }, false);
                    Array.from(directory[1]).forEach(file => {
                        document.getElementById('delfile_' + file[0]).addEventListener('click', function() { deleteHandler(file[0], 'file') }, false);
                    })
                })
            }
        }
    });
}

function mainFiles(data) {
    var html = "<ul>";
    Array.from(data.directories).forEach(directory => {
        html += '<li><a class="dir" href="/index/0"><div style="font-weight: bold;" class="leftalign">';
        for (var i = 0; i < directory[0][2]; i++)
            html += '&ensp;';
        html += ' | ' + directory[0][1] + '\\</div></a></li>';

        Array.from(directory[1]).forEach(file => {
            html += '<li><span class="file" onclick="codeHandler(' + file[0] + ')"><div class="leftalign">';
            for (var i = 0; i < directory[0][2]; i++)
                html += '&ensp;';
            html += '&ensp; | ' + file[1] + '</div></span></li>';
        });
    });
    html += '</ul>';
    return html;
}

function deleteFiles(data) {
    var html = "";
    Array.from(data.directories).forEach(directory => {
        html += '<li><a id="deldir_' + directory[0][0] + '" class="dir dela"><div class="leftalign"><div class="unhider">';
        for (var i = 0; i < directory[0][2]; i++)
            html += '&ensp;';
        html += '| ' + directory[0][1] + '</div><div class="hide" style="float:right;">&emsp;&lt;--------</div></div></a></li>';

        Array.from(directory[1]).forEach(file => {
            html += '<li><a id="delfile_' + file[0] + '"class="file dela"><div class="leftalign"><div class="unhider">';
            for (var i = 0; i < directory[0][2]; i++)
                html += '&ensp;';
            html += '&ensp; | ' + file[1] + '</div><div class="hide">&emsp;&lt;--------</div></div></a></li>';
        });
    });
    return html;
}

function deleteHandler(id, type) {
    $.ajax({
        url: type == 'dir' ? "/deleteDirectory/" : "/deleteFile/",
        data: { pk: id },
        dataType: "json",
        success: function(data) {
            fileHandler('main');
            fileHandler('delete');
            document.getElementById("mainpage").style.display = "";
            document.getElementById("delfile").style.display = "none";
        }
    });
}