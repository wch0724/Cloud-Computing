from libvmi import Libvmi
from utils import pause
import sys

def get_pid_by_name(vmi,process_name):

    tasks_offset = vmi.get_offset("linux_tasks")
    name_offset = vmi.get_offset("linux_name")
    pid_offset = vmi.get_offset("linux_pid")

    list_head = vmi.translate_ksym2v("init_task")
    list_head += tasks_offset
    
    cur_list_entry = list_head
    next_list_entry = vmi.read_addr_va(cur_list_entry,0)
    
    pids = []
    while True:
        cur_process_name = vmi.read_str_va(next_list_entry + name_offset - tasks_offset,0)
        pid = vmi.read_32_va(next_list_entry + pid_offset - tasks_offset,0)
        cur_list_entry = next_list_entry
        next_list_entry = vmi.read_addr_va(cur_list_entry,0)
        
        if pid < 1<<16 and cur_process_name == process_name:
            pids.append(pid)
        if cur_list_entry == list_head: 
            break

    return pids

def main(args):

    if len(args) != 3:
        print("./mem_vmi.py <process_name> <string_addr>")
        return 1
    
    vm_name = "ubuntu16.04"
    process_name = args[1]
    string_addr = args[2]

    with Libvmi(vm_name) as vmi: #class Libvmi,the default parameters calls vmi_init_complete
        #init offsets values, init libvmi library
        tasks_offset = vmi.get_offset("linux_tasks")
        name_offset = vmi.get_offset("linux_name")
        pid_offset = vmi.get_offset("linux_pid")

        #pause vm for consistent memory access
        with pause(vmi):
            pids = get_pid_by_name(vmi,process_name)
            if not pids:
                print("Cannot find process %s" % process_name)
            pid = pids[0]
            print("process %s:%d" % (process_name,pid))

            #get output string of exp
            string = vmi.read_str_va(int(string_addr,16),pid)
            print("output:%s" % string)

            #alter output string of exp
            vmi.write_8_va(int(string_addr,16),pid,0x77) 
            return 0

if __name__ == '__main__':

    main(sys.argv)
