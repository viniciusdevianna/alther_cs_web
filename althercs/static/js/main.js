function updateRollResultBox(rollResult, actionID) {
    const rollBox = $(`#action-${actionID}`);
    rollBox.text(rollResult);
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

$('#input-char-xp').on('keypress', (event) => {
    if (event.which == 13) {
        const totalXP = $(event.target).val();
        const char_ID = $('.main-information').data('character');
        $.ajax({
            type: 'GET',
            url: '/sheet/level_up/',
            data: {
                'char_ID': char_ID,
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
