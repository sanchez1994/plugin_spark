#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Alejandro Sánchez Carrion"
__copyright__ = "Copyright 2021, PandoraFMS"
__maintainer__ = "Projects department"
__status__ = "Production"
__version__ = "030921"

import json, requests, argparse, sys
from datetime import datetime

parser = argparse.ArgumentParser(description= "", formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-i', '--ip', help='spark ip', required=True)
parser.add_argument('-g', '--group', help='PandoraFMS destination group', default='weblogic')
parser.add_argument('--data_dir', help='PandoraFMS data dir (default: /var/spool/pandora/data_in/)', default='/var/spool/pandora/data_in/')

args = parser.parse_args()

user_ip = args.ip

### Pandora Tools ###
modules = []

config = {
    "data_in": args.data_dir,
    "group" : args.group
}

def print_agent(agent, modules, prt=1):
    """Prints agent XML. Requires Agent object as argument."""
    header = "<?xml version='1.0' encoding='UTF-8'?>\n"
    header += "<agent_data"
    for dato in agent:
        agent_name = agent["agent_name"]
        header += " " + str(dato) + "='" + str(agent[dato]) + "'"
    header += ">\n"
    xml = header
    for module in modules:
        modules_xml = print_module(module, 1)
        xml += str(modules_xml)
    xml += "</agent_data>"
    if prt == 2 :
        print (xml)
    else :
        write_xml(xml, agent_name)

def print_module(module, not_print_flag = None):
    """Returns module in XML format. Accepts only {dict}.\n
    + Only works with one module at a time: otherwise iteration is needed.
    + Module "value" field accepts str type or [list] for datalists.
    + Use not_print_flag to avoid printing the XML (only populates variables).
    """
    data = dict(module)
    module_xml = ("<module>\n"
                  "\t<name><![CDATA[" + str(data["name"]) + "]]></name>\n"
                  "\t<type>" + str(data["type"]) + "</type>\n"
                  )
    
    if type(data["type"]) is not str and "string" not in data["type"]: #### Limpia espacios si el módulo no es tipo string
        data["value"] = data["value"].strip()
    if isinstance(data["value"], list): # Checks if value is a list
        module_xml += "\t<datalist>\n"
        for value in data["value"]:
            if type(value) is dict and "value" in value:
                module_xml += "\t<data>\n"
                module_xml += "\t\t<value><![CDATA[" + str(value["value"]) + "]]></value>\n"
                if "timestamp" in value:
                    module_xml += "\t\t<timestamp><![CDATA[" + str(value["timestamp"]) + "]]></timestamp>\n"
        module_xml += "\t</data>\n"
    else:
        module_xml += "\t<data><![CDATA[" + str(data["value"]) + "]]></data>\n"
    if "desc" in data:
        module_xml += "\t<description><![CDATA[" + str(data["desc"]) + "]]></description>\n"
    if "unit" in data:
        module_xml += "\t<unit><![CDATA[" + str(data["unit"]) + "]]></unit>\n"
    if "interval" in data:
        module_xml += "\t<module_interval><![CDATA[" + str(data["interval"]) + "]]></module_interval>\n"
    if "tags" in data:
        module_xml += "\t<tags>" + str(data["tags"]) + "</tags>\n"
    if "module_group" in data:
        module_xml += "\t<module_group>" + str(data["module_group"]) + "</module_group>\n"
    if "module_parent" in data:
        module_xml += "\t<module_parent>" + str(data["module_parent"]) + "</module_parent>\n"
    if "min_warning" in data:
        module_xml += "\t<min_warning><![CDATA[" + str(data["min_warning"]) + "]]></min_warning>\n"
    if "max_warning" in data:
        module_xml += "\t<max_warning><![CDATA[" + str(data["max_warning"]) + "]]></max_warning>\n"
    if "min_critical" in data:
        module_xml += "\t<min_critical><![CDATA[" + str(data["min_critical"]) + "]]></min_critical>\n"
    if "max_critical" in data:
        module_xml += "\t<max_critical><![CDATA[" + str(data["max_critical"]) + "]]></max_critical>\n"
    if "str_warning" in data:
        module_xml += "\t<str_warning><![CDATA[" + str(data["str_warning"]) + "]]></str_warning>\n"
    if "str_critical" in data:
        module_xml += "\t<str_critical><![CDATA[" + str(data["str_critical"]) + "]]></str_critical>\n"
    if "critical_inverse" in data:
        module_xml += "\t<critical_inverse><![CDATA[" + str(data["critical_inverse"]) + "]]></critical_inverse>\n"
    if "warning_inverse" in data:
        module_xml += "\t<warning_inverse><![CDATA[" + str(data["warning_inverse"]) + "]]></warning_inverse>\n"
    if "max" in data:
        module_xml += "\t<max><![CDATA[" + str(data["max"]) + "]]></max>\n"
    if "min" in data:
        module_xml += "\t<min><![CDATA[" + str(data["min"]) + "]]></min>\n"
    if "post_process" in data:
        module_xml += "\t<post_process><![CDATA[" + str(data["post_process"]) + "]]></post_process>\n"
    if "disabled" in data:
        module_xml += "\t<disabled><![CDATA[" + str(data["disabled"]) + "]]></disabled>\n"
    if "min_ff_event" in data:
        module_xml += "\t<min_ff_event><![CDATA[" + str(data["min_ff_event"]) + "]]></min_ff_event>\n"
    if "status" in data:
        module_xml += "\t<status><![CDATA[" + str(data["status"]) + "]]></status>\n"
    if "timestamp" in data:
        module_xml += "\t<timestamp><![CDATA[" + str(data["timestamp"]) + "]]></timestamp>\n"
    if "custom_id" in data:
        module_xml += "\t<custom_id><![CDATA[" + str(data["custom_id"]) + "]]></custom_id>\n"
    if "critical_instructions" in data:
        module_xml += "\t<critical_instructions><![CDATA[" + str(data["critical_instructions"]) + "]]></critical_instructions>\n"
    if "warning_instructions" in data:
        module_xml += "\t<warning_instructions><![CDATA[" + str(data["warning_instructions"]) + "]]></warning_instructions>\n"
    if "unknown_instructions" in data:
        module_xml += "\t<unknown_instructions><![CDATA[" + str(data["unknown_instructions"]) + "]]></unknown_instructions>\n"
    if "quiet" in data:
        module_xml += "\t<quiet><![CDATA[" + str(data["quiet"]) + "]]></quiet>\n"
    if "module_ff_interval" in data:
        module_xml += "\t<module_ff_interval><![CDATA[" + str(data["module_ff_interval"]) + "]]></module_ff_interval>\n"
    if "crontab" in data:
        module_xml += "\t<crontab><![CDATA[" + str(data["crontab"]) + "]]></crontab>\n"
    if "min_ff_event_normal" in data:
        module_xml += "\t<min_ff_event_normal><![CDATA[" + str(data["min_ff_event_normal"]) + "]]></min_ff_event_normal>\n"
    if "min_ff_event_warning" in data:
        module_xml += "\t<min_ff_event_warning><![CDATA[" + str(data["min_ff_event_warning"]) + "]]></min_ff_event_warning>\n"
    if "min_ff_event_critical" in data:
        module_xml += "\t<min_ff_event_critical><![CDATA[" + str(data["min_ff_event_critical"]) + "]]></min_ff_event_critical>\n"
    if "ff_type" in data:
        module_xml += "\t<ff_type><![CDATA[" + str(data["ff_type"]) + "]]></ff_type>\n"
    if "ff_timeout" in data:
        module_xml += "\t<ff_timeout><![CDATA[" + str(data["ff_timeout"]) + "]]></ff_timeout>\n"
    if "each_ff" in data:
        module_xml += "\t<each_ff><![CDATA[" + str(data["each_ff"]) + "]]></each_ff>\n"
    if "module_parent_unlink" in data:
        module_xml += "\t<module_parent_unlink><![CDATA[" + str(data["parent_unlink"]) + "]]></module_parent_unlink>\n"
    if "global_alerts" in data:
        for alert in data["alert"]:
            module_xml += "\t<alert_template><![CDATA[" + alert + "]]></alert_template>\n"
    module_xml += "</module>\n"

    if not not_print_flag:
        print (module_xml)

    return (module_xml)

def write_xml(xml, agent_name):
    Utime = datetime.now().strftime('%s')
    data_file = "%s/%s.%s.data" %(str(config["data_in"]),agent_name,str(Utime))
    #print (data_file)
    try :
        with open(data_file, 'x') as data:
            data.write(xml)
        data.close()
    except OSError as e :
        pass
        

    return 0

# # default agent
def clean_agent() :
    global agent
    agent = {
        "agent_name"  : "",
        "agent_alias" : "",
        "parent_agent_name" : "",
        "description" : "",
        "version"     : "",
        "os_name"     : "",
        "os_version"  : "",
        "timestamp"   : datetime.today().strftime('%Y/%m/%d %H:%M:%S'),
        #"utimestamp"  : int(datetime.timestamp(datetime.today())),
        "address"     : "127.0.0.1",
        "group"       : config["group"],
        "interval"    : "",
        }
    return agent

# default module
def clean_module() :
    global modulo
    modulo = {
        "name"   : "",
        "type"   : "generic_data_string",
        "desc"   : "",
        "value"  : "",
    }
    return modulo


# request url
# request url
req = {
    "applications": "http://" + user_ip + "/api/v1/applications",
}
try:
    result = requests.get(req["applications"])
    result_data = json.loads(result.content)
except Exception as e :
    print('0')
    sys.exit("\nError requesting %s, please check conectivity" %(req["applications"],))

for dato in result_data:

    clean_agent()
    agent.update(
        agent_name = "Spark_application" + (dato['id']),
        agent_alias = "Spark_application" + (dato['name']),
        description = "Spark_application_detailed stats" 
    )

    req = {
    "executors": "http://" + user_ip + "/api/v1/applications/" + dato['id'] + "/executors",
    }
    try:
        result = requests.get(req["executors"])
        result_data2 = json.loads(result.content)
    except Exception as e :
        print('0')
        sys.exit("\nError requesting %s, please check conectivity" %(req["executors"],))

    for dato2 in result_data2:

        clean_module()
        modulo.update(
            name=dato2['id'] + "id",
            type="generic_data_string",
            desc="",
            value=dato2['id'],
            unit=""
        )
        modules.append(modulo)

        clean_module()
        modulo.update(
            name=dato2['id'] + "hostPort",
            type="generic_data_string",
            desc="",
            value=dato2['hostPort'],
            unit=""
        )
        modules.append(modulo)

        clean_module()
        modulo.update(
            name=dato2['id'] + "rddBlocks",
            type="generic_data",
            desc="",
            value=dato2['rddBlocks'],
            unit=""
        )
        modules.append(modulo)

        clean_module()
        modulo.update(
            name=dato2['id'] + "memoryUsed",
            type="generic_data",
            desc="",
            value=dato2['memoryUsed'],
            unit=""
        )
        modules.append(modulo)

        clean_module()
        modulo.update(
            name=dato2['id'] + "diskUsed",
            type="generic_data",
            desc="",
            value=dato2['diskUsed'],
            unit=""
        )
        modules.append(modulo)

        clean_module()
        modulo.update(
            name=dato2['id'] + "activeTasks",
            type="generic_data",
            desc="",
            value=dato2['activeTasks'],
            unit=""
        )
        modules.append(modulo)

        clean_module()
        modulo.update(
            name=dato2['id'] + "failedTasks",
            type="generic_data",
            desc="",
            value=dato2['failedTasks'],
            unit=""
        )
        modules.append(modulo)

        clean_module()
        modulo.update(
            name=dato2['id'] + "completedTasks",
            type="generic_data",
            desc="",
            value=dato2['completedTasks'],
            unit=""
        )
        modules.append(modulo)

        clean_module()
        modulo.update(
            name=dato2['id'] + "totalTasks",
            type="generic_data",
            desc="",
            value=dato2['totalTasks'],
            unit=""
        )
        modules.append(modulo)

        clean_module()
        modulo.update(
            name=dato2['id'] + "totalDuration",
            type="generic_data",
            desc="",
            value=dato2['totalDuration'],
            unit=""
        )
        modules.append(modulo)   

        clean_module()
        modulo.update(
            name=dato2['id'] + "totalInputBytes",
            type="generic_data",
            desc="",
            value=dato2['totalInputBytes'],
            unit=""
        )
        modules.append(modulo)

        clean_module()
        modulo.update(
            name=dato2['id'] + "totalShuffleRead",
            type="generic_data",
            desc="",
            value=dato2['totalShuffleRead'],
            unit=""
        )
        modules.append(modulo) 

        clean_module()
        modulo.update(
            name=dato2['id'] + "totalShuffleWrite",
            type="generic_data",
            desc="",
            value=dato2['totalShuffleWrite'],
            unit=""
        )
        modules.append(modulo) 

        clean_module()
        modulo.update(
            name=dato2['id'] + "maxMemory",
            type="generic_data",
            desc="",
            value=dato2['maxMemory'],
            unit=""
        )
        modules.append(modulo) 
        print_agent(agent, modules) 

print("1")
