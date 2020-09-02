# -*- coding: utf-8 -*-
import hashlib
import json
import os
import time
import zlib
import datetime
import hmac
import random
import requests
import base64
import urllib
import urllib3
from Constant import VERSION, RES, HEADER, g, log, init_data
from Error import error_find, HmError
from Net import session, HEADER

is_write = True


class GameData:
    _login_award = 0
    @property
    def login_award(self):
        return GameData._login_award

    @login_award.setter
    def login_award(self, num):
        GameData._login_award = num

    def __init__(self):
        """
        功能：定义初始变量
        """
        self.login_name = ""

        self.allData = {}
        self.userDetail = {}

        self.res_url = ""
        # other
        self.is_first_login = True
        # 登陆数据
        self.cookies = None
        self.headers = None
        self.version = None
        self.server = None
        self.channel = None
        # 玩家数据
        self.main_data = dict()
        self.uid = 0
        self.username = None
        self.level = 0
        self.exp = 0
        self.nextExp = 0
        self.secretary = 0

        # 玩家资源
        self.gold = 0
        self.oil = 0  # 油
        self.ammo = 0  # 弹
        self.steel = 0  # 弹
        self.aluminium = 0  # 铝
        self.shipNumTop = 0
        self.spoils = 0  # 战利品

        self.oilFirst = 0  # 油
        self.ammoFirst = 0  # 弹
        self.steelFirst = 0  # 弹
        self.aluminiumFirst = 0  # 铝
        self.fastRepairFirst = 0  # 快修
        self.spoilsFirst = 0  # 战利品

        self.oilChange = 0  # 油
        self.ammoChange = 0  # 弹
        self.steelChange = 0  # 弹
        self.aluminiumChange = 0  # 铝
        self.fastRepairChange = 0  # 快修
        self.spoilsChange = 0  # 战利品
        self.todaySpoilsNum = 0  # 今日战利品

        self.fastRepair = 0
        self.fastRepairFirst = 0
        self.fastBuild = 0
        self.shipBlueMap = 0
        self.equipmentMap = 0
        self.cvCube = 0
        self.bbCube = 0
        self.clCube = 0
        self.ddCube = 0
        self.ssCube = 0

        self.exploreInfo = []
        self.taskInfo = {}

        self.startTime = 0

        self.login_award = 0

        # 战役
        self.campaignTotal = 0
        self.campaignRemainNum = 0
        self.campaignMap = []

        # 建造开发
        self.dock = []
        self.repairDock = []
        self.equipmentDock = []
        # 菜谱数据
        self.eatdata = {}
        # 战术学习
        self.Tactics = []
        # 请求榜单
        self.rank_count = 0
        self.rank = {}

        # 玩家队伍
        self.fleet = {0: [0, 0, 0, 0, 0, 0],
                      1: [0, 0, 0, 0, 0, 0],
                      2: [0, 0, 0, 0, 0, 0],
                      3: [0, 0, 0, 0, 0, 0],
                      4: [0, 0, 0, 0, 0, 0],
                      5: [0, 0, 0, 0, 0, 0],
                      6: [0, 0, 0, 0, 0, 0],
                      7: [0, 0, 0, 0, 0, 0]
                      }
        self.fleetName = {0: "第一舰队", 1: "第二舰队", 2: "第三舰队", 3: "第四舰队"}
        # 玩家船只数据
        self.allShip = {}
        self.allEquipment = {}
        self.allPoint = {}
        self.allLevel = {}
        self.allpveBuff = {}
        self.unlockShip = []
        self.package = {}
        self.activedata = {}
        self.mine = {}
        # 玩家节点数据
        self.my_pveLevel = []
        self.my_passedNodes = []
        self.my_missLine = []
        self.useSupport = False
        # five数据
        self.fivedata = {}
        self.joyFleet = []
        self.joyShipVo = []
        # 版本控制
        self.verurl = []

    def get_joyship(self, id):
        for joyship in self.joyShipVo:
            if joyship["id"] == int(id):
                return joyship
        return {}

    def get_map_now(self, mapid):
        if "hardLevels" in self.activedata and len(self.activedata["hardLevels"]) != 0:
            if "levels" in self.activedata and len(self.activedata["levels"]) != 0:
                if mapid >= self.activedata["levels"][0] and mapid <= self.activedata["hardLevels"][len(self.activedata["hardLevels"])-1]:
                    return True
        return False

    def get_mine_version(self):
        url = 'https://fengzhiwenisgod.github.io/version.json'
        try:
            self.mine = json.loads(requests.get(url, timeout=(3, 4)).text)
        except Exception as e:
            print('Check upgrade Error:', e)

    def get_data(self, version, cookies, server, channel):
        self.cookies = cookies
        self.version = version
        self.server = server
        self.channel = channel
        self.get_user_data()
        self.get_pve_data()
        self.get_activity_point()
        # windows_login.statusBarSignal.emit("请求商店数据...")
        self.decurl("shop/canBuy/1/")
        # windows_login.statusBarSignal.emit("请求海域数据...")
        api_getShipList = self.decurl("api/getShipList/")
        if 'userShipVO' in api_getShipList:
            for eachShip in api_getShipList['userShipVO']:
                self.allShip[eachShip['id']] = eachShip

        self.decurl("bsea/getData/")
        # windows_login.statusBarSignal.emit("请求海域数据...")

        # windows_login.statusBarSignal.emit("请求宿舍数据...")
        self.decurl("live/getUserInfo")

        # windows_login.statusBarSignal.emit("请求背景音乐数据...")
        self.decurl("live/getMusicList/")

        # windows_login.statusBarSignal.emit("请求活动数据...")
        active_getUserData = self.decurl("active/getUserData")
        if "marketingData" in active_getUserData:
            if "activeList" in active_getUserData["marketingData"]:
                if len(active_getUserData["marketingData"]["activeList"]) > 0:
                    gameData.activedata = active_getUserData["marketingData"]["activeList"][0]

        # windows_login.statusBarSignal.emit("请求影片数据...")
        self.decurl("pve/getMovieList/")
        self.decurl("pve/getCgList/")
        self.decurl("task/getAchievementList/")

        # windows_login.statusBarSignal.emit("请求用户海域数据...")
        pve_getUserData = self.decurl("pve/getUserData/")
        self.userin(pve_getUserData)
        self.get_campaign_data()
        if "map_id" in gameData.activedata and gameData.activedata["map_id"] == "9601":
            self.get_ocean_data()
            self.get_ocean_user()
            self.get_ocean_level()
        if "map_id" in gameData.activedata and gameData.activedata["map_id"] == "9423":
            self.get_five_data()
            self.get_five_user_data()

    def get_pveLevel(self, node):
        for level in gameData.my_pveLevel:
            if level["id"] == str(node):
                return level
        return {}

    def get_campaign_data(self):
        """
        功能：获取战役信息
        无返回值
        """
        print('Getting campaign data...')
        try:
            user_data = zlib.decompress(
                session.get(url=self.server + 'campaign/getUserData/' + self.get_url_end(), headers=HEADER,
                            cookies=self.cookies, timeout=20).content)
            user_data = json.loads(user_data)
            error_find(user_data)
            self.campaignTotal = user_data['passInfo']['totalNum']
            self.campaignRemainNum = user_data['passInfo']['remainNum']
            self.campaignMap = user_data['canCampaignChallengeLevel']

            if is_write and os.path.exists('requestsData'):
                with open('requestsData/get_campaign_data.json', 'w') as f:
                    f.write(json.dumps(user_data))
            return user_data
        except HmError as e:
            print('Get campaign data FAILED! Reason:', e.message)
            raise
        except Exception as e:
            print('Get campaign data FAILED! Reason:', e)
            raise

    def remove_ship(self, fleet):
        temp = {}
        fleet2 = [int(x) for x in fleet]
        for ids, data in self.allShip.items():
            if ids not in fleet2:
                temp[int(ids)] = data
        self.allShip.clear()
        self.allShip = temp
        return len(self.allShip)

    @staticmethod
    def add_ship(id, data):
        if id in gameData.allShip:
            raise Exception("船只重复!")
        else:
            gameData.allShip[int(id)] = data

    def get_user_data(self):
        """
        功能：首次登陆获取信息
        无返回值
        """
        print('Getting user data...')
        try:
            user_data = zlib.decompress(
                session.get(url=self.server + 'api/initGame?&crazy=0' + self.get_url_end(), headers=HEADER,
                            cookies=self.cookies, timeout=20).content)
            user_data = json.loads(user_data)
            error_find(user_data)
            if is_write and os.path.exists('requestsData'):
                with open('requestsData/user_data.json', 'w') as f:
                    f.write(json.dumps(user_data))
            self.allData = user_data

            if "detailInfo" in user_data["userVo"]:
                self.userDetail = user_data["userVo"]["detailInfo"]

            self.uid = user_data['userVo']['uid']
            self.username = user_data['userVo']['username']
            self.level = user_data['userVo']['level']
            self.shipNumTop = user_data['userVo']['shipNumTop']
            self.exp = user_data['userVo']['exp']
            self.nextExp = user_data['userVo']['nextExp']

            self.upgrade_fleet(user_data)

            self.oil = user_data['userVo']['oil']
            self.ammo = user_data['userVo']['ammo']
            self.steel = user_data['userVo']['steel']
            self.aluminium = user_data['userVo']['aluminium']
            self.secretary = int(user_data['secretary'])

            self.login_award = user_data['marketingData']['continueLoginAward']['canGetDay']
            self.main_data = user_data

            self.startTime = user_data['systime']

            self.exploreInfo.clear()
            for eachExplore in user_data['pveExploreVo']['levels']:
                self.exploreInfo.append(eachExplore)

            self.taskInfo.clear()
            for eachTask in user_data['taskVo']:
                self.taskInfo[int(eachTask['taskCid'])] = eachTask

            self.allShip.clear()
            if 'userShipVO' in user_data:
                for eachShip in user_data['userShipVO']:
                    self.allShip[eachShip['id']] = eachShip

            self.allEquipment.clear()
            for eachEquipment in user_data['equipmentVo']:
                self.allEquipment[eachEquipment['equipmentCid']
                                  ] = eachEquipment

            self.package.clear()
            for eachPackage in user_data['packageVo']:
                self.package[eachPackage['itemCid']] = eachPackage['num']

            self.unlockShip.clear()
            for eachUnlockShip in user_data["unlockShip"]:
                self.unlockShip.append(int(eachUnlockShip))

            self.dock = user_data['dockVo']
            self.equipmentDock = user_data['equipmentDockVo']
            self.repairDock = user_data['repairDockVo']

            if 541 in self.package:
                self.fastRepair = int(self.package[541])
            if 141 in self.package:
                self.fastBuild = int(self.package[141])
            if 741 in self.package:
                self.equipmentMap = int(self.package[741])
            if 241 in self.package:
                self.shipBlueMap = int(self.package[241])

            if 10141 in self.package:
                self.cvCube = int(self.package[10141])
            if 10241 in self.package:
                self.bbCube = int(self.package[10241])
            if 10341 in self.package:
                self.clCube = int(self.package[10341])
            if 10441 in self.package:
                self.ddCube = int(self.package[10441])
            if 10541 in self.package:
                self.ssCube = int(self.package[10541])

            if self.is_first_login is True:
                self.oilFirst = self.oil
                self.ammoFirst = self.ammo
                self.steelFirst = self.steel
                self.aluminiumFirst = self.aluminium
                self.fastRepairFirst = self.fastRepair
                self.is_first_login = False

            print('Get user data success!')
        except HmError as e:
            print('Get user data FAILED! Reason:', e.message)
            raise
        except Exception as Error_information:
            print('Get user data FAILED! Reason:', Error_information)
            raise

    def get_activity_point(self):
        print('Get_activity_point')
        try:
            pve_data = zlib.decompress(
                session.get(url=self.server + 'pevent/getPveData/' + self.get_url_end(), headers=HEADER,
                            cookies=self.cookies, timeout=20).content)
            pve_data = json.loads(pve_data)
            error_find(pve_data)
            if is_write and os.path.exists('requestsData'):
                with open('requestsData/peventGetPveData.json', 'w') as f:
                    f.write(json.dumps(pve_data))

            if type(pve_data) == dict:
                if "pveNode" in pve_data:
                    for eachPoint in pve_data['pveNode']:
                        self.allPoint[int(eachPoint['id'])] = eachPoint

                if "pveEventLevel" in pve_data:
                    for level in pve_data['pveEventLevel']:
                        self.allLevel[int(level['id'])] = level
                if 'pveActive' in pve_data:
                    self.activedata = pve_data['pveActive']

            print('Get pve data success!')
        except HmError as e:
            print('Get ship info FAILED! Reason:', e.message)
            raise
        except Exception as e:
            print('Get ship info FAILED! Reason:', e)
            raise

    def get_pve_data(self):
        print('Getting pve data...')
        try:
            pve_data = zlib.decompress(
                session.get(url=self.server + 'pve/getPveData/' + self.get_url_end(), headers=HEADER,
                            cookies=self.cookies, timeout=20).content)
            pve_data = json.loads(pve_data)
            error_find(pve_data)
            if is_write and os.path.exists('requestsData'):
                with open('requestsData/get_pve_data.json', 'w') as f:
                    f.write(json.dumps(pve_data))
            for eachPoint in pve_data['pveNode']:
                self.allPoint[int(eachPoint['id'])] = eachPoint
            for level in pve_data['pveLevel']:
                self.allLevel[int(level['id'])] = level
            if 'pveBuff' in pve_data:
                for pveBuff in pve_data['pveBuff']:
                    self.allpveBuff[int(pveBuff['id'])] = pveBuff
            print('Get pve data success!')
        except HmError as e:
            print('Get ship info FAILED! Reason:', e.message)
            raise
        except Exception as e:
            print('Get ship info FAILED! Reason:', e)
            raise

    def get_rank_list(self):
        print('Getting rank list...')
        try:
            if self.rank_count / 8 == int(self.rank_count / 8):
                # self.rank = zlib.decompress(
                #     session.get(url=self.server + 'rank/getData/' + self.get_url_end(), headers=HEADER,
                #                 cookies=self.cookies, timeout=20).content)
                self.rank = self.Mdecompress(
                    url=self.server + 'rank/getData/' + self.get_url_end())
                self.rank = json.loads(self.rank)
                error_find(self.rank)
            if is_write and os.path.exists('requestsData'):
                with open('requestsData/get_rank_list.json', 'w') as f:
                    f.write(json.dumps(self.rank))
            print('Get rank list success!')
            self.rank_count += 1
            return self.rank
        except HmError as e:
            print('Get rank list FAILED! Reason:', e.message)
            raise
        except Exception as e:
            print('Get rank list FAILED! Reason:', str(e))
            raise

    def get_ocean_data(self):
        """
        功能：获取活动数据
        返回值：dict
        """
        try:
            url = self.server + 'ocean/getOceanData/' + self.get_url_end()
            data = zlib.decompress(
                session.get(url=url, headers=HEADER,
                            cookies=self.cookies, timeout=20).content)
            data = json.loads(data)
            error_find(data)
            for node in data['oceanNode']:
                gameData.allPoint[int(node["id"])] = node
            for node in data['oceanLevel']:
                gameData.allLevel[int(node["id"])] = node
            if is_write and os.path.exists('requestsData'):
                with open('requestsData/get_ocean_data.json', 'w') as f:
                    f.write(json.dumps(data))
            return data
        except HmError as e:
            print('Get ocean data FAILED! Reason:', e.message)
            raise
        except Exception as Error_information:
            print('Get ocean data FAILED! Reason:', Error_information)
            raise

    def get_ocean_level(self):
        """
        功能：获取活动数据
        返回值：dict
        """
        try:
            url = self.server + 'ocean/getCIAList/' + self.get_url_end()
            data = zlib.decompress(
                session.get(url=url, headers=HEADER,
                            cookies=self.cookies, timeout=20).content)
            data = json.loads(data)
            error_find(data)
            if "pveEventLevel" in data:
                for level in data['pveEventLevel']:
                    self.allLevel[int(level['id'])] = level
            if is_write and os.path.exists('requestsData'):
                with open('requestsData/get_ocean_data.json', 'w') as f:
                    f.write(json.dumps(data))
            return data
        except HmError as e:
            print('Get ocean data FAILED! Reason:', e.message)
            raise
        except Exception as Error_information:
            print('Get ocean data FAILED! Reason:', Error_information)
            raise

    def set_ocean_fleet(self, fleet, node):
        """
        功能：获取活动数据
        返回值：dict
        """
        try:
            url = self.server + \
                'ocean/setFleet/{}/{}/'.format(str(node),
                                               str(fleet)) + self.get_url_end()
            data = self.Mdecompress(url)
            data = json.loads(data)
            error_find(data)
            if is_write and os.path.exists('requestsData'):
                with open('requestsData/set_ocean_fleet.json', 'w') as f:
                    f.write(json.dumps(data))
            return data
        except HmError as e:
            print('Get set_ocean_fleet data FAILED! Reason:', e.message)
            raise
        except Exception as Error_information:
            print('Get set_ocean_fleet data FAILED! Reason:', Error_information)
            raise

    def get_ocean_user(self):
        """
        功能：获取活动用户数据
        返回值：dict
        """
        try:
            url = self.server + \
                'ocean/getUserData' + self.get_url_end()
            data = zlib.decompress(
                session.get(url=url, headers=HEADER,
                            cookies=self.cookies, timeout=20).content)
            data = json.loads(data)
            error_find(data)
            if is_write and os.path.exists('requestsData'):
                with open('requestsData/get_ocean_Userdata.json', 'w') as f:
                    f.write(json.dumps(data))
            return data
        except HmError as e:
            print('Get ocean data FAILED! Reason:', e.message)
            raise
        except Exception as Error_information:
            print('Get ocean data FAILED! Reason:', Error_information)
            raise

    def get_five_data(self):
        """
        功能：获取活动数据
        返回值：dict
        """
        try:
            url = self.server + 'five/getPveData/' + self.get_url_end()
            data = zlib.decompress(
                session.get(url=url, headers=HEADER,
                            cookies=self.cookies, timeout=20).content)
            data = json.loads(data)
            error_find(data)
            for node in data['fifth_level_node']:
                gameData.allPoint[int(node["id"])] = node
            for node in data['fifth_level']:
                gameData.allLevel[int(node["id"])] = node
            self.fivedata = data
            if is_write and os.path.exists('requestsData'):
                with open('requestsData/get_five_data.json', 'w') as f:
                    f.write(json.dumps(data))
            return data
        except HmError as e:
            print('Get five data FAILED! Reason:', e.message)
            raise
        except Exception as Error_information:
            print('Get five data FAILED! Reason:', Error_information)
            raise

    def get_five_user_data(self):
        """
        功能：获取活动数据
        返回值：dict
        """
        try:
            url = self.server + 'five/getUserData/' + self.get_url_end()
            data = zlib.decompress(
                session.get(url=url, headers=HEADER,
                            cookies=self.cookies, timeout=20).content)
            data = json.loads(data)
            error_find(data)
            if "joyFleet" in data:
                self.joyFleet = data["joyFleet"]
            if "joyShipVo" in data:
                self.joyShipVo = data["joyShipVo"]

            if is_write and os.path.exists('requestsData'):
                with open('requestsData/get_ocean_data.json', 'w') as f:
                    f.write(json.dumps(data))
            return data
        except HmError as e:
            print('Get ocean data FAILED! Reason:', e.message)
            raise
        except Exception as Error_information:
            print('Get ocean data FAILED! Reason:', Error_information)
            raise

    def is_five_map(self, smap):

        if "fifth_level" in self.fivedata and len(self.fivedata["fifth_level"]) != 0:
            for level in self.fivedata["fifth_level"]:
                if level["mapId"] == smap:
                    return True
        return False

    def is_toudi_map(self, smap):

        if "hardLevels" in gameData.activedata and len(gameData.activedata["hardLevels"]) != 0:
            if smap in gameData.activedata["hardLevels"]:
                return True
        return False

    def upgrade_ship(self, ids, jsons):
        """
        功能：新添加一个船只数据
        :param ids: 船只id
        :param jsons: 船只数据
        :return: None
        """
        self.allShip[ids] = jsons

    def upgrade_point(self, data):
        """
        功能：更新活动点信息
        """
        for eachPoint in data['oceanNode']:
            self.allPoint[int(eachPoint['id'])] = eachPoint

    def upgrade_level(self, data):
        """
        功能：更新活动点信息
        """
        for eachLevel in data['oceanLevel']:
            self.allLevel[int(eachLevel['id'])] = eachLevel

    def upgrade_equipment(self, data):
        self.allEquipment.clear()
        for eachEquipment in data['equipmentVo']:
            self.allEquipment[eachEquipment['equipmentCid']] = eachEquipment

    def upgrade_fleet(self, user_data):
        if "fleetVo" in user_data:
            self.fleet[0] = user_data['fleetVo'][0]['ships']
            self.fleet[1] = user_data['fleetVo'][1]['ships']
            self.fleet[2] = user_data['fleetVo'][2]['ships']
            self.fleet[3] = user_data['fleetVo'][3]['ships']
            self.fleet[4] = user_data['fleetVo'][4]['ships']
            self.fleet[5] = user_data['fleetVo'][5]['ships']
            self.fleet[6] = user_data['fleetVo'][6]['ships']
            self.fleet[7] = user_data['fleetVo'][7]['ships']

            self.fleetName[0] = user_data['fleetVo'][0]['title']
            self.fleetName[1] = user_data['fleetVo'][1]['title']
            self.fleetName[2] = user_data['fleetVo'][2]['title']
            self.fleetName[3] = user_data['fleetVo'][3]['title']

    def get_refresh_data(self):
        """
        功能：回到港口内容刷新
        无返回值
        """
        print('Getting refresh data...')
        # log.info("start refresh_data")
        try:
            getData = self.decurl('bsea/getData/')
            getUserInfo = self.decurl('live/getUserInfo')
            getMusicList = self.decurl('live/getMusicList')
            getUserData = self.decurl('active/getUserData/')
            self.decurl('pve/getMovieList/')
            self.decurl('pve/getCgList/')
            self.decurl('task/getAchievementList/')
            pve_getUserData = self.decurl('pve/getUserData/')
            self.userin(pve_getUserData)
            CgetUserData = self.decurl('campaign/getUserData/')
            if 'passInfo' in CgetUserData:
                gameData.campaignTotal = CgetUserData['passInfo']['totalNum']
                gameData.campaignRemainNum = CgetUserData['passInfo']['remainNum']
                gameData.campaignMap = CgetUserData['canCampaignChallengeLevel']
            log.info("refresh_data finished")
        except HmError as e:
            log.e("Get refresh data FAILED! Reason:", e)
            print('Get refresh data FAILED! Reason:', e.message)
            raise
        except Exception as e:
            log.e("Get refresh data FAILED! Reason:", e)
            print('Get refresh data FAILED! Reason:', e)
            raise

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

    def userin(self, pve_getUserData):
        if 'todaySpoilsNum' in pve_getUserData:
            gameData.todaySpoilsNum = int(
                pve_getUserData["todaySpoilsNum"])
        if 'pveLevel' in pve_getUserData:
            gameData.my_pveLevel = pve_getUserData["pveLevel"]
        if 'passedNodes' in pve_getUserData:
            gameData.my_passedNodes = pve_getUserData["passedNodes"]
        if 'missLine' in pve_getUserData:
            gameData.my_missLine = pve_getUserData["missLine"]
        if 'todaySupportStatus' in pve_getUserData:
            if pve_getUserData["todaySupportStatus"] == 0:
                gameData.useSupport = False
            else:
                gameData.useSupport = True

    def decurl(self, name, ret=True):
        if name not in self.verurl:
            url_cheat = self.server + name + self.get_url_end()
            cont = session.get(url=url_cheat, headers=HEADER, cookies=self.cookies, timeout=20).content
            try:  # 解码统一
                cont = zlib.decompress(cont)
            except Exception as e_s:
                if "not exist" in str(cont, 'utf-8'):
                    self.verurl.append(name)
                    log.info("忽略请求: " + name)
                return {}
            shop_canbuy = json.loads(cont)
            disname = name.strip("/").replace("/", "_")
            if is_write and os.path.exists('requestsData') and ret:
                with open("requestsData/" + disname + ".json", 'w') as f:
                    f.write(json.dumps(shop_canbuy))
            return shop_canbuy
        else:
            return {}

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


class GameLogin:
    """
    第一次: channal cookie version server_list
    的二次: 什么也不返回,用于初始化游戏数据
    """

    def __init__(self):
        self.pastport_headers = {
            "Accept-Encoding": "gzip",
            'User-Agent': 'okhttp/3.4.1',
            "Content-Type": "application/json; charset=UTF-8"
        }
        self.init_data_version = "0"
        self.hm_login_server = ""
        self.portHead = ""
        self.key = "kHPmWZ4zQBYP24ubmJ5wA4oz0d8EgIFe"
        self.login_server = ""
        self.res = ""

        # 第一次登录返回值
        self.version = "3.8.0"
        self.channel = '100016'
        self.cookies = None
        self.server_list = []  # 不同服务器的索引
        self.defaultServer = 0
        self.uid = None

        # 状态寄存器
        self.is_login_success = False
        # 状态寄存器
        self.first_finish = False
        self.second_finish = False
        self.is_sl_login = False
        self.isauto = False
        self.istart = 0
        # 暂存数据

        # 取出数据
        self.username = ""
        self.password = ""
        self.server = 0
        self.host = ""

        # 得到数据
        self.cookie = None

    # 第一次登录,获取cookies和服务器列表
    def first_login_usual(self, server, username, pwd, windows_login):
        """
        第一次登录,获取cookies和服务器列表
        :return:
        """
        try:
            # windows_login.tv_selfVersion.setText(str(VERSION))
            # windows_login.tv_selfVersion.setFont(
            #     QFont("Roman times", 10, QFont.Bold))
            url_version = ""
            if server == 0:  # 安卓服
                url_version = 'http://version.jr.moefantasy.com/' \
                              'index/checkVer/4.6.0/100016/2&version=4.6.0&channel=100016&market=2'
                self.res = 'http://login.jr.moefantasy.com/index/getInitConfigs/'
                self.channel = "100016"
                self.portHead = "881d3SlFucX5R5hE"
                self.key = "kHPmWZ4zQBYP24ubmJ5wA4oz0d8EgIFe"
            elif server == 1:  # ios服
                url_version = 'http://version.jr.moefantasy.com/' \
                              'index/checkVer/4.1.0/100015/2&version=4.1.0&channel=100015&market=2'
                self.res = 'http://loginios.jr.moefantasy.com/index/getInitConfigs/'
                self.channel = "100015"
                self.portHead = "881d3SlFucX5R5hE"
                self.key = "kHPmWZ4zQBYP24ubmJ5wA4oz0d8EgIFe"
            elif server == 2:  # 台服
                url_version = 'http://version.jr.moepoint.tw/' \
                              'index/checkVer/4.0.3/100033/2&version=4.0.3&channel=100033&market=2'
                self.res = "http://login.jr.moepoint.tw/index/getInitConfigs/"
                self.channel = "100033"
                self.portHead = "6f67d7612241"
                self.key = "c918ae4f4a75464fa964093ae8a66dae"
            elif server == 3:  # 日服
                url_version = 'http://version.jp.warshipgirls.com/' \
                              'index/checkVer/4.0.3/100024/2&version=3.8.0&channel=100024&market=2'
                self.res = "https://loginand.jp.warshipgirls.com/index/getInitConfigs/"
                self.channel = "100024"
            elif server == 4:  # 国际服
                url_version = 'http://enversion.warshipgirls.com/' \
                              'index/checkVer/4.1.0/100060/2&version=4.1.0&channel=100060&market=2'
                self.res = "http://enlogin.warshipgirls.com/index/getInitConfigs/"
                self.channel = "100060"
                self.portHead = "krtestfrontend"
                self.key = "abcdef01234567890abcdef01234567890"
            # 请求version
            # -----------------
            # 拉取版本信息
            # windows_login.statusBarSignal.emit("拉取版本信息...")
            response_version = session.get(
                url=url_version, headers=HEADER, timeout=20)
            response_version = response_version.text
            response_version = json.loads(response_version)
            if 'eid' in response_version:
                return_data = {
                    "error": 0,
                    "errmsg": ''
                }
                if response_version['eid'] == -9999:
                    log.error("拉取版本信息出错:", "服务器维护中...")
                    return_data["errmsg"] = "服务器维护中..."
                else:
                    log.error("拉取版本信息出错:", "未知错误...")
                    return_data["errmsg"] = "未知错误..."
                windows_login.first_login_deal(return_data)
                return False
            init_data.new_init_version = response_version['DataVersion']
            error_find(response_version)
            if is_write and os.path.exists('requestsData'):
                with open('requestsData/version.json', 'w') as f:
                    f.write(json.dumps(response_version))

            # 获取版本号, 登录地址
            self.version = response_version["version"]["newVersionId"]
            self.login_server = response_version["loginServer"]
            self.hm_login_server = response_version["hmLoginServer"]
            # windows_login.tv_gameVersion.setText(str(self.version))
            # windows_login.tv_gameVersion.setFont(
            #     QFont("Roman times", 10, QFont.Bold))
            # # ------------------
            # 进行登录游戏
            server_data = {}
            if server == 0 or server == 1 or server == 2 or server == 4:
                server_data = self.login_usual(
                    server=server, username=username, pwd=pwd)
            else:
                server_data = self.login_japan(username=username, password=pwd)

            self.defaultServer = int(server_data["defaultServer"])
            self.server_list = server_data["serverList"]
            self.uid = server_data["userId"]

            return_data = {
                "version": self.version,
                "channel": self.channel,
                "cookie": self.cookies,
                "server_list": self.server_list,
                "default_server": self.defaultServer,
                "uid": self.uid
            }
            windows_login.first_login_deal(return_data)
            return True

        except HmError as e:
            return_data = {
                "error": 0,
                "errmsg": e.message
            }
            windows_login.first_login_deal(return_data)
            log.error("第一次登录出错:", e.message)
            return False
        except Exception as e:
            return_data = {
                "error": 0,
                "errmsg": str(e)
            }
            windows_login.first_login_deal(return_data)
            log.error("第一次登录出错:", e)
            return False

    # 第二次登录,用于连接对应服务器
    def second_login(self, host, uid, windows_login):
        try:
            # 生成随机设备码
            # windows_login.statusBarSignal.emit("生成设备随机码...")
            now_time = str(int(round(time.time() * 1000)))
            random.seed(hashlib.md5(self.uid.encode('utf-8')).hexdigest())
            data_dict = {'client_version': self.version,
                         'phone_type': 'huawei tag-al00',
                         'phone_version': '5.1.1',
                         'ratio': '1280*720',
                         'service': 'CHINA MOBILE',
                         'udid': str(random.randint(100000000000000, 999999999999999)),
                         'source': 'android',
                         'affiliate': 'WIFI',
                         't': now_time,
                         'e': self.get_url_end(now_time),
                         'gz': '1',
                         'market': '2',
                         'channel': self.channel,
                         'version': self.version
                         }
            random.seed()
            # 获取欺骗数据
            # windows_login.statusBarSignal.emit("连接服务器...")
            login_url_1 = host + 'index/login/' + uid + \
                '?&' + urllib.parse.urlencode(data_dict)
            session.get(url=login_url_1, headers=HEADER,
                        cookies=self.cookies, timeout=20)
            # windows_login.statusBarSignal.emit("请求init数据...")
            self.get_init_data()
            # windows_login.statusBarSignal.emit("初始化界面...")
            windows_login.second_login_deal({})
            return True
        except HmError as e:
            log.e("第二次登录请求数据出错", e.message)
            windows_login.second_login_deal(
                {"error": 0, "errmsg": e.message})
            return False
        except Exception as e:
            log.e("第二次登录请求数据出错", e)
            windows_login.second_login_deal(
                {"error": 0, "errmsg": str(e)})
            return False

    # 普通登录实现方法
    def login_usual(self, username, pwd, server):
        try:
            def login_token():
               # windows_login.statusBarSignal.emit("获取token...")
                url_login = self.hm_login_server + "1.0/get/login/@self"
                # 获取tokens
                data = {}
                if server == 0 or server == 1 or server == 4:  # 安卓服 ios服 国际服
                    data = {
                        "platform": "0",
                        "appid": "0",
                        "app_server_type": "0",
                        "password": pwd,
                        "username": username
                    }
                elif server == 2:  # 台服
                    data = {
                        "appId": "0",
                        "appServerType": "0",
                        "password": pwd,
                        "userName": username
                    }
                self.refresh_headers(url_login)
                login_response = session.post(url=url_login, data=json.dumps(data).replace(" ", ""),
                                              headers=self.pastport_headers, timeout=20).text
                login_response = json.loads(login_response)

                if "error" in login_response and int(login_response["error"]) != 0:
                    if "errmsg" in login_response:
                        raise HmError(-113, login_response["errmsg"])
                    else:
                        raise HmError(-113, "无法登录服务器")

                # 字段里是否存在存在token
                tokens = ""
                if "access_token" in login_response:
                    tokens = login_response["access_token"]
                if "token" in login_response:
                    tokens = login_response["token"]

                token_list = {}
                # 写入tokens
                if os.path.exists("config/token.json"):
                    with open("config/token.json", 'r') as f2:
                        token_list = json.loads(f2.read())
                token_list[username] = tokens
                with open("config/token.json", 'w') as f1:
                    f1.write(json.dumps(token_list))
                return tokens

            # 第一个意义不明
           # windows_login.statusBarSignal.emit("请求initConfig...")
            url_init = self.hm_login_server + "1.0/get/initConfig/@self"
            self.refresh_headers(url_init)
            session.post(url=url_init, data="{}",
                         headers=self.pastport_headers, timeout=20)
            time.sleep(1)

            # 获取token
            token = ""
            if os.path.exists("config/token.json"):
                with open("config/token.json", "r") as f:
                    token_json = json.loads(f.read())
                    if username in token_json:
                        token = token_json[username]

            while True:
                # 没有token,获取token
                if len(token) < 10:
                    token = login_token()
                    time.sleep(1)

                # 验证token
               # windows_login.statusBarSignal.emit("验证token...")
                url_info = self.hm_login_server + "1.0/get/userInfo/@self"
                login_data = {}
                if server == 0 or server == 1:
                    login_data = json.dumps({"access_token": token})
                else:
                    login_data = json.dumps({"token": token})
                self.refresh_headers(url_info)
                user_info = session.post(
                    url=url_info, data=login_data, headers=self.pastport_headers, timeout=20).text
                user_info = json.loads(user_info)
                # 口令失效, 重新获取
                if "error" in user_info and user_info["error"] != 0:
                    token = ""
                    continue
                else:  # 口令正确
                    break

            # 获取用户信息
           # windows_login.statusBarSignal.emit("获取用户信息...")
            login_url = self.login_server + "index/hmLogin/" + token + self.get_url_end()
            login_response = session.get(
                url=login_url, headers=HEADER, timeout=20)
            login_text = json.loads(zlib.decompress(login_response.content))

            if is_write and os.path.exists('requestsData'):
                with open("requestsData/login.json", 'w') as f:
                    f.write(json.dumps(login_text))
            self.cookies = login_response.cookies.get_dict()
            self.uid = str(login_text['userId'])
            return login_text
        except HmError as e:
            raise
        except Exception as e:
            log.error("登录游戏出错", e)

    # 日服登录实现方法
    def login_japan(self, username, password):
        """
        功能：登录游戏并返回cookies
        无返回值
        """
        # 生成登录字典  login_dict：登录密码字典  login_url:登录url
        login_dict = {'username': base64.b64encode(
            username.encode()), 'pwd': base64.b64encode(password.encode())}
        login_url = self.login_server + 'index/passportLogin/' + self.get_url_end()

        # 登录游戏
        login_response = session.post(
            url=login_url, data=login_dict, headers=HEADER, timeout=20)
        login_text = json.loads(zlib.decompress(login_response.content))
        # 检测帐号是否正常
        if 'eid' in login_text and int(login_text['eid']) == -113:
            raise HmError(-113, "错误代码:帐号或者密码错误")
        error_find(login_text)
        if is_write:
            with open("login.json", 'w') as f:
                f.write(json.dumps(login_text))
        # 得到cookie和uid
        self.cookies = login_response.cookies.get_dict()
        self.uid = str(login_text['userId'])
        return login_text

    def get_url_end(self, now_time=str(int(round(time.time() * 1000)))):
        """
        功能：返回url尾部
        返回值：文本型
        """
        url_time = now_time
        md5_raw = url_time + 'ade2688f1904e9fb8d2efdb61b5e398a'
        md5 = hashlib.md5(md5_raw.encode('utf-8')).hexdigest()
        url_end = '&t={time}&e={key}&gz=1&market=2&channel={channel}&version={version}'
        url_end_dict = {'time': url_time, 'key': md5,
                        'channel': self.channel, 'version': self.version}
        url_end = url_end.format(**url_end_dict)
        return url_end

    def encryption(self, url, method):
        times = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')

        data = ""
        data += str(method)
        data += "\n"
        data += times
        data += "\n"
        data += "/" + url.split("/", 3)[-1]
        mac = hmac.new(self.key.encode(), data.encode(), hashlib.sha1)
        data = mac.digest()
        return base64.b64encode(data).decode("utf-8"), times

    def refresh_headers(self, url):
        data, times = self.encryption(url=url, method="POST")
        self.pastport_headers["Authorization"] = "HMS {}:".format(
            self.portHead) + data
        self.pastport_headers["Date"] = times

    def get_init_data(self):
        print('Getting init data...')
        try:
            if not os.path.exists('data'):
                os.mkdir('data')

            need_upgrade = True
            if os.path.exists('data/init.json'):
                init_data.read_init()
                if int(init_data.new_init_version) <= int(init_data.init_version):
                    need_upgrade = False
            if init_data.res_url != self.res:
                need_upgrade = True
            if need_upgrade:
                user_data = self.get_init_data2(
                    self.res, self.get_url_end())
                if not os.path.exists('data'):
                    os.mkdir('data')
                with open('data/init.json', 'w') as f:
                    f.write(user_data)
                init_data.read_init()
            return True
        except HmError as e:
            print('Get init data FAILED! Reason:', e.message)
            raise
        except Exception as e:
            print('Get init data FAILED! Reason:', e)
            raise

    def re_login(self, windows_login):
        """
        进行SL,重新登录游戏
        :return:
        """
        for i in range(5):
            result1 = self.first_login_usual(
                windows_login.server, windows_login.username, windows_login.password, windows_login)
            result2 = self.second_login(windows_login.host, windows_login.uid, windows_login)
            if result1 and result2:
                break
            else:
                continue

    def get_init_data2(self, res_url, end):
        """
        获取init数据
        :return:
        """
        try:
            print("请求新的res数据")
            user_data = zlib.decompress(
                session.get(url=res_url + end,
                            headers=HEADER, timeout=30).content)
            user_data = json.loads(user_data)
            user_data["res_url"] = res_url
            user_data = json.dumps(user_data)
            return user_data
        except Exception as e_s:
            log.e("获取init数据出错", e_s)
            raise


gameLogin = GameLogin()
gameData = GameData()
