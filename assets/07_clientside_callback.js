var DEBUG_MODE=false, DEBUG_OBJ={"err":[], "state":"STOP", "tick":0}, DEBUG_STEP_TICK=5;

window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        test_client_side: function () {
            if (DEBUG_MODE) {
                DEBUG_OBJ["tick"] += 1
                if (DEBUG_OBJ["tick"] == 1*DEBUG_STEP_TICK) {
                    DEBUG_OBJ["obj"]=20+Math.trunc(30*Math.random())
                }
                if (DEBUG_OBJ["tick"] == 2*DEBUG_STEP_TICK) {
                    DEBUG_OBJ["lat"]=Math.random()*180-90;
                    DEBUG_OBJ["lon"]=Math.random()*360-180;
                }
                if (DEBUG_OBJ["tick"] == 3*DEBUG_STEP_TICK) {
                    DEBUG_OBJ["year"]=Math.trunc(2025*Math.random());
                }
                if (DEBUG_OBJ["tick"] == 4*DEBUG_STEP_TICK) {
                    DEBUG_OBJ["state"]="GO";
                }
                if (DEBUG_OBJ["tick"] == 5*DEBUG_STEP_TICK) {
                    DEBUG_OBJ = {"err":[], "state":"STOP", "tick":0};
                }
              return DEBUG_OBJ
            } else {
                sobj=ticktick()
                console.log("B",sobj)
                return sobj;
            }
        }
    }
});