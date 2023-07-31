'''
概述：
1.项目文件
各种文件所在位置：file_position
路网：network.net.xml
交通需求:route.rou.xml
trip文件：trips.xml
模拟后的信息：tripinfo.xml
2.流程
(1)生成随机trip(由起始边、终止边组成),使用seed保证可复现
(2)根据trip生成车辆初始路线.rou.xml
开始模拟:直到所有车辆离开
    模拟步
    其他算法
模拟结束
'''

import os,sys

#将‘SUMO_HOME'/tools添加到加载路径中，方便直接调用
if 'SUMO_HOME' in os.environ:
    tools=os.path.join(os.environ['SUMO_HOME'],'tools')
    sys.path.append(tools)#运行时修改，结束后失效
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

from tool import *
#用到的文件名
file_position=''
net=os.path.join(file_position,'network.net.xml')
route=os.path.join(file_position,'route.rou.xml')
trip=os.path.join(file_position,'trips.xml')
configuration=os.path.join(file_position,'configuration.sumocfg')
tripinfo=os.path.join(file_position,'tripinfo.xml')
result_file=os.path.join(file_position,'result.xls')
randomTrip=True#是否产生随机trip



#编写命令行以启动 sumo或sumo-gui
sumoBinary="sumo-gui"
sumoCmd=[
            sumoBinary,
            '--net-file', net,
            '--route-files', route,
            '--tripinfo-output',tripinfo,
        ]


if __name__ == "__main__":
    if randomTrip==True:
        # 生成随机trip,参数可自行设置,使用seed保证可复现
        generateRandomTrips(net=net, begin=0, end=200, period=4, seed=6, fringe_factor=1, output=trip)
    else:
        #生成指定起点边和终止边的trip，参数可自行设置
        generateTrips(net=net,begin=0,end=200,period=4,from_edge='42195400#0',to_edge='301781877#2',output=trip)

    # 根据trips文件生成初始.rou.xml
    generateRoute(trip=trip,net=net,output=route)

    import traci
    traci.start(sumoCmd)
    step=0
    while traci.simulation.getMinExpectedNumber()>0:#直到全部车辆离开路网，停止模拟

        traci.simulationStep()#进行一步模拟

        #在这里添加你的算法

        step=step+1
    traci.close()

    print('模拟时长:%i'%step,end=' ')
    writeResultFile(tripinfo,result_file)

