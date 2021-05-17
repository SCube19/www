const existingTabs = new Set(["PROVERS", "VCs", "RESULT"])
const existingTabContent = new Set(["proversContent", "vcsContent", "resultContent"])

let prover = "Default";
let enableRte = 'off';
let VCs = "";
let fileId = null;

let framaArr = null;

function framaOutputHandler(event) {
    var id = event.target.id;
    id = id[0] == 'u' ? id.slice(8, id.length) : id.slice(6, id.length);

    //document.getElementById('rolled' + id).style.visibility = document.getElementById('rolled' + id).style.visibility == 'hidden' ? 'visible' : 'hidden';
    //document.getElementById('unrolled' + id).style.visibility = document.getElementById('unrolled' + id).style.visibility == 'hidden' ? 'visible' : 'hidden';
    unroller('rolled' + id);
    unroller('unrolled' + id);
}

function unroller(id) {
    var doc = document.getElementById(id);
    if (doc.style.visibility == 'hidden') {
        doc.style.visibility = 'visible';
        doc.style.maxWidth = '1000px';
        doc.style.maxHeight = '1000px';
    } else {
        doc.style.visibility = 'hidden';
        doc.style.maxHeight = '0';
        doc.style.maxWidth = '0';
    }
}

function tabsHandler(tabId, toUnhide) {
    existingTabContent.forEach(element => {
        document.getElementById(element).style.display = "none";
    });

    existingTabs.forEach(element => {
        document.getElementById(element).className = "";
    })

    document.getElementById(toUnhide).style.display = "block";
    document.getElementById(tabId).className = "active";

    console.log(fileId);
    if (tabId == "RESULT" && fileId != null) {
        document.getElementById("actualResultContent").innerHTML = ""
        document.getElementById("loading").style.display = "block";
        $.ajax({
            url: "/resultAction/",
            data: { pk: fileId },
            dataType: "json",
            success: function(data) {
                document.getElementById("loading").style.display = "none";
                document.getElementById("actualResultContent").innerHTML = data.result;
            }
        });
    } else if (tabId == "RESULT") {
        document.getElementById("actualResultContent").innerHTML = "NO FILE SELECTED";
    }
}

function framaParser(data) {
    var frama = "";
    if (data.framaStringList != null) {
        frama += '------------------------------------------------------------<br>';
        // wrap-content forces one line of code
        let i = 0;
        Array.from(data.framaStringList).forEach(section => {
            frama += '<abbr style="border-bottom: none; cursor: pointer;text-decoration: none;" title="' + section[2] + '"><span class="framaAnimation" id="rolled' + i + '" style="max-height:1000px;max-width:1000px;display:inline-block;visibility:visible;overflow:hidden;background:' + section[1] + ';">' + section[2] + '\n</span><span class="framaAnimation" id="unrolled' + i + '" style="display:inline-block;max-width:0;max-height:0;visibility:hidden;overflow:hidden;background:' + section[1] + ';">' + section[0] + '</span></abbr><span style="display:block;">------------------------------------------------------------</span>';
            i++;
        });
    }
    document.getElementById("frama").innerHTML = frama;

    var arr = Array.from(data.framaStringList);
    framaArr = Array.from(Array(arr.length).keys());
    for (var i = 0; i < arr.length; i++) {
        document.getElementById('rolled' + i).addEventListener('click', framaOutputHandler, false);
        document.getElementById('unrolled' + i).addEventListener('click', framaOutputHandler, false);
    }
}

function codeHandler(codeId) {
    document.getElementById("code").innerHTML = "";
    document.getElementById("pepeimg").src = "/static/pepe.png";
    document.getElementById("pepe").style.display = "block";
    document.getElementById("frama").innerHTML = "";
    fileId = null;

    if (codeId != 'pepe') {
        document.getElementById("pepeimg").src = "/static/load.gif";
        $.ajax({
            url: "/showFile/",
            data: { pk: codeId },
            dataType: "json",
            success: function(data) {
                var code = "";
                Array.from(data.code).forEach(line => {
                    code += '<span style="background:var(--linenum)">' + line[1] + '  </span>  ' + line[0];
                });
                document.getElementById("pepe").style.display = "none";
                document.getElementById("code").innerHTML = code;
                framaParser(data);
                fileId = codeId;
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
            if (fileId != null) {
                document.getElementById("run").style.background = 'green';
                $.ajax({
                    url: "/runFrama/",
                    data: { 'pk': fileId, 'prover': prover, 'flags': VCs, 'enableRte': enableRte },
                    dataType: "json",
                    success: function(data) {
                        framaParser(data);
                        document.getElementById("run").style.background = '';
                    }
                });
            }
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
        html += '<li><a class="dir"><div style="font-weight: bold;" class="leftalign">';
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
        html += '<li><a style="cursor:pointer;" id="deldir_' + directory[0][0] + '" class="dir dela"><div class="leftalign"><div class="unhider">';
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

function flagHandler() {
    prover = document.getElementById('chosenProver').value;
    enableRte = document.getElementById('enableRte').checked;
    VCs = document.getElementById('flgs').value;
    document.getElementById('currProver').innerHTML = prover;
    document.getElementById('currFlags').innerHTML = VCs;
    document.getElementById('enableRte').checked = enableRte;
}