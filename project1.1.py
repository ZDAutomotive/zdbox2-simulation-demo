import Can_Simulation as cs 
from Can_Trace import Trace_App
import Upload_Dbc as ud
import requests
import json
import time
import websocket
import _thread


boxurl_pure = "192.168.1.163"  # switch to "?.1.0.0" when the code run in zdbox 
boxurl = "http://" + boxurl_pure + ":8010"  
sim_dbc_list = ['E3_1_1_MEB_ACANFD_KMatrix_V10.07.04F_20201102_MH.dbc', 'siggen_lite_standard.json']
trace_dbc_list = ['siggen_lite_standard.json']

reqID = 1
switch1_status = 0
speed_status = 0

msg_ab = cs.Simulation(boxurl_pure, "airbag", "can1", "E3_1_1_MEB_ACANFD_KMatrix_V10.07.04F_20201102_MH.json" )
msg_speed = cs.Simulation(boxurl_pure, "velocity", "can2", "E3_1_1_MEB_ACANFD_KMatrix_V10.07.04F_20201102_MH.json" )
msg_led = cs.Simulation(boxurl_pure, "led", "can4", "siggen_lite_standard.json" )



def msg_start():

    msg_ab.simulation_start()
    msg_speed.simulation_start()
    msg_led.simulation_start()
    
    msg_ab.signal_start()
    msg_speed.signal_start()
    msg_led.signal_start()

    msg_ab.message_activate("1349")
    msg_ab.message_activate("64")
    msg_speed.message_activate("253")

    msg_ab.message_change_raw("64", "ASM_Masterzeit", "0")

    switch1_off()

def simulation_stop():  #stop simulation 
    cmdurl = "http://" + boxurl_pure + "/api/standard-simulation/clearall"
    res = requests.delete(cmdurl)
    return res.json

def speed_change(speed): 
    msg_speed.message_change_phys("253", "ESP_v_Signal", speed)
    

def switch1_off(): 
    msg_ab.message_change_raw("64", "AB_Gurtschloss_FA_ext", "2")

    time.sleep(0.5)# sleep 0.5s
    msg_ab.message_change_raw("1349", "AB_Belegung_VF_ext", "2")
    msg_ab.message_change_raw("64", "AB_Belegung_VF", "2")

    msg_led.message_change_raw("102", "LED_1", "0")
    msg_led.message_activate("102")


def switch1_on():

    msg_ab.message_change_raw("1349", "AB_Belegung_VF_ext", "3")
    msg_ab.message_change_raw("1349", "AB_Belegung_VF", "3")

    time.sleep(0.5)# sleep 0.5s

    msg_ab.message_change_raw("64", "AB_Gurtschloss_FA_ext", "3")

    msg_led.message_change_raw("102", "LED_1", "1")
    msg_led.message_activate("102")


def on_message(ws, message):
    new_message = json.loads(message) 
    global switch1_status
    global speed_status
    # print(new_message.json())
    try:
        if new_message["data"][0]["parsed"]["name"] == "POTI_STATUS":
            if abs(int(new_message["data"][0]["parsed"]["signals"][1]["raw"]) - speed_status) > 5 :
                speed_status = int(new_message["data"][0]["parsed"]["signals"][1]["raw"])
                # print(speed_status)
                speed_change(str(speed_status))
        

        if new_message["data"][0]["parsed"]["name"] == "SWITCH_STATUS":
            
            # print(new_message["data"][0]["parsed"]["signals"][1]["raw"])
            if int(new_message["data"][0]["parsed"]["signals"][1]["raw"]) != switch1_status:
                switch1_status = int(new_message["data"][0]["parsed"]["signals"][1]["raw"])
                if switch1_status :
                    switch1_on()
                    
                else:
                    switch1_off()
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
        
        # if "data" in new_message:
        #     if len(new_message["data"]) == 1:
        #         if "parsed" in new_message["data"][0]:
        #             if "name" in new_message["data"][0]["parsed"]:
        #                 if new_message["data"][0]["parsed"]["name"] == "POTI_STATUS":
        # if abs(int(new_message["data"][0]["parsed"]["signals"][1]["raw"]) - speed_status) > 5 :
        #     speed_status = int(new_message["data"][0]["parsed"]["signals"][1]["raw"])
        #     # print(speed_status)
        #     msg_speed.message_change_phys("253", "ESP_v_Signal", speed)
    

    # if new_message["data"][0]["parsed"]["name"] == "SWITCH_STATUS":
        
    #     # print(new_message["data"][0]["parsed"]["signals"][1]["raw"])
    #     if int(new_message["data"][0]["parsed"]["signals"][1]["raw"]) != switch1_status:
    #         switch1_status = int(new_message["data"][0]["parsed"]["signals"][1]["raw"])
    #         if switch1_status :
    #             switch1_on()
                
    #         else:
    #             switch1_off()
    def on_error(ws, error):
      print(error)

    def on_close(ws, close_status_code, close_msg):
        print("### closed ###")

    def on_open(ws):
        requests.put("http://" + boxurl_pure + "/api/trace-service/codec/default/dbc/can", data={"path":"siggen_lite_standard.json"})
        time.sleep(1)
        ws.send('{"opcode":"addChannel","requestId":"100","data":{"channel":"ipdu.can.can4.*","codec": ["default-can"]} }')
        ws.send('{"opcode":"setRule","requestId":"101","data":{"rule":"()=>true"} }')
        def heartbit(*args):
            while(1): 
                global reqID
                test='{"opcode":"heartbeat","requestId":'+str(reqID)+'}'
                ws.send(test)
                reqID+=1
                print("Send heartbit")
                time.sleep(5)

        _thread.start_new_thread(heartbit, ())


def main():

    simulation_stop()
    time.sleep(3)   
    msg_start()
    ws = websocket.WebSocketApp("ws://" + boxurl_pure + ":6001/",
                              on_open=on_open,
                              on_message=on_message,
                              on_error=on_error,
                              on_close=on_close)
    # ws = Trace_App( "ws://" + boxurl_pure + ":6001/",
    #                           channel = "ipdu.can.can4.*",
    #                           on_message=on_message,
    #                           )
    # ws.on_open()
    ws.run_forever()

if __name__ == "__main__":
    main()
    