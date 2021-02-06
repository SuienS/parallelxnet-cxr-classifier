/**************************************************************************************
 * Project     : Chest X-Ray Pathology Detection and Localization using Deep Learning
 * Author Name : Rammuni Ravidu Suien Silva
 * UoW No      : 16267097
 * IIT No      : 2016134
 * Module      : Final Year Project 20/21
 * Supervisor  : Mr Pumudu Fernando

 * Prototype    : Web Interface - FrontEnd [Draft: .v01]
 * University of Westminster, UK || IIT Sri Lanka
 **************************************************************************************/

// consts for DOM objects
const detResults = $('#result');
const cxrPreview = $('.cxr-preview');
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
        let pathology = key;

        $(cxrLocalizationPopup(pathology_id, pathology)).appendTo('#main-app-body');

        let detectionRate = dataJSON[pathology];

        let cxr_popup_id = "#cxrPopup-" + pathology_id;
        let cxr_popup_id_span = "#cxrPopup-" + pathology_id + "-span";

        // Highlighting high probable diseases
        if (parseFloat(detectionRate) > 0.45) {
            tableHTML += '<div class="row bg-warning det-row" data-toggle="modal" data-target="' + cxr_popup_id + '">';
        } else {
            tableHTML += '<div class="row det-row" data-toggle="modal" data-target="' + cxr_popup_id + '">';
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
        '                <div class="card-img"><img id="cxrPopupImg-' + pathology_id + '" class="img-fluid cxr-loc-img" ' +
        '                   alt="Run Localization to view the Localized CXR" ' +
        '                   style="display: block; margin-left: auto; margin-right: auto;"></div>\n' +
        '                <div class="card-text">\n' +
        '                    <p>Localization Result for:</p>\n' +
        '                    <p><b>' + pathology + '</b></p>\n' +
        '                </div>\n' +
        '            </div>\n' +
        '        </div>\n' +
        '    </div>';
    return popupCXRHTML
}
//TODO: SEE  WHAT HAPPENS WHEN YOU LOAD 2ND CXR IMAGE
function localizationPathAdd(count_str) {
    let count = parseInt(count_str);// Can be used for error handling

    // Dynamic src creation
    $('.det-row').each(function (i, row_el) {
        let pathology_id = i;
        let cxr_popup_img_id = "#cxrPopupImg-" + pathology_id;
        $(row_el).on("click", function () {
            let forceRefresh = '?' + Math.floor(Math.random() * 10000); // Force the browser to refresh image
            // URL generation for the target image
            // used library - http://stewartpark.github.io/Flask-JSGlue/ (PIP Installed)
            let urlPath = Flask.url_for('get_cxr_detect_img', {"pathology_id": pathology_id}) + forceRefresh;
            //Setting the image src
            $(cxr_popup_img_id).attr('src', urlPath);
        });
    });
}

function setLoaderIcon() {
    let loadingURL = Flask.url_for("static", {"filename": "icons/loading_gif.gif"});
    $(".cxr-loc-img").attr('src', loadingURL);
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
            $('.img-preview').each(function (i, row_el) {
                if (i >= input.files.length || !input.files[i].type.match('image.*')) {
                    return false;
                }

                let reader = new FileReader();
                let cxrPreviewId = "#cxr-preview-" + i;

                $(this).css('display', 'inline-block');
                reader.onload = function (e) {
                    $(cxrPreviewId).css('background-image', 'url(' + e.target.result + ')');
                    $(cxrPreviewId).hide();
                    $(cxrPreviewId).fadeIn(650);
                }
                reader.readAsDataURL(input.files[i]);
            });
        }
    }

    // Image upload button events and animations
    $("#imageUpload").on("change", function () {
        $('.image-section').show();
        $('.cxr-preview').css('background-image', '');
        $('.img-preview').hide();
        $('#btn-detect').show();
        $('#loader_localized').hide();
        $('#btn-localize').hide();
        $('.det-row').off("click")
        $(".cxr-loc-img").attr('src', "");
        detResults.text('');
        detResults.hide();
        readURL(this);
    });

    // Detection results request
    $('#btn-detect').on("click", function () {

        let form_data = new FormData();
        // Read selected files
        let totalFiles = document.getElementById('imageUpload').files.length;
        for (let index = 0; index < totalFiles; index++) {
            form_data.append("file_" + index, document.getElementById('imageUpload').files[index]);
        }

        // Show loading animation
        $(this).hide();
        $('#loader_ani').show();

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
                $('#loader_ani').hide();
                detResults.fadeIn(600);
                // Call for the creation of the detection results table
                $(cxrResultsDisplayTable(data)).appendTo('#result');
                console.log('Detection DONE!');
                $('#btn-localize').show();
            },
            error: function () {
                $('#loader_ani').hide();
                alert("Couldn't Scan CXR Image");
            },
        });
    });

    $('#btn-localize').on("click", function () {
        setLoaderIcon(); // TODO: Choice option popup for which img to localize
        // Show loading animation
        $(this).hide();
        $('#loader_ani_localize').show();

        // Initiating the localization
        $.ajax({
            url: '/localize',
            dataType: 'text',
            contentType: false,
            cache: false,
            processData: false,
            async: true,
            success: function (data) {
                // Displaying detection results
                $('#loader_ani_localize').hide();
                detResults.fadeIn(600);
                localizationPathAdd(data);
                $('#loader_localized').show();
                console.log('Path adding DONE!');
            },
            error: function () {
                $('#loader_ani_localize').hide();
                alert("Couldn't Localize CXR");
            },
        });
    });

});