/**************************************************************************************
 * Project     : Chest X-Ray Pathology Detection and Localization using Deep Learning
 * Author Name : Rammuni Ravidu Suien Silva
 * UoW No      : 16267097
 * IIT No      : 2016134
 * Module      : Final Year Project 20/21
 * Supervisor  : Mr Pumudu Fernando

 * Prototype    : Web Interface - FrontEnd
 * File         : JS for creation of dynamic HTML UI elements
 * University of Westminster, UK || IIT Sri Lanka
 **************************************************************************************/

// consts for DOM objects
const detResults = $('#result');
let localized = false;
let symptoms_json;


// Displaying the dynamic detection table
function cxrResultsDisplayTable(dataJSON) {
    let tableHTML = '<div class="limiter">';
    tableHTML += '<div class="container-table100">';
    tableHTML += '<div class="wrap-table100" style="margin: 20px auto auto;">';
    tableHTML += '<div class="table">';
    tableHTML += '<div class="row header">' +
        '<div class="cell text-dark">Pathology</div>' +
        '<div class="cell text-dark">Detection Rate</div>' +
        '</div>';

    let pathology_id = 0

    // Dynamic table creation
    Object.keys(dataJSON).forEach(function (key) {
        let pathology = key;

        $(cxrLocalizationPopup(pathology_id, pathology)).appendTo('#main-app-body');
        $(cxrLocalizationPrint(pathology_id, pathology)).appendTo('.loc-result-print');


        let detectionRate = dataJSON[pathology];

        let cxr_popup_id = "#cxrPopup-" + pathology_id;

        // Highlighting high probable diseases
        if (parseFloat(detectionRate.split("%")[0]) >= 50) {
            tableHTML += '<div class="row bg-warning det-row" data-toggle="modal" data-target="' + cxr_popup_id + '">';
        } else {
            tableHTML += '<div class="row det-row" data-toggle="modal" data-target="' + cxr_popup_id + '">';
        }

        tableHTML += '<div class="cell" data-title="Pathology">';
        tableHTML += pathology;
        tableHTML += '</div>';
        tableHTML += '<div class="cell text-dark" data-title="Detection Rate   (Max - Min)">';
        tableHTML += detectionRate;
        tableHTML += '</div>';
        tableHTML += '</div>';

        pathology_id += 1;
    });

    tableHTML += '</div>';
    tableHTML += '</div>';
    tableHTML += '</div>';
    tableHTML += '</div>';
    return tableHTML;
}

// Dynamic popup card builder for localized image display
function cxrLocalizationPopup(pathology_id, pathology) {
    let popupCXRHTML =
        '<div class="modal fade" id="cxrPopup-' + pathology_id + '" role="dialog">\n' +
        '        <div class="modal-dialog">\n' +
        cxrLocalizationPrint(pathology_id, pathology) +
        '        </div>\n' +
        '    </div>';
    return popupCXRHTML
}

// Print section UI creation
function cxrLocalizationPrint(pathology_id, pathology) {
    let locCXRPrint =
        '<div class="card print-cxr-card">\n' +
        '   <div class="card-img"><img id="cxrPopupImg-' + pathology_id +
        '" class="img-fluid cxr-loc-img cxrPopupImg-' + pathology_id + '" ' +
        '        alt="Run/Click Localization to view the Localized CXR" ' +
        '        style="display: block; margin-left: auto; margin-right: auto;"></div>\n' +
        '   <div class="card-text">\n' +
        '        <p>Localization Result for:</p>\n' +
        '        <p><b>' + pathology + '</b></p>\n' +
        '   </div>\n' + symptomsAdd(pathology, symptoms_json) +
        '</div>\n';
    return locCXRPrint
}

// Displaying possible symptoms from the Symptoms.JSON from the server
function symptomsAdd(pathology, symptoms_json) {
    let symptoms = symptoms_json[pathology]['Symptoms']
    let listHTML = '  ' +
        '<span class="list-group-item list-group-item-action flex-column align-items-start">\n' +
        '    <div class="d-flex w-100 justify-content-between">\n' +
        '      <h5 class="mb-1">Possible Symptoms</h5>\n' +
        '      <small class="text-muted">Confirm the findings</small>\n' +
        '    </div>';

    for (let i = 0; i < symptoms.length; i++) {
        listHTML += '<p class="mb-1">' + symptoms[i] + '</p>\n';
    }

    listHTML += '<small class="text-muted">These are indicative symptoms only!</small>\n' +
        '</span>'
    return listHTML;
}