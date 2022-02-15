import cmd
import requests
import json

sim_start_time = 0
sig_start_time = 0
headers={ 'Content-Type':'application/json',"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"}

class Simulation:
    def __init__(self, url, uuid, signal_out, dbc_name):
        self.url = url
        self.uuid = uuid
        self.signal_out = signal_out
        self.dbc_name = dbc_name
        self.simulation_url = "http://%s:8010/modules/%s/" %(url,  self.uuid)
        self.data = json.dumps({ 

            "uuid": self.uuid,
            "type": "CAN-SIM",
            "format": "DBC",
            "dst_phy_id": self.signal_out,
            "file_path": self.dbc_name,
            "file_src": "DATABASE",
            "options" : {
                "timerType" : 1,
                "sendType" : 1,
                "crc" : True 
            }
        })

    def simulation_start(self):
        global sim_start_time
        try:
            cmdurl = "http://%s:8010" %self.url
            res = requests.post(cmdurl, data=self.data, headers=headers)
            print(res.json())
            res.raise_for_status()
        except requests.exceptions.RequestException as e:
            if sim_start_time < 2:
                sim_start_time+= 1
                self.signal_start()
            else:
                raise SystemExit(e) 



    def signal_start(self):
        global sig_start_time
        try:
            cmdurl = self.simulation_url + "start"
            res = requests.post(cmdurl, data=self.data, headers=headers)
            print(res.json())
            res.raise_for_status()
        except requests.exceptions.RequestException as e:
            if sig_start_time < 2:
                sig_start_time+= 1
                self.signal_start()
            else:
                raise SystemExit(e) 

    def signal_stop(self):
        cmdurl = self.simulation_url + "stop"
        requests.post(cmdurl, data=self.data, headers=headers)

    def simulation_stopall(self):  #stop simulation 
        cmdurl = "http://" + self.url + "/api/standard-simulation/clearall"
        requests.delete(cmdurl, headers=headers)

    def message_activate(self, msg_id):
        cmdurl = self.simulation_url + "activate/" + msg_id
        res = requests.post(cmdurl, headers=headers)
        print(res.json())

    def message_stop(self, msg_id):
        cmdurl = self.simulation_url + "activate/" + msg_id
        requests.delete(cmdurl, headers=headers)

    def message_change_raw(self, msg_id, data_name, raw):
        cmdurl = self.simulation_url + "data/" + msg_id + "/signal"
        data =json.dumps([{ "name": data_name, "raw": raw }])   
        res = requests.put(cmdurl, data=data, headers=headers)
        print(res.json())
        
    def message_change_phys(self, msg_id, data_name, phys):
        cmdurl = self.simulation_url + "data/" + msg_id + "/signal"
        data =json.dumps([{ "name": data_name, "phys": phys }])  
        res = requests.put(cmdurl, data=data, headers=headers)
        print(res.json())



# import requests
# import json

# sim_start_time = 0
# headers={ 'Content-Type':'application/json',"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"}
# url = ""
# uuid =""
# signal_out = ""
# dbc_name = ""
# simulation_url = "http://%s:8010/modules/%s/" %(url,  uuid)
# data = json.dumps({
#     "uuid": uuid,
#     "type": "CAN-SIM",
#     "format": "DBC",
#     "dst_phy_id": signal_out,
#     "file_path": dbc_name,
#     "file_src": "DATABASE",
#     "options" : {
#         "timerType" : 1,
#         "sendType" : 1,
#         "crc" : True 
#     }
# })

# def simulation_start():
#     global sim_start_time
#     try:
#         cmdurl = simulation_url + "start"
#         res = requests.post(cmdurl, data=data, headers=headers)
#         res.raise_for_status()
#     except requests.exceptions.RequestException as e:
#         if sim_start_time <= 2:
#             sim_start_time+= 1
#             simulation_start()
#         else:
#             raise SystemExit(e) 

# def simulation_stop(self):
#     cmdurl = self.simulation_url + "stop"
#     requests.post(cmdurl, data=self.data, headers=headers)

# def simulation_stopall(self):  #stop simulation 
#     cmdurl = "http://" + self.url + "/api/standard-simulation/clearall"
#     requests.delete(cmdurl, headers=headers)

# def message_activate(self, msg_id):
#     cmdurl = self.simulation_url + "activate/" + msg_id
#     requests.post(cmdurl, headers=headers)

# def message_stop(self, msg_id):
#     cmdurl = self.simulation_url + "activate/" + msg_id
#     requests.delete(cmdurl, headers=headers)

# def message_change_raw(self, msg_id, data_name, raw):
#     cmdurl = self.simulation_url + "data/" + msg_id + "/signal"
#     data =json.dumps([{ "name": data_name, "raw": raw }])   
#     requests.put(cmdurl, data=data, headers=headers)

# def message_change_phys(self, msg_id, data_name, phys):
#     cmdurl = self.simulation_url + "data/" + msg_id + "/signal"
#     data =json.dumps([{ "name": data_name, "phys": phys }])  
#     requests.put(cmdurl, data=data, headers=headers)
