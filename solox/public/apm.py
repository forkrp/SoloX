import datetime
import re
import time
from functools import reduce
from logzero import logger
import tidevice
from public._iosPerf import DataType,Performance
from public.adb import adb
from public.common import Devices, file
from public.fps import FPSMonitor, TimeUtils
import traceback

d = Devices()
_iosD = tidevice.Device()

class CPU:

    def __init__(self, pkgName, deviceId,platform='Android'):
        self.pkgName = pkgName
        self.deviceId = deviceId
        self.platform = platform
        self.apm_time = datetime.datetime.now().strftime('%H:%M:%S.%f')

    def getprocessCpuStat(self):
        """获取某个时刻的某个进程的cpu损耗"""
        pid = d.getPid(pkgName=self.pkgName, deviceId=self.deviceId)
        cmd = f'cat /proc/{pid}/stat'
        result = adb.shell(cmd=cmd, deviceId=self.deviceId)
        r = re.compile("\\s+")
        toks = r.split(result)
        processCpu = float(int(toks[13]) + int(toks[14]))
        return processCpu

    def getTotalCpuStat(self):
        """获取某个时刻的总cpu损耗"""
        cmd = f'cat /proc/stat |{d._filterType()} ^cpu'
        result = adb.shell(cmd=cmd, deviceId=self.deviceId)
        r = re.compile(r'(?<!cpu)\d+')
        toks = r.findall(result)
        idleCpu = float(toks[3])
        totalCpu = float(reduce(lambda x, y: int(x) + int(y), toks))
        return totalCpu

    def getSingCpuRate(self):
        """获取进程损耗cpu的占比%"""
        if self.platform == 'Android':
            processCpuTime_1 = self.getprocessCpuStat()
            totalCpuTime_1 = self.getTotalCpuStat()
            time.sleep(1)
            processCpuTime_2 = self.getprocessCpuStat()
            totalCpuTime_2 = self.getTotalCpuStat()
            cpuRate = round(float((processCpuTime_2 - processCpuTime_1) / (totalCpuTime_2 - totalCpuTime_1) * 100), 2)
        else:
            apm = iosAPM(self.pkgName,_iosD)
            cpuRate = round(float(apm.getPerformance(apm.cpu)), 2)

        with open(f'{file().report_dir}/cpu.log', 'a+') as f:
            f.write(f'{self.apm_time}={str(cpuRate)}' + '\n')
        return cpuRate


class MEM:
    def __init__(self, pkgName, deviceId,platform='Android'):
        self.pkgName = pkgName
        self.deviceId = deviceId
        self.platform = platform
        self.apm_time = datetime.datetime.now().strftime('%H:%M:%S.%f')

    def getProcessMem(self):
        """获取进程内存Total、NativeHeap、NativeHeap;单位MB"""
        if self.platform == 'Android':
            pid = d.getPid(pkgName=self.pkgName, deviceId=self.deviceId)
            cmd = f'dumpsys meminfo {pid}'
            output = adb.shell(cmd=cmd, deviceId=self.deviceId)
            m = re.search(r'TOTAL\s*(\d+)', output)
            # m1 = re.search(r'Native Heap\s*(\d+)', output)
            # m2 = re.search(r'Dalvik Heap\s*(\d+)', output)
            time.sleep(1)
            PSS = round(float(float(m.group(1))) / 1024, 2)
            # NativeHeap = round(float(float(m1.group(1))) / 1024, 2)
            # DalvikHeap = round(float(float(m2.group(1))) / 1024, 2)
        else:
            apm = iosAPM(self.pkgName, _iosD)
            PSS = round(float(apm.getPerformance(apm.memory)), 2)
        with open(f'{file().report_dir}/mem.log', 'a+') as f:
            f.write(f'{self.apm_time}={str(PSS)}' + '\n')
        return PSS


class Battery:
    def __init__(self, deviceId, platform='Android'):
        self.deviceId = deviceId
        self.platform = platform
        self.apm_time = datetime.datetime.now().strftime('%H:%M:%S.%f')

    def getBattery(self):
        """获取Android手机电量"""
        # 切换手机电池为非充电状态
        cmd = 'dumpsys battery set status 1'
        adb.shell(cmd=cmd, deviceId=self.deviceId)
        # 获取手机电量
        cmd = 'dumpsys battery'
        output = adb.shell(cmd=cmd, deviceId=self.deviceId)
        battery = int(re.findall(u'level:\s?(\d+)', output)[0])
        time.sleep(1)
        with open(f'{file().report_dir}/battery.log', 'a+') as f:
            f.write(f'{self.apm_time}={str(battery)}' + '\n')
        return battery

    def SetBattery(self):
        """重置手机充电状态"""
        # 退出时恢复手机充电状态
        cmd = 'dumpsys battery set status 2'
        adb.shell(cmd=cmd, deviceId=self.deviceId)

class Flow:

    def __init__(self, pkgName, deviceId,platform='Android'):
        self.pkgName = pkgName
        self.deviceId = deviceId
        self.platform = platform
        self.apm_time = datetime.datetime.now().strftime('%H:%M:%S.%f')

    def getUpFlow(self):
        """获取上行流量，单位MB"""
        if self.platform == 'Android':
            pid = d.getPid(pkgName=self.pkgName, deviceId=self.deviceId)
            cmd = f'cat /proc/{pid}/net/dev |{d._filterType()} wlan0'
            output = adb.shell(cmd=cmd, deviceId=self.deviceId)
            m = re.search(r'wlan0:\s*(\d+)\s*\d+\s*\d+\s*\d+\s*\d+\s*\d+\s*\d+\s*\d+\s*(\d+)', output)
            if m:
                sendNum = round(float(float(m.group(2)) / 1024 / 1024), 2)
            else:
                raise ValueError("Couldn't get rx and tx data from: %s!" % output)
        else:
            apm = iosAPM(self.pkgName, _iosD)
            sendNum = round(float(apm.getPerformance(apm.network)[1]), 2)
        with open(f'{file().report_dir}/upflow.log', 'a+') as f:
            f.write(f'{self.apm_time}={str(sendNum)}' + '\n')
        return sendNum

    def getDownFlow(self):
        """获取下行流量，单位MB"""
        if self.platform == 'Android':
            pid = d.getPid(pkgName=self.pkgName, deviceId=self.deviceId)
            cmd = f'cat /proc/{pid}/net/dev |{d._filterType()} wlan0'
            output = adb.shell(cmd=cmd, deviceId=self.deviceId)
            m = re.search(r'wlan0:\s*(\d+)\s*\d+\s*\d+\s*\d+\s*\d+\s*\d+\s*\d+\s*\d+\s*(\d+)', output)
            time.sleep(1)
            if m:
                recNum = round(float(float(m.group(1)) / 1024 / 1024), 2)
            else:
                raise ValueError("Couldn't get rx and tx data from: %s!" % output)
        else:
            apm = iosAPM(self.pkgName, _iosD)
            recNum = round(float(apm.getPerformance(apm.network)[0]), 2)
        with open(f'{file().report_dir}/downflow.log', 'a+') as f:
            f.write(f'{self.apm_time}={str(recNum)}' + '\n')
        return recNum


class FPS:

    def __init__(self, pkgName, deviceId,platform='Android'):
        self.pkgName = pkgName
        self.deviceId = deviceId
        self.platform = platform
        self.apm_time = datetime.datetime.now().strftime('%H:%M:%S.%f')

    def getFPS(self):
        """获取fps、jank"""
        if self.platform == 'Android':
            monitors = FPSMonitor(device_id=self.deviceId, package_name=self.pkgName, frequency=1,
                                  start_time=TimeUtils.getCurrentTimeUnderline())
            monitors.start()
            fps, jank = monitors.stop()
            time.sleep(1)
            with open(f'{file().report_dir}/fps.log', 'a+') as f:
                f.write(f'{self.apm_time}={str(fps)}' + '\n')
            with open(f'{file().report_dir}/jank.log', 'a+') as f:
                f.write(f'{self.apm_time}={str(jank)}' + '\n')
            return fps, jank
        else:
            apm = iosAPM(self.pkgName, _iosD)
            fps = int(apm.getPerformance(apm.fps))
            time.sleep(1)
            with open(f'{file().report_dir}/fps.log', 'a+') as f:
                f.write(f'{self.apm_time}={str(fps)}' + '\n')
            return fps,0

class iosAPM():

    def __init__(self, pkgName ,deviceId):
        self.pkgName = pkgName
        self.deviceId = deviceId
        self.apm_time = datetime.datetime.now().strftime('%H:%M:%S.%f')
        self.cpu = DataType.CPU
        self.memory = DataType.MEMORY
        self.network = DataType.NETWORK
        self.fps = DataType.FPS

    def callback(self,_type: DataType, value: dict):
        logger.info(value)

    def getPerformance(self,_perfType: DataType):
        perf = Performance(self.deviceId,[_perfType])# DataType.MEMORY, DataType.NETWORK, DataType.FPS
        _perfValue = perf.start(self.pkgName, callback=self.callback)
        return _perfValue


if __name__ == '__main__':
    apm = iosAPM("com.google.chrome.ios", tidevice.Device())
    _perfValue = apm.getPerformance(apm.cpu)
    logger.info(_perfValue)