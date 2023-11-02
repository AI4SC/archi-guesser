window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        test_client_side: function (n_intervals) {
            console.log("called it ", n_intervals);
            return (n_intervals * 2);
        }
    }
});