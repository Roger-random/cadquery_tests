import math
import cadquery as cq

from dovetailstoragegrid import DovetailStorageGrid as dsg

dsg_01 = dsg(20, 15, 25)
show_object(dsg_01.tray(1,1))
