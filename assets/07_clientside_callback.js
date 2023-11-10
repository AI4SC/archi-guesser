var DEBUG_MODE=true, DEBUG_OBJ={"err":[], "status":"STOP", 'tick':0};

window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        test_client_side: function () {
            if (DEBUG_MODE) {
                DEBUG_OBJ['tick']+=1
                if (DEBUG_OBJ['tick']>20) {
                    if (DEBUG_OBJ['status']=='STOP') {
                        DEBUG_OBJ={"err":[], "status":"GO", "lat":Math.random()*360-180, "lon":Math.random()*180-90, 'obj':20+Math.trunc(10*Math.random()), 'year':Math.trunc(2500*Math.random()-500), 'tick':0}
                    } else {
                        DEBUG_OBJ={"err":[], "status":"STOP", 'tick':0}
                    }
                    console.log(DEBUG_OBJ)
                }
              return DEBUG_OBJ
            } else {
                return ticktick();
            }
        }
    }
});