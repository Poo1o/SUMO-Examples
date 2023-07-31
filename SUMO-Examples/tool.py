def generateRandomTrips(net,begin,end,period,seed,fringe_factor,output):
    '''
    调用randomTrips生成随机trip,trip由边edge组成，不保证trip一定可达
    :param net: 路网
    :param begin: 开始时间
    :param end: 结束时间
    :param period: 产生trip的时间间隔
    :param seed: 随机种子
    :param fringe_factor:增加行程在网络边缘开始/结束的可能性
    :param output:
    :return:
    '''
    import os, sys
    # 将‘SUMO_HOME'/tools添加到加载路径中，方便直接调用
    if 'SUMO_HOME' in os.environ:
        tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
        sys.path.append(tools)  # 运行时修改，结束后失效
    else:
        sys.exit("please declare environment variable 'SUMO_HOME'")

    import randomTrips  # noqa
    randomTrips.main(randomTrips.get_options([
        '-b', str(begin),
        '-e', str(end),
        '-n', str(net),
        '--period', str(period),
        '--seed', str(seed),
        '--fringe-factor', str(fringe_factor),
        '-o', str(output),
    ]))

def generateTrips(net,begin,end,period,from_edge,to_edge,output):
    '''
    产生一组由固定起点边到固定终点边的trip
    :param net: 路网
    :param begin: 开始时间
    :param end: 结束时间
    :param period: 产生trip的时间间隔
    :param from_edge: 起始边
    :param to_edge: 终点边
    :param output: 输出trip文件名
    :return:
    '''
    with open(output, "w") as trips:
        print("""<routes>
        """, file=trips)
        # <trip id="0" depart="0.00" from="E0" to="E1"/>
        id = 0
        time = begin
        while time < end:  # 写入id time 随机选取2个点
            print('''    <trip id="%i" depart="%i" from="%s" to="%s"/>
            ''' % (id, time, from_edge, to_edge), file=trips)
            id += 1
            time += period

        print("</routes>", file=trips)

def generateRoute(trip,net,output="route.rou.xml"):
    '''
    调用duarouter根据trips和net生成车辆的路线，对于有误的trip会摒弃，出发速度设置为max
    :param trip: 定义trip的.xml文件
    :param net: 定义路网的.net.xml文件
    :param output: 输出交通需求的.rou.xml文件
    :return: 无
    '''

    import os, sys
    # 将‘SUMO_HOME'/bin添加到加载路径中，方便直接调用
    if 'SUMO_HOME' in os.environ:
        bin = os.path.join(os.environ['SUMO_HOME'], 'bin')
        sys.path.append(bin)  # 运行时修改，结束后失效
    else:
        sys.exit("please declare environment variable 'SUMO_HOME'")

    from subprocess import call
    duarouter=os.path.join(bin,'duarouter.exe')
    call([duarouter,
          '-t', trip,
          '-n', net,
          '-o', output,
          '--departspeed', 'max',
          '--repair'
          ])

def get_departed_info(tripinfo):#读取tripinfo文件获得每辆车的id 总行驶时间 总行驶长度
    import xml.etree.ElementTree as ET

    # 解析tripinfo.xml文件
    tree = ET.parse(tripinfo)
    root = tree.getroot()
    result=[]
    total_time=0.0
    total_length=0.0

    # 遍历每辆车辆的tripinfo记录，获取id 时间 行驶长度
    for tripinfo in root.findall("tripinfo"):
        veh_id = tripinfo.get("id")
        time = tripinfo.get("duration")
        distance = float(tripinfo.get("routeLength"))
        tmp={}
        tmp['id']=veh_id
        tmp['time']=time
        tmp['distance']=distance
        result.append(tmp)
        total_time=total_time+float(time)
        total_length=total_length+float(distance)

    return result,total_time,total_length

def writeResultFile(tripinfo,result_file):
    '''
    读取模拟生成的tripinfo文件，输出模拟结果，并将模拟的详细信息写到result_file(excel文件)
    '''
    import pandas as pd
    import warnings
    warnings.filterwarnings('ignore')
    result, total_time, total_length = get_departed_info(tripinfo)
    result=sorted(result,key=lambda x: int(x['id']))
    result_p = pd.DataFrame(data=None, columns=['id', 'time', 'distance'])
    for item in result:
        result_p = result_p.append(item, ignore_index=True)
    result_p.to_excel(result_file, index=0)
    print('所有车辆用时:%f,vehicles 所有车辆行驶路程:%f' % (total_time, total_length))