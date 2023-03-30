// Character identification
const charID = $('.main-information').data('character');

function updateRollResultBox(rollResult, actionType) {
    const rollValue = $('#rollResultValue');
    const rollAction = $('#rollResultAction');
    rollValue.html(rollResult);
    rollAction.html(actionType);
}

function updateBasicInfo(selector, infoToUpdate, event) {
    if (event.which == 13) {
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

function updatePathInfo(event) {    
    const activePath = $(event.target).val();
    $.ajax({
        type: 'GET',
        url: '/sheet/update/active/path/',
        data: {
            'active_path': activePath,
            'char_ID': charID
        },
        success: (response) => {
            $('#active-current-pp').text(response['current_pp']);
            $('#active-total-pp input').val(response['total_pp']);
            $('#active-level').text(response['level']);
            if (response['is_master']) {
                $('#active-is-master').text('\u2713');
            } else {
                $('#active-is-master').text('');
            }
            $('#intrinsic-skill-name').text(response['skill_name']);
            $('#intrinsic-skill-description').text(response['skill_description']);
        },
        error: (response) => {
            console.log('Error');
        }
    });
    event.preventDefault();
}

function updateInventoryAndAnnotations(event) {
    const newText = $(event.target).val();
    const infoToUpdate = $(event.target).data('field');
    $.ajax({
        type: 'GET',
        url: '/sheet/update/text/',
        data: {
            'char_ID': charID,
            'info_to_update': infoToUpdate,
            'new_text': newText
        },
        success: (response) => {
            $(event.target).blur();
        },
        error: (response) => {
            console.log('Error')
        }
    });
    event.preventDefault();
}

function equipSkill(event) {    
    const slot = $(event.target).data('slot');
    const skillID = $(event.target).val();
    $.ajax({
        type: 'GET',
        url: '/sheet/skills/equip/',
        data: {
            'char_ID': charID,
            'slot': slot,
            'skill_ID': skillID
        },
        success: (response) => {
            $(`#${slot}-skill-description`).text(response['skill_description']);
        },
        error: (response) => {
            console.log('Error');
        }
    });
    event.preventDefault();
}

$('.roll-button').on('click', (event) => {
        const actionID = $(event.target).val();
        $.ajax({
        type: 'GET',
        url:'/sheet/roll_action/',
        data: { 'action_ID': actionID },
        success: (response) => {
            rollResult = response.roll.result;
            actionType = response.action;
            updateRollResultBox(rollResult, actionType);
        },
        error: () => {
            console.log("Error");
        }
    });
        event.preventDefault();
    }
);

$('#inputCharXP').on('keydown', (event) => {
    if (event.which == 13) {
        const totalXP = $(event.target).val();        
        $.ajax({
            type: 'GET',
            url: '/sheet/level_up/',
            data: {
                'char_ID': charID,
                'total_XP': totalXP
            },
            success: (response) => {
                $('#inputCharXP').val(response['xp_total']);
                $('#charXPCurrent').html(`XP ${response['xp_current']} / `);
                $('#charLevel').text(`Nível ${response['level']}`);
                $('#inputCharXP').blur();
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
});

// Manipulating active path
$('#path-selection').on('change', '#active-path-select', (event) => {
    updatePathInfo(event);
});

$('#active-total-pp').on('keydown', 'input', (event) => {
    if (event.which == 13) {
        const activePath = $('#active-path-select').val();
        const newTotalPp = $(event.target).val();
        $.ajax({
            type: 'GET',
            url: '/sheet/manipulate/pathpoints/',
            data: {
                'active_path': activePath,
                'new_total_pp': newTotalPp
            },
            success: (response) => {
                $('#active-current-pp').text(response['current_pp']);
                $('#active-level').text(response['level']);
                if (response['is_master']) {
                    $('#active-is-master').text('\u2713');
                } else {
                    $('#active-is-master').text('');
                }
                $(event.target).blur();
            },
            error: (response) => {
                console.log('Error');
            }
        });
        event.preventDefault();
    }
});

$.each([$('#equip-skills-table select')], (index, element) => {
    element.on('change', (event) => {        
        equipSkill(event);
    })
});

$('#input-inventory').on('change', (event) => {
    updateInventoryAndAnnotations(event);
})

$('#input-annotations').on('change', (event) => {
    updateInventoryAndAnnotations(event);
})
