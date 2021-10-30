# -*- coding: utf-8 -*-
# NVDA Add-on: Salat Time
# Copyright (C) 2021 AlaqsaVoice 
# This add-on is free software, licensed under the terms of the GNU General Public License (version 2).
# See the file COPYING for more details.

import appModuleHandler
import api
import ui
import controlTypes
from logHandler import log

if hasattr(controlTypes, 'Role'):
	controlTypes.ROLE_BUTTON= controlTypes.Role.BUTTON

todayList= []
objList= []
salatList = ["  ", "الفجر", "الشروق", "الظهر", "العصر", "المغرب", "العِشاء"]
x = 0
class AppModule(appModuleHandler.AppModule):
	def __init__(self, *args, **kwargs):
		super(AppModule, self).__init__(*args, **kwargs)

	__gestures={'kb:%s'%i: 'slatTime' for i in "123456"}

	def event_NVDAObject_init(self, obj):
		if obj.role== controlTypes.ROLE_BUTTON and obj.windowControlID in [190, 210, 181, 153, 142, 169, 40]:
			obj.name="play"
		elif obj.role== controlTypes.ROLE_BUTTON and obj.windowControlID in [45, 170, 140, 155, 183, 208, 192, 196, 201, 179, 151, 133, 165, 46]:
			obj.name ="stop"
		elif obj.role== controlTypes.ROLE_BUTTON and obj.windowControlID in [194, 206, 174, 146, 138, 160, 39]:
			obj.name = "play للملف الخاص"
		elif obj.role== controlTypes.ROLE_BUTTON and obj.windowControlID in [195, 203, 177, 149, 135, 163, 43]:
			obj.name = "اختيار ملف آخر"
		elif obj.role== controlTypes.ROLE_BUTTON and obj.windowControlID in [199, 14]:
			obj.name = "اجعل الجميع كهذا"

	def event_gainFocus(self, obj, nextHandler):
		#log.info('under gain focus event...')
		global objList, todayList, x
		if obj.windowClassName== 'ThunderRT6PictureBoxDC':
			x= 0
			if not todayList:
				try:
					target= obj.parent.parent.firstChild.firstChild.firstChild.firstChild.lastChild.firstChild.firstChild
					todayList=target.name.split('\t')
				except: pass
#				x=0
				#log.info(f"todayList: {todayList}")
			for key in ('downArrow', 'upArrow', 'leftArrow', 'rightArrow'):
				self.bindGesture(f'kb:{key}', 'times')

		if obj.windowClassName == 'ThunderRT6ListBox':
			x=0
			for key in ('downArrow', 'upArrow', 'leftArrow', 'rightArrow'):
				self.bindGesture(f'kb:{key}', 'times')
			objList = obj.IAccessibleObject.accName(obj.IAccessibleChildID).split('	')
			n = objList[0].split(' ')
			obj.name = ' '.join(n[::-1])
		#else:
		if obj.windowClassName not in ('ThunderRT6PictureBoxDC', 'ThunderRT6ListBox'):
			self.clearGestureBindings()
			self.bindGestures(self.__gestures)
		nextHandler()

	def script_slatTime (self, gesture):
		focus= api.getFocusObject()
		if focus.windowClassName== 'ThunderRT6ListBox':
			_list= objList
		elif focus.windowClassName== 'ThunderRT6PictureBoxDC':
			_list= todayList
		k= gesture.mainKeyName
		ui.message(f"{salatList[int(k)]}: الساعة {_list[int(k)]}")

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
		focus= api.getFocusObject()
		if focus.windowClassName== 'ThunderRT6ListBox':
			_list= objList
		elif focus.windowClassName== 'ThunderRT6PictureBoxDC':
			_list= todayList
		#log.info(f"x: {x}, objLis: {objList}")
		ui.message(f"{salatList[int(x)]}: الساعة {_list[int(x)]}")
