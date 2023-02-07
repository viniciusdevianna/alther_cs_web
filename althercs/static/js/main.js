function updateRollResultBox(rollResult, actionID) {
    const rollBox = $(`#action-${actionID}`);
    rollBox.text(rollResult);
}

function updateBasicInfo(selector, infoToUpdate, event) {
    if (event.which == 13) {
        const charID = $('.main-information').data('character');
        const newValue = $(event.target).val();
        $.ajax({
            type: 'GET',
            url: '/sheet/update/basic/',
            data: {
                'char_ID': charID,
                'info_to_update': infoToUpdate,
                'new_value': newValue
            },
            success: (response) => {
                $(selector).val(response[infoToUpdate]);
                $(selector).blur();
            },
            error: (response) => {
                console.log('Error');
            }
        });
        event.preventDefault();
    }
}

$('.roll-button').on('click', (event) => {
        const actionID = $(event.target).val();
        $.ajax({
        type: 'GET',
        url:'/sheet/roll_action/',
        data: { 'action_ID': actionID },
        success: (response) => {
            rollResult = response.roll.result;
            updateRollResultBox(rollResult, actionID);
        },
        error: () => {
            console.log("Error");
        }
    });
        event.preventDefault();
    }
);

$('#input-char-xp').on('keydown', (event) => {
    if (event.which == 13) {
        const totalXP = $(event.target).val();
        const charID = $('.main-information').data('character');
        $.ajax({
            type: 'GET',
            url: '/sheet/level_up/',
            data: {
                'char_ID': charID,
                'total_XP': totalXP
            },
            success: (response) => {
                $('#input-char-xp').val(response['xp_total']);
                $('#char-xp-current').text(`${response['xp_current']} / `);
                $('.char-level').text(`Nível ${response['level']}`);
                $('#input-char-xp').blur();
            },
            error: () => {
                console.log('Error')
            }
        });
        event.preventDefault();
    }    
});

// A dict with all the inputs for basic char info and their respective model fields
// dict[selector, model_field]
basicInfo = {
    '#input-unbalance-points': 'unbalance',
    '#input-health-points-current': 'hp_current',
    '#input-health-points-total': 'hp_total',
    '#input-health-points-temp': 'hp_temp',
    '#input-coin': 'coin',
};

// Iterate through all basic char info and add the onkeydown event listener
$.each(basicInfo, (selector, infoToUpdate) => {
    $(selector).on('keydown', (event) => {
        updateBasicInfo(selector, infoToUpdate, event);
    })
});

// Manipulating character's attributes
function changeAttributeCurrentValue(event) {
    const attrID = $(event.target).val();
    const operation = $(event.target).attr('id').startsWith('increment') ? 1 : -1;
    const attrCurrentField = $(`#current-${attrID}`);
    const attrCurrentValue = parseInt(attrCurrentField.text());
    const attrTotalValue = parseInt($(`#total-${attrID}`).text());
    if ((operation > 0 && attrCurrentValue < attrTotalValue) ||
     (operation < 0 && attrCurrentValue > 0)) {
        $.ajax({
            type: 'GET',
            url: '/sheet/manipulate/attribute/',
            data: {
                'attr_ID': attrID,
                'operation': operation
            },
            success: (response) => {
                attrCurrentField.text(response['new_value']);
            },
            error: (response) => {
                console.log('Error');   
            }
        });
        event.preventDefault();
    } else {
        console.log('Attribute cannot go higher than total or lower than zero');
    }
    
}

$('.button-manipulate-attr').on('click', (event) => {
    changeAttributeCurrentValue(event);
})