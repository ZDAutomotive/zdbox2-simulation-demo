import requests
import json

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
        try:
            cmdurl = "http://%s:8010" %self.url
            res = requests.post(cmdurl, data=self.data, headers=headers)            
        except requests.exceptions.RequestException as e:
            raise SystemExit(e) 
        finally:
            return res

    def signal_start(self):
        try:
            cmdurl = self.simulation_url + "start"
            res = requests.post(cmdurl, data=self.data, headers=headers)
        except requests.exceptions.RequestException as e:
            raise SystemExit(e) 
        finally:
            return res

    def signal_stop(self):
        try:
            cmdurl = self.simulation_url + "stop"
            res = requests.post(cmdurl, data=self.data, headers=headers)
        except requests.exceptions.RequestException as e:
            raise SystemExit(e) 
        finally:
            return res

    def simulation_stopall(self):  #stop simulation   
        try:
            cmdurl = "http://" + self.url + "/api/standard-simulation/clearall"
            res = requests.delete(cmdurl, headers=headers)
        except requests.exceptions.RequestException as e:
            raise SystemExit(e) 
        finally:
            return res

    def message_activate(self, msg_id):
        try:
            cmdurl = self.simulation_url + "activate/" + msg_id
            res = requests.post(cmdurl, headers=headers)
            print(res.json())
        except requests.exceptions.RequestException as e:
            raise SystemExit(e) 
        finally:
            return res

    def message_stop(self, msg_id):
        try:
            cmdurl = self.simulation_url + "activate/" + msg_id
            res = requests.delete(cmdurl, headers=headers)
        except requests.exceptions.RequestException as e:
            raise SystemExit(e) 
        finally:
            return res

    def message_change_raw(self, msg_id, data_name, raw):
        try:
            cmdurl = self.simulation_url + "data/" + msg_id + "/signal"
            data =json.dumps([{ "name": data_name, "raw": raw }])   
            res = requests.put(cmdurl, data=data, headers=headers)
            print(res.json())
        except requests.exceptions.RequestException as e:
            raise SystemExit(e) 
        finally:
            return res

    def message_change_phys(self, msg_id, data_name, phys):  
        try:
            cmdurl = self.simulation_url + "data/" + msg_id + "/signal"
            data =json.dumps([{ "name": data_name, "phys": phys }])  
            res = requests.put(cmdurl, data=data, headers=headers)
            print(res.json())
        except requests.exceptions.RequestException as e:
            raise SystemExit(e) 
        finally:
            return res       


