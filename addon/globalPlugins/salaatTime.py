# -*- coding: utf-8 -*-
# salaat time announcement Global Plugin for NVDA
# Copyright (C) 2020 ibrahim hamadeh <ibra.hamadeh@hotmail.com>
# This file is covered by the GNU General Public License.
# most of stuff in this addon is borrowed from dropBox addon by Patrick ZAJDA.
# Shortcut: NVDA+Alt+s

import globalPluginHandler,addonHandler,scriptHandler
import ui
import NVDAObjects
import api
import winUser
import mouseHandler
import core
import controlTypes
from logHandler import log

def findSalatTimeObject():
	# We get the systray
	l = (u"shell_TrayWnd", u"TrayNotifyWnd", u"SysPager", u"ToolbarWindow32")
	#prefex of notification messages,or name of salat time object.
	namePrefex= (u'حان وقت صلاة', u'الصلاة التالية هي', u'الفجر ينتهي في',
	u'It is time to pray', u'Next is', u'Fajr ends at',
	u'Il est temps de prier', u'Prochaine est', u'Fajr se termine à'
	)
	# for Turkish language
	turkishWords= (u'Namazı Vakti', u'Sonraki', u'Sabah Namazı Bitiş Vakti', u'Kılma Zaman')
	h,FindWindowExW = 0, winUser.user32.FindWindowExW
	for element in l:
		h = FindWindowExW(h, 0, element, 0)
		if not h:
			continue

		obj=NVDAObjects.IAccessible.getNVDAObjectFromEvent(h,-4,0)
		o = obj.firstChild
		while o:
			name=o.name
			if  name != None and (any(name.startswith(s) for s in namePrefex) 
			or any(s in name for s in turkishWords)):
				# salat time object found , quit while loop
				break

			o=o.next

		if o:
			#salatTime object found, quit for loop
			break
	return o

def doLeftClick(obj):
		""" Perform left mouse click on the object.
		"""
		oldMouseObj= api.getMouseObject()
		api.moveMouseToNVDAObject(obj)
		mouseHandler.executeMouseEvent(winUser.MOUSEEVENTF_LEFTDOWN,0,0)
		mouseHandler.executeMouseEvent(winUser.MOUSEEVENTF_LEFTUP,0,0)
		# Return the mouse to previous position 
		core.callLater(200, api.moveMouseToNVDAObject, oldMouseObj)

# We initialize translation support
addonHandler.initTranslation()

class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	# We initialize the scripts category shown on input gestures dialog
	scriptCategory = _("Salaat Time")

	def script_announceSalatTime(self, gesture):
		o = findSalatTimeObject()
		if not o:
			# Translators: the message presented when salatTime tray icon was not found
			ui.message(_("Salat Time not found"))
			return

		name=o.name
		repeatCount = scriptHandler.getLastScriptRepeatCount()
		if repeatCount ==0 :
			# announce salaattime state
			ui.message (name)
			
		else:
			#log.info('under else, double press is done')
			# activate salaatTime icon
			# If we are already inside of the context menu, stop the script
			objFocused = api.getFocusObject()
			currentProcess = objFocused.appModule.appName.lower()
			if (currentProcess.lower() == u'salaattime' and objFocused.windowClassName.lower() == u'#32768') and objFocused.role in ({controlTypes.ROLE_POPUPMENU, controlTypes.ROLE_MENUITEM}):
				return
			else:
				try:
					doLeftClick(o)
				except NotImplementedError:
					# Translators: the message reported when it is not possible to activate salaatTime icon.
					ui.message(_("Unable to activate salaatTime icon"))

	# Translators: message presented when user performes input help for the alt+NVDA+S gesture
	script_announceSalatTime.__doc__ = _("If pressed once, announces salaattime status. If pressed twice, activates salaattime icon and opens main window of Salaat Time.")

	__gestures={
		"kb:NVDA+alt+s": "announceSalatTime",
	}

