/**************************************************************************************
 * Project     : Chest X-Ray Pathology Detection and Localization using Deep Learning
 * Author Name : Rammuni Ravidu Suien Silva
 * UoW No      : 16267097
 * IIT No      : 2016134
 * Module      : Final Year Project 20/21
 * Supervisor  : Mr Pumudu Fernando

 * Prototype    : Web Interface - FrontEnd
 * File         : Server AJAX requests functions
 * University of Westminster, UK || IIT Sri Lanka
 **************************************************************************************/


// Image upload front-end
// Initialization of page
jQuery(function () {
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
        if ($('#imageUpload').get(0).files.length !== 0) {
            $('.image-section').show();
            $('.cxr-preview').css('background-image', '');
            $('#btn-detect').show();

            $('.img-preview').hide();
            $('#modelSelect').prop('disabled', false)
            $('#loader_localized').hide();
            $('#btn-save').hide();
            $('#btn-localize').hide();
            $('.det-row').off("click")
            $(".cxr-loc-img").attr('src', "");
            detResults.text('');
            detResults.hide();
            localized = false;

            readURL(this);
        }

    });

    // Detection results request
    $('#btn-detect').on("click", function () {

        let form_data = new FormData();
        // Read selected files
        let totalFiles = document.getElementById('imageUpload').files.length;
        for (let index = 0; index < totalFiles; index++) {
            form_data.append("file_" + index, document.getElementById('imageUpload').files[index]);
        }

        // Model request link
        let model_id = $("#modelSelect").val()
        let urlLink = '/predict/' + model_id
        $('#modelSelect').prop('disabled', true)

        // Show loading animation
        $(this).hide();
        $('#loader_ani').show();

        // Requesting the detection results by calling api /predict (ajax POST call)
        $.ajax({
            type: 'POST',
            url: urlLink,
            data: form_data,
            dataType: 'json',
            contentType: false,
            cache: false,
            processData: false,
            async: true,
            success: function (data) {
                // Displaying detection results
                $('#loader_ani').hide();
                $('#btn-save').show();
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
        $.ajax({
            type: 'GET',
            url: '/get_symptoms',
            dataType: 'json',
            contentType: false,
            cache: false,
            processData: false,
            async: true,
            success: function (data) {
                symptoms_json = data
            },
            error: function () {
                alert("Couldn't Load Symptoms");
            },
        });
    });

    // Localization function
    $('#btn-localize').on("click", function () {
        setLoaderIcon();

        // Show loading animation
        $(this).hide();
        $('#loader_ani_localize').show();
        $('#btn-save').prop("disabled", true);

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
                localized = true

                // Setting initial localized images
                $('.det-row').each(function (i, row_el) {
                    let pathology_id = i;
                    let cxr_popup_img_id = ".cxrPopupImg-" + pathology_id;
                    srcAdd(pathology_id, cxr_popup_img_id);
                })

                $('#loader_ani_localize').hide();
                detResults.fadeIn(600);
                localizationPathAdd(data);

                $('#loader_localized').show();
                $('#btn-save').prop("disabled", false);
                console.log('Path adding DONE!');
            },
            error: function () {
                $('#loader_ani_localize').hide();
                alert("Couldn't Localize CXR");
            },
        });
    });

    $('#btn-save').on("click", function () {
        printResults();
    });

});