# -*- coding: utf-8 -*-
from pca9685_driver import Device

from modules import cbpi, app, ActorBase

import json
import os, re, time
from modules.core.props import Property
import traceback

@cbpi.actor
class PCA9685Actor(ActorBase):
    a_busad = Property.Text("Bus Address", configurable=True, default_value="0x40", description="Bus address of PCA9685, 0x40 is 1st, 0x41 is 2nd etc")
    b_chan = Property.Text("Channel", configurable=True, default_value="0", description="PCA Output channel")
    p1_high = Property.Number("High PWM", configurable=True, default_value=4096, description="Ouput at 100%, defualt is 4096")
    p2_low = Property.Number("Low PWM", configurable=True, default_value=0, description="Output when on at 0%, default is 0%")
    p3_off = Property.Number("Off PWM", configurable=True, default_value=0, description="Output when off, default is 0%")
    p4_set = Property.Number("User PWM", configurable=True, default_value=0, description="Output when % for User setpoint Action 1")
    p4_set2 = Property.Number("User PWM2", configurable=True, default_value=0, description="Output when % for User setpoint Action 2")
    p4_set3 = Property.Number("User PWM3", configurable=True, default_value=0, description="Output when % for User setpoint Action 3")
    #f_inv = Property.Select("Invert Output", options=["No","Yes"], default_value = "No", description="Pull Up or down ressitor on input")


    def init(self):
        try:
         self.dev = None
         self.busad = int(self.a_busad,16)
         self.chan = int(self.b_chan)
         self.p1_high = int(self.p1_high)
         self.p2_low = int(self.p2_low)
         self.p3_off = int(self.p3_off)
         self.p4_set = int(self.p4_set)
         self.p4_set2 = int(self.p4_set2)
         self.p4_set3 = int(self.p4_set3)
         
         # set the pwm frequency (Hz)
         self.get_dev()
         self.dev.set_pwm_frequency(self.speed)
         self.dev.set_pwm(self.chan, self.p3_off)
         
         
         self.pow_step = (self.p1_high - self.p2_low) / 100.0
         self.power = 100
         self.is_on = False 
 
         
        except Exception as e:
         traceback.print_exc()
         raise

    def on(self, power=100):
        self.is_on = True
        if power != None:
            self.power = power
        self.dev.set_pwm(self.chan, self.pwr(self.power))
        
    def off(self):
        self.is_on = False
        self.dev.set_pwm(self.chan, self.p3_off)
        
    def set_power(self, power):
        self.power = power 
        if self.is_on:
            self.dev.set_pwm(self.chan, self.pwr(power))
        
    def pwr(self, power):
        power = int(power)
        if power == 100:
            return self.p1_high
        if power == 0:
            return self.p2_low
        ret = int(self.p2_low + (self.pow_step * power))
        return ret
        
    @cbpi.action("Set to User Pwm 1")
    def set_user1(self):
        self.dev.set_pwm(self.chan, self.p4_set)
        self.power = ((self.p4_set - self.p2_low) / self.pow_step)
        actor = cbpi.cache.get("actors").get(int(self.id))
        actor.power = self.power
        actor.state = 1
        cbpi.emit("SWITCH_ACTOR", actor)
        
    @cbpi.action("Set to User Pwm 2")
    def set_user2(self):
        self.dev.set_pwm(self.chan, self.p4_set2)
        self.power = ((self.p4_set - self.p2_low) / self.pow_step)
        actor = cbpi.cache.get("actors").get(int(self.id))
        actor.power = self.power
        actor.state = 1
        cbpi.emit("SWITCH_ACTOR", actor)
        
    @cbpi.action("Set to User Pwm 3")
    def set_user3(self):
        self.dev.set_pwm(self.chan, self.p4_set3)
        self.power = ((self.p4_set - self.p2_low) / self.pow_step)
        actor = cbpi.cache.get("actors").get(int(self.id))
        actor.power = self.power
        actor.state = 1
        cbpi.emit("SWITCH_ACTOR", actor)

    @cbpi.action("Reconnect to Device")
    def recon(self):
        pass       
        

    def get_dev(self):
        self.speed = cbpi.get_config_parameter("PCA_" + self.a_busad + "_Hz", None)
        if self.speed is None:
            self.speed = "50"
            cbpi.add_config_parameter("PCA_" + self.a_busad + "_Hz", "50", "text", "PCA Frequency")
        print self.speed        
        self.dev = Device(self.busad)
