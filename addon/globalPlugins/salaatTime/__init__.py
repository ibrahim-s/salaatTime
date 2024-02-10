# -*- coding: utf-8 -*-
# salaat time announcement Global Plugin for NVDA
# Copyright (C) 2020 ibrahim hamadeh <ibra.hamadeh@hotmail.com>
# This file is covered by the GNU General Public License.
# most of stuff in this addon is borrowed from dropBox addon by Patrick ZAJDA.
# Shortcut: NVDA+Alt+s

import ctypes
import globalPluginHandler, scriptHandler
from scriptHandler import script
import ui
import NVDAObjects
import api
import winUser
import windowUtils
import mouseHandler
import core
import controlTypes
import config
import gui, wx
from gui import guiHelper
from .update import Initialize
from logHandler import log
# We initialize translation support
import addonHandler
addonHandler.initTranslation()

# Constents for roles to keep compatibility
if hasattr(controlTypes, 'ROLE_POPUPMENU'):
	POPUP_MENU = controlTypes.ROLE_POPUPMENU
else:
	POPUP_MENU = controlTypes.Role.POPUPMENU
if hasattr(controlTypes, 'ROLE_MENUITEM'):
	MENU_ITEM = controlTypes.ROLE_MENUITEM
else:
	MENU_ITEM = controlTypes.Role.MENUITEM

#prefex of notification messages,or name of salat time object.
namePrefex= (u'حان وقت صلاة', u'الصلاة التالية هي', u'الفجر ينتهي في',
'It is time to pray', 'Next is', 'Fajr ends at',
u'Il est temps de prier', u'Prochaine est', u'Fajr se termine à'
)
# for Turkish language
turkishWords= (u'Namazı Vakti', u'Sonraki', u'Sabah Namazı Bitiş Vakti', u'Kılma Zaman')

# For windows 11 22h2 and above.
def _findAccessibleLeafsFromWindowClassPath11_22h2():
	"""
	From a list of systray icons search for salaat time object
	borrowed from Systray list add-on
	"""
	# Starting to find the handle of the Shell_TrayWnd window
	h = winUser.FindWindow("Shell_TrayWnd", None)
	# Now, lets get the handle of Windows.UI.Input.InputSite.WindowClass window, where the icons reside...
	hwnd = windowUtils.findDescendantWindow(
		h, visible=None, controlID=None, className="Windows.UI.Input.InputSite.WindowClass"
	)
	# Now, lets get all objects in this window and its location
	obj = NVDAObjects.IAccessible.getNVDAObjectFromEvent(hwnd, -4, 0).children
	# We start in the second object because the first object do not interesse us...
	i = 1
	while i in range(len(obj)):
		o= obj[i]
		name=o.name
		#log.info(f'name: {name}')
		if  name and (any(s in name for s in namePrefex) 
		or any(s in name for s in turkishWords)):
			# salat time object found , quit while loop
			break
		i = i + 1
	if o:
		return o

# For windows 11 less than 22h2
def _findAccessibleLeafsFromWindowClassPath11(windowClassPath):
	# From a list of systray icons search for salaat time object
	# borrowed from Systray list NVDA add-on
	h = 0
	for className in windowClassPath:
		h = ctypes.windll.user32.FindWindowExA(h, 0, className, 0)
		if not h:
			continue
		objList = NVDAObjects.IAccessible.getNVDAObjectFromEvent(h, -4, 0).firstChild.children
		for o in objList:
			name=o.name
			#log.info(f'name: {name}')
			if  name and (any(s in name for s in namePrefex) 
			or any(s in name for s in turkishWords)):
				# salat time object found , quit for loop and return
				return o

# For windows 10 and lower
def _findAccessibleLeafsFromWindowClassPath(windowClassPath):
	# From the systray icon we search for salaat time object
	h,FindWindowExW = 0, winUser.user32.FindWindowExW
	for element in windowClassPath:
		h = FindWindowExW(h, 0, element, 0)
		if not h:
			continue
		obj=NVDAObjects.IAccessible.getNVDAObjectFromEvent(h,-4,0)
		o = obj.firstChild
		while o:
			name=o.name
			if  name and (any(s in name for s in namePrefex) 
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

def findSalatTimeObject():
	path = ("shell_TrayWnd", "TrayNotifyWnd", "SysPager", "ToolbarWindow32")
	path11 = ("shell_TrayWnd", "TrayNotifyWnd", "Windows.UI.Composition.DesktopWindowContentBridge")
	try:
		from winVersion import getWinVer, WinVersion
		global win11_22h2
		win11_22h2 = getWinVer() >= WinVersion(major=10, minor=0, build=22621)
		win11 = getWinVer() >= WinVersion(major=10, minor=0, build=22000)
	except ImportError:
		win11 = False
	if win11_22h2:
		object = _findAccessibleLeafsFromWindowClassPath11_22h2()
	elif win11:
		object = _findAccessibleLeafsFromWindowClassPath11(path11)
	else:
		object = _findAccessibleLeafsFromWindowClassPath(path)
	return object

class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	# We initialize the scripts category shown on input gestures dialog
	scriptCategory = _("Salaat Time")
	def __init__(self):
		super(GlobalPlugin, self).__init__()
		gui.settingsDialogs.NVDASettingsDialog.categoryClasses.append(SalaatTime)
		# To allow check for update after NVDA started.
		core.postNvdaStartup.register(self.checkForUpdate)

	def checkForUpdate(self):
		if not config.conf["salaatTime"]["autoUpdate"]:
			# Auto update is False
			return
		# starting the update process...
		def checkWithDelay():
			_beginChecking = Initialize()
			_beginChecking.start()
		wx.CallLater(7000, checkWithDelay)

	def terminate(self):
			gui.settingsDialogs.NVDASettingsDialog.categoryClasses.remove(SalaatTime)

	@script(
		# Translators: message presented in input mode.
		description=_("If pressed once, announces salaattime status. If pressed twice, activates salaattime icon and opens main window of Salaat Time."),
		gesture="kb:NVDA+alt+s"
	)
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
			if (currentProcess.lower() == u'salaattime' and objFocused.windowClassName.lower() == u'#32768') and objFocused.role in ({ROLE_POPUPMENU, ROLE_MENUITEM}):
				return
			else:
				try:
					doLeftClick(o)
				except NotImplementedError:
					# Translators: the message reported when it is not possible to activate salaatTime icon.
					ui.message(_("Unable to activate salaatTime icon"))

#default configuration 
configspec={
	"autoUpdate": "boolean(default= True)"
}
config.conf.spec["salaatTime"]= configspec

# Seting panel for Salaat time.
class SalaatTime(gui.settingsDialogs.SettingsPanel):
	# Translators: title of the dialog
	title= _("Salaat Time")

	def makeSettings(self, sizer):
		settingsSizerHelper = guiHelper.BoxSizerHelper(self, sizer=sizer)

		# Translators: label of the check box 
		self.updateCheckBox=wx.CheckBox(self,label=_("Check for update on startup"))
		settingsSizerHelper.addItem(self.updateCheckBox)
		self.updateCheckBox.SetValue(config.conf["salaatTime"]["autoUpdate"])

	def onSave(self):
		config.conf["salaatTime"]["autoUpdate"]= self.updateCheckBox.IsChecked() 
