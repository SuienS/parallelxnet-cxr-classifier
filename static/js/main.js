var detResults = $('#result');
var cxrPreview = $('#imagePreview');
var popupCXRImg = $('#img-fluid');

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

    Object.keys(dataJSON).forEach(function (key) {

        $(cxrLocalizationPopup(pathology_id, 'view1_frontal')).appendTo('#main-app-body');

        let pathology = key;
        let detectionRate = dataJSON[pathology];
        if(parseFloat(detectionRate)>0.45){
            tableHTML += '<div class="row bg-warning" data-toggle="modal" data-target="#cxrPopup-' + pathology_id + '">';
        } else{
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

//used library - http://stewartpark.github.io/Flask-JSGlue/ (PIP Installed)
function cxrLocalizationPopup(pathology_id, cxr_id) {
    let urlPath =  Flask.url_for('get_cxr_detect_img', {"cxr_img_id": cxr_id});
    let popupCXRHTML =
        '<div class="modal fade" id="cxrPopup-' + pathology_id + '" role="dialog">\n' +
        '        <div class="modal-dialog">\n' +
        '            <div class="card">\n' +
        '                <div class="card-img"><img class="img-fluid" ' +
        'src="'+ urlPath +'"></div>\n' +
        '                <div class="card-text">\n' +
        '                    <p>Localization Result</p>\n' +
        '                </div>\n' +
        '            </div>\n' +
        '        </div>\n' +
        '    </div>';
    return popupCXRHTML
}


$(document).ready(function () {
    // Init
    $('.image-section').hide();
    $('.loader').hide();
    detResults.hide();

    // Upload Preview
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

    $("#imageUpload").change(function () {
        $('.image-section').show();
        $('#btn-detect').show();
        detResults.text('');
        detResults.hide();
        readURL(this);
    });

    // Predict
    $('#btn-detect').click(function () {
        var form_data = new FormData($('#upload-file')[0]);

        // Show loading animation
        $(this).hide();
        $('.loader').show();

        // Make prediction by calling api /predict
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
                $(cxrResultsDisplayTable(data)).appendTo('#result');
                console.log('Success!');
            },
        });
    });

});