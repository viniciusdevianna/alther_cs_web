$('.roll-button').click((e) => {
        const actionID = $(this).val()
        $.ajax({
        type: 'GET',
        url:'/sheet/roll_action/',
        data: { 'action_ID': actionID },
        success: (response) => {
            console.log(response);
        },
        error: () => {
            console.log("Error");
        }
    });
    e.preventDefault();
    }
);