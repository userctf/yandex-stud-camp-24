# coding:utf-8
"""
树莓派WiFi无线视频小车机器人驱动源码
作者：Sence
版权所有：小R科技（深圳市小二极客科技有限公司www.xiao-r.com）；WIFI机器人网论坛 www.wifi-robots.com
本代码可以自由修改，但禁止用作商业盈利目的！
本代码已申请软件著作权保护，如有侵权一经发现立即起诉！
"""
"""
@version: python3.7
@Author  : xiaor
@Explain :超声波模块
@Time    :2020/05/09
@File    :xr_ultrasonic.py
@Software: PyCharm
"""
import time
from builtins import int, chr, object

import xr_gpio as gpio
import xr_config as cfg

from xr_motor import RobotDirection
go = RobotDirection()

from xr_servo import Servo
servo = Servo()


class Ultrasonic(object):
	def __init__(self):
		self.MAZE_ABLE = 0
		self.MAZE_CNT = 0
		self.MAZE_TURN_TIME = 0
		self.dis = 0
		self.s_L = 0
		self.s_R = 0

	def get_filtered_distance(self, n=5):
		all_data = sorted([self.get_distance() for _ in range(n)])
		median = 0
		if n % 2 == 0:
			median = (all_data[n // 2 - 1] + all_data[n // 2]) / 2
		else:
			median = all_data[n // 2] 
		cfg.DISTANCE = round(median, 2)
		return cfg.DISTANCE
	
	def get_distance(self):
		"""
		获取超声波距离函数,有返回值distance，单位cm
		"""
		time_count = 0
		gpio.digital_write(gpio.TRIG, True)  
		time.sleep(0.000015)  
		gpio.digital_write(gpio.TRIG, False)  
		while not gpio.digital_read(gpio.ECHO): 
			pass
		t1 = time.time()  
		while gpio.digital_read(gpio.ECHO): 
			if time_count < 2000:  # todo: how much in secnods?
				time_count = time_count + 1
				time.sleep(0.000001)
				pass
			else:
				print("NO ECHO receive! Please check connection")
				break
		t2 = time.time() 
		distance = (t2 - t1) * 340 / 2 * 100 
		if distance < 500: 
			cfg.DISTANCE = round(distance, 2)
		else:
			cfg.DISTANCE = 500
		return cfg.DISTANCE

	def avoidbyragar(self):
		"""
		超声波避障函数
		"""
		cfg.LEFT_SPEED = 30
		cfg.RIGHT_SPEED = 30
		dis = self.get_distance()
		if 25 < dis < 300 or dis == 0:  # 距离大于25cm小于300cm超声波的测距范围,等于0的时候是远距离超过超声波测距范围
			cfg.AVOID_CHANGER = 1
		else:
			if cfg.AVOID_CHANGER == 1:
				go.stop()
				cfg.AVOID_CHANGER = 0

	def maze(self):
		"""
		超声波走迷宫函数
		"""
		cfg.LEFT_SPEED = 35
		cfg.RIGHT_SPEED = 35
		# print("超声波走迷宫函数")
		self.dis = self.get_distance()		# 获取距离值
		if self.MAZE_ABLE == 0 and ((self.dis > 30) or self.dis == 0):  # 前方没有障碍物时候并且不是死胡同
			while ((self.dis > 30) or self.dis == 0) and cfg.CRUISING_FLAG:
				self.dis = self.get_distance()
				go.forward()
			if cfg.CRUISING_FLAG:		# 在退出模式时不运行这个，避免退出模式后仍然不停车
				self.MAZE_CNT = self.MAZE_CNT+1
				print(self.MAZE_CNT)
				go.stop()
				time.sleep(0.05)
				go.back()		# 后退一点点
				time.sleep(0.15)
				go.stop()
				time.sleep(0.05)
				if self.MAZE_CNT > 3:		# 多次检测前方是否为障碍物，避免误检测
					self.MAZE_CNT = 0
					self.MAZE_ABLE = 1		# 如果前面是胡同

		else:
			go.stop()
			self.s_L = 0
			self.s_R = 0
			time.sleep(0.1)
			servo.set(7, 5)		# 先把超声波转动的舵机转到右边
			if cfg.CRUISING_FLAG:
				time.sleep(0.25)
			self.s_R = self.get_distance()
			if cfg.CRUISING_FLAG:
				time.sleep(0.2)

			servo.set(7, 175)		# 再把舵机转动到左边
			if cfg.CRUISING_FLAG:
				time.sleep(0.3)
			self.s_L = self.get_distance()
			if cfg.CRUISING_FLAG:
				time.sleep(0.2)
			servo.set(7, 80)		# 再把舵机转动到中间
			time.sleep(0.1)

			if (self.s_R == 0) or (self.s_R > self.s_L and self.s_R > 20): # 如果右边宽阔，并且障碍物距离大于20，并且右侧大于左侧
				self.MAZE_ABLE = 0
				cfg.LEFT_SPEED = 99		# 转向速度，如果在不同得地面需要实际手动调节其速度满足转向力度，这里是地毯上的速度需要高点
				cfg.RIGHT_SPEED = 99
				go.right()
				if cfg.CRUISING_FLAG:
					time.sleep(cfg.MAZE_TURN_TIME/1000)			# 转向的时间，根据上面转向的速度调节，实测转到90度左右即可
				cfg.LEFT_SPEED = 45
				cfg.RIGHT_SPEED = 45

			elif (self.s_L == 0) or (self.s_R < self.s_L and self.s_L > 20): 		# 如果左边宽阔，并且障碍物距离大于20，并且左侧大于右侧
				self.MAZE_ABLE = 0
				cfg.LEFT_SPEED = 99  	# 转向速度，如果在不同得地面需要实际手动调节其速度满足转向力度，这里是地毯上的速度需要高点
				cfg.RIGHT_SPEED = 99
				go.left()
				if cfg.CRUISING_FLAG:
					time.sleep(cfg.MAZE_TURN_TIME/1000)		# 转向的时间，根据上面转向的速度调节，实测转到90度左右即可
				cfg.LEFT_SPEED = 45
				cfg.RIGHT_SPEED = 45

			else: 	# 前方不能走，左右都不能走，即进入了死胡同，只能原路返回
				self.MAZE_ABLE = 1 		# 把标志置1，避免又重复进入死胡同，只能一点点后退再左右检测是否有其他通道，当左右通道任意一方畅通时标志位置0，才可往前进
				go.back()
				if cfg.CRUISING_FLAG:
					time.sleep(0.3)

			go.stop()
			time.sleep(0.1)