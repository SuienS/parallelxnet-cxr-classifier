/*************************************************************************
 * Project     : Chest X-Ray Pathology Detection using Deep Learning
 * Author Name : Rammuni Ravidu Suien Silva
 * UoW No      : 16267097
 * IIT No      : 2016134
 * Module      : Final Year Project 20/21
 * Supervisor  : Mr Pumudu Fernando

 * Prototype    : Web Interface - FrontEnd [Draft: .v01]
 * University of Westminster, UK || IIT Sri Lanka
 *************************************************************************/

// consts for DOM objects
const detResults = $('#result');
const cxrPreview = $('#imagePreview');
const popupCXRImg = $('#img-fluid');


// Displaying the dynamic detection table
function cxrResultsDisplayTable(dataJSON) {
    let tableHTML = '<div class="limiter">';
    tableHTML += '<div class="container-table100">';
    tableHTML += '<div class="wrap-table100">';
    tableHTML += '<div class="table">';
    tableHTML += '<div class="row header">' +
        '<div class="cell text-dark">Pathology</div>' +
        '<div class="cell text-dark">Detection Rate</div>' +
        '</div>';

    let keyList = Object.keys(dataJSON);
    let pathology_id = 0

    // Dynamic table creation
    Object.keys(dataJSON).forEach(function (key) {
        let forceRefresh = '?' + Math.floor(Math.random() * 10000) // Force the browser to refresh image
        let pathology = key;

        // URL generation for the target image
        //used library - http://stewartpark.github.io/Flask-JSGlue/ (PIP Installed)
        let urlPath = Flask.url_for('get_cxr_detect_img', {"pathology_id": pathology_id}) + forceRefresh;
        $(cxrLocalizationPopup(pathology_id, pathology)).appendTo('#main-app-body');

        //Setting the image src
        let cxr_popup_img_id = "#cxrPopupImg-" + pathology_id;
        $(cxr_popup_img_id).attr('src', urlPath);

        let detectionRate = dataJSON[pathology];
        // Highlighting high probable diseases
        if (parseFloat(detectionRate) > 0.45) {
            tableHTML += '<div class="row bg-warning" data-toggle="modal" data-target="#cxrPopup-' + pathology_id + '">';
        } else {
            tableHTML += '<div class="row" data-toggle="modal" data-target="#cxrPopup-' + pathology_id + '">';
        }
        tableHTML += '<div class="cell" data-title="Pathology">';
        tableHTML += pathology;
        tableHTML += '</div>';
        tableHTML += '<div class="cell text-dark" data-title="Detection Rate">';
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
        '            <div class="card">\n' +
        '                <div class="card-img"><img id="cxrPopupImg-' + pathology_id + '" class="img-fluid"></div>\n' +
        '                <div class="card-text">\n' +
        '                    <p>Localization Result for:</p>\n' +
        '                    <p><b>'+pathology+'</b></p>\n' +
        '                </div>\n' +
        '            </div>\n' +
        '        </div>\n' +
        '    </div>';
    return popupCXRHTML
}

// Image upload front-end
$(document).ready(function () {
    // Initialization of page
    $('.image-section').hide();
    $('.loader').hide();
    detResults.hide();

    // Uploaded CXR Preview
    function readURL(input) {
        if (input.files && input.files[0]) {
            let reader = new FileReader();
            reader.onload = function (e) {
                cxrPreview.css('background-image', 'url(' + e.target.result + ')');
                cxrPreview.hide();
                cxrPreview.fadeIn(650);
            }
            reader.readAsDataURL(input.files[0]);
        }
    }

    // Image upload button events and animations
    $("#imageUpload").on("change", function () {
        $('.image-section').show();
        $('#btn-detect').show();
        detResults.text('');
        detResults.hide();
        readURL(this);
    });

    // Detection results request
    $('#btn-detect').on("click", function () {
        var form_data = new FormData($('#upload-file')[0]);

        // Show loading animation
        $(this).hide();
        $('.loader').show();

        // Requesting the detection results by calling api /predict (ajax POST call)
        $.ajax({
            type: 'POST',
            url: '/predict',
            data: form_data,
            dataType: 'json',
            contentType: false,
            cache: false,
            processData: false,
            async: true,
            success: function (data) {
                // Displaying detection results
                $('.loader').hide();
                detResults.fadeIn(600);

                // Call for the creation of the detection results table
                $(cxrResultsDisplayTable(data)).appendTo('#result');
                console.log('Detection DONE!');
            },
        });
    });

});