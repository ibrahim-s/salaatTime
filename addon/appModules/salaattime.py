# -*- coding: utf-8 -*-
# NVDA Add-on: Salat Time
# Copyright (C) 2021 AlaqsaVoice 
# This add-on is free software, licensed under the terms of the GNU General Public License (version 2).
# See the file COPYING for more details.

import appModuleHandler
import api
import ui

salatList = ["  ", "الفجر", "الشروق", "الظهر", "العصر", "المغرب", "العِشاء"]
x = 0
class AppModule(appModuleHandler.AppModule):
	def __init__(self, *args, **kwargs):
		super(AppModule, self).__init__(*args, **kwargs)

	__gestures={'kb:%s'%i: 'slatTime' for i in "123456"}

	def event_NVDAObject_init(self, obj):
		if obj.windowControlID in [190, 210, 181, 153, 142, 169, 40]:
			obj.name="play"
		elif obj.windowControlID in [45, 170, 140, 155, 183, 208, 192, 196, 201, 179, 151, 133, 165, 46]:
			obj.name ="stop"
		elif obj.windowControlID in [194, 206, 174, 146, 138, 160, 39]:
			obj.name = "play للملف الخاص"
		elif obj.windowControlID in [195, 203, 177, 149, 135, 163, 43]:
			obj.name = "اختيار ملف آخر"
		elif obj.windowControlID in [199, 14]:
			obj.name = "اجعل الجميع كهذا"

	def event_gainFocus(self, obj, nextHandler):
		global objList
		if obj.windowClassName == 'ThunderRT6ListBox':
			for key in ('downArrow', 'upArrow', 'leftArrow', 'rightArrow'):
				self.bindGesture(f'kb:{key}', 'times')
			objList = obj.IAccessibleObject.accName(obj.IAccessibleChildID).split('	')
			n = objList[0].split(' ')
			obj.name = ' '.join(n[::-1])
		else:
			self.clearGestureBindings()
			self.bindGestures(self.__gestures)
		nextHandler()

	def script_slatTime (self, gesture):
		k= gesture.mainKeyName
		ui.message(f"{salatList[int(k)]}: الساعة {objList[int(k)]}")

	def script_times (self, gesture):
		global x
		k= gesture.mainKeyName
		if k =="upArrow" or k =="downArrow":
			gesture.send()
			x=0
			return
		elif k =="rightArrow":
			x-=1
			if x  ==0:
				x=6
		elif k == "leftArrow":
			x+=1
			if x==7 or x==0:
				x=1
		ui.message(f"{salatList[int(x)]}: الساعة {objList[int(x)]}")
