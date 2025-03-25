#!/usr/bin/python3.4
# Setup Python ----------------------------------------------- #
import pygame, sys, random
import app
class Particle:
    def __init__(self,pos,velocity,size,color,lifetime,maxlifetime,origin,tpe):
        self.pos=pos
        self.vel=velocity
        self.size=size
        self.color=color
        self.lifetime = lifetime
        self.maxlifetime = maxlifetime
        self.origin = origin
        self.tpe = tpe
    def update(self,dt):
        self.pos[0]+=self.vel[0]
        self.pos[1]+=self.vel[1]
        self.vel[1]*=0.98
        self.vel[0]*=0.98
        if self.origin[0]!=-1:
            self.vel[1]+=0.2
        self.lifetime-=dt*30
        #add removal at the end


    