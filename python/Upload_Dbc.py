import requests
from fnmatch import fnmatch
import json


sim_dbc_list= ['demosim.dbc', 'demosim.json']    
trace_dbc_list = ['demotrace.json']
# headers={ 'Content-Type':'application/json',"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"}
boxurl_pure = "192.168.1.1"


def upload_sim_dbc(boxurl_pure, sim_dbc_list):
    dbc_sim_url = "http://" + boxurl_pure + "/api/database-management/general/dbc/can/" 

    for file in sim_dbc_list:
        if fnmatch(file, "*.dbc"):
            if requests.get(dbc_sim_url + file[:-3] + "json").status_code :
                print(file + " exists")
            else:
                res = requests.post(dbc_sim_url, files={'file': open(file, 'rb')})
                print(res.json())
                # print(file, 'not exists')
        elif fnmatch(file, "*.json"):
            res = requests.post(dbc_sim_url, files={'file': open(file, 'rb')})
            print(res.json())
        else:
            print(file + ' is not dbc or json file' )


def upload_trace_dbc(boxurl_pure, trace_dbc_list):
    dbc_trace_url = "http://" + boxurl_pure + "/api/trace-service/codec/default/dbc/can"

    for file in trace_dbc_list:
        if fnmatch(file, "*.json"):
            res = requests.put(dbc_trace_url, data={"path" : file})
            print(res.json())
    


def main():
    upload_sim_dbc(boxurl_pure, sim_dbc_list)
    upload_trace_dbc(boxurl_pure, trace_dbc_list)


if __name__ == "__main__":
    main()