# -*- coding: utf-8 -*-
import datetime
import json
import os
import random
import re
import shutil
import time

import requests.exceptions
import urllib3


from Constant import *
from Function import *


class WindowsLogin():

    def __init__(self):
        self.is_login_success = False
        # 状态寄存器
        self.first_finish = False
        self.second_finish = False
        self.is_sl_login = False
        self.isauto = False
        self.istart = 0
        # 暂存数据
        self.server_list = []

        # 取出数据
        self.username = ""
        self.password = ""
        self.server = 0
        self.host = ""

        # 得到数据
        self.channel = None
        self.cookie = None
        self.host = None
        self.version = None
        self.uid = ""
        if os.path.exists("config/user.json"):
            with open("config/user.json") as f:
                user = json.loads(f.read())
                if "username" in user:
                    self.username = user["username"]
                if "password" in user:
                    self.password = user["password"]
                if "server" in user:
                    self.server = user["server"]
                if "isauto" in user:
                    self.isauto = user["isauto"]

    def re_login(self):
        """
        进行SL,重新登录游戏
        :return:
        """
        for i in range(5):
            result1 = gameLogin.first_login_usual(
                self.server, self.username, self.password, self)
            result2 = gameLogin.second_login(self.host, self.uid, self)
            if result1 and result2:
                break
            else:
                continue

    # 首次登录进行处理
    def first_login(self):
        # 先显示自己
        try:
            # 开启子线程进行数据请求
            if len(self.username) != 0 and len(self.password) != 0:
                gameData.login_name = self.username.upper()
                gameLogin.first_login_usual(self.server, self.username, self.password, self)
        except Exception as e:
            log.error("windows第一次登录失败", e)

    # 首次登录回调函数
    def first_login_deal(self, data):
        try:
            # 如果登录出现了问题
            if "error" in data:
                ##self.statusBarSignal.emit("首次登录错误:" + data["errmsg"])
                self.first_finish = False
                return False

            # 如果登录成功,则初始化内容
            self.cookie = data["cookie"]
            self.version = data["version"]
            self.channel = data["channel"]
            self.server_list = data["server_list"]
            self.uid = data["uid"]
            default_server = data["default_server"]
            for server in self.server_list:
                print(str(server["id"])+"-"+server["name"])

            # 加入基本服务器
            # index = 0
            # for server in self.server_list:
            #     self.cb_server.addItem(server["name"])
            #     if int(server["id"]) == default_server:
            #         self.cb_server.setCurrentIndex(index)
            #     index += 1
            # self.statusBarSignal.emit("登录成功,请选择服务器")
            self.first_finish = True
            if self.isauto and self.istart == 0:
                self.istart += 1
                time.sleep(2)
                self.second_login(default_server)
            return True
        except Exception as e:
            log.error("第一次登录deal失败", str(e))
            ##self.statusBarSignal.emit("第一次登录deal失败" + str(e))

    # 按钮绑定实现,实现第二次登录
    def second_login(self, default_server):
        try:
            if self.first_finish:

                self.host = self.gethost(default_server)
                log.info("第二次登录", self.host, self.uid)
                gameLogin.second_login(self.host, self.uid, self)
            else:
                pass
                # self.statusBarSignal.emit("游戏登录错误!无法进入游戏!")
        except Exception as e:
            #self.statusBarSignal.emit("第二次登录失败" + str(e))
            log.error("第二次登录失败", str(e))

    def gethost(self, default_server):
        for server in self.server_list:
            if str(server["id"]) == str(default_server):
                return server["host"]
        return ""

    def second_login_deal(self, data):
        try:
            # 如果第二次登录出现问题
            if "error" in data:
                #self.statusBarSignal.emit("第二次登录错误:" + data["errmsg"])
                self.second_finish = False
                return False
            # 第二次登录完成
            # self.statusBarSignal.emit("初始化信息...")
            gameFunction.start_game_function(version=self.version, channel=self.channel,
                                             cookies=self.cookie, server=self.host)
            # self.statusBarSignal.emit("获取用户信息...")
            gameData.get_data(version=self.version, channel=self.channel, cookies=self.cookie,
                              server=self.host)
            self.second_finish = True
            if not self.is_sl_login:
                self.is_sl_login = True
                # self.statusBarSignal.emit("初始化界面...")
                # login()
            return True
        except urllib3.exceptions.ReadTimeoutError as e:
            pass
            #self.statusBarSignal.emit("登录超时:" + str(e))
        except Exception as e:
            pass
            #self.statusBarSignal.emit("第二次登录错误:" + str(e))


class BattleMain:
    """
    出征各种处理,远征检测等
    """

    def __init__(self):
        self.config_name = ''
        self.fleet = 0
        self.skip_num = 0

        self.config = dict()
        self.point = ""
        self.pointNode = 0
        self.pointNextNode = 0
        self.map = ''
        self.format = 0
        self.spyFail = False
        self.skip = False
        self.skipDeal = 0
        self.hmChange = False
        self.qmChange = False
        self.qtChange = False
        self.reward = False
        self.nightFight = False
        self.resource = False
        self.detail_flag = None
        self.rwList = {}
        self.nowPoint = '0'
        self.name = ""
        # 常量信息
        self.END_500_SHIP = 0
        self.END_SL = 1
        self.END_FINISH = 3
        self.END_SPECIAL_SHIP = 4
        self.END_ERROR = 5

        # 保存信息
        self.repair_format = 0
        self.is_dismantle = False
        self.run_num = 0
        self.run_max_num = 0

    @staticmethod
    def check_explore():
        """
        功能:检测远征
        :return: None
        """
        explore_list = {}
        for eachExplore in gameData.exploreInfo:
            if eachExplore['endTime'] < int(time.time()):
                explore_list[eachExplore['fleetId']] = eachExplore['exploreId']
        if len(explore_list) != 0:
            explore_new = {}
            for fleet, exploreId in explore_list.items():
                explore_result = gameFunction.get_explore(exploreId)  # 取远征结果
                if explore_result['bigSuccess'] == 1:
                    result = ["大成功", ' big success']
                else:
                    result = ["成功", ' success']
                map_name = re.sub(pattern="000", repl="-",
                                  string=str(exploreId))
                # 获取奖励
                reward = ",获得:"
                if 'newAward' in explore_result and len('newAward') != 0:
                    for cid, num in explore_result['newAward'].items():
                        count.add_other(str(cid), num)
                        reward += battle_main.getshipItem(
                            int(cid))["title"] + str(num) + " "
                # 更新任务信息
                gameFunction.updateTaskVo(explore_result)
                # 更新资源信息
                if 'userResVo' in explore_result and len(explore_result['userResVo']) != 0:
                    gameData.oil = explore_result['userResVo']['oil']
                    gameData.ammo = explore_result['userResVo']['ammo']
                    gameData.steel = explore_result['userResVo']['steel']
                    gameData.aluminium = explore_result['userResVo']['aluminium']
                # 更新详细信息
                if "detailInfo" in explore_result:
                    gameData.userDetail = explore_result["detailInfo"]
                set_log('远征' + map_name + result[0] + reward, 0)
                log.info('Explored ' + map_name + result[1])
                log.info('Start explore ' + map_name)
                other_function.refresh_base_data()
                time.sleep(2)
                set_log("开始远征 " + map_name, 1)
                explore_new = gameFunction.start_explore(
                    maps=exploreId, team=fleet)  # 开启新远征
                time.sleep(2)
            gameData.exploreInfo.clear()
            for eachExplore in explore_new['pveExploreVo']['levels']:
                gameData.exploreInfo.append(eachExplore)

    @staticmethod
    def check_task():
        """
        功能:检测任务
        :return: None
        """
        try:
            task_finish = []
            task_add = {}
            for cid, task in gameData.taskInfo.items():
                if task['condition'][0]['finishedAmount'] >= task['condition'][0]['totalAmount']:
                    task_finish.append(int(cid))
            if len(task_finish) != 0:
                for taskCid in task_finish:
                    task_data = gameFunction.get_task(cid=taskCid)
                    # 更新资源信息
                    if 'userResVo' in task_data:
                        gameData.oil = task_data['userResVo']['oil']
                        gameData.ammo = task_data['userResVo']['ammo']
                        gameData.steel = task_data['userResVo']['steel']
                        gameData.aluminium = task_data['userResVo']['aluminium']
                        other_function.refresh_base_data()
                    # 获取资源
                    reward = ',获得:'
                    if len(task_data['attach']) != 0:
                        for cid, num in task_data['attach'].items():
                            count.add_other(str(cid), num)
                            reward += battle_main.getshipItem(
                                int(cid))["title"] + str(num) + " "
                    log.info('Complete task ' +
                             gameData.taskInfo[taskCid]['title'])
                    set_log(
                        "完成任务:" + gameData.taskInfo[taskCid]['title'] + reward, 0)
                    del gameData.taskInfo[taskCid]
                    if 'taskVo' in task_data:
                        for newTask in task_data['taskVo']:
                            task_add[int(newTask['taskCid'])] = newTask
                    time.sleep(3)
                gameData.taskInfo.update(task_add)
                # windows_main.task_data.emit(gameData.taskInfo)  # 游戏任务
                log.info("Task Check Complete")
        except Exception as e:
            log.error("Check Task ERROR:", str(e))
            raise

    @staticmethod
    def getEquipment(cid):
        """
        获取装备说明 
        """
        shipEquipmnt = init_data.init_data["shipEquipmnt"]
        for eq in shipEquipmnt:
            if eq["cid"] == cid:
                return eq

    @staticmethod
    def getCookbook(cid):
        """
        获取菜谱说明 
        """
        Cookbook = init_data.init_data["ShipCookbook"]
        for cb in Cookbook:
            if cb["cid"] == cid:
                return cb

    @staticmethod
    def getshipItem(cid):
        """
        获取资源说明
        """

        if cid in RES:
            return {"title": RES[int(cid)]}
        shipItem = init_data.init_data["shipItem"]
        for st in shipItem:
            if st["cid"] == cid:
                return st
        shipEquipmnt = init_data.init_data["shipEquipmnt"]
        for sq in shipEquipmnt:
            if sq["cid"] == cid:
                return sq
        shipCardWu = init_data.init_data["shipCardWu"]
        for scw in shipCardWu:
            if scw["cid"] == cid:
                return scw

        return {"title": "未知物品"}


class CampaignMain:
    """
    战役战斗
    """

    def __init__(self):
        self.campaignTotal = 0
        self.remainNum = 0
        self.map = '101'
        self.isNightFight = False
        self.difficult = 0
        self.campaignMap = []
        self.repair = 0
        self.format = 0
        self.fleet = []

    def main(self, maps, repair, formats, night, sl):
        """
        战役主要
        :return:None
        """
        self.campaignTotal = gameData.campaignTotal
        self.campaignMap = gameData.campaignMap  # 储存着战役的对应关系
        self.localmap = ['101', '102', '201', '202',
                         '301', '302', '401', '402', '501', '502']
        self.remainNum = gameData.campaignRemainNum
        self.repair = repair
        self.isNightFight = night
        self.format = formats + 1
        if gameData.campaignRemainNum == 0:  # 战役完成,删除任务
            return False
        if int(maps) >= len(self.localmap):  # 检测是否能打这个点
            return False
        else:
            if self.localmap[int(maps)] in self.campaignMap:
                self.map = self.localmap[int(maps)]
            else:
                return False

        try:
            log.info('=-=-=-=-=-=-Start-=-=-=-=-=-=')
            # 选图页面
            # windows_main.lt_our_2.clear()
            time.sleep(3)
            map_data = gameFunction.campaign_get_fleet(maps=self.map)
            self.fleet.clear()
            for each_ship in map_data['campaignLevelFleet']:
                if each_ship != 0 and each_ship != '0':
                    self.fleet.append(int(each_ship))
            other_function.refresh_our_ship_data(fleet=self.fleet, name='战役队伍')
            # 进行修理检测
            self.check_repair(fleet=self.fleet, repair=self.repair)
            # 进行补给
            gameFunction.supply(ship=self.fleet)
            time.sleep(2)
            # 进行索敌
            log.info('Campaign spy')
            set_log('进行战役索敌...', 1)
            spy_data = gameFunction.campaign_get_spy(maps=self.map)
            other_function.refresh_foe_ship_data(
                spy_data['enemyVO']['enemyShips'])
            time.sleep(2)
            # 开始战斗
            log.info('Campaign fight start')
            campaign_data = gameFunction.campaign_fight(
                maps=self.map, formats=self.format)
            fight_time = other_function.ai_delay(campaign_data['warReport'])
            set_log('开始战役...等待' + str(fight_time) + '秒', 1)
            # 判断是否进行SL
            if sl is True:
                set_log("战役SL..执行完成", 0)
                other_function.refresh_base_data()
                time.sleep(5)
                return True
            time.sleep(fight_time)
            # 判断是否需要夜战
            if campaign_data['warReport']['canDoNightWar'] == 1 and self.isNightFight is True:
                # 可以进行夜战
                set_log('开始战役夜战...', 1)
                log.info('Campaign night fight...')
                campaign_result = gameFunction.campaign_get_result(
                    is_night_fight=1)
                fight_time = other_function.ai_delay_night(
                    campaign_result['extraProgress'])
                set_log('夜战...等待' + str(fight_time) + '秒', 1)
                time.sleep(fight_time)
            else:
                # 不进行夜战
                campaign_result = gameFunction.campaign_get_result(
                    is_night_fight=0)
                log.info('Finish campaign')
            campaign_name = ['驱逐简单战役', '驱逐困难战役', '巡洋简单战役', '巡洋困难战役', '战列简单战役',
                             '战列困难战役', '航母简单战役', '航母困难战役', '潜艇简单战役', '潜艇困难战役']
            reward = ""
            # 刷新任务信息
            gameFunction.updateTaskVo(campaign_result)
            if "newAward" in campaign_result:
                for index, num in campaign_result['newAward'].items():
                    count.add_other(str(index), num)
                    reward += battle_main.getshipItem(int(index)
                                                      )["title"] + ":" + str(num) + " "
            set_log(campaign_name[int(maps)] + '  获得:' + reward, 0)

            # 更新人物血量信息
            # windows_main.lt_our_2.clear()
            for ship in campaign_result['shipVO']:
                gameData.upgrade_ship(ids=ship['id'], jsons=ship)
            # 更新资源信息
            other_function.refresh_base_data()
            time.sleep(3)
            # 完成战役并刷新战役数据

            gameData.get_campaign_data()
            if len(gameData.Tactics) != 0:
                gameFunction.getTactics()  # 战术刷新
                # windows_main.tactics_data.emit(gameData.Tactics)
        except Exception as e:
            log.error('Campaign ERROR:', str(e))
            raise
        return True

    @staticmethod
    def check_repair(fleet, repair):
        need_repair = []
        if len(fleet) != 0:
            for each_ship in fleet:
                if repair == 0:  # 中破修理
                    if gameData.allShip[each_ship]['battleProps']['hp'] * 2 < \
                            gameData.allShip[each_ship]['battlePropsMax']['hp']:
                        need_repair.append(each_ship)
                elif repair == 1:  # 大破修理
                    if gameData.allShip[each_ship]['battleProps']['hp'] * 4 < \
                            gameData.allShip[each_ship]['battlePropsMax']['hp']:
                        need_repair.append(each_ship)
        if len(need_repair) != 0:
            time.sleep(3)
            repair_data = gameFunction.repair(ship=need_repair)
            ship = [init_data.ship_cid_wu[gameData.allShip[int(
                ids)]['shipCid']]['title'] for ids in need_repair]
            ship = " ".join(ship)
            log.info('修理船只:' + str(len(need_repair)) + "个:" + ship)
            set_log('修理船只:' + str(len(need_repair)) + "个:" + ship, 0)
            # 更新快修信息
            if 'packageVo' in repair_data and repair_data['packageVo'][0]['itemCid'] == 541:
                gameData.fastRepair = repair_data['packageVo'][0]['num']
                other_function.refresh_base_data()
            # 更新资源信息
            if 'userVo' in repair_data and len(repair_data['userVo']) != 0:
                gameData.oil = repair_data['userVo']['oil']
                gameData.ammo = repair_data['userVo']['ammo']
                gameData.steel = repair_data['userVo']['steel']
                gameData.aluminium = repair_data['userVo']['aluminium']
                other_function.refresh_base_data()
            # 更新任务信息
            gameFunction.updateTaskVo(repair_data)
            log.info('Finish Repair')
            time.sleep(3)


class PvpMain:
    def __init__(self):
        self.team = 0
        self.format = 0
        self.night = False
        self.cv = False
        self.ss = False
        self.pvp = "pvp"
        self.friendlist = ""
        self.listfriend = []
        self.lost5 = []  # 5次未能击败的对手id

    def main(self, team, formats, night, cv, ss, pvp="pvp", friendlist=""):
        self.team = team + 1
        self.format = formats + 1
        self.night = night
        self.cv = cv
        self.ss = ss
        self.pvp = pvp
        self.friendlist = friendlist.replace(' ', '')
        self.listfriend = []
        if pvp == "pvp":

            list_data = gameFunction.pvp_get_list  # 演习对手列表
            self.upgrade_list(list_data)
        else:

            if len(self.friendlist) == 0:
                return False
            self.friendlist = self.friendlist.split(',')
            if len(self.friendlist) == 0:
                return False
            num = 0
            for x in self.friendlist:
                self.listfriend.append(x)
                num += 1
                if num >= 3:
                    break
            if len(self.listfriend) == 0:
                return False

            list_data = gameFunction.friend_get_list  # 演习好友对手列表
        log.debug('Refresh {pvp} list'.format(pvp=pvp))

        fight_td = []  # 0uid, 1user_name, 2fleet_name
        other_function.refresh_our_ship_data(fleet=gameData.fleet[self.team - 1],
                                             name=gameData.fleetName[self.team - 1])
        log.debug('Start {pvp}'.format(pvp=pvp))
        if 'list' not in list_data:
            set_log('{pvp}列表获取失败'.format(pvp=pvp), 1)
            return False
        try:
            if pvp == "pvp":
                for each_td in list_data['list']:
                    if each_td['resultLevel'] == 0 and each_td['uid'] not in self.lost5:
                        fight_td.append(
                            [each_td['uid'], each_td['username'], each_td['fleetName']])

            else:
                for each_td in list_data["list"]:
                    if each_td['uid'] not in self.listfriend or each_td['uid'] in self.lost5:
                        continue
                    resultfriend = gameFunction.friend_visitorFriend(
                        each_td['uid'])
                    if resultfriend['challengeScore'] == 0:

                        fight_td.append(
                            [each_td['uid'], each_td['username'], each_td['sign']])

            if len(fight_td) == 0:
                return False
            # 检测胜率
            if config_function.cb_flagwin and th_main.Flagship >= 5:
                self.lost5.append(fight_td[0][0])
                set_log("击沉旗舰, 进行跳过该对手："+str(th_main.Flagship), 1)
                th_main.Flagship = 0
                return
            # 开始索敌
            fight_td = fight_td[0]
            log.info('{pvp} spy...'.format(pvp=pvp))
            set_log('{pvp}演习...索敌...'.format(pvp=pvp), 1)
            spy_data = gameFunction.pvp_spy(
                uid=fight_td[0], fleet=self.team, pvp=pvp)
            other_function.refresh_foe_ship_data(
                spy_data['enemyVO']['enemyShips'])
            time.sleep(2)
            # 开始战斗
            random_time = random.randint(15, 30)
            log.info('{pvp} fight...wait'.format(pvp=pvp), random_time, '秒')
            set_log('{pvp}演习开始战斗,等待...'.format(
                pvp=pvp) + str(random_time) + "秒", 1)
            fight_data = gameFunction.pvp_fight(
                uid=fight_td[0], fleet=self.team, formats=self.format, pvp=pvp)
            # 是否击沉旗舰检测
            if fight_data['warReport']['hpBeforeNightWarEnemy'][0] != 0 and th_main.Flagship < 5:
                th_main.Flagship = th_main.Flagship+1
                set_log("宣战未击沉旗舰, 进行SL 次数："+str(th_main.Flagship), 1)
                log.info(
                    "Flagship not kill to reLogin")
                other_function.re_login()  # 重启sl
                count.add_items(count.SL_COUNT, 1)
                return
            time.sleep(random_time)
            # 进行夜战
            if fight_data['warReport']['canDoNightWar'] == 1 and self.night is True:
                log.info(pvp+' night fight...')
                set_log('{pvp}演习...夜战...'.format(pvp=pvp), 1)
                result_data = gameFunction.pvp_get_result(
                    is_night_fight=1, pvp=pvp)
                time.sleep(random_time)
            else:
                result_data = gameFunction.pvp_get_result(
                    is_night_fight=0, pvp=pvp)
            # 进行结算
            # windows_main.lt_our_2.clear()
            gameFunction.updateTaskVo(result_data)

            pj = ['-', 'SS', 'S', 'A', 'B', 'C', 'D']
            set_log(
                '{pvp}演习..'.format(pvp=pvp) + str(fight_td[1]) + '-' + str(
                    fight_td[2]) + '--' + pj[result_data['warResult']['resultLevel']],
                0)
            log.info(pvp,
                     str(fight_td[1]) + '-' + str(fight_td[2]) + '--' + pj[result_data['warResult']['resultLevel']])
            th_main.Flagship = 0
            return True
        except Exception as e:
            log.error(pvp+' ERROR:', str(e))
            raise

    @staticmethod
    def upgrade_friend_list(data):
        try:
            num = 0
            friendstrs = ""
            if 'list' not in data:
                return
            for user in data['list']:
                friendstrs += user['uid']+','
                num += 1
                if num >= 3:
                    friendstrs = friendstrs.rstrip(',')
                    break
            print(friendstrs)

        except Exception as e:
            log.error('Upgrade friend list ERROR:', str(e))
            raise

    @staticmethod
    def upgrade_list(data):
        try:
            pj = ['-', 'SS', 'S', 'A', 'B', 'C', 'D']
            #windows_add_pvp.add_signal.emit({'cls': 'cls'})
            for user in data['list']:
                # 显示用户信息
                user_name = user['username'][: 4]
                uesr_level = "Lv." + str(user['level'])
                user_pj = "评价:" + pj[user['resultLevel']]
                user_ship = []
                for ship in user['ships']:
                    ship_cid = ship['shipCid']  # 演习不能打开
                    ship_data = init_data.ship_cid_wu[ship_cid]
                    ship_path = ""
                    if "shipIndex" in ship_data:
                        ship_path = 'icon/photo/' + \
                            str(int(ship_data['shipIndex'])) + ".png"
                    if "picId" in ship_data:
                        ship_path = 'icon/photo/' + \
                            str(ship_data['picId']) + ".png"
                    ship_name = ship['title'][: 4]
                    ship_level = "Lv." + str(ship['level'])
                    user_ship.append(
                        {'ship_name': ship_name, 'ship_level': ship_level, 'ship_path': ship_path})
                data = {'user_name': user_name, 'user_level': uesr_level,
                        'user_pj': user_pj, 'user_ship': user_ship}
                # windows_add_pvp.add_signal.emit(data)

        except Exception as e:
            log.error('Upgrade pvp list ERROR:', str(e))
            raise


class OtherFunction:
    def __init__(self):
        self.wait_shower = []
        self.wait_shower_low = []
        self.on_rank = False
        self.showeron_lock = False

    @staticmethod
    def change_fleet(fleet, ships):
        data = {}
        s = [-1, -1, -1, -1, -1, -1]  # 新队伍
        n = [-1, -1, -1, -1, -1, -1]  # 老队伍

        # 检测船只是否出现变动
        for ship in ships:
            if ship not in gameData.allShip:
                return False, "船只不存在"
        # 检测船只是否正在远征
        for ship in ships:
            if gameData.allShip[ship]["fleetId"] in [5, 6, 7, 8]:
                return False, "船只正在远征队伍中"

        # 循环检测添加船只进入列表
        index = 0
        for ship in ships:
            s[index] = int(ship)
            index += 1

        # 移除2号机
        for i in range(6):
            if s[i] != -1:
                fi = 0
                for fship in gameData.fleet[fleet]:
                    # 设置不同船但是同编号
                    scid = gameData.allShip[s[i]]["shipCid"]  # 获取cid
                    secid = init_data.ship_cid[scid]["evoCid"]  # 获取唯一evocid
                    fcid = gameData.allShip[fship]["shipCid"]
                    fecid = init_data.ship_cid[fcid]["evoCid"]
                    if secid == fecid and s[i] != fship:
                        data = gameFunction.remove_ship(
                            fleet=fleet + 1, path=fi)
                        # 设置换下来的船队伍id为0
                        gameData.allShip[fship]['fleetId'] = 0
                        gameData.allShip[fship]['fleet_id'] = 0
                        set_log(
                            "移除船只："+gameData.allShip[fship]["title"], 1)
                        if len(data["fleetVo"]) > 1:
                            gameData.fleet[fleet] = data["fleetVo"][fleet]["ships"]
                        else:  # 国际服返回的是单个队伍
                            gameData.fleet[fleet] = data["fleetVo"][0]["ships"]

                        time.sleep(2)
                    fi += 1

        index = 0
        fleet_ship = gameData.fleet[fleet]
        for ship in fleet_ship:
            n[index] = int(ship)
            index += 1

        remove_index = -1
        is_operate = False
        for i in range(6):
            if s[i] == -1 and n[i] != -1:  # 新队伍不存在而老队伍存在
                is_operate = True
                if remove_index == -1:
                    remove_index = i
                data = gameFunction.remove_ship(
                    fleet=fleet + 1, path=remove_index)
                # 设置换下来的船队伍id为0
                set_log("移除船只："+gameData.allShip[n[i]]["title"], 1)
                if n[i] not in s:  # 这船不属于新队伍
                    gameData.allShip[n[i]]['fleetId'] = 0
                    gameData.allShip[n[i]]['fleet_id'] = 0
                if len(data["fleetVo"]) > 1:
                    gameData.fleet[fleet] = data["fleetVo"][fleet]["ships"]
                else:  # 国际服返回的是单个队伍
                    gameData.fleet[fleet] = data["fleetVo"][0]["ships"]
                time.sleep(2)
            elif int(s[i]) != int(n[i]) and int(s[i]) != -1:  # 该船不等于新队伍而且新队伍不为空
                is_operate = True
                # 如果已经是该船了将不进行换船
                if s[i] in gameData.fleet[fleet] and gameData.fleet[fleet].index(s[i]) == i:
                    continue
                data = gameFunction.change_ship(
                    fleet=fleet + 1, ids=s[i], path=i)
                gameData.fleet[fleet] = data["fleetVo"][fleet]["ships"]
                set_log("换上船只："+gameData.allShip[s[i]]["title"], 1)
                if int(n[i]) != -1 and n[i] not in s:
                    # 设置换下来的船队伍交换上船的队伍id
                    gameData.allShip[n[i]
                                     ]['fleetId'] = gameData.allShip[s[i]]['fleetId']
                    gameData.allShip[n[i]
                                     ]['fleet_id'] = gameData.allShip[s[i]]['fleet_id']
                time.sleep(2)
        if is_operate:
            name = [init_data.ship_cid_wu[gameData.allShip[x]["shipCid"]]["title"] for x in ships if
                    x in gameData.allShip]
            set_log("编队:队伍%d %s" % (fleet + 1, " ".join(name)), 0)
            log.i("编队:队伍%d %s" % (fleet + 1, " ".join(name)))

        other_function.refresh_our_ship_data(
            fleet=gameData.fleet[fleet], name=gameData.fleetName[fleet])
        return True, ""

    @staticmethod
    def show_mine(windows):
        try:
            QMessageBox.information(windows, '护萌宝·Re-我的',
                                    "等级:" + str(gameData.userDetail["level"])
                                    + "\n经验:" + str(gameData.userDetail["exp"])
                                    + "\n距离下一级:" +
                                    str(gameData.userDetail["lastLevelExpNeed"])
                                    + "\n收集率:" +
                                    str(gameData.userDetail["collection"])

                                    + "\n\n总出征:" +
                                    str(gameData.userDetail["pveNum"])
                                    + "\n出征成功:" +
                                    str(gameData.userDetail["pveWin"])
                                    + "\n出征失败:" +
                                    str(gameData.userDetail["pveLost"])
                                    + "\n胜率:" + str(
                                        int(gameData.userDetail["pveWin"]) / int(gameData.userDetail["pveNum"]) * 100)[
                                        : 4] + "%"


                                    + "\n\n演习次数:" +
                                    str(gameData.userDetail["pvpNum"])
                                    + "\n演习成功:" +
                                    str(gameData.userDetail["pvpWin"])
                                    + "\n演习失败:" +
                                    str(gameData.userDetail["pvpLost"])
                                    + "\n胜率:" + str(
                                        int(gameData.userDetail["pvpWin"]) / int(gameData.userDetail["pvpNum"]) * 100)[
                                        : 4] + "%"

                                    + "\n\n远征数量:" +
                                    str(gameData.userDetail["exploreNum"])
                                    + "\n远征大成功:" + str(
                                        gameData.userDetail["exploreBigSuccessNum"])
                                    + "\n大成功率:" + str(
                                        int(gameData.userDetail["exploreBigSuccessNum"]) / int(gameData.userDetail["exploreNum"]) * 100)[
                                        : 4] + "%", QMessageBox.Yes)
        except Exception as e:
            print(e)

    @staticmethod
    def get_log(windows):
        log.get_log()
        QMessageBox.information(
            windows, "护萌宝·Re", "已将日志输出至桌面!", QMessageBox.Yes)

    @staticmethod
    def show_mine_collection():
        windows_mine.select_ship = -1
        windows_mine.tw_detail.clear()
        windows_mine.refresh_list()
        windows_mine.show()

    @staticmethod
    def autoSecretary():
        """ 
        自动更换秘书舰
        """
        if gameData.secretary == 0:
            set_log("未获取到秘书舰id", 0)
            set_log("关闭功能[更换秘书舰]", 0)
            # windows_main.cb_secretary.setChecked(False)
            return
        Secretaryship = gameData.allShip[gameData.secretary]
        if Secretaryship["love"] == Secretaryship["loveMax"]:
            shipid = 0
            for ids, ship in gameData.allShip.items():

                if ship["isLocked"] == 1:
                    if ship["love"] != ship["loveMax"]:
                        shipid = ids
                        break
            if shipid != 0:
                time.sleep(2)
                gameFunction.setSecretary(shipid)
                time.sleep(2)
                Secretaryship = gameData.allShip[shipid]
                set_log("设置秘书舰为:"+Secretaryship["title"]+"♥ "+str(
                    Secretaryship["love"])+"/"+str(Secretaryship["loveMax"]), 0)
            else:
                set_log("关闭功能[更换秘书舰]", 0)
                config_function.cb_secretary = False
                # windows_main.cb_secretary.setChecked(False)

    @staticmethod
    def free_shower(isduwu=False):
        """ 
        泡澡 isduwu 是否泡澡队伍
        """
        if other_function.showeron_lock:
            time.sleep(5)  # 延迟
            other_function.showeron_lock = False
            return
        else:
            other_function.showeron_lock = True

        OtherFunction.repair_complete()

        repairring_data = []
        # 遍历船只数据
        for dock in gameData.repairDock:
            if "shipId" in dock:
                repairring_data.append(int(dock["shipId"]))
        # 正在修理的船

        wait_shower = []
        for ids, ship in gameData.allShip.items():
            if "fleet_id" in ship and ship["fleet_id"] != 0:
                if isduwu:
                    if ship["fleet_id"] in [5, 6, 7, 8]:
                        continue
                else:
                    continue

            if ids in repairring_data:
                continue
            if ship["isLocked"] != 1:
                continue
            if ship["battleProps"]["hp"] != ship["battlePropsMax"]["hp"]:
                wait_shower.append(int(ship["id"]))

        repair_data = {}
        for dock in gameData.repairDock:
            if dock["locked"] == 0:
                if "endTime" not in dock:
                    if len(wait_shower) > 0:

                        if OtherFunction.repair_Docking(wait_shower[0]):
                            del wait_shower[0]
                            continue
                        showerdata = gameFunction.shower(ship=wait_shower[0])
                        if 'eid' in showerdata:
                            if showerdata['eid'] == -208 or showerdata['eid'] == -209:
                                time.sleep(3)
                                set_log("延迟修理", 1)
                                repair_data = gameFunction.repair(
                                    [wait_shower[0]])
                                del wait_shower[0]
                                time.sleep(3)
                                continue

                        set_log(
                            "泡澡船只:" + init_data.ship_cid_wu[gameData.allShip[wait_shower[0]]["shipCid"]]['title'], 0)
                        time.sleep(3)
                        repair_data = gameFunction.rubdown(ship=wait_shower[0])
                        if repair_data != {}:
                            if 'repairDockVo' in repair_data:
                                gameData.repairDock = repair_data['repairDockVo']
                        set_log(
                            "搓澡船只:" + init_data.ship_cid_wu[gameData.allShip[wait_shower[0]]["shipCid"]]['title'], 1)

                        del wait_shower[0]

        limit_time = ""
        if False:

            limit_time = 0
            if limit_time != 0:
                # 检查是否有超时的
                for dock in gameData.repairDock:
                    if 'endTime' in dock:
                        if limit_time != -1 and float(limit_time) * 60 * 60 < dock['endTime'] - time.time():
                            repair_data = gameFunction.repair([dock['shipId']])
                            set_log(
                                "超过设定时间["+limit_time+"]快修船只:" + gameData.allShip[int(dock['shipId'])]['title'], 0)
                            time.sleep(3)
        other_function.showeron_lock = False

    @staticmethod
    def repair_complete():
        """ 
        检查修理
        """
        data = {}
        for dock in gameData.repairDock:
            if "endTime" in dock and dock["endTime"] < time.time():
                ids = int(dock["shipId"])
                data = gameFunction.repair_complete(
                    ids=dock["id"], ship=dock["shipId"])
                gameData.allShip[ids] = data["shipVO"]
                set_log(
                    "出浴:" + init_data.ship_cid_wu[gameData.allShip[ids]["shipCid"]]["title"], 0)
                time.sleep(3)
        if "repairDockVo" in data:
            gameData.repairDock = data["repairDockVo"]

    @staticmethod
    def repair_Docking(ship):

        for dock in gameData.repairDock:
            if "shipId" in dock and int(dock["shipId"]) == ship:
                return True
        return False

    def shower(self, repair_ship, limit_time):
        """  
        泡澡任务
        """
        if self.showeron_lock:
            self.showeron_lock = False
            return -1, (time.time()+20)  # 延迟20秒
        else:
            self.showeron_lock = True
        OtherFunction.repair_complete()
        able_dock = 0
        # 正在泡澡的船只
        showering = []
        self.wait_shower = []
        for dock in gameData.repairDock:
            if "shipId" in dock:
                showering.append(int(dock["shipId"]))
        for ship in repair_ship:
            if gameData.allShip[int(ship)]["battleProps"]['hp'] != gameData.allShip[int(ship)]["battlePropsMax"]['hp'] and int(ship) not in showering:
                self.wait_shower.append(ship)
        left_time = -1
        # 获取空位数量
        for i in range(4):
            if gameData.repairDock[i]['locked'] == 0 and ('endTime' not in gameData.repairDock[i] or (
                    'endTime' in gameData.repairDock[i] and gameData.repairDock[i]['endTime'] < time.time())):
                able_dock += 1
        # 没有没有空位了
        if able_dock == 0:
            self.showeron_lock = False
            return -1, other_function.get_min_repair_time()
        repair_data = None
        # 将船只添加入
        while able_dock > 0 and len(self.wait_shower) > 0:
            if OtherFunction.repair_Docking(self.wait_shower[0]):
                del self.wait_shower[0]
                continue
            showerdata = gameFunction.shower(ship=self.wait_shower[0])
            if 'eid' in showerdata:
                if showerdata['eid'] == -208 or showerdata['eid'] == -209:
                    time.sleep(3)
                    set_log("延迟修理", 1)
                    repair_data = gameFunction.repair([self.wait_shower[0]])
                    del self.wait_shower[0]
                    time.sleep(3)
                    continue
            set_log(
                "泡澡船只:" + init_data.ship_cid_wu[gameData.allShip[self.wait_shower[0]]["shipCid"]]['title'], 0)
            time.sleep(3)
            repair_data = gameFunction.rubdown(ship=self.wait_shower[0])
            set_log(
                "搓澡船只:" + init_data.ship_cid_wu[gameData.allShip[self.wait_shower[0]]["shipCid"]]['title'], 1)
            able_dock -= 1
            # 检查是否有超时的
            for dock in repair_data['repairDockVo']:
                if 'endTime' in dock:
                    if limit_time != -1 and float(limit_time) * 60 * 60 < dock['endTime'] - dock['startTime']:
                        repair_data = gameFunction.repair([dock['shipId']])
                        able_dock += 1
                        time.sleep(3)
            del self.wait_shower[0]
            time.sleep(3)
        # 刷新船只数据
        if repair_data is not None:
            if 'repairDockVo' in repair_data:
                gameData.repairDock = repair_data['repairDockVo']
            left_time = other_function.get_min_repair_time()
            self.showeron_lock = False
            return -1, left_time
        self.showeron_lock = False
        return -1, other_function.get_min_repair_time()

    @staticmethod
    def re_login():
        try:
            log.info("Try to relogin")
            session.new_session()
            gameLogin.re_login(windows_login)
            config_function.main_save()

        except HmError as e:
            log.error('Re login ERROR:', e.message)
            raise
        except Exception as e:
            log.error('Re login ERROR:', str(e))

    @staticmethod
    def check_support(fleet):
        """
        功能:进行补给检测
        :return:None
        """
        set_log('补给检测', 1)
        log.info('Check support')
        # 检测是否需要补给
        need_support = False
        for ship in fleet:
            if str(gameData.allShip[int(ship)]['tactics']['3']) == "10001774":
                tacticsinfo = {}
                shipt = {}
                for shiptactic in gameData.Tactics:
                    if str(shiptactic["boat_id"]) == str(ship) and str(10001774) == str(shiptactic["tactics_id"]):
                        shipt = shiptactic
                        break
                for shiptact in init_data.init_data['ShipTactics']:
                    if shiptact['cid'] == shipt["cid"]:
                        tacticsinfo = shiptact
                        break
                if "needRes" in tacticsinfo:
                    if '10341' in tacticsinfo["needRes"]:
                        baifen = 1.1
                        if tacticsinfo['level'] == 3:
                            baifen = 1.2
                        set_log('后备弹技能 Level'+str(tacticsinfo['level']), 1)
                        if gameData.allShip[int(ship)]['battleProps']['ammo'] != \
                                int(gameData.allShip[int(ship)]['battlePropsMax']['ammo']*baifen):
                            need_support = True
            elif gameData.allShip[int(ship)]['battleProps']['ammo'] != \
                    gameData.allShip[int(ship)]['battlePropsMax']['ammo']:
                need_support = True
            if gameData.allShip[int(ship)]['battleProps']['oil'] != \
                    gameData.allShip[int(ship)]['battlePropsMax']['oil']:
                need_support = True

            if gameData.allShip[int(ship)]['battleProps']['aluminium'] != \
                    gameData.allShip[int(ship)]['battlePropsMax']['aluminium']:
                need_support = True

        if need_support is False:
            log.info("Support--needn't support")
            set_log('无需补给', 1)
            return True
        # 补给全部
        try:
            supply_ship_str = [str(x) for x in fleet]
            supply_data = gameFunction.supply(supply_ship_str)
            try:
                if 'userVo' in supply_data:
                    gameData.oil = supply_data['userVo']['oil']
                    gameData.ammo = supply_data['userVo']['ammo']
                    gameData.steel = supply_data['userVo']['steel']
                    gameData.aluminium = supply_data['userVo']['aluminium']
                    other_function.refresh_base_data()
                if "shipVO" in supply_data:
                    for ship in supply_data["shipVO"]:
                        gameData.upgrade_ship(ship["id"], ship)
            except Exception as e:
                log.error('Support Error:', str(e))
                raise
        except Exception as e:
            print('Support Error:', str(e))
            if e.code == -411:
                set_log("补给错误正在尝试重新登录", 1)
                other_function.re_login()
                other_function.check_support(fleet)
        time.sleep(3)
        log.info('Check support finish')
        return True

    def check_rank(self, fleet):
        """
        功能:上榜监测
        :param fleet: 船只
        :return: dict(上榜船只)
        """
        try:
            rank_in_fleet = []
            rank_data = gameData.get_rank_list()
            if 'destroyRank' not in rank_data:
                return rank_in_fleet

            # 击沉榜
            if rank_data['destroyRank']['my'] != 0:
                self.on_rank = True
                for rank_ship in rank_data['destroyRank']['list']:
                    if str(rank_ship['uid']) == str(gameData.uid):
                        cid = rank_ship['shipCid']
                        lev = rank_ship['level']
                        for ids, ship_data in gameData.allShip.items():
                            if int(ship_data['shipCid']) == int(cid) and int(ship_data['level']) == int(lev):
                                if ids in fleet:
                                    rank_in_fleet.append(ids)
            #  收集榜
            for rank in rank_data['handbookRank']['list']:
                if str(rank['uid']) == str(gameData.uid):
                    self.on_rank = True
                    break
            # 实力榜
            if rank_data['fleetRank']['my']['rank'] != 0:
                self.on_rank = True
            # 功勋榜
            if rank_data['exploitRank']['my']['rank'] != 0:
                self.on_rank = True
            return rank_in_fleet
        except HmError as e:
            log.error('Rank Error::', e.message)
            raise
        except Exception as e:
            log.error('Rank Error:', e)
            raise

    @staticmethod
    def continue_login_award():
        """
        功能:领取签到奖励
        :return:
        """
        if gameData.login_award != -1:
            data = gameFunction.login_award()
            if 'eid' in data:
                if int(data['eid']) == -1206:
                    set_log('签到奖励已经领取', 0)
                    return
            if "fixAward" in data:
                for ke in data["fixAward"]:
                    st = battle_main.getshipItem(int(ke))
                    set_log('签到获得' + st["title"]+"*" +
                            str(data["fixAward"][ke]), 0)
                    log.info('Login award', st["title"] +
                             "*"+str(data["fixAward"][ke]))
            gameData.login_award = data['marketingData']['continueLoginAward']['canGetDay']

    @staticmethod
    def cookfood():
        """
        功能:烹饪食物
        :return:
        """
        gameFunction.getUserInfo()
        if 'chief' in gameData.eatdata and int(gameData.eatdata['chief']) > 0 and int(gameData.eatdata['eatTimes']) < 3 and type(gameData.eatdata['buff']) == str:
            boatbuff = []
            if 'cookbookProficiency' in gameData.eatdata:
                for cookbookProficiency in gameData.eatdata["cookbookProficiency"]:
                    if cookbookProficiency["boat_id"] == gameData.eatdata["chief"]:
                        boatbuff.append(cookbookProficiency)
            if len(boatbuff) > 0:
                eatdata = gameFunction.eat(boatbuff[0]["cid"])
                cookname = battle_main.getCookbook(int(boatbuff[0]["cid"]))
                set_log('烹饪-'+cookname['title']+"结束时间："+time.strftime(
                    '%H:%M:%S', time.localtime(eatdata['buff']['endtime'])), 0)
                if 'userResVo' in eatdata and len(eatdata['userResVo']) != 0:
                    gameData.oil = eatdata['userResVo']['oil']
                    gameData.ammo = eatdata['userResVo']['ammo']
                    gameData.steel = eatdata['userResVo']['steel']
                    gameData.aluminium = eatdata['userResVo']['aluminium']
        time.sleep(2)

    @staticmethod
    def refresh_base_data():
        # 基础数据导入

        log.info('Refreshing base data...')
        # windows_main.base_data.emit(gameData.__dict__)
        count.save_count()
        log.info('Refresh base data success!')

    @staticmethod
    def upgrade_add_battle_fleet(fleet):
        try:
            if len(fleet) > 0:
                windows_add_battle.lt_fleet.clear()
                for each_ship in fleet:
                    windows_add_battle.lt_fleet.addItem(
                        'Lv.' + str(gameData.allShip[int(each_ship)]['level']) + ' ' + str(
                            gameData.allShip[int(each_ship)]['title']))
        except Exception as e:
            log.error('Upgrade start fleet ERROR:', str(e))
            raise

    @staticmethod
    def upgrade_add_pvp_fleet(fleet):
        try:
            if len(fleet) > 0:
                windows_add_pvp.lt_fleet.clear()
                for each_ship in fleet:
                    windows_add_pvp.lt_fleet.addItem(
                        'Lv.' + str(gameData.allShip[int(each_ship)]['level']) + ' ' + str(
                            gameData.allShip[int(each_ship)]['title']))
        except Exception as e:
            log.error('Upgrade start fleet ERROR:', str(e))
            raise

    @staticmethod
    def check_upgrade():
        """
        功能:检测脚本更新
        :return:
        """
        gameData.get_mine_version()
        if "notice" in gameData.mine:
            print(gameData.mine["notice"])
        if 'version' in gameData.mine:
            if gameData.mine['version'] > VERSION:  # 版本过期
                download = gameData.mine['url']
                new_version = gameData.mine['version']
                data = ''
                if str(new_version) in gameData.mine['history']:
                    data = gameData.mine['history'][str(new_version)]
                speak = '发现新版本:' + str(new_version)
                if data != '':
                    speak += '\n更新日志:' + data
                speak += '\n是否去下载最新版本?'
                print(speak)
            else:
                return False
        return False

    @staticmethod
    def refresh_foe_ship_data(dicts):
        """
        刷新敌人信息
        :return: None
        """
        log.info("Refreshing foe ship data... ")
        try:
            foe_ship = []
            foe_ship.clear()
            for ship in dicts:
                name = ship['title']
                hp = "HP   " + str(ship['hp']) + "/" + str(ship['hpMax'])
                foe_ship.append({'title': name, 'hp': hp})
            # windows_main.foe_ship.emit(foe_ship)
            log.info("Refresh finish")
        except Exception as e:
            log.error('Refresh foe ERROR:', str(e))
            raise

    @staticmethod
    def refresh_our_ship_data(fleet, name):
        """
        功能:刷新己方船只信息
        无返回值
        """
        log.info("Refreshing our ship data...")
        log.debug(fleet)
        try:
            # windows_main.tv_fleetName.setText(name)
            data = []
            for ship in fleet:
                name = init_data.ship_cid_wu[gameData.allShip[int(
                    ship)]['shipCid']]['title']
                hp = str(gameData.allShip[int(ship)]['battleProps']['hp']) + "/" + str(
                    gameData.allShip[int(ship)]['battlePropsMax']['hp'])
                level = "Lv." + str(gameData.allShip[int(ship)]['level'])
                path = "icon/photo/" + \
                    str(int(
                        init_data.handbook_id[gameData.allShip[int(ship)]['shipCid']])) + ".png"
                data.append({'title': name, 'hp': hp,
                             'level': level, 'path': path})
            # windows_main.our_ship.emit(data)
        except Exception as e:
            log.error('Refresh our ship data ERROR', str(e))
            raise
        log.info("Refresh our ship data finished")

    @staticmethod
    def refresh_our_joy_ship_data(fleet, name):
        """
        功能:刷新己方joy船只信息
        无返回值
        """
        log.info("Refreshing our joy ship data...")
        log.debug(fleet)
        try:
            # windows_main.tv_fleetName.setText(name)
            data = []
            for ship in fleet:
                shipdata = gameData.get_joyship(ship)
                name = shipdata["title"]
                hp = str(shipdata['battleProps']['hp']) + "/" + str(
                    shipdata['battlePropsMax']['hp'])
                level = "Lv." + str(shipdata['level'])
                path = ""
                if shipdata['shipCid'] in init_data.handbook_id:
                    path = "icon/photo/" + \
                        str(int(
                            init_data.handbook_id[shipdata['shipCid']])) + ".png"
                data.append({'title': name, 'hp': hp,
                             'level': level, 'path': path})
            # windows_main.our_ship.emit(data)
        except Exception as e:
            log.error('Refresh our ship data ERROR', str(e))
            raise
        log.info("Refresh our ship data finished")

    def ai_delay(self, data):
        times = 0
        if 'selfBuffs' in data and len(data['selfBuffs']) != 0:
            times += 4.12
        if 'openAirAttack' in data and len(data['openAirAttack']) != 0:
            times += 4.32
        if 'openMissileAttack' in data and len(data['openMissileAttack']) != 0:
            times += 4.93
        if 'openAntiSubAttack' in data and len(data['openAntiSubAttack']) != 0:
            times += 4.64
        if 'openTorpedoAttack' in data and len(data['openTorpedoAttack']) != 0:
            times += 5.14
        if 'normalAttacks' in data:
            times += len(data['normalAttacks']) * 2.78
        if 'normalAttacks2' in data:
            times += len(data['normalAttacks2']) * 2.78
        if 'closeTorpedoAttack' in data and len(data['closeTorpedoAttack']) != 0:
            times += 4.93
        if 'closeMissileAttack' in data and len(data['closeMissileAttack']) != 0:
            times += 4.93

        if times < 15:
            times += random.uniform(4, 8)
        times -= random.uniform(1, 2)
        return round(times, 2)

    def ai_delay_night(self, data):
        times = random.uniform(2, 3)
        times *= len(data['nightAttacks'])

        return round(times, 2)

    @staticmethod
    def get_min_repair_time():
        max_time = -1
        for dock in gameData.repairDock:
            if dock["locked"] == 0:
                if "endTime" in dock and dock['endTime'] > time.time():
                    if max_time != -1:
                        max_time = min(max_time, dock['endTime'])
                    else:
                        max_time = dock['endTime']
        return max_time


class ThMain:
    def __init__(self):
        self.classical_list = []
        self.timer_list = []
        self.is_running = False
        self.now_rw = ''
        self.automishujian = False
        self.set_time_unix = time.mktime(
            datetime.datetime(2021, 7, 1, 0, 0, 0).timetuple())

        self.list_read()

        # 任务计数模块
        self.num_max = 0
        self.num = 0

        # 任务保存模块
        self.rw_tmp = [0, '']

        # 登录失效
        self.login_fin = 0
        # 空闲泡澡 4次计算一次泡澡
        self.pz_num = 0
        # 0点是否重新登录过
        self.relo = False
        # 是否开启了黑钢
        self.cheigang = False
        # 未击沉旗舰sl次数
        self.Flagship = 0

    def th_main_def(self):
        set_log("进行初始化...", 0)
        log.info("Start main th")
        #rank_data = gameData.get_rank_list()
        set_log("开启主线程...", 0)
        while True:
            try:
                self.th_main()
            except HmError as e:
                set_log(e.message, 0)
                log.error(e.message)
                if e.code == -9995:  # 登录失效

                    self.login_fin += 1
                    set_log("第"+str(self.login_fin)+'次登录失效', 3)
                    time.sleep(5)
                    other_function.re_login()
                elif e.code == -102 or e.code == -105 or e.code == -106 or e.code == -107 or e.code == -108:
                    set_log('资源不足,终止任务', 3)

                    other_function.re_login()
                    continue
                elif e.code == -204 or e.code == -213:
                    set_log('资源不足,终止任务', 3)
                    log.cri("资源不足,终止任务")

                    other_function.re_login()
                    continue

                elif e.code == -9999:  # 服务器维护
                    set_log('服务器维护中...终止程序', 3)
                    log.cri('服务器维护中...终止程序')
                    break
                elif e.code == -411:  # 正在出征中
                    other_function.re_login()
                    continue
                elif e.code == -99999:  # 正在出征中
                    set_log('错误99999', 3)
                    log.cri('错误99999...')
                    break
                else:
                    other_function.re_login()
                    continue
            except requests.exceptions.ConnectTimeout as e:
                log.error('连接超时, 可能网络状态不好...')
                other_function.re_login()
                continue
            except requests.exceptions.HTTPError as e:
                log.error('网络错误:', str(e))
                other_function.re_login()
                continue
            except Exception as e:
                log.error('主线程错误:', str(e))
                set_log('主线程错误:' + str(e), 1)
                other_function.re_login()
                continue
        set_log("主线程被终止!", 0)

    def th_main(self):
        # classical [0name, 1type, 2num, 3num_max, 4data]
        # timer [0name, 1type, 2time, 3last_time, 4num, 5num_max, 6data]
        # type  0:经典 1:演习 2:战役
        while True:
            if True:

                # 任务刷新
                time.sleep(1)
                self.upgrade_list()
                # 定时任务检测并加入到经典任务
                if len(self.timer_list) != 0:
                    time_change = []
                    now_time = datetime.datetime.now()  # 取现行时间对象
                    now_time_unix = int(time.mktime(
                        now_time.timetuple()))  # 取现行时间时间戳
                    num = -1
                    for each_timer in self.timer_list:  # 遍历时间数组
                        num += 1
                        set_time_time = each_timer['time'].split(
                            ':')  # 分割设定时间部分
                        set_time_unix = int(time.mktime(datetime.datetime(now_time.year, now_time.month, now_time.day,
                                                                          int(set_time_time[0]), int(
                                                                              set_time_time[1]),
                                                                          now_time.second).timetuple()))  # 取设定时间时间戳
                        if now_time_unix > set_time_unix and each_timer['last_time'] != now_time.day:
                            # 满足现行时间大于设定时间且今日没运行
                            # 是周常任务
                            if 'week' in each_timer and each_timer['week'] > 0:
                                week = now_time.weekday()  # 0-6是星期一到星期日
                                if week+1 != each_timer['week']:  # 未满足跳过条件
                                    continue

                            time_change.append(num)
                            if each_timer['type'] == 0:
                                # 经典刷图
                                pass
                            elif each_timer['type'] == 1:
                                # 演习
                                classical = {
                                    'name': each_timer['name'],
                                    'num': 0,
                                    'num_max': 5,
                                    'type': 1,
                                    'data': each_timer['data']
                                }
                                self.classical_list.insert(0, classical)
                            elif each_timer['type'] == 2:
                                # 战役
                                classical = {
                                    'name': each_timer['name'],
                                    'num': 0,
                                    'num_max': 12,
                                    'type': 2,
                                    'data': each_timer['data']
                                }
                                self.classical_list.insert(0, classical)
                            elif each_timer['type'] == 5:
                                # 好友演习
                                classical = {
                                    'name': each_timer['name'],
                                    'num': 0,
                                    'num_max': 3,
                                    'type': 5,
                                    'data': each_timer['data']
                                }
                                self.classical_list.insert(0, classical)
                    if len(time_change) != 0:
                        for each_timer_change in time_change:
                            self.timer_list[each_timer_change]['last_time'] = now_time.day
                        self.list_save()
                        self.upgrade_list()
                # 经典任务
                # -----------------------
                # classical [0name, 1type, 2num, 3num_max, 4data]
                # timer [0name, 1type, 2time, 3last_time, 4num, 5num_max, 6data]
                # type  0:经典 1:演习 2:战役
                # ------------------------
                able_task = []
                if len(self.classical_list) != 0:
                    # 增加任务任务的冻结参数(用于旧版本)
                    num = 0
                    add_unlocked = []
                    for task in self.classical_list:
                        if task['type'] == 0 and 'locked' not in task:
                            add_unlocked.append(num)
                    for x in add_unlocked:
                        self.classical_list[x]['locked'] = -1
                        self.upgrade_list()
                        self.list_save()
                    # 检查冻结任务是否到解冻的时候
                    num = 0
                    unlocked_task = []
                    for task in self.classical_list:
                        if task['type'] == 0 and 'locked' in task and task['locked'] != -1 and time.time() > task['locked']:
                            unlocked_task.append(num)
                        num += 1
                    for x in unlocked_task:
                        self.classical_list[x]['locked'] = -1
                    # 检查可用任务
                    num = 0
                    for task in self.classical_list:
                        if task['type'] == 0 and task['locked'] == -1:
                            able_task.append({'data': task, 'index': num})
                        elif task['type'] != 0:
                            able_task.append({'data': task, 'index': num})
                        num += 1
                # 正式执行任务
                if len(able_task) != 0 and True:
                    now_rw = able_task[0]['data']
                    index = able_task[0]['index']

                    if self.now_rw != now_rw['name']:
                        log.info('Start', now_rw['name'])
                        set_log('开始任务:' + now_rw['name'], 3)
                        self.now_rw = now_rw['name']
                    if 'num_max' in now_rw:
                        self.num_max = now_rw['num_max']
                    if 'num' in now_rw:
                        self.num = now_rw['num']
                    if now_rw['type'] == 0:  # 经典出击任务
                        pass

                    elif now_rw['type'] == 1:  # 演习任务
                        config = now_rw['data']
                        battle_result = pvp_main.main(formats=config['format'], team=config['fleet'], night=config['night'],
                                                      cv=config['cv'], ss=config['ss'])
                        if len(self.classical_list) == 0:  # 判断是否存在经典任务
                            continue
                        if battle_result is False:
                            del self.classical_list[index]
                            self.list_save()
                            self.upgrade_list()
                            continue
                        elif battle_result is True:
                            self.classical_list[index]['num'] += 1
                            self.list_save()
                            self.upgrade_list()
                    elif now_rw['type'] == 2:  # 战役任务
                        if now_rw['num'] >= now_rw['num_max']:  # 超过出征计划
                            log.info("Del battle task")
                            del self.classical_list[index]
                            self.list_save()
                            self.upgrade_list()
                            continue
                        config = now_rw['data']
                        battle_result = campaign_main.main(maps=config['map'], formats=config['format'],
                                                           night=config['night'], repair=config['repair'], sl=config["sl"])
                        if len(self.classical_list) == 0:  # 判断是否存在经典任务
                            continue
                        if battle_result is False:
                            del self.classical_list[index]
                            self.list_save()
                            self.upgrade_list()
                            continue
                        elif battle_result is True:
                            self.classical_list[index]['num'] += 1
                            self.list_save()
                            self.upgrade_list()

                    elif now_rw['type'] == 3:  # 改名
                        other_function.change_name(1)
                        del self.classical_list[index]
                        self.list_save()
                        self.upgrade_list()
                    elif now_rw['type'] == 4:  # 分解装备
                        other_function.dismantle_equipment(1)
                        del self.classical_list[index]
                        self.list_save()
                        self.upgrade_list()
                    elif now_rw['type'] == 5:  # 好友演习
                        config = now_rw['data']
                        battle_result = pvp_main.main(formats=config['format'], team=config['fleet'], night=config['night'],
                                                      cv=config['cv'], ss=config['ss'], pvp="friend", friendlist=config['friendlist'])
                        if len(self.classical_list) == 0:  # 判断是否存在经典任务
                            continue
                        if battle_result is False:
                            del self.classical_list[index]
                            self.list_save()
                            self.upgrade_list()
                            continue
                        elif battle_result is True:
                            self.classical_list[index]['num'] += 1
                            self.list_save()
                            self.upgrade_list()
                    elif now_rw['type'] == 6:  # 远征任务
                        config = now_rw['data']
                        time.sleep(2)
                        if len(gameData.exploreInfo) < 4:
                            set_log("开始远征 " + str(config["exploreid"]), 1)
                            explore_new = gameFunction.start_explore(
                                maps=config["exploreid"], team=(config["fleetid"]+1))  # 开启新远征
                            time.sleep(2)
                            if 'pveExploreVo' in explore_new:
                                gameData.exploreInfo.clear()
                                for eachExplore in explore_new['pveExploreVo']['levels']:
                                    gameData.exploreInfo.append(eachExplore)
                        else:
                            set_log("没有空余的远征位。。。", 1)

                        del self.classical_list[index]
                        self.list_save()
                        self.upgrade_list()

                else:
                    # 远征任务
                    if config_function.cb_secretary:
                        other_function.autoSecretary()
                    battle_main.check_task()
                    if True:
                        battle_main.check_explore()
                    if True:
                        if self.pz_num/4 == int(self.pz_num/4):
                            if True:
                                other_function.free_shower(True)
                            else:
                                other_function.free_shower()

                        self.pz_num += 1.0
                    battle_main.check_task()

                    if time.localtime().tm_hour == 0 and time.localtime().tm_min == 0 and not self.relo:
                        set_log('0点→进行重新登录:', 0)
                        gameData.useSupport = False
                        self.relo = True
                        other_function.re_login()
                    if time.localtime().tm_min != 0:
                        self.relo = False
                    if gameData.login_award != -1:
                        other_function.continue_login_award()
            time.sleep(5)

    def upgrade_list(self):
        # classical [0name, 1type, 2num, 3num_max, 4data]
        # timer [0name, 1type, 2time, 3last_time, 4num, 5num_max, 6data]
        # type  0:经典 1:演习 2:战役
        data = {"rw": self.classical_list, "time": self.timer_list}

    def list_save(self):
        with open('./config/classical_list.json', 'w') as f:
            f.write(json.dumps(self.classical_list))
        with open('./config/timer_list.json', 'w') as f:
            f.write(json.dumps(self.timer_list))

    def list_read(self):
        if os.path.exists('./config/classical_list.json'):
            with open('./config/classical_list.json', 'r') as f:
                self.classical_list = json.loads(f.read())
        if os.path.exists('./config/timer_list.json'):
            with open('./config/timer_list.json', 'r') as f:
                self.timer_list = json.loads(f.read())
        self.upgrade_list()


class ConfigFunction:
    """ 
    配置读取与加载

    """

    def __init__(self):
        self.version = 0.3
        self.main_1 = {}
        self.main_2 = {}
        self.main_3 = {}
        self.main_build = {}
        self.qh_ship = []
        self.qh = {}
        self.cb_free_explore = True
        self.cb_secretary = False
        self.cb_flagship = False
        self.cb_flagwin = False
        self.active_code = {}

        if not os.path.exists('config'):
            os.mkdir('config')

        if os.path.exists('./config/version.json'):
            is_del = False
            with open('./config/version.json', 'r') as f:
                version_config = f.read()
                if float(version_config) != float(self.version):
                    is_del = True
            if is_del:
                shutil.rmtree('config')
                time.sleep(2)
                os.mkdir('config')
                with open('config/version.json', 'w') as f2:
                    f2.write(str(self.version))

        else:
            shutil.rmtree('config')
            time.sleep(2)
            os.mkdir('config')
            with open('config/version.json', 'w') as f2:
                f2.write(str(self.version))

    def main_save(self):
        log.info('Save main config')

    def main_read(self):
        log.info('Read main config')

        self.main_other_read()
        log.info("Read main config finish")

    def main_other_read(self):
        if os.path.exists('./config/other.json'):
            try:
                with open('./config/other.json', 'r') as file:
                    data = json.loads(file.read())

                if "cb_free_shower" in data:
                    self.cb_free_shower = data['cb_free_shower']

                if "cb_secretary" in data:
                    self.cb_secretary = data['cb_secretary']
                if "cb_flagship" in data:
                    self.cb_flagship = data['cb_flagship']
                if "cb_flagwin" in data:
                    self.cb_flagwin = data['cb_flagwin']

            except Exception as e:
                log.error('Main other read Error', str(e))
                raise


class Count:
    """ 
    统计类

    """

    def __init__(self):
        self.SPOILS = 0
        self.FIGHT_COUNT = 1
        self.FINISH_COUNT = 2
        self.SHIP_COUNT = 3
        self.SL_COUNT = 4
        self.PATH_COUNT = 5

        self.now_time = time.strftime("%y%m%d", time.localtime(time.time()))

        self.count_data = {}
        self.spoils = 0
        self.fight_count = 0
        self.finish_count = 0
        self.ship_count = 0
        self.sl_count = 0
        self.path_count = 0

        self.other_count = {}
        self.read_count()

    def add_items(self, item, num):
        now_time = time.strftime("%y%m%d", time.localtime(time.time()))
        if now_time not in self.count_data:
            self.spoils = 0
            self.fight_count = 0
            self.finish_count = 0
            self.ship_count = 0
            self.sl_count = 0
            self.path_count = 0
            self.other_count = {}
        if item == self.SPOILS:
            self.spoils += num
        elif item == self.FIGHT_COUNT:
            self.fight_count += num
        elif item == self.FINISH_COUNT:
            self.finish_count += num
        elif item == self.SHIP_COUNT:
            self.ship_count += num
        elif item == self.SL_COUNT:
            self.sl_count += num
        elif item == self.PATH_COUNT:
            self.path_count += num
        self.save_count(False)
        self.read_count()
        self.refresh_table()

    def save_count(self, isqk=True):
        time_day = time.strftime("%y%m%d", time.localtime(time.time()))
        if time_day not in self.count_data and isqk:
            self.spoils = 0
            self.fight_count = 0
            self.finish_count = 0
            self.ship_count = 0
            self.sl_count = 0
            self.path_count = 0
            self.other_count = {}
        data = {
            'spoils': self.spoils,
            'fight_count': self.fight_count,
            'finish_count': self.finish_count,
            'ship_count': self.ship_count,
            'sl_count': self.sl_count,
            'other_count': self.other_count,
            'path_count': self.path_count
        }
        self.count_data[time_day] = data
        with open('count/count.json', 'w') as f:
            f.write(json.dumps(self.count_data))
        with open('count/mycount.json', 'w') as f:
            f.write("var mydata=["+json.dumps(self.count_data)+"]")

    def read_count(self):
        time_day = time.strftime("%y%m%d", time.localtime(time.time()))
        if not os.path.exists('count'):
            os.mkdir('count')
        if os.path.exists('count/count.json'):
            with open('count/count.json', 'r') as f:
                self.count_data = json.loads(f.read())
        else:
            self.save_count()

        if time_day in self.count_data:  # 如果已经有数据
            data = self.count_data
            self.spoils = data[time_day]['spoils']
            self.fight_count = data[time_day]['fight_count']
            self.finish_count = data[time_day]['finish_count']
            self.ship_count = data[time_day]['ship_count']
            self.sl_count = data[time_day]['sl_count']
            self.other_count = data[time_day]['other_count']
            self.path_count = data[time_day]['path_count']
        else:
            self.count_data[time_day] = {
                'spoils': self.spoils,
                'fight_count': self.fight_count,
                'finish_count': self.finish_count,
                'ship_count': self.ship_count,
                'sl_count': self.sl_count,
                'path_count': self.path_count,
                'other_count': self.other_count
            }

    def add_other(self, index, num):
        time_day = time.strftime("%y%m%d", time.localtime(time.time()))
        if time_day not in self.count_data:
            self.spoils = 0
            self.fight_count = 0
            self.finish_count = 0
            self.ship_count = 0
            self.sl_count = 0
            self.path_count = 0
            self.other_count = {}

        if index not in self.other_count:
            self.other_count[index] = num
        else:
            self.other_count[index] += num
        self.save_count()
        self.read_count()
        self.refresh_table()

    def refresh_table(self):
        pass
        # windows_main.count_data.emit(self.__dict__)


def login():
    """
    功能:登录
    无返回值
    """

    try:
        windows_login.first_login()
        config_function.main_read()  # 读取配置文件
        other_function.continue_login_award()  # 进行签到
        th_main.th_main_def()  # 开启主进程
    except HmError as e:
        log.error('Login Error:', e.message)
        return 0
    except Exception as e:
        log.error('Login Error:', str(e))
        return 0


def set_log(strs, i):

    g.all_log += 1
    print(strs)
    ##windows_main.log_data.emit({"all_log": g.all_log, "i": i, "strs": strs})

    # -------------------------------------


# 设置环境变量
os.environ["OMP_NUM_THREADS"] = "1"

# 实例化对象
th_main = ThMain()
other_function = OtherFunction()
windows_login = WindowsLogin()


count = Count()
battle_main = BattleMain()
campaign_main = CampaignMain()
pvp_main = PvpMain()
config_function = ConfigFunction()
# if len(sys.argv)>1:

login()
