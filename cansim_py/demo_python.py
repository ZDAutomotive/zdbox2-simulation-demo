from distutils.command.upload import upload
import Can_Simulation as cs 
import Upload_Dbc as ud
import requests
import json
import time
import websocket
import _thread


boxurl_pure = "192.168.1.1"  # switch to local url when the code run in zdbox 
boxurl = "http://" + boxurl_pure + ":8010"  
sim_dbc_list = ['demosim.dbc', 'demosim.json']
trace_dbc_list = ['demotrace.json']

reqID = 1
switch1_status = 0
speed_status = 0

msg_ab = cs.Simulation(boxurl_pure, "airbag", "can1", "demosim.json" )
msg_speed = cs.Simulation(boxurl_pure, "velocity", "can2", "demosim.json" )
msg_led = cs.Simulation(boxurl_pure, "led", "can4", "demosim.json" )


def upload_dbc():
    ud.upload_sim_dbc(boxurl_pure, sim_dbc_list)
    ud.upload_trace_dbc(boxurl_pure, trace_dbc_list)


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
    try:
        cmdurl = "http://" + boxurl_pure + "/api/standard-simulation/clearall"
        res = requests.delete(cmdurl)            
    except requests.exceptions.RequestException as e:
        raise SystemExit(e) 
    finally:
        return res


def speed_change(speed): 
    msg_speed.message_change_phys("253", "ESP_v_Signal", speed)
    

def switch1_off(): 
    msg_ab.message_change_raw("64", "AB_Gurtschloss_FA_ext", "2")

    time.sleep(0.5)
    msg_ab.message_change_raw("1349", "AB_Belegung_VF_ext", "2")
    msg_ab.message_change_raw("64", "AB_Belegung_VF", "2")

    msg_led.message_change_raw("102", "LED_1", "0")
    msg_led.message_activate("102")


def switch1_on():

    msg_ab.message_change_raw("1349", "AB_Belegung_VF_ext", "3")
    msg_ab.message_change_raw("1349", "AB_Belegung_VF", "3")

    time.sleep(0.5)

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
        
    def on_error(ws, error):
      print(error)

    def on_close(ws, close_status_code, close_msg):
        print("### closed ###")

    def on_open(ws):
        requests.put("http://" + boxurl_pure + "/api/trace-service/codec/default/dbc/can", data={"path":"demotrace.json"})
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
    upload_dbc()
    simulation_stop()
    time.sleep(3)   
    msg_start()
    ws = websocket.WebSocketApp("ws://" + boxurl_pure + ":6001/",
                              on_open=on_open,
                              on_message=on_message,
                              on_error=on_error,
                              on_close=on_close)
    ws.run_forever()

if __name__ == "__main__":
    main()
    