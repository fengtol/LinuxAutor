# -*- coding: utf-8 -*-
import hashlib
import json
import os
import random
import time
import zlib
from urllib.request import quote

from Data import gameData, gameLogin, log, session, HEADER
from Error import error_find, HmError

is_write = True


class GameFunction:
    def __init__(self):
        self.cookies = None
        self.version = None
        self.server = None
        self.channel = None

    def start_game_function(self, version, cookies, server, channel):
        self.cookies = cookies
        self.version = version
        self.server = server
        self.channel = channel

    def login_award(self):
        """
        功能：获取签到奖励
        :return:dict
        """
        try:
            log.debug("Login award:", "")
            url = self.server + \
                'active/getLoginAward/c3ecc6250c89e88d83832e3395efb973/' + self.get_url_end()
            data = self.Mdecompress(url)
            data = json.loads(data)
            if 'eid' in data:
                if int(data['eid']) == -1206:
                    return data
            error_find(data, url)
            if is_write and os.path.exists('requestsData'):
                with open('requestsData/login_award.json', 'w') as f:
                    f.write(json.dumps(data))
            return data
        except HmError as e_s:
            print('Start challenge FAILED! Reason:', e_s.message)
            raise
        except Exception as e_s:
            print('Start challenge FAILED! Reason:', e_s)
            raise

    def challenge_start(self, maps, team, head="pve"):
        """
        功能：开始出征
        返回值：dict
        """

        try:
            if "levels" in gameData.activedata and 9601 in gameData.activedata["levels"] and (int(maps) in gameData.activedata["levels"] or int(maps) in gameData.activedata["hardLevels"]):
                team = 0
                maps = maps+"01"
            url = self.server + '{head}/cha11enge/{map}/{team}/0/'.format(
                map=maps, team=team, head=head) + self.get_url_end()
            log.debug("Start challenge:",
                      "{head}/cha11enge/{map}/{team}".format(map=maps, team=team, head=head))
            data = self.Mdecompress(url, {'pve_level': 1, 'pid': random.randint(1000000, 2000000)})  # , {'pve_level': 1, 'pid': random.randint(1000000, 2000000)}
            data = json.loads(data)
            error_find(data, url)
            if is_write and os.path.exists('requestsData'):
                with open('requestsData/challenge_start.json', 'w') as f:
                    f.write(json.dumps(data))
            return data
        except HmError as e_s:
            print('Start challenge FAILED! Reason:', e_s.message)
            raise
        except Exception as e_s:
            print('Start challenge FAILED! Reason:', e_s)
            raise

    def challenge_new_next(self, head="pve"):
        """
        功能：下一点
        返回值：bytes
        """
        try:
            url = self.server + \
                '{head}/newNext/'.format(head=head) + self.get_url_end()
            data = self.Mdecompress(url)
            data = json.loads(data)
            error_find(data, url)
            if is_write and os.path.exists('requestsData'):
                with open('requestsData/challenge_new_next.json', 'w') as f:
                    f.write(json.dumps(data))
            return data
        except HmError as e_s:
            print('New next FAILED! Reason:', e_s.message)
            raise
        except Exception as Error_information:
            print('New next FAILED! Reason:', Error_information)
            raise

    def challenge_fight(self, maps, team, formats, head="pve", dealto='dealto', toudi=False):
        """
        功能：开始战斗
        返回值：dict
        """
        try:
            arg = self.str_arg(maps=maps, team=team,
                               formats=formats, head=head, dealto=dealto)
            # 玩具图
            # if int(maps) > 941900:
            #     arg["team"] = '0'
            if toudi:
                arg["team"] = '0'
            log.debug("Challenge fight", arg)
            url = self.server + \
                '{head}/{dealto}/{maps}/{team}/{formats}/'.format(
                    **arg) + self.get_url_end()
            data = self.Mdecompress(url)
            data = json.loads(data)
            error_find(data, url)
            if is_write and os.path.exists('requestsData'):
                with open('requestsData/challenge_fight.json', 'w') as f:
                    f.write(json.dumps(data))
            return data
        except HmError as e_s:
            print('Challenge fight FAILED! Reason:', e_s.message)
            raise
        except Exception as e_s:
            print('Challenge fight FAILED! Reason:', e_s)
            raise

    def challenge_get_result(self, is_night_fight, head="pve"):
        """
        功能：取战斗结果
        返回值：dict
        """
        # isNightFight:是否夜战，是：1，不是：0
        try:
            url = self.server + '{head}/getWarResult/'.format(
                head=head) + str(is_night_fight) + '/' + self.get_url_end()
            log.debug("Get Result", url)
            data = self.Mdecompress(url)
            data = json.loads(data)
            error_find(data, url)
            if is_write and os.path.exists('requestsData'):
                with open('requestsData/challenge_get_result.json', 'w') as f:
                    f.write(json.dumps(data))
            return data
        except HmError as e_s:
            print('Get Result FAILED! Reason:', e_s.message)
            raise
        except Exception as e_s:
            print('Get Result FAILED! Reason:', e_s)
            raise

    def getSpoilsShopList(self):
        """
        功能：获取商店数据
        返回值：dict
        """
        try:
            url = self.server + 'shop/getSpoilsShopList' + self.get_url_end()

            data = self.Mdecompress(url)
            data = json.loads(data)
            if 'spoils' in data:
                gameData.spoils = int(data['spoils'])
                gameData.spoilsFirst = int(data['spoils'])
            if is_write and os.path.exists('requestsData'):
                with open('requestsData/getSpoilsShopList.json', 'w') as f:
                    f.write(json.dumps(data))
            return data
        except HmError as e_s:
            print('Get getSpoilsShopList FAILED! Reason:', e_s.message)

        except Exception as e_s:
            print('Get getSpoilsShopList FAILED! Reason:', e_s)

    def getTactics(self):
        """
        功能：获取战术数据
        返回值：dict
        """
        try:
            url = self.server + 'live/getTactics' + self.get_url_end()

            data = self.Mdecompress(url)
            data = json.loads(data)
            error_find(data, url)
            if 'tactics' in data:
                gameData.Tactics = data['tactics']
            if is_write and os.path.exists('requestsData'):
                with open('requestsData/getTaactics.json', 'w') as f:
                    f.write(json.dumps(data))
            return data
        except HmError as e_s:
            print('Get getTaactics FAILED! Reason:', e_s.message)

        except Exception as e_s:
            print('Get getTaactics FAILED! Reason:', e_s)

    def challenge_skip_war(self, head="pve"):
        """
        功能：迂回
        返回值：dict
        """
        try:
            url = self.server + \
                '{head}/SkipWar/'.format(head=head) + self.get_url_end()
            data = self.Mdecompress(url)
            data = json.loads(data)
            error_find(data, url)
            if is_write and os.path.exists('requestsData'):
                with open('requestsData/challenge_skip_war.json', 'w') as f:
                    f.write(json.dumps(data))
            return data
        except Exception as e_s:
            print('Skip war FAILED! Reason:', e_s)
            raise

    def challenge_selectBuff(self, buff, head="pve"):
        """
                功能：选择buff
                返回值：dict
        """
        try:
            url = self.server + \
                '{head}/selectBuff/'.format(head=head) + \
                str(buff) + self.get_url_end()
            data = self.Mdecompress(url)
            data = json.loads(data)
            error_find(data, url)
            if is_write and os.path.exists('requestsData'):
                with open('requestsData/challenge_selectBuff.json', 'w') as f:
                    f.write(json.dumps(data))
            return data
        except HmError as e_s:
            print('selectBuff FAILED! Reason:', e_s.message)
            raise
        except Exception as e_s:
            print('selectBuff FAILED! Reason:', e_s)
            raise

    def challenge_spy(self, head="pve"):
        """
                功能：索敌
                返回值：dict
        """
        try:
            url = self.server + \
                '{head}/spy/'.format(head=head) + self.get_url_end()
            data = self.Mdecompress(url)
            data = json.loads(data)
            error_find(data, url)
            if is_write and os.path.exists('requestsData'):
                with open('requestsData/challenge_spy.json', 'w') as f:
                    f.write(json.dumps(data))
            return data
        except HmError as e_s:
            print('Spy FAILED! Reason:', e_s.message)
            raise
        except Exception as e_s:
            print('Spy FAILED! Reason:', e_s)
            raise

    def repair(self, ship):
        """
        功能：修理
        返回值：dict
        """
        try:
            wait = [str(x) for x in ship]
            url = self.server + \
                'boat/instantRepairShips/[' + \
                ','.join(wait) + ']/' + self.get_url_end()
            log.debug("Repair:", ','.join(wait))
            data = self.Mdecompress(url)
            data = json.loads(data)
            error_find(data, url)
            if 'packageVo' in data:
                gameData.fastRepair = data['packageVo'][0]['num']
            if "userVo" in data:
                gameData.oil = data['userVo']['oil']
                gameData.steel = data['userVo']['steel']
                gameData.ammo = data['userVo']['ammo']
                gameData.aluminium = data['userVo']['aluminium']
            if "shipVOs" in data:
                for ship in data['shipVOs']:
                    gameData.upgrade_ship(ship['id'], ship)
            if 'repairDockVo' in data:
                gameData.repairDock = data['repairDockVo']

            if is_write and os.path.exists('requestsData'):
                with open('requestsData/repair.json', 'w') as f:
                    f.write(json.dumps(data))
            return data
        except HmError as e_s:
            print('Repair FAILED! Reason:', e_s.message)
            raise
        except Exception as e_s:
            print('Repair FAILED! Reason:', e_s)
            raise

    def strengthen(self, ids, ship):
        """
        功能：强化
        返回值：dict
        """
        try:
            wait = [str(x) for x in ship]
            arg = self.str_arg(ids=str(ids), ship=','.join(wait))
            url = self.server + \
                'boat/strengthen/{ids}/[{ship}]/'.format(
                    **arg) + self.get_url_end()
            data = self.Mdecompress(url)
            data = json.loads(data)
            if 'eid' in data:
                if data["eid"] != -412:
                    error_find(data, url)
            self.updateTaskVo(data)

            if is_write and os.path.exists('requestsData'):
                with open('requestsData/strengthen.json', 'w') as f:
                    f.write(json.dumps(data))
            return data
        except HmError as e_s:
            print('Repair FAILED! Reason:', e_s.message)
            raise
        except Exception as e_s:
            print('Repair FAILED! Reason:', e_s)
            raise

    def skillLevelUp(self, ship):
        """
        功能：升级
        返回值：dict
        """
        try:

            url = self.server + \
                'boat/skillLevelUp/{ship}/'.format(ship=ship) + \
                self.get_url_end()
            data = self.Mdecompress(url)
            data = json.loads(data)
            if 'eid' in data:
                if data["eid"] != -317 and data["eid"] != -315 and data["eid"] != -316:
                    error_find(data, url)

            if is_write and os.path.exists('requestsData'):
                with open('requestsData/skillLevelUp.json', 'w') as f:
                    f.write(json.dumps(data))
            return data
        except HmError as e_s:
            print('skillLevelUp FAILED! Reason:', e_s.message)
            raise
        except Exception as e_s:
            print('skillLevelUp FAILED! Reason:', e_s)
            raise

    def setSecretary(self, ship):
        """
        功能：设置秘书舰船
        返回值：dict
        """
        try:

            url = self.server + \
                'boat/setSecretary/{ship}/'.format(ship=ship) + \
                self.get_url_end()
            data = self.Mdecompress(url)
            data = json.loads(data)
            error_find(data, url)
            if 'shipId' in data:
                gameData.secretary = int(data["shipId"])

            if is_write and os.path.exists('requestsData'):
                with open('requestsData/setSecretary.json', 'w') as f:
                    f.write(json.dumps(data))
            return data
        except HmError as e_s:
            print('setSecretary FAILED! Reason:', e_s.message)
            raise
        except Exception as e_s:
            print('setSecretary FAILED! Reason:', e_s)
            raise

    def updateTaskVo(self, result_data):
        """
         更新任务信息
        """
        # 更新任务信息
        if 'updateTaskVo' in result_data and len(result_data["updateTaskVo"]) != 0:
            log.info('Upgrade task information')
            for eachTask in result_data['updateTaskVo']:
                try:
                    gameData.taskInfo[int(eachTask['taskCid'])
                                      ]['condition'] = eachTask['condition']
                except Exception as e_s:
                    log.error('Upgrade task error', e_s)

    def eat(self, food):
        """
        功能：用餐
        返回值：dict
        """
        try:

            url = self.server + \
                'live/eat/{food}'.format(food=food) + self.get_url_end()
            data = self.Mdecompress(url)
            data = json.loads(data)
            error_find(data, url)
            self.updateTaskVo(data)

            if is_write and os.path.exists('requestsData'):
                with open('requestsData/eat.json', 'w') as f:
                    f.write(json.dumps(data))
            return data
        except HmError as e_s:
            print('eat FAILED! Reason:', e_s.message)
            raise
        except Exception as e_s:
            print('eat FAILED! Reason:', e_s)
            raise

    def useSupport(self, isuse=False):
        """
        功能：使用buff
        返回值：dict
        """
        try:
            if gameData.useSupport == isuse:
                return 0

            url = self.server + \
                'pve/useSupport/0' + self.get_url_end()
            data = self.Mdecompress(url)
            data = json.loads(data)
            if '-eid' in data:  # 关闭状态
                gameData.useSupport = isuse
                return 0

            error_find(data, url)
            if 'todaySupportStatus' in data and data['todaySupportStatus'] == 1:
                gameData.useSupport = True
            else:
                gameData.useSupport = False
            # if gameData.useSupport!=isuse:
            #     time.sleep(2)
            #     self.useSupport(isuse)

            if is_write and os.path.exists('requestsData'):
                with open('requestsData/useSupport.json', 'w') as f:
                    f.write(json.dumps(data))
            return data
        except HmError as e_s:
            print('useSupport FAILED! Reason:', e_s.message)
            raise
        except Exception as e_s:
            print('useSupport FAILED! Reason:', e_s)
            raise

    def getUserInfo(self):
        """
        功能：获取菜谱 列表
        返回值：dict
        """
        try:

            url = self.server + 'live/getUserInfo' + self.get_url_end()
            data = self.Mdecompress(url)
            data = json.loads(data)
            error_find(data, url)
            if is_write and os.path.exists('requestsData'):
                with open('requestsData/getUserInfo.json', 'w') as f:
                    f.write(json.dumps(data))
            gameData.eatdata = data
            self.getAddPopularity()
            return data
        except HmError as e_s:
            print('getUserInfo FAILED! Reason:', e_s.message)
            raise
        except Exception as e_s:
            print('getUserInfo FAILED! Reason:', e_s)
            raise

    def getAddPopularity(self):
        """
        功能：获取菜谱
        返回值：dict
        """
        try:

            url = self.server + 'live/getAddPopularity' + self.get_url_end()
            data = self.Mdecompress(url)
            data = json.loads(data)
            error_find(data, url)
            if is_write and os.path.exists('requestsData'):
                with open('requestsData/getAddPopularity.json', 'w') as f:
                    f.write(json.dumps(data))
            return data
        except HmError as e_s:
            print('getAddPopularity FAILED! Reason:', e_s.message)
            raise
        except Exception as e_s:
            print('getAddPopularity FAILED! Reason:', e_s)
            raise

    def shower(self, ship):
        """
        功能：泡澡
        返回值：dict
        """
        try:
            arg = self.str_arg(ship=ship)
            url = self.server + \
                'boat/repair/{ship}/0/'.format(**arg) + self.get_url_end()
            data = self.Mdecompress(url)
            data = json.loads(data)
            if 'eid' in data:
                if data['eid'] == -208 or data['eid'] == -209:
                    if data['eid'] == -208:
                        gameData.allShip[ship]['battleProps']['hp'] = gameData.allShip[ship]['battlePropsMax']['hp']
                    return data
            error_find(data, url)
            self.updateTaskVo(data)
            if is_write and os.path.exists('requestsData'):
                with open('requestsData/shower.json', 'w') as f:
                    f.write(json.dumps(data))
            return data
        except HmError as e_s:
            print('Shower FAILED! Reason:', e_s.message)
            raise
        except Exception as e_s:
            print('Shower FAILED! Reason:', e_s)
            raise

    def rubdown(self, ship):
        """
        功能：修理
        返回值：dict
        """
        try:
            arg = self.str_arg(ship=ship)
            url = self.server + \
                'boat/rubdown/{ship}'.format(**arg) + self.get_url_end()
            data = self.Mdecompress(url)
            data = json.loads(data)
            error_find(data, url)
            if is_write and os.path.exists('requestsData'):
                with open('requestsData/rubdown.json', 'w') as f:
                    f.write(json.dumps(data))
            return data
        except HmError as e_s:
            print('Rubdown FAILED! Reason:', e_s.message)
            raise
        except Exception as e_s:
            print('Rubdown FAILED! Reason:', e_s)
            raise

    def repair_complete(self, ids, ship):
        """
        功能：出浴
        返回值：dict
        """
        try:
            arg = self.str_arg(ship=ship, ids=ids)
            url = self.server + \
                'boat/repairComplete/{ids}/{ship}/'.format(
                    **arg) + self.get_url_end()
            data = self.Mdecompress(url)
            data = json.loads(data)
            error_find(data, url)
            if is_write and os.path.exists('requestsData'):
                with open('requestsData/repair_complete.json', 'w') as f:
                    f.write(json.dumps(data))
            return data
        except HmError as e_s:
            print('RepairComplete FAILED! Reason:', e_s.message)
            raise
        except Exception as e_s:
            print('RepairComplete FAILED! Reason:', e_s)
            raise

    def supply(self, ship):
        """
                功能：快速补给
                返回值：dict
        """
        try:
            wait = []
            for each in ship:
                wait.append(str(each))
            url = self.server + \
                'boat/supplyBoats/[' + \
                ','.join(wait) + ']/0/0/' + self.get_url_end()
            data = self.Mdecompress(url)
            data = json.loads(data)
            error_find(data, url)
            if 'shipVO' in data:
                for ship in data['shipVO']:
                    gameData.upgrade_ship(ids=ship['id'], jsons=ship)
            if "userVo" in data:
                gameData.oil = data['userVo']['oil']
                gameData.steel = data['userVo']['steel']
                gameData.ammo = data['userVo']['ammo']
                gameData.aluminium = data['userVo']['aluminium']
            if is_write and os.path.exists('requestsData'):
                with open('requestsData/supply.json', 'w') as f:
                    f.write(json.dumps(data))
            return data
        except HmError as e_s:
            print('Fast supply FAILED! Reason:', e_s.message)
            raise
        except Exception as Error_information:
            print('Fast supply FAILED! Reason:', Error_information)
            raise

    def dismantle(self, ship, is_save):
        """
        功能：分解
        返回值：dict
        """
        try:
            url = self.server + 'dock/dismantleBoat/[' + ','.join(ship) \
                + ']/' + str(is_save) + '/' + self.get_url_end()
            data = self.Mdecompress(url)
            data = json.loads(data)
            error_find(data, url)
            if is_write and os.path.exists('requestsData'):
                with open('requestsData/dismantle.json', 'w') as f:
                    f.write(json.dumps(data))
            return data
        except HmError as e_s:
            print('Decompose FAILED! Reason:', e_s.message)
            raise
        except Exception as e_s:
            print('Decompose FAILED! Reason:', e_s)
            raise

    def get_explore(self, maps):
        """
        功能：收远征
        返回值：bytes
        """
        try:
            arg = self.str_arg(maps=maps)
            url = self.server + \
                'explore/getResult/{maps}/'.format(**arg) + self.get_url_end()
            data = self.Mdecompress(url)
            data = json.loads(data)
            if 'eid' in data:
                if int(data['eid']) == -601:
                    for eachExplore in gameData.exploreInfo:
                        if eachExplore['endTime'] < int(time.time()):
                            if eachExplore['exploreId'] == maps:
                                gameData.exploreInfo.remove(eachExplore)
                                break

            error_find(data, url)
            if is_write and os.path.exists('requestsData'):
                with open('requestsData/get_explore.json', 'w') as f:
                    f.write(json.dumps(data))
            return data
        except HmError as e_s:
            print('Get explore FAILED! Reason:', e_s.message)
            raise
        except Exception as e_s:
            print('Get explore FAILED! Reason:', e_s)
            raise

    def get_task(self, cid):
        """
        功能：收任务
        返回值：bytes
        """
        try:
            arg = self.str_arg(cid=cid)
            url = self.server + \
                'task/getAward/{cid}/'.format(**arg) + self.get_url_end()
            data = self.Mdecompress(url)
            data = json.loads(data)
            error_find(data, url)
            if is_write and os.path.exists('requestsData'):
                with open('requestsData/get_task.json', 'w') as f:
                    f.write(json.dumps(data))
            return data
        except HmError as e_s:
            print('Get explore FAILED! Reason:', e_s.message)
            raise
        except Exception as e_s:
            print('Get explore FAILED! Reason:', e_s)
            raise

    def start_explore(self, maps, team):
        """
        功能：开始远征
        返回值：bytes
        """
        try:
            arg = self.str_arg(maps=maps, team=team)
            url = self.server + \
                'explore/start/{team}/{maps}/'.format(**arg) + \
                self.get_url_end()
            data = self.Mdecompress(url)
            data = json.loads(data)

            error_find(data, url)

            if is_write and os.path.exists('requestsData'):
                with open('requestsData/start_explore.json', 'w') as f:
                    f.write(json.dumps(data))
            return data
        except HmError as e_s:
            print('Start explore FAILED! Reason:', e_s.message)
            raise
        except Exception as Error_information:
            print('Start explore FAILED! Reason:', Error_information)
            raise

    def lock_ship(self, ship):
        """
        功能：开始远征
        返回值：bytes
        """
        try:
            url = self.server + \
                'boat/lock/{ship}/'.format(ship=str(ship)) + self.get_url_end()
            data = self.Mdecompress(url)
            data = json.loads(data)
            error_find(data, url)
            if is_write and os.path.exists('requestsData'):
                with open('requestsData/lock_ship.json', 'w') as f:
                    f.write(json.dumps(data))
            return data
        except HmError as e_s:
            print('Lock ship FAILED! Reason:', e_s.message)
            raise
        except Exception as Error_information:
            print('Lock ship FAILED! Reason:', Error_information)
            raise

    def campaign_get_fleet(self, maps):
        """
        获取用户战役船只信息
        :return:
        """
        try:
            url = self.server + \
                'campaign/getFleet/{maps}/'.format(
                    maps=str(maps)) + self.get_url_end()
            data = self.Mdecompress(url)
            data = json.loads(data)
            error_find(data, url)
            if is_write and os.path.exists('requestsData'):
                with open('requestsData/campaign_get_fleet.json', 'w') as f:
                    f.write(json.dumps(data))
            return data
        except HmError as e_s:
            print('Skip war FAILED! Reason:', e_s.message)
            raise
        except Exception as e_s:
            print('Skip war FAILED! Reason:', e_s)
            raise

    def campaign_get_spy(self, maps):
        """
        获取用户战役船只信息
        :return:
        """
        try:
            url = self.server + \
                'campaign/spy/{maps}/'.format(maps=str(maps)) + \
                self.get_url_end()
            data = self.Mdecompress(url)
            data = json.loads(data)
            if is_write and os.path.exists('requestsData'):
                with open('requestsData/campaign_get_spy.json', 'w') as f:
                    f.write(json.dumps(data))
            return data
        except HmError as e_s:
            print('Campaign spy FAILED! Reason:', e_s.message)
            raise
        except Exception as e_s:
            print('Campaign spy FAILED! Reason:', e_s)
            raise

    def campaign_fight(self, maps, formats):
        """
        获取用户战役船只信息
        :return:
        """
        try:
            arg = self.str_arg(maps=maps, formats=formats)
            url = self.server + \
                'campaign/challenge/{maps}/{formats}/'.format(
                    **arg) + self.get_url_end()
            data = self.Mdecompress(url)
            data = json.loads(data)
            error_find(data, url)
            if is_write and os.path.exists('requestsData'):
                with open('requestsData/campaign_fight.json', 'w') as f:
                    f.write(json.dumps(data))
            return data
        except HmError as e_s:
            print('Campaign fight FAILED! Reason:', e_s.message)
            raise
        except Exception as Error_information:
            print('Campaign fight FAILED! Reason:', Error_information)
            raise

    def campaign_get_result(self, is_night_fight):
        """
        功能：取战斗结果
        返回值：dict
        """
        # isNightFight:是否夜战，是：1，不是：0
        try:
            url = self.server + \
                'campaign/getWarResult/{0}/'.format(
                    str(is_night_fight)) + self.get_url_end()
            data = self.Mdecompress(url)
            data = json.loads(data)
            error_find(data, url)
            if is_write and os.path.exists('requestsData'):
                with open('requestsData/campaign_get_result.json', 'w') as f:
                    f.write(json.dumps(data))
            return data
        except HmError as e_s:
            print('Campaign get result FAILED! Reason:', e_s.message)
            raise
        except Exception as e_s:
            print('Campaign get result FAILED! Reason:', e_s)
            raise

    @property
    def pvp_get_list(self):
        """
                功能：取演习列表
                返回值：dict
                """
        try:
            url = self.server + 'pvp/getChallengeList/' + self.get_url_end()
            data = self.Mdecompress(url)
            data = json.loads(data)
            error_find(data, url)
            if is_write and os.path.exists('requestsData'):
                with open('requestsData/pvp_list.json', 'w') as f:
                    f.write(json.dumps(data))
            return data
        except HmError as e_s:
            print('PVP get list FAILED! Reason:', e_s.message)
            raise
        except Exception as e_s:
            print('PVP get list FAILED! Reason:', e_s)
            raise

    @property
    def friend_get_list(self):
        """
                功能：取好友演习列表
                返回值：dict
                """
        try:
            url = self.server + 'friend/getlist' + self.get_url_end()
            data = self.Mdecompress(url)
            data = json.loads(data)
            error_find(data, url)
            if is_write and os.path.exists('requestsData'):
                with open('requestsData/friend_list.json', 'w') as f:
                    f.write(json.dumps(data))
            return data
        except HmError as e_s:
            print('friend get list FAILED! Reason:', e_s.message)
            raise
        except Exception as e_s:
            print('friend get list FAILED! Reason:', e_s)
            raise

    def friend_visitorFriend(self, uid):
        """
                功能：查询好友状态
                返回值：dict
                """
        try:
            arg = self.str_arg(uid=uid)
            url = self.server + \
                'friend/visitorFriend/{uid}/'.format(**arg) + \
                self.get_url_end()
            data = self.Mdecompress(url)
            data = json.loads(data)
            error_find(data, url)
            if is_write and os.path.exists('requestsData'):
                with open('requestsData/visitor_Friend.json', 'w') as f:
                    f.write(json.dumps(data))
            return data
        except HmError as e_s:
            print('visitor_Friend FAILED! Reason:', e_s.message)
            raise
        except Exception as e_s:
            print('visitor_Friend FAILED! Reason:', e_s)
            raise

    def pvp_spy(self, uid, fleet, pvp="pvp"):
        """
                功能：索敌
                返回值：dict
                """
        try:
            arg = self.str_arg(uid=uid, fleet=fleet, pvp=pvp)
            url = self.server + \
                '{pvp}/spy/{uid}/{fleet}/'.format(**arg) + self.get_url_end()
            data = self.Mdecompress(url)
            data = json.loads(data)
            error_find(data, url)
            if is_write and os.path.exists('requestsData'):
                with open('requestsData/pvp_spy.json', 'w') as f:
                    f.write(json.dumps(data))
            return data
        except HmError as e_s:
            print('PVP spy FAILED! Reason:', e_s.message)
            raise
        except Exception as e_s:
            print('PVP spy FAILED! Reason:', e_s)
            raise

    def pvp_fight(self, uid, fleet, formats, pvp="pvp"):
        """
        功能：战斗
        返回值：dict
        """
        try:
            arg = self.str_arg(uid=uid, fleet=fleet, formats=formats, pvp=pvp)
            url = self.server + \
                '{pvp}/challenge/{uid}/{fleet}/{formats}/'.format(
                    **arg) + self.get_url_end()
            data = self.Mdecompress(url)
            data = json.loads(data)
            error_find(data, url)
            if is_write and os.path.exists('requestsData'):
                with open('requestsData/pvp_fight.json', 'w') as f:
                    f.write(json.dumps(data))
            return data
        except HmError as e_s:
            print('PVP fight FAILED! Reason:', e_s.message)
            raise
        except Exception as Error_information:
            print('PVP fight FAILED! Reason:', Error_information)
            raise

    def pvp_get_result(self, is_night_fight, pvp="pvp"):
        """
        功能：取战斗结果
        返回值：dict
        """
        # isNightFight:是否夜战，是：1，不是：0
        try:
            arg = self.str_arg(is_night_fight=str(is_night_fight), pvp=pvp)
            url = self.server + \
                '{pvp}/getWarResult/{is_night_fight}/'.format(
                    **arg) + self.get_url_end()
            data = self.Mdecompress(url)
            data = json.loads(data)
            error_find(data, url)
            if is_write and os.path.exists('requestsData'):
                with open('requestsData/PVP_get_result.json', 'w') as f:
                    f.write(json.dumps(data))
            return data
        except HmError as e_s:
            print('PVP get Result FAILED! Reason:', e_s.message)
            raise
        except Exception as Error_information:
            print('PVP get Result FAILED! Reason:', Error_information)
            raise

    def build_ship(self, dock, oil, ammo, steel, aluminium):
        """
        功能：建造船只
        返回值：dict
        """
        #
        try:
            arg = self.str_arg(dock=dock, oil=oil, ammo=ammo,
                               steel=steel, aluminium=aluminium)
            url = self.server + 'dock/buildBoat/{dock}/{oil}/{steel}/{ammo}/{aluminium}'.format(
                **arg) + self.get_url_end()
            data = self.Mdecompress(url)
            data = json.loads(data)
            error_find(data, url)
            self.updateTaskVo(data)
            if is_write and os.path.exists('requestsData'):
                with open('requestsData/Build_ship.json', 'w') as f:
                    f.write(json.dumps(data))
            return data
        except HmError as e_s:
            print('Build ship FAILED! Reason:', e_s.message)
            raise
        except Exception as Error_information:
            print('Build ship FAILED! Reason:', Error_information)
            raise

    def build_equipment(self, dock, oil, ammo, steel, aluminium):
        """
        功能：开发装备
        返回值：dict
        """
        #
        try:
            arg = self.str_arg(dock=dock, oil=oil, ammo=ammo,
                               steel=steel, aluminium=aluminium)
            url = self.server + 'dock/buildEquipment/{dock}/{oil}/{steel}/{ammo}/{aluminium}'.format(
                **arg) + self.get_url_end()
            data = self.Mdecompress(url)
            data = json.loads(data)
            error_find(data, url)
            if is_write and os.path.exists('requestsData'):
                with open('requestsData/Build_equipment.json', 'w') as f:
                    f.write(json.dumps(data))
            return data
        except HmError as e_s:
            print('Build equipment FAILED! Reason:', e_s.message)
            raise
        except Exception as Error_information:
            print('Build equipment FAILED! Reason:', Error_information)
            raise

    def build_get_ship(self, dock):
        """
        功能：收船
        返回值：dict
        """
        try:
            arg = self.str_arg(dock=dock)
            url = self.server + \
                'dock/getBoat/{dock}/'.format(**arg) + self.get_url_end()
            data = self.Mdecompress(url)
            data = json.loads(data)
            error_find(data, url)
            if is_write and os.path.exists('requestsData'):
                with open('requestsData/build_get_ship.json', 'w') as f:
                    f.write(json.dumps(data))
            return data
        except HmError as e_s:
            print('Build get ship FAILED! Reason:', e_s.message)
            raise
        except Exception as Error_information:
            print('Build get ship FAILED! Reason:', Error_information)
            raise

    def build_get_equipment(self, dock):
        """
        功能：收装备
        返回值：dict
        """
        try:
            arg = self.str_arg(dock=dock)
            url = self.server + \
                'dock/getEquipment/{dock}/'.format(**arg) + self.get_url_end()
            data = self.Mdecompress(url)
            data = json.loads(data)
            error_find(data, url)
            if is_write and os.path.exists('requestsData'):
                with open('requestsData/build_get_equipment.json', 'w') as f:
                    f.write(json.dumps(data))
            return data
        except HmError as e_s:
            print('Build get equipment FAILED! Reason:', e_s.message)
            raise
        except Exception as Error_information:
            print('Build get equipment FAILED! Reason:', Error_information)
            raise

    def build_instant_ship(self, dock):
        """
        功能：快速建造
        返回值：dict
        """
        try:
            arg = self.str_arg(dock=dock)
            url = self.server + \
                'dock/instantBuild/{dock}/'.format(**arg) + self.get_url_end()
            data = self.Mdecompress(url)
            data = json.loads(data)
            error_find(data, url)
            if is_write and os.path.exists('requestsData'):
                with open('requestsData/build_instant_ship.json', 'w') as f:
                    f.write(json.dumps(data))
            return data
        except HmError as e_s:
            print('Build instant ship FAILED! Reason:', e_s.message)
            raise
        except Exception as Error_information:
            print('Build instant ship FAILED! Reason:', Error_information)
            raise

    def build_instant_equipment(self, dock):
        """
        功能：快速开发
        返回值：dict
        """
        try:
            arg = self.str_arg(dock=dock)
            url = self.server + \
                'dock/instantEquipmentBuild/{dock}/'.format(
                    **arg) + self.get_url_end()
            data = self.Mdecompress(url)
            data = json.loads(data)
            error_find(data, url)
            if is_write and os.path.exists('requestsData'):
                with open('requestsData/build_instant_equipment.json', 'w') as f:
                    f.write(json.dumps(data))
            return data
        except HmError as e_s:
            print('Build instant equipment FAILED! Reason:', e_s.message)
            raise
        except Exception as Error_information:
            print('Build instant equipment FAILED! Reason:', Error_information)
            raise

    def change_ship(self, fleet, ids, path):
        """
        功能：换船
        返回值：dict
        """
        try:
            arg = self.str_arg(fleet=fleet, ids=ids, path=path)
            url = self.server + \
                'boat/changeBoat/{fleet}/{ids}/{path}/'.format(
                    **arg) + self.get_url_end()
            data = self.Mdecompress(url)
            data = json.loads(data)
            error_find(data, url)
            if is_write and os.path.exists('requestsData'):
                with open('requestsData/change_ship.json', 'w') as f:
                    f.write(json.dumps(data))
            return data
        except HmError as e_s:
            print('Change ship FAILED! Reason:', e_s.message)
            raise
        except Exception as Error_information:
            print('Change ship FAILED! Reason:', Error_information)
            raise

    def remove_ship(self, fleet, path):
        """
        功能：换船
        返回值：dict
        """
        try:
            arg = self.str_arg(fleet=fleet, path=path)
            url = self.server + \
                'boat/removeBoat/{fleet}/{path}/'.format(
                    **arg) + self.get_url_end()
            data = self.Mdecompress(url)
            data = json.loads(data)
            error_find(data, url)
            if is_write and os.path.exists('requestsData'):
                with open('requestsData/remove_ship.json', 'w') as f:
                    f.write(json.dumps(data))
            return data
        except HmError as e_s:
            print('Remove ship FAILED! Reason:', e_s.message)
            raise
        except Exception as Error_information:
            print('Change ship FAILED! Reason:', Error_information)
            raise

    def remove_equipment(self, ids, path):
        """
        功能：移除装备
        返回值：dict
        """
        try:
            arg = self.str_arg(ids=ids, path=path)
            url = self.server + \
                'boat/removeEquipment/{ids}/{path}'.format(
                    **arg) + self.get_url_end()
            data = self.Mdecompress(url)
            data = json.loads(data)
            error_find(data, url)
            if is_write and os.path.exists('requestsData'):
                with open('requestsData/remove_equipment.json', 'w') as f:
                    f.write(json.dumps(data))
            return data
        except HmError as e_s:
            print('Remove equipment FAILED! Reason:', e_s.message)
            raise
        except Exception as Error_information:
            print('Remove equipment FAILED! Reason:', Error_information)
            raise

    def change_equipment(self, ids, cid, path):
        """
        功能：更换装备
        返回值：dict
        """
        try:
            arg = self.str_arg(ids=ids, path=path, cid=cid)
            url = self.server + \
                'boat/changeEquipment/{ids}/{cid}/{path}'.format(
                    **arg) + self.get_url_end()
            data = self.Mdecompress(url)
            data = json.loads(data)
            error_find(data, url)
            if is_write and os.path.exists('requestsData'):
                with open('requestsData/change_equipment.json', 'w') as f:
                    f.write(json.dumps(data))
            return data
        except HmError as e_s:
            print('Change equipment FAILED! Reason:', e_s.message)
            raise
        except Exception as e_s:
            print('Change equipment FAILED! Reason:', e_s)
            raise

    def rename(self, ids, new_name):
        """
        功能：改名
        返回值：dict
        """
        try:
            arg = self.str_arg(ids=ids, new_name=new_name)
            url = self.server + \
                'boat/renameShip/{ids}/{new_name}/'.format(
                    **arg) + self.get_url_end()
            url = quote(url, safe=";/?:@&=+$,", encoding="utf-8")
            data = self.Mdecompress(url)
            data = json.loads(data)
            error_find(data, url)
            gameData.allShip[int(ids)]['title'] = new_name
            if is_write and os.path.exists('requestsData'):
                with open('requestsData/rename.json', 'w') as f:
                    f.write(json.dumps(data))
            return data
        except HmError as e_s:
            print('Rename FAILED! Reason:', e_s.message)
            raise
        except Exception as Error_information:
            print('Rename FAILED! Reason:', Error_information)
            raise

    def dismantle_equipment(self, cid, num):
        """
         功能：分解装备
         返回值：dict
         """
        try:
            url = self.server + 'dock/dismantleEquipment/' + self.get_url_end()
            vdata = 'content={' + '"{}":{}'.format(str(cid), str(num)) + '}'
            data = self.Mdecompress(url, vdata)
            data = json.loads(data)
            error_find(data, url)
            if is_write and os.path.exists('requestsData'):
                with open('requestsData/dismantle_equipment.json', 'w') as f:
                    f.write(json.dumps(data))
            return data
        except HmError as e_s:
            print('Dismantle equipment FAILED! Reason:', e_s.message)
            raise
        except Exception as Error_information:
            print('Dismantle equipment FAILED! Reason:', Error_information)
            raise

    def get_active_data(self):
        """
                功能：收装备
                返回值：dict
                """
        try:
            url = self.server + 'ocean/getCIAList/' + self.get_url_end()
            data = self.Mdecompress(url)
            data = json.loads(data)
            error_find(data, url)
            if is_write and os.path.exists('requestsData'):
                with open('requestsData/get_active_data.json', 'w') as f:
                    f.write(json.dumps(data))
            return data
        except HmError as e_s:
            print('Get active data FAILED! Reason:', e_s.message)
            raise
        except Exception as Error_information:
            print('Get active data FAILED! Reason:', Error_information)
            raise

    def instant_fleet(self, fleet, ship):

        try:

            ships = "[" + ",".join([str(x) for x in ship]) + "]"
            args = self.str_arg(fleet=fleet, ships=ships)
            url = self.server + \
                'boat/instantFleet/{fleet}/{ships}/'.format(
                    **args) + self.get_url_end()
            data = self.Mdecompress(url)
            data = json.loads(data)
            error_find(data, url)
            if is_write and os.path.exists('requestsData'):
                with open('requestsData/instant_fleet.json', 'w') as f:
                    f.write(json.dumps(data))
            return data
        except HmError as e_s:
            print('Instant fleet FAILED! Reason:', e_s.message)
            raise
        except Exception as Error_information:
            print('Instant fleet FAILED! Reason:', Error_information)
            raise

    def get_icon(self, index):
        url = "http://ima.ntwikis.com/cancollezh/20151119/M_NORMAL_{}.png".format(
            str(index))
        try:
            data = session.get(url).content
            if not os.path.exists("icon/big"):
                os.mkdir('icon/big')
            if os.path.exists('icon/big/{}.png'.format(str(index))):
                return
            with open('icon/big/{}.png'.format(str(index)), 'wb') as f:
                f.write(data)
        except Exception as e_s:
            print('icon E', e_s)

    def get_eqicon(self, index):
        url = "http://ima.ntwikis.com/cancollezh/20151119/equip_large_{}.png".format(
            str(index))
        try:
            data = session.get(url).content
            if not os.path.exists("icon/eq"):
                os.mkdir('icon/eq')
            if os.path.exists('icon/eq/{}.png'.format(str(index))):
                return
            with open('icon/eq/{}.png'.format(str(index)), 'wb') as f:
                f.write(data)
        except Exception as e_s:
            print('eqicon E', e_s)

    def get_url_end(self):
        """
        功能：返回url尾部
        返回值：文本型
        """
        url_time = str(int(round(time.time() * 1000)))
        md5_raw = url_time + 'ade2688f1904e9fb8d2efdb61b5e398a'
        md5 = hashlib.md5(md5_raw.encode('utf-8')).hexdigest()
        url_end = '&t={time}&e={key}&gz=1&market=2&channel={channel}&version={version}'
        url_end_dict = {'time': url_time, 'key': md5,
                        'channel': self.channel, 'version': self.version}
        url_end = url_end.format(**url_end_dict)
        return url_end

    def Mdecompress(self, url, *vdata):
        if len(vdata) == 0:
            content = session.get(url=url, headers=HEADER,
                                  cookies=self.cookies, timeout=20).content
        else:
            h = HEADER
            h["Content-Type"] = "application/x-www-form-urlencoded"
            content = session.post(url=url, data=str(
                vdata[0]), headers=h, cookies=self.cookies, timeout=20).content

        try:  # 解码统一
            data = zlib.decompress(content)
        except Exception as e_s:
            data = content
        if data == b'':
            data = '{}'
        return data

    @staticmethod
    def get_md5(data):
        return hashlib.md5(str(data).encode('utf-8')).hexdigest()

    @staticmethod
    def str_arg(**arg):
        new_arg = {}
        for index, key in arg.items():
            new_arg[index] = str(key)
        return new_arg

    @staticmethod
    def set_text_size(size, strs):
        return '<html><head/><body><p><span style=" font-size:{:s}pt;">{:s}</span></p></body></html>'.format(str(size),
                                                                                                             str(strs))


gameFunction = GameFunction()
