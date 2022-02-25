import requests
import json
import sys

frame_list = []
headers={ 'Content-Type':'application/json' }

class LinSim:
    def __init__(self, url ):
        self.url = url

    def sim_clearall(self): 
        try:
            cmdurl = "http://%s/api/lin-simulation/clearall" %self.url
            res = requests.delete(cmdurl)
        except requests.exceptions.RequestException as e:
            raise SystemExit(e) 
        finally:
            return res

    def sim_startall(self):
        try:
            cmdurl = "http://%s/api/lin-simulation/start" %self.url
            res = requests.post(cmdurl)
        except requests.exceptions.RequestException as e:
            raise SystemExit(e) 
        finally:
            return res

    def sim_stopall(self):
        try:
            cmdurl = "http://%s/api/lin-simulation/stop" %self.url
            res = requests.post(cmdurl)
        except requests.exceptions.RequestException as e:
            raise SystemExit(e) 
        finally:
            return res
    
    def sim_get_cur(self):
        try:
            cmdurl = "http://%s/api/lin-simulation/" %self.url
            res = requests.get(cmdurl)
        except requests.exceptions.RequestException as e:
            raise SystemExit(e) 
        finally:
            return res.json()


class LinMasterSim(LinSim):
    def __init__(self, url, dst_phy_id, file_path):
        super().__init__(url)
        self.dst_phy_id = dst_phy_id 
        self.file_path = file_path

    def sim_create(self):
        try:
            cmdurl = "http://%s/api/lin-simulation/" %self.url
            data = {
                    "type": "master",
                    "format": "LDF",
                    "dst_phy_id": self.dst_phy_id,
                    "file_path": self.file_path,
                    "file_src": "DATABASE"
                }
            res = requests.post(cmdurl, data=data)
        except requests.exceptions.RequestException as e:
            raise SystemExit(e) 
        finally:
            return res

    def sim_delete(self):
        try:
            cmdurl = "http://%s/api/lin-simulation/" %self.url
            data = {
                    "uuid": self.dst_phy_id
                }
            res = requests.delete(cmdurl, data=data)
        except requests.exceptions.RequestException as e:
            raise SystemExit(e) 
        finally:
            return res

    def check_cur_schedule(self):
        try:
            cmdurl = "http://%s/api/lin-simulation/modules/%s/schedule/table" %(self.url, self.dst_phy_id)
            res = requests.get(cmdurl)
        except requests.exceptions.RequestException as e:
            raise SystemExit(e) 
        finally:
            return res.json()

    def switch_cur_schedule(self, table):
        try:
            cmdurl = "http://%s/api/lin-simulation/modules/%s/schedule/table" %(self.url, self.dst_phy_id)
            data = {
                    "name": table
                }            
            res = requests.put(cmdurl, data=data)
        except requests.exceptions.RequestException as e:
            raise SystemExit(e) 
        finally:
            return res.json()


class LinSlaveSim(LinSim):
    def __init__(self, url, dst_phy_id, file_path, Master=None):
        super().__init__(url)
        self.dst_phy_id = dst_phy_id 
        self.file_path = file_path
        self.is_slave = True
        if Master:
            if self.dst_phy_id == Master.dst_phy_id:
                raise SystemExit('Master and Slave can not share a same lin')

    def sim_create(self):
        try:
            cmdurl = "http://%s/api/lin-simulation/" %self.url
            data = {
                    "type": "slave",
                    "format": "LDF",
                    "dst_phy_id": self.dst_phy_id,
                    "file_path": self.file_path,
                    "file_src": "DATABASE"
                }
            res = requests.post(cmdurl, data=data)
        except requests.exceptions.RequestException as e:
            raise SystemExit(e) 
        finally:
            return res

    def sim_status(self):
        try:
            cmdurl = "http://%s/api/lin-simulation/modules/%s/status" %(self.url, self.dst_phy_id)
            res = requests.get(cmdurl)

        except requests.exceptions.RequestException as e:
            raise SystemExit(e) 
        finally:
            return res

    def sim_start(self):
        try:
            cmdurl = "http://%s/api/lin-simulation/modules/%s/start" %(self.url, self.dst_phy_id)
            res = requests.post(cmdurl)            

        except requests.exceptions.RequestException as e:
            raise SystemExit(e) 
        finally:
            return res

    def sim_stop(self):
        try:
            cmdurl = "http://%s/api/lin-simulation/modules/%s/stop" %(self.url, self.dst_phy_id)
            res = requests.post(cmdurl)            
        except requests.exceptions.RequestException as e:
            raise SystemExit(e) 
        finally:
            return res    
    
    def sim_get_alldata(self):
        try:
            cmdurl = "http://%s/api/lin-simulation/modules/%s/data" %(self.url, self.dst_phy_id)
            res = requests.get(cmdurl) 
                      
        except requests.exceptions.RequestException as e:
            raise SystemExit(e) 
        finally:
            return res.json()  

    def sim_mod_alldata(self, data=None):
        if not data:
            print('original data is as follows , please modify the data and input as the parameter. ') 
            print('original data is : %s'%self.sim_get_alldata()) 
        else:
            try:
                cmdurl = "http://%s/api/lin-simulation/modules/%s/data" %(self.url, self.dst_phy_id)
                res = requests.put(cmdurl, data) 
                print(res.json())           
            except requests.exceptions.RequestException as e:
                raise SystemExit(e) 
            finally:
                return res.json()   

    
class Frame():
    def __init__(self, slave, frameid):
        global frame_list
        if not slave.is_slave:
            print("Frame must under a Slave Simulation")
            sys.exit(0)
        if frameid in frame_list:
            print("Frameid must be unique")
            sys.exit(0)            
        self.url = slave.url
        self.name = slave.dst_phy_id
        self.frameid = frameid 
        frame_list.append(frameid)        

    def frame_status(self):
        try:
            cmdurl = "http://%s/api/lin-simulation/modules/%s/activate/%s" %(self.url, self.name, self.frameid)
            res = requests.get(cmdurl)           
        except requests.exceptions.RequestException as e:
            raise SystemExit(e) 
        finally:
            return res

    def frame_deactivate(self):
        try:
            cmdurl = "http://%s/api/lin-simulation/modules/%s/activate/%s" %(self.url, self.name, self.frameid)
            res = requests.delete(cmdurl)            
        except requests.exceptions.RequestException as e:
            raise SystemExit(e) 
        finally:
            return res 

    def frame_activate(self):
        try:
            cmdurl = "http://%s/api/lin-simulation/modules/%s/activate/%s" %(self.url, self.name, self.frameid)
            res = requests.post(cmdurl)            
        except requests.exceptions.RequestException as e:
            raise SystemExit(e) 
        finally:
            return res 

    def frame_get_data(self):
        try:
            cmdurl = "http://%s/api/lin-simulation/modules/%s/data/%s" %(self.url, self.name, self.frameid)
            res = requests.get(cmdurl)        
        except requests.exceptions.RequestException as e:
            raise SystemExit(e) 
        finally:
            return res.json() 

    def frame_mod_data(self, data=None):
        if not data:
            print('original data is as follows , please modify the data and input as the parameter. ')
            print('original data is : %s'%self.frame_get_data()) 
        else:
            try:
                cmdurl = "http://%s/api/lin-simulation/modules/%s/data/%s" %(self.url, self.name, self.frameid)
                res = requests.put(cmdurl, data=json.dumps(data), headers=headers)       
            except requests.exceptions.RequestException as e:
                raise SystemExit(e) 
            finally:
                return res.json()

    def frame_get_data_by_sig(self, name):
        try:
            cmdurl = "http://%s/api/lin-simulation/modules/%s/data/%s/signal?name=%s" %(self.url, self.name, self.frameid, name)
            res = requests.get(cmdurl)       
        except requests.exceptions.RequestException as e:
            raise SystemExit(e) 
        finally:
            return res.json() 

    def frame_mod_by_raw(self, name, raw=None):
        if not raw:
            print('original data is as follows , please modify the data and input as the parameter. ') 
            print('original data is : %s'%self.frame_get_data_by_sig()) 
        else:
            try:
                cmdurl = "http://%s/api/lin-simulation/modules/%s/data/%s/signal" %(self.url, self.name, self.frameid)
                data = [
                        {
                            "name": name,
                            "raw": raw,
                            }
                        ]
                res = requests.put(cmdurl, data=json.dumps(data), headers=headers)
                print(res.json())        
            except requests.exceptions.RequestException as e:
                raise SystemExit(e) 
            finally:
                return res 

    def frame_mod_by_phys(self, name, phys=None):
        if not phys:
            print('original data is as follows , please modify the data and input as the parameter. ') 
            print('original data is : %s'%self.frame_get_data_by_sig()) 
        else:
            try:
                cmdurl = "http://%s/api/lin-simulation/modules/%s/data/%s/signal" %(self.url, self.name, self.frameid)
                data = [
                        {
                            "name": name,
                            "phys": phys,
                            }
                        ]
                res = requests.put(cmdurl, data=data, headers=headers)      
            except requests.exceptions.RequestException as e:
                raise SystemExit(e) 
            finally:
                return res 

