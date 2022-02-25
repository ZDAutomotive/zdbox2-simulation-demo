import LinSimulation as LS
import json

url = "192.168.1.111"

def main():
    linsim = LS.LinSim(url)
    lclear = linsim.sim_clearall()
    print(lclear.json())

    master = LS.LinMasterSim(url, dst_phy_id="lin2", file_path="door_ldf.json")
    mcreate = master.sim_create()
    mstart = master.sim_startall()
    print(mstart.json())

    # mcheckschedule = master.check_cur_schedule()
    # mswtschedule = master.switch_cur_schedule("Table1")

    slave = LS.LinSlaveSim(url, dst_phy_id="lin1", file_path="door_ldf.json", Master=master)
    screate = slave.sim_create()
    sstart = slave.sim_start()
    sgetdata = slave.sim_get_alldata()
    # smoddata = slave.sim_mod_alldata(data = {'0': ['1', '1'], '1': ['1', '1', '1', '1'], '2': ['0', '0'], '3': ['0', '0'], '4': ['0', '0'], '5': ['0', '0'], '6': ['0', '0'], '7': ['0', '0'], '8': ['0', '0'], '61': ['0', '0', '0', '0', '0', '0', '0', '0']})
    print("slave's data is %s "%sgetdata) 

    frame1 = LS.Frame(slave, frameid="0x02")
    factivate = frame1.frame_activate()
    fstatus = frame1.frame_status()
    fgetdata = frame1.frame_get_data()
    print("frame's status: %s" %fstatus.json()) 
    print("frame's data is %s" %fgetdata)
    # fmoddata = frame1.frame_mod_data(data=["0","1"])
    fgetsig = frame1.frame_get_data_by_sig("DWRL_WinPos")
    print("signal's data is %s" %fgetsig)
    # fmoddata = frame1.frame_mod_by_raw("DWRL_WinPos", raw="200")

    # fdeactivate = frame1.frame_deactivate()
    # lclear = linsim.sim_clearall()

if __name__ == "__main__":
    main()
    