import math
import cadquery as cq

from dovetailstoragegrid import DovetailStorageGrid as dsg

dsg_01 = dsg(20, 15, 25)

show_object(dsg_01.label_tray(1,1), options = {"alpha":0.5, "color":"blue"})
