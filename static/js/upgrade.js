const charID = $('.main-information').data('character');

function upgradeAttributeValue(event) {
    const attributeType = $(event.target).val();
    const actionToTake = $(event.target).attr('id').startsWith('increment') ? 1 : -1;
    const isTraining = $(event.target).attr('class').includes('train')
    $.ajax({
        type: 'GET',
        url: '/sheet/upgrade/attribute/',
        data: {
            'attribute_type': attributeType[0],
            'action_to_take': actionToTake,
            'char_ID': charID,
            'is_training': isTraining
        },
        success: (response) => {
            if (isTraining) {
                $(`#${attributeType}-training-level`).text(response['result']);
            } else {
                $(`#${attributeType}-total-value`).text(response['result']);
            }            
            $('#current-xp').text(`XP Disponível: ${response['update_xp']}`);
        },
        error: (response) => {
            alert(response.responseJSON.error);
        }
    });
    event.preventDefault();
}

function upgradeBattleAction(event) {
    const battleActionType = $(event.target).val();
    const actionToTake = $(event.target).attr('id').startsWith('increase') ? 1 : -1;
    $.ajax({
        type: 'GET',
        url: '/sheet/upgrade/character/battle/',
        data: {
            'battle_action_type': battleActionType,
            'action_to_take': actionToTake,
            'char_ID': charID
        },
        success: (response) => {
            $(`#character-${battleActionType}-actions`).text(response['result']);
            $('#current-xp').text(`XP Disponível: ${response['update_xp']}`);
            $(`#increase-${battleActionType}-button`).html(`${response['new_cost']} XP`);
        },
        error: (response) => {
            alert(response.responseJSON.error);
        }
    });
    event.preventDefault();
}

function upgradeActionDice(event) {
    const actionType = $(event.target).val();
    const actionToTake = $(event.target).attr('id').startsWith('add') ? 1 : -1;
    const dice = $(event.target).attr('id').split('-').pop();
    $.ajax({
        type: 'GET',
        url: '/sheet/upgrade/action/',
        data: {
            'action_type': actionType[0],
            'action_to_take': actionToTake,
            'char_ID': charID,
            'dice': dice
        },
        success: (response) => {
            $(`#${actionType}-${dice}`).text(response['result']);
            $('#current-xp').text(`XP Disponível: ${response['update_xp']}`);
        },
        error: (response) => {
            alert(response.responseJSON.error);
        }
    });
    event.preventDefault();
}

$.each([$('.attributes-information button')], (index, element) => {
    element.on('click', (event) => {        
        upgradeAttributeValue(event);
    })
});

$.each([$('.actions-information button')], (index, element) => {
    element.on('click', (event) => {
        upgradeActionDice(event);
    })
});

$.each([$('.battle-information button')], (index, element) => {
    element.on('click', (event) => {
        upgradeBattleAction(event);
    })
});