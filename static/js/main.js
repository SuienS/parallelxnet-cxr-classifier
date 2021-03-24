/**************************************************************************************
 * Project     : Chest X-Ray Pathology Detection and Localization using Deep Learning
 * Author Name : Rammuni Ravidu Suien Silva
 * UoW No      : 16267097
 * IIT No      : 2016134
 * Module      : Final Year Project 20/21
 * Supervisor  : Mr Pumudu Fernando

 * Prototype    : Web Interface - FrontEnd
 * File         : Main JS logic functions for the UI functionality
 * University of Westminster, UK || IIT Sri Lanka
 **************************************************************************************/
// TODO: USER GUIDE
// Setting path for relevant localization images
function localizationPathAdd(count_str) {
    let count = parseInt(count_str);// Can be used for error handling
    // Dynamic src creation
    $('.det-row').each(function (i, row_el) {
        let pathology_id = i;
        let cxr_popup_img_class = ".cxrPopupImg-" + pathology_id;

        $(row_el).on("click", function () {
            srcAdd(pathology_id, cxr_popup_img_class);
        });
    });
}

// Modifying the SRC
function srcAdd(pathology_id, cxr_popup_img_id) {
    let forceRefresh = '?' + Math.floor(Math.random() * 10000); // Force the browser to refresh image
    // URL generation for the target image
    // used library - http://stewartpark.github.io/Flask-JSGlue/ (PIP Installed)
    let urlPath = Flask.url_for('get_cxr_detect_img', {"pathology_id": pathology_id}) + forceRefresh;
    //Setting the image src
    $(cxr_popup_img_id).attr('src', urlPath);
}

// PDF Results
function printResults() {
    if (localized) {
        let completed = $('.det-row').each(function (i, row_el) {
            let pathology_id = i;
            let cxr_popup_img_id = ".cxrPopupImg-" + pathology_id;
            srcAdd(pathology_id, cxr_popup_img_id);
        });
        $.when(completed).then(function (x) {
            setTimeout(
                function () {
                    window.print();
                }, 1000);
        });
    } else {
        window.print();
    }
}

// Temporary loading icon for localization images
function setLoaderIcon() {
    let loadingURL = Flask.url_for("static", {"filename": "icons/loading_gif.gif"});
    $(".cxr-loc-img").attr('src', loadingURL);
}