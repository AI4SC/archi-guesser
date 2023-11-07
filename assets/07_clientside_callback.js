window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        test_client_side: function () {
            console.log("called it ");
            data = { style: "Ancient Egyptian", epoche: Math.random(), location: { x: 20, y: 30 } }
            return data;
        }
    }
});