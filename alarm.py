#!/usr/bin/python

''' 
 license: are you kidding? :)
'''
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject, Pango, Gst, Gdk
import pygst
from datetime import datetime
import os
Gst.init(None)

class MainWindow(Gtk.Window):

		
		def __init__(self):
			Gtk.Window.__init__(self, title="Alarm Clock")
			self.alarm_state = False
                        self.set_default_size(600, 500)
			self.table = Gtk.Table(5,4,True)
			self.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse("#333"))
			self.add(self.table)
			# # GST
			self.player = Gst.ElementFactory.make("playbin", "player")
			self.player.set_property('uri','file://'+os.path.abspath('alarm.mp3'))

			# # Clock label
			self.labelClock = Gtk.Label()
			self.labelClock.modify_font(Pango.FontDescription("sans 14"))
                        self.labelClock.override_color(Gtk.StateType.NORMAL, Gdk.RGBA(1, 1,1, 0.9))

			self.table.attach(self.labelClock,0, 6, 0, 1)
			#  initially set time to clock label otherwise there is a delay 
			#  when displaying the clock when app is first run
			self.labelClock.set_label(str(datetime.now()))

			# # alarm switch
			self.alarmSwitch = Gtk.Switch()
			self.table.attach(self.alarmSwitch,0,6,1,2)

			# # alarm label
			self.labelSetAlarm = Gtk.Label("No Alarm Set")
                        self.labelSetAlarm.override_color(Gtk.StateType.NORMAL, Gdk.RGBA(1, 1,1, 0.9))
			self.table.attach(self.labelSetAlarm,0, 6, 2, 3)

			# # time labels
			self.time_hr_label = Gtk.Label("Hour")
                        self.time_hr_label.override_color(Gtk.StateType.NORMAL, Gdk.RGBA(1, 1,1, 0.9))
			self.table.attach(self.time_hr_label,0,1, 3,4)
			self.time_min_label = Gtk.Label("Min")
                        self.time_min_label.override_color(Gtk.StateType.NORMAL, Gdk.RGBA(1, 1,1, 0.9))
			self.table.attach(self.time_min_label,2,3, 3,4)
			self.time_sec_label = Gtk.Label("Sec")
                        self.time_sec_label.override_color(Gtk.StateType.NORMAL, Gdk.RGBA(1, 1,1, 0.9))
			self.table.attach(self.time_sec_label,4,5, 3,4)
			
			# # hours
			self.hr_adj = Gtk.Adjustment(value = 1, lower=0, upper=23, step_incr=1)
			self.time_hr_spinner = Gtk.SpinButton()
			self.time_hr_spinner.set_adjustment(self.hr_adj)
			self.table.attach(self.time_hr_spinner,0,1, 4,5)

			# # mins
			self.min_adj = Gtk.Adjustment(value = 1, lower=0, upper=59, step_incr=1)
			self.time_min_spinner = Gtk.SpinButton()
			self.time_min_spinner.set_adjustment(self.min_adj)
			self.table.attach(self.time_min_spinner,2,3, 4,5)

			# # seconds
			self.sec_adj = Gtk.Adjustment(value = 1, lower=0, upper=59, step_incr=1)
			self.time_sec_spinner = Gtk.SpinButton()
			self.time_sec_spinner.set_adjustment(self.sec_adj)
			self.table.attach(self.time_sec_spinner,4,5, 4,5)

			# # alarm media file
			self.fileEntryLabel = Gtk.Label("Enter full filename")
                        self.fileEntryLabel.override_color(Gtk.StateType.NORMAL, Gdk.RGBA(1, 1,1, 0.9))
			self.table.attach(self.fileEntryLabel,0,6, 5,6)
			self.fileEntry = Gtk.Entry()
			self.table.attach(self.fileEntry,0,6, 6,7)
			
			# # connect methods
			self.alarmSwitch.connect("notify::active", self.alarm_trigger)
			self.alarmSwitch.set_active(False)


		# # format time to str for comparison
		def format_time(self,time):
			rounded = int(round(time))
			if len(str(rounded)) == 1:
				formatted = "{}{}".format("0",rounded)
				return formatted
			else:
				return rounded


		# # main alarm function
		def set_alarm(self):
			#  get current time for compatison to alarm time
			timenow = str(datetime.now())[11:19]

			#  get values from our time spinners
			hour = self.time_hr_spinner.get_value()
			minute = self.time_min_spinner.get_value()
			seconds = self.time_sec_spinner.get_value()
		
			#  format our time for comparison against timenow
			alarm_formated = "{}:{}:{}".format(self.format_time(hour),self.format_time(minute),self.format_time(seconds))

			#  if the alarm state is true, wait for the alarm time to equal current time then trigger alarm
			if self.alarm_state:
				if timenow == alarm_formated:
					#  if no file is supplied to be played, play the default alarm.mp3 in CWD
					if self.fileEntry.get_text() == "":
						self.player.set_property('uri','file://'+os.path.abspath('alarm.mp3'))
						print "beep beep beep"
					#  as above except file is supplied so lets play that one instead!
					else:
						alarmFile = 'file://'+self.fileEntry.get_text()
						self.player.set_property('uri',alarmFile)
						print "beep beep beep"
					#  set gst to start playing whatever file	
					self.player.set_state(Gst.State.PLAYING)
					self.alarm_state = False
					self.labelSetAlarm.set_label("Alarm OFF!")
			else:
				self.labelSetAlarm.set_label("No Alarm Set")
			#  return tree true to ensure timeout_add continues
			return True

		#  this is called from our "alarmSwitch" button and will set our alarm state to True
		def alarm_trigger(self,switch,gparam):
			if self.alarmSwitch.get_active():
				self.alarm_state = True
				self.labelSetAlarm.set_label("Alarm ON!")
			else:
				self.alarm_state = True
				self.labelSetAlarm.set_label("Alarm OFF!")
				self.player.set_state(Gst.State.NULL)

		# # run clock
		def displayclock(self,state):
			#  putting our datetime into a var and setting our label to the result. 
			#  we need to return "True" to ensure the timer continues to run, otherwise it will only run once.
			datetimenow = str(datetime.now())[11:19]
			self.labelClock.set_label(datetimenow)
			return state

		# Initialize Timer
		def startclocktimer(self):
			#  this takes 2 args: (how often to update in millisec, the method to run)
			GObject.timeout_add(100, self.displayclock, True)
			GObject.timeout_add(1000, self.set_alarm)


win = MainWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
win.startclocktimer()
Gtk.main()
