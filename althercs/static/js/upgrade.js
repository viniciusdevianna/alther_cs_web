$('.attributes-table #decrement-CORPO').on('click', (event) => {
    const upgradeBought = 'C';
    const actionToTake = -1;
    const charID = $('.main-information').data('character');
    $.ajax({
        type: 'GET',
        url: '/sheet/upgrade/',
        data: {
            'upgrade_bought': upgradeBought,
            'action_to_take': actionToTake,
            'char_ID': charID          
        },
        success: (response) => {
            console.log(response['result'])
        },
        error: (response) => {
            console.log('Error')
        }
    });
    event.preventDefault();
})