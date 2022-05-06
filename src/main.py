#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
from colorama import Fore, Style
import json
import logging
import subprocess

from kubernetes import client, config
from prettytable import PrettyTable

__version__ = "0.1.1"

class resources:

    def __init__(self, namespace, lowusage, threshold):
        config.load_kube_config()
        self.v1 = client.CoreV1Api()
        self.outputTable = PrettyTable()
        self.namespace = namespace
        self.lowusage = lowusage

        self.threshold = threshold

        # set up the table for PrettyTable()
        self.configureOutputTable()

    def checkRequestSetting(self, usage, request):
        """
        Check the percentage differnce between usage and request

        returns True if the difference is below threshold
        returns False by default

        e.g. usage of 10Mi, request of 100Mi and threshold of 90%
        Usage would be 10% 
        10 < 90 return True
        """
        if usage < request:
            pcnt = usage / request * 100
            if pcnt < self.threshold:
                return True
        return False

    def outputAsTable(self, data):
        try:
            for p in data.items:
                if p.status.phase == "Running":
                    for c in p.spec.containers:
                        r = c.resources
                        reqMem = r.requests['memory'] if isinstance(r.requests, dict) else "none"
                        reqCpu = r.requests['cpu'] if isinstance(r.requests, dict) else "none"
                        limMem = r.limits['memory'] if isinstance(r.limits, dict) else "none"
                        limCpu = r.limits['cpu'] if isinstance(r.limits, dict) else "none"
                        currentUsage = self.getCurrentResourceMetrics(p.metadata.name, c.name)
                        logging.info(f"Adding row to table for {self.namespace}/{p.metadata.name}/{c.name}")

                        memRequestHigh = self.checkRequestSetting(int(float(currentUsage['memory'].strip('Mi').strip('G'))), int(reqMem.strip('Mi').strip('G'))) if reqMem != "none" else False
                        cpuRequestHigh = self.checkRequestSetting(int(currentUsage['cpu'].strip('m')), int(reqCpu.strip('m'))) if reqCpu != "none" else False
                        memColour = Fore.RED if memRequestHigh else Fore.GREEN
                        cpuColour = Fore.RED if cpuRequestHigh else Fore.GREEN

                        if (self.lowusage and (memRequestHigh or cpuRequestHigh)) or not self.lowusage:
                            self.outputTable.add_row([self.namespace, p.metadata.name, c.name,
                                        f"{memColour}{currentUsage['memory']}{Style.RESET_ALL}", reqMem, limMem,
                                        f"{cpuColour}{currentUsage['cpu']}{Style.RESET_ALL}", reqCpu, limCpu])
            print(self.outputTable)
        except Exception as te:
            print(f"Type Error:\n\t{te}")
        except Exception as e:
            print(f"Error trying to print table\n\t{e}")

    def configureOutputTable(self):
        """Configures the PrettyTable with column headers"""

        self.outputTable.field_names = ["Namespace", "Pod", "Container", 
                                        "Memory Used", "Memory Requested", "Memory Limit",
                                        "CPU used", "CPU Requested", "CPU Limit"]



    def getCurrentResourceMetrics(self, pod, container):
        topUri = f"/apis/metrics.k8s.io/v1beta1/namespaces/{self.namespace}/pods/{pod}"

        try:
            logging.info(f"Connecting to {topUri}")
            output = subprocess.check_output(['kubectl', 'get', '--raw', topUri])
        except Exception as e:
            print(e)

        podContainers = json.loads(output)['containers']
        for c in podContainers:
            if c['name'] == container:
                cpu = int(c['usage']['cpu'].strip("n")) / 1000 / 1000 # get cpu cores
                mem = round(int(c['usage']['memory'].strip("Ki")) / 1024, 2) # get memory usage in Mi to 2dp
                usageDict = {"cpu": f"{int(cpu)}m", "memory": f"{mem}Mi"} # build a dict to return, using int() to round cpu
                logging.info(f"Found resource usage info for {self.namespace}/{pod}/{container}")
                return usageDict


    def getResourceSpec(self):
        """Fetches pod information and outputs a table"""

        pods = self.v1.list_namespaced_pod(self.namespace)
        self.outputAsTable(pods)

    def main(self):
        logging.info("Getting pod information")
        self.getResourceSpec()


if __name__ == "__main__":
    version = __version__
    parser = argparse.ArgumentParser(allow_abbrev=True, 
                                    description="Show decoded secrets information")
    parser.add_argument("--version", "-v",
                        action="version",
                        version=version)
    parser.add_argument("--namespace", "-n",
                        dest="ns",
                        type=str,
                        default="default",
                        help="Set namespace",
                        )
    parser.add_argument("--debug", "-d",
                        dest="debug",
                        action="store_true",
                        default=False,
                        help="Print debug information")
    parser.add_argument("--show-lowusage",
                        dest="lowusage",
                        action="store_true",
                        default=False,
                        help="Only show containers with lower usage than requested")
    parser.add_argument("--threshold", "-t",
                        dest="threshold",
                        type=int,
                        default=30,
                        help="percent of requested resources used to alert on")
    args = parser.parse_args()
    logging.basicConfig(level=logging.WARN) if not args.debug else logging.basicConfig(level=logging.INFO)

    logging.info(f"{__version__} running")
    
    rcs = resources(namespace=args.ns, lowusage=args.lowusage, threshold=args.threshold)
    rcs.main()