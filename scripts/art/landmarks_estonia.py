"""Tallinn's limestone towers and Hanseatic roofs, built in projected (i, j, z).

Run directly for isolated 4× studies. Sources and compressed anchors: DEVELOPMENT_PLAN.md.
"""
import math

import iso
from iso import rgb
from landmarks_paris import P, seg, poly, corners, preview, GLASS
from landmarks_iberia import hip_roof, stone_courses, arch_opening, palette_of, tones, crenellate
from landmarks_amsterdam import gable_roof
from landmarks_italy import cylinder, ellipse
from landmarks_denmark import spire, clock
from landmarks_slovakia import block, band, pediment

STONE = tones('#F5F0DC', '#D5D1B6', '#BCBA9F', '#969B85', '#68745F', '#A9AD94', '#414D3C')
WHITE = tones('#FFF9E7', '#EEE4CC', '#D7CCB4', '#B5AC96', '#847B64', '#C6BBA2', '#514B39')
CLAY = tones('#F1AC7B', '#C9724B', '#AD583C', '#82402F', '#592B24', '#A14E36', '#49261F')
COPPER = tones('#B6D4B8', '#7BA58D', '#5E8976', '#3D6355', '#29483E', '#527866', '#243A30')
DARK = tones('#9BABA5', '#637970', '#4B615B', '#304740', '#1D302C', '#41574E', '#172B25')
BRONZE = tones('#C4AB85', '#958164', '#7D6A54', '#5D503F', '#3D352C', '#6F5E49', '#302B24')
PINK = tones('#FFE3D9', '#E8BAB6', '#CB9895', '#A47B7D', '#765255', '#BD8A87', '#543C3F')
RED = tones('#E8A18C', '#B86554', '#9D4F43', '#763B35', '#512A27', '#8C483D', '#3E2723')
GOLD = tones('#FFF2B0', '#E7C568', '#C6A04B', '#9C792F', '#6F5423', '#B38D3B', '#514224')
WALLS = [rgb(c) for c in ('#D9C68F', '#CFABA0', '#BCD0C1', '#E4DCC5', '#B5C7D0', '#C8BBCE', '#B99475')]
IRON, WOOD = rgb('#344438'), rgb('#70523C')
WATER = (rgb('#477E91'), rgb('#345E75'), rgb('#C3DDE1'))


def lifted(draw, z):
    """Draw a model z pixels up (on a raised plateau) by shifting the projection origin while it paints."""
    if not z:
        return draw
    def raised(s):
        s.oy -= z
        try:
            draw(s)
        finally:
            s.oy += z
    return raised


def windows(material, height, bay=10, floor=12, gothic=False):
    joints = stone_courses(material, 4, 11)
    def pattern(u, v, lit):
        c, level = int(u) % bay, int(v) % floor
        trim = WHITE['lit' if lit else 'dark']
        if v < 2 or int(v) in (height-1, height-3): return trim
        top = floor-3-abs(c-bay/2)*(1.1 if gothic else .12)
        if 2 <= c <= bay-2 and 3 <= level <= top and v < height-4:
            if c in (2, bay-2, bay//2) or level in (3, 6, int(top)): return trim
            return GLASS['mid' if lit else 'dark']
        return joints(u, v, lit) if material == STONE else None
    return pattern


def cross(s, i, j, z):
    block(s, i-.06, j-.06, .12, .12, 7, GOLD, z=z)
    block(s, i-.3, j-.06, .6, .12, 1.2, GOLD, z=z+4)
    seg(s, P(s, i-.2, j, z+1), P(s, i+.2, j, z+2), GOLD['dark'])


def flag(s, i, j, z):
    seg(s, P(s,i,j,z), P(s,i,j,z+16), IRON)
    for n,colour in enumerate((rgb('#579BC4'), rgb('#273232'), WHITE['hi'])):
        poly(s,[P(s,i+a,j,z+15-n*2-b) for a,b in ((0,0),(1.2,0),(1.2,2),(0,2))],lambda x,y,c=colour:c)


def round_tower(s, i, j, radius, height, roof=True):
    joints = stone_courses(STONE, 4, 10)
    def openings(u,v,lit):
        c,level=int(u)%12,int(v)%16
        if 5<=c<=6 and 4<level<12 and v>8:return STONE['deep']
        return joints(u,v,lit)
    cylinder(s,i,j,radius,radius,0,height,STONE,openings)
    ellipse(s,i,j,radius+.08,radius+.08,height,STONE['hi'])
    if roof:spire(s,i,j,radius+.18,height+1,21,CLAY,conical=True)


def townhouse(scene,i,j,wi=2.5,wj=3,floors=2,seed=0,z=0):
    """Narrow Hanseatic merchant houses, pointed storage gables and hoisting hatches."""
    wall,height=palette_of(WALLS[seed%len(WALLS)]),floors*10+3
    base=windows(wall,height,9,10)
    def pattern(u,v,lit):
        c,level=int(u)%9,int(v)%10
        if v<9 and 1<=c<=7:
            if c in (1,7) or int(v) in (1,8):return WHITE['lit' if lit else 'dark']
            return WOOD if (int(u)//9+seed)%3==0 else GLASS['dark']
        if seed%4==0 and v>=10 and level==2 and 1<=c<=7:return IRON
        return base(u,v,lit)
    def draw(s):
        block(s,i,j,wi,wj,height,wall,pattern)
        band(s,i,j,wi,wj,1,STONE,2);band(s,i,j,wi,wj,height-1,WHITE)
        gable_roof(s,i,j,wi,wj,height,17,CLAY,wall,'step' if seed%7==0 else 'point')
        # Recessed loft hatch and a solid timber hoisting beam on the end gable.
        fj=j+wj+.15
        poly(s,[P(s,i+wi/2+a,fj,height+z) for a,z in ((-.22,4),(.22,4),(.22,9),(-.22,9))],lambda x,y:WOOD)
        seg(s,P(s,i+wi/2,fj,height+11),P(s,i+wi/2,fj+.65,height+11),IRON,2)
        if seed%3==0:
            block(s,i+.8,j+.5,.55,.6,5,WHITE,windows(WHITE,9,5,9),z=height+5)
            hip_roof(s,i+.75,j+.45,.65,.7,height+10,4,CLAY)
        block(s,i+wi-.7,j+.3,.45,.5,9,STONE,z=height+7)
        band(s,i+wi-.7,j+.3,.45,.5,height+15,CLAY,2)
    scene.add(i+j+wi+wj,lifted(draw,z))


def fat_margaret(scene,i,j):
    """Broad flat artillery tower, cannon ports and Great Coastal Gate with heraldic plaque."""
    def draw(s):
        # Gate and pitched-roof annex sit behind the broad artillery drum.
        block(s,i,j+4,5.7,2.3,23,STONE,windows(STONE,23,10,13))
        hip_roof(s,i,j+4,5.7,2.3,23,14,CLAY)
        fj=j+6.34
        poly(s,[P(s,i+a,fj,z) for a,z in ((1,0),(2.7,0),(2.7,10),(1.85,15),(1,10))],lambda x,y:STONE['deep'])
        for a in (.9,2.7):block(s,i+a,fj,.18,.18,11,WHITE)
        block(s,i+1.55,fj,.65,.12,5,WHITE,z=16)
        seg(s,P(s,i+1.7,fj+.1,18),P(s,i+2,fj+.1,20),RED['dark'],2)
        ci,cj=i+5.2,j+3.5
        joints=stone_courses(STONE,4,12)
        def ports(u,v,lit):
            c,level=int(u)%15,int(v)%12
            if 5<=c<=9 and 4<=level<=7:
                return WHITE['dark'] if c in (5,9) else STONE['deep']
            return joints(u,v,lit)
        cylinder(s,ci,cj,2.65,2.65,0,30,STONE,ports)
        ellipse(s,ci,cj,2.75,2.75,30,WHITE['dark'])
        ellipse(s,ci,cj,2.4,2.4,30.3,STONE['deep'])
        ellipse(s,ci,cj,2.23,2.23,30.5,
                lambda x,y:WHITE['line'] if int(y)%5==0 and int(x)%3==0 else WHITE['mid'])
        # Low rooftop terrace rail, with a sparse rhythm rather than a cage.
        rim=[P(s,ci+2.5*math.cos(a*math.tau/32),cj+2.5*math.sin(a*math.tau/32),33) for a in range(33)]
        for a,b in zip(rim,rim[1:]):seg(s,a,b,IRON)
        for a in range(12):
            t=a*math.tau/12;seg(s,P(s,ci+2.5*math.cos(t),cj+2.5*math.sin(t),30),P(s,ci+2.5*math.cos(t),cj+2.5*math.sin(t),33),IRON)
    scene.add(i+j+14,draw)


def st_olaf(scene,i,j):
    """Tall white Gothic nave, copper roof and steep green spire with four corner pinnacles."""
    def draw(s):
        block(s,i,j,5.2,7.5,36,WHITE,windows(WHITE,36,12,25,True))
        gable_roof(s,i,j,5.2,7.5,36,25,COPPER,WHITE,'point')
        for b in (.4,2.3,4.2,6.1):
            block(s,i+4.95,j+b,.55,.45,29,STONE)
            seg(s,P(s,i+5.2,j+b,29),P(s,i+4.9,j+b,37),WHITE['hi'],2)
        ti,tj=i+.8,j+5.5
        def belfry(u,v,lit):
            c=int(u)%12
            if 3<=c<=9 and 47<v<65-abs(c-6):
                return STONE['mid'] if c in (3,6,9) else DARK['deep']
            if 5<=c<=6 and 15<v<23:return DARK['dark']
            if 5<=c<=7 and 31<v<40:
                return STONE['mid'] if c in (5,7) else DARK['dark']
            # Restrained plaster mottling, rather than coarse ashlar on a white shaft.
            if iso.h01(int(u),int(v),1934)<.035:return WHITE['mid' if lit else 'line']
            return None
        block(s,ti,tj,3,3,72,WHITE,belfry)
        for z in (3,22,48,70):band(s,ti,tj,3,3,z,STONE)
        spire(s,ti+1.5,tj+1.5,1.95,73,65,DARK,conical=True)
        for a,b in ((0,0),(3,0),(0,3),(3,3)):
            spire(s,ti+a,tj+b,.35,72,13,DARK,conical=True)
        cross(s,ti+1.5,tj+1.5,139)
        # Pointed recessed doorway, with a splayed pale surround.
        fj=tj+3.05
        pts=[P(s,ti+a,fj,z) for a,z in ((.7,1),(2.3,1),(2.3,11),(1.5,18),(.7,11))]
        poly(s,pts,lambda x,y:WOOD)
        for a,b in zip(pts[1:],pts[2:]):seg(s,a,b,STONE['hi'],2)
    scene.add(i+j+15,draw)


def kadriorg(scene,i,j):
    """Petrine Baroque palace: red stucco, white pilasters, raised central hall and garden steps."""
    def draw(s):
        for a,b,w,d,h in ((i,j+1,11,3.4,26),(i+3.8,j,3.4,5,40)):
            base=windows(RED,h,11,13)
            def pattern(u,v,lit,base=base):
                if int(u)%11 in (0,1):return WHITE['lit' if lit else 'dark']
                return base(u,v,lit)
            block(s,a,b,w,d,h,RED,pattern)
            for z in (2,14,h-2):band(s,a,b,w,d,z,WHITE)
            hip_roof(s,a-.08,b-.08,w+.16,d+.16,h,13,CLAY)
            if h==26:
                for start,width in ((0,3.7),(7.3,3.7)):
                    seg(s,P(s,i+start,j+4.5,31),P(s,i+start+width,j+4.5,31),WHITE['lit'],2)
                    for n in range(8):
                        u=start+n*width/7
                        seg(s,P(s,i+u,j+4.5,27),P(s,i+u,j+4.5,31),WHITE['dark'])
        # Curved Baroque attic with volutes and pale roof balustrades.
        profile=[(0,0),(0,5),(.18,4),(.3,6),(.34,11),(.45,9),(.5,14),
                 (.55,9),(.66,11),(.7,6),(.82,4),(1,5),(1,0)]
        front=[P(s,i+3.8+u*3.4,j+5.06,40+v) for u,v in profile]
        rear=[P(s,i+3.8+u*3.4,j+4.8,40+v) for u,v in profile]
        for a in range(len(profile)-1):
            poly(s,[rear[a],rear[a+1],front[a+1],front[a]],lambda x,y:WHITE['dark'])
        poly(s,front,lambda x,y:RED['lit'])
        for a,b in zip(front,front[1:]):seg(s,a,b,WHITE['hi'],2)
        cylinder(s,i+5.5,j+5.1,.28,.16,45,3,GOLD)
        # Main portal: open pilastered porch, balcony and dressed door behind.
        block(s,i+4.7,j+4.9,1.6,.12,11,WHITE,
              lambda u,v,lit:arch_opening(u,v,6.4,4.5,7,WOOD) or WHITE['lit'])
        for a in (4.5,6.4):block(s,i+a,j+5.2,.22,.22,13,WHITE)
        block(s,i+4.4,j+5.1,2.35,.55,2,STONE,z=13)
        for a in range(8):seg(s,P(s,i+4.5+a*.3,j+5.65,15),P(s,i+4.5+a*.3,j+5.65,19),IRON)
        seg(s,P(s,i+4.4,j+5.65,19),P(s,i+6.75,j+5.65,19),IRON)
        for a in range(5):block(s,i+4,j+5.1+a*.28,3,.3,6-a,STONE)
        for a in (0,2.4,8,10.5):
            block(s,i+a,j+4.8,.3,.3,7,WHITE)
            ellipse(s,i+a+.15,j+4.95,.2,.2,8,WHITE['hi'])
        for a,b in ((.2,2.6),(8.2,10.7)):
            seg(s,P(s,i+a,j+4.95,7),P(s,i+b,j+4.95,7),WHITE['hi'],2)
    scene.add(i+j+18,draw)


def town_hall(scene,i,j):
    """Limestone Gothic hall, open pointed arcade, dragon drains and Old Thomas vane."""
    def draw(s):
        # Far wall, separate arcade piers, then the upper great hall.
        block(s,i,j,9.5,2,16,STONE,windows(STONE,16,12,15,True))
        for n in range(7):
            block(s,i+n*1.52,j+3,.38,.5,13,STONE)
        block(s,i,j,9.5,3.5,19,STONE,windows(STONE,19,12,18,True),z=15)
        # Individual pointed voussoirs leave real openings between the piers.
        for n in range(6):
            ai=i+n*1.52+.38;fj=j+3.52
            left,tip,right=P(s,ai,fj,10),P(s,ai+.57,fj,15),P(s,ai+1.14,fj,10)
            seg(s,left,tip,WHITE['hi'],2);seg(s,tip,right,STONE['dark'],2)
        band(s,i,j,9.5,3.5,33,WHITE)
        # The long ridge follows i, parallel to the arcade, with stone end gables.
        t,r,b,l=corners(s,i,j,9.5,3.5,34)
        a,c=P(s,i,j+1.75,60),P(s,i+9.5,j+1.75,60)
        for pts,lit in (([t,r,c,a],False),([l,b,c,a],True)):
            poly(s,pts,lambda x,y,lit=lit:CLAY['line'] if int(y)%3==0 else
                 CLAY['hi'] if (int(x)+int(y)//3*2)%7==0 else CLAY['lit' if lit else 'dark'])
        poly(s,[r,b,c],lambda x,y:STONE['dark'] if int(y)%4 else STONE['line'])
        seg(s,a,c,CLAY['hi']);seg(s,l,b,CLAY['outline']);seg(s,b,c,STONE['hi'])
        crenellate(s,i,j+3.25,9.5,.25,35,STONE,set(),step=5,height=3)
        clock(s,i+5,j+3.55,2.5,29)
        # Tower pierces the eastern end of the roof, with open bell lantern.
        ti,tj=i+8.2,j+2.1
        block(s,ti,tj,1.75,1.75,69,STONE,windows(STONE,69,7,16,True))
        band(s,ti,tj,1.75,1.75,68,WHITE,2)
        spire(s,ti+.875,tj+.875,1.1,71,15,BRONZE,onion=True)
        for a,b in ((.4,.4),(1.25,.4),(.4,1.25),(1.25,1.25)):
            block(s,ti+a,tj+b,.13,.13,9,BRONZE,z=84)
        spire(s,ti+.875,tj+.875,.65,93,17,BRONZE,conical=True)
        # Filled Old Thomas: coat, head, hat, arm and banner.
        cylinder(s,ti+.875,tj+.875,.14,.14,112,5,GOLD)
        ellipse(s,ti+.875,tj+.875,.2,.2,118,GOLD['lit'])
        block(s,ti+.62,tj+.72,.5,.3,1,GOLD,z=119)
        seg(s,P(s,ti+.9,tj+.9,115),P(s,ti+1.4,tj+.9,116),GOLD['dark'],2)
        poly(s,[P(s,ti+1.5,tj+.9,z) for z in (115,122)]+[P(s,ti+2.2,tj+.9,120)],lambda x,y:GOLD['lit'])
        for a in (.5,7.6):
            seg(s,P(s,i+a,j+3.5,32),P(s,i+a,j+4.2,31),DARK['dark'],2)
            poly(s,[P(s,i+a+u,j+4.2+v,z) for u,v,z in ((0,0,30),(.35,0,32),(.1,.3,32))],lambda x,y:DARK['lit'])
    scene.add(i+j+16,draw)


def st_nicholas(scene,i,j):
    """Niguliste: Gothic basilica, stepped buttresses, clock tower and copper Baroque spire."""
    def draw(s):
        block(s,i,j,5,7,34,STONE,windows(STONE,34,11,24,True))
        gable_roof(s,i,j,5,7,34,24,CLAY,STONE,'point')
        for b in (.4,2.4,4.4):
            block(s,i+4.7,j+b,.65,.5,26,STONE)
            block(s,i+4.85,j+b,.4,.5,31,STONE)
        ti,tj=i+.9,j+5.1
        block(s,ti,tj,2.8,2.8,64,STONE,windows(STONE,64,11,17,True))
        for z in (2,23,47,62):band(s,ti,tj,2.8,2.8,z,WHITE)
        clock(s,ti+1.4,tj+2.85,4.5,49)
        clock(s,ti+2.85,tj+1.4,4.5,49,False)
        spire(s,ti+1.4,tj+1.4,1.8,66,23,DARK,onion=True)
        cylinder(s,ti+1.4,tj+1.4,.42,.42,84,10,DARK,windows(WHITE,10,5,9,True))
        spire(s,ti+1.4,tj+1.4,.8,94,24,DARK,conical=True)
        cross(s,ti+1.4,tj+1.4,120)
    scene.add(i+j+14,draw)


def onion(s,ci,cj,radius,base,height):
    """A full bulb mesh on an arched drum; its five silhouettes remain distinct."""
    cylinder(s,ci,cj,radius*.6,radius*.6,base,13,RED,windows(WHITE,13,7,12,True))
    profile=[(0,.55),(.12,.85),(.3,1),(.48,.92),(.69,.64),(1,.03)]
    for (z0,r0),(z1,r1) in zip(profile,profile[1:]):
        parts=[]
        for n in range(24):
            a,b=n*math.tau/24,(n+1)*math.tau/24
            pts=[P(s,ci+radius*r*math.cos(t),cj+radius*r*math.sin(t),base+13+height*z)
                 for z,r,t in ((z0,r0,a),(z0,r0,b),(z1,r1,b),(z1,r1,a))]
            lit=math.sin((a+b)/2)-.5*math.cos((a+b)/2)>0
            parts.append((math.cos(a)+math.sin(a),pts,lit))
        for _,pts,lit in sorted(parts):
            poly(s,pts,lambda x,y,lit=lit:DARK['lit' if lit else 'dark'])
            if lit:seg(s,pts[0],pts[3],DARK['mid'])
    cross(s,ci,cj,base+height+14)


def nevsky(scene,i,j,z=0):
    """Five dark onion domes, red/white Russian Revival walls, kokoshnik arches and mosaic portals."""
    def draw(s):
        # Far pair, central drum and near pair: all five bulbs have separate silhouettes.
        block(s,i+.6,j+.4,6.8,5.6,30,RED,windows(WHITE,30,11,16,True))
        hip_roof(s,i+.5,j+.3,7,5.8,30,10,DARK)
        parts=[(i+.4,j+1.8,1.03,40,19),(i+6.9,j+.8,1.03,34,19),
               (i+4,j+3,1.65,52,28),(i+.2,j+5.3,1.12,34,20),(i+7.1,j+5.3,1.12,34,20)]
        for ci,cj,r,z,h in parts:
            cylinder(s,ci,cj,r*.78,r*.78,z-8,8,WHITE,windows(WHITE,8,7,8,True))
            onion(s,ci,cj,r,z,h)
        fj=j+6.05
        # Three actual porch openings, each set in layered semicircular archivolts.
        for a in (1.2,3.5,5.8):
            block(s,i+a,fj,1.3,.6,19,WHITE,
                  lambda u,v,lit:arch_opening(u,v,5.2,3.5,9,WOOD) or RED['lit'])
            for n in range(15):
                t=n*math.pi/14
                seg(s,P(s,i+a+.65+.7*math.cos(t),fj+.62,13+7*math.sin(t)),
                    P(s,i+a+.65+.7*math.cos(t),fj+.62,14+7*math.sin(t)),WHITE['hi'],2)
            ellipse(s,i+a+.65,fj+.65,.25,.08,23,GOLD['mid'])
        for z in (3,17,28):band(s,i+.6,j+.4,6.8,5.6,z,WHITE)
        # Layered kokoshnik crowns and gold mosaic panels above each porch.
        for a in (1.2,3.5,5.8):
            points=[P(s,i+a+u,fj+.65,z) for u,z in
                    ((-.15,20),(-.15,25),(.2,27),(.65,32),(1.1,27),(1.45,25),(1.45,20))]
            poly(s,points,lambda x,y:WHITE['lit'])
            for left,right in zip(points[1:],points[2:]):seg(s,left,right,RED['dark'])
            poly(s,[P(s,i+a+u,fj+.67,z) for u,z in ((.2,22),(1.1,22),(1.1,25),(.65,29),(.2,25))],
                 lambda x,y:GOLD['lit'] if (int(x)+int(y))%3 else GOLD['dark'])
            block(s,i+a+.57,fj+.7,.16,.12,3,RED,z=23)
        for a in range(3):block(s,i+2.5,j+6.7+a*.3,3,.3,4-a,STONE)
    scene.add(i+j+18,lifted(draw,z))


def toompea(scene,i,j,z=0):
    """Pink parliamentary façade, medieval limestone curtain and flag-topped Tall Hermann."""
    def draw(s):
        block(s,i-.4,j-.4,9.8,6.5,8,STONE)
        # Northwest medieval curtain, with the pink east/front palace beyond it.
        block(s,i,j,.8,5.7,38,STONE,stone_courses(STONE,4,10),z=8)
        block(s,i,j,9,1,35,STONE,windows(STONE,35,12,16),z=8)
        block(s,i+1,j+1,8,4.5,32,PINK,windows(PINK,32,10,12),z=8)
        hip_roof(s,i+1,j+1,8,4.5,40,15,CLAY)
        for z in (10,24,39):band(s,i+1,j+1,8,4.5,z,WHITE)
        block(s,i+4,j+4.8,2.5,.8,35,PINK,windows(PINK,35,10,12),z=8)
        pediment(s,i+4,j+5.3,2.5,.35,43,9,WHITE)
        # Southwest Tall Hermann is a cylindrical keep with open crenellation.
        ci,cj=i+.5,j+5.3
        cylinder(s,ci,cj,1.25,1.25,8,69,STONE,stone_courses(STONE,4,10))
        ellipse(s,ci,cj,1.4,1.4,77,STONE['hi'])
        ellipse(s,ci,cj,1.08,1.08,77.2,STONE['deep'])
        for n in range(10):
            a=n*math.tau/10
            block(s,ci+1.2*math.cos(a)-.16,cj+1.2*math.sin(a)-.16,.32,.32,4,STONE,z=77)
        flag(s,ci,cj,81)
    scene.add(i+j+18,lifted(draw,z))


def viru_gate(scene,i,j):
    """The two surviving barbican towers: conical clay roofs and an open street between."""
    def draw(s):
        # No invented overhead gate links the two surviving round towers.
        block(s,i-.6,j+1,.65,2.6,17,STONE,stone_courses(STONE,4,10))
        block(s,i+7.7,j+1,.65,2.6,17,STONE,stone_courses(STONE,4,10))
        for a,b in ((i+1,j+2.4),(i+6.6,j+2.4)):
            round_tower(s,a,b,1.15,35)
            # Projected door at the foot of the lit face.
            poly(s,[P(s,a+u,b+1.05,z) for u,z in ((-.22,0),(.22,0),(.22,7),(0,10),(-.22,7))],lambda x,y:WOOD)
    scene.add(i+j+14,draw)


# name, builder, footprint, real longitude/latitude, compressed north-up ground anchor, elevation
# (the Toompea plateau stands above the Lower Town).
SITES = [
    ('fat-margaret', fat_margaret, (8,8), (24.74955,59.44253), (595,112), 0),
    ('st-olaf', st_olaf, (5.2,8.5), (24.747806,59.441417), (505,220), 0),
    ('kadriorg', kadriorg, (11,6.5), (24.79084,59.43851), (635,287), 0),
    ('town-hall', town_hall, (10,4), (24.7454694,59.4370917), (450,355), 0),
    ('viru-gate', viru_gate, (8.5,4), (24.7503639,59.4366306), (610,395), 0),
    ('st-nicholas', st_nicholas, (5,8), (24.74263,59.43598), (340,425), 0),
    ('nevsky', nevsky, (8,7.5), (24.739361,59.435833), (203,456), 24),
    ('toompea', toompea, (9.5,6.5), (24.7372,59.4356), (82,480), 24),
]


def main():
    for name,builder,_,_,_,_ in SITES:
        print(preview([lambda s,b=builder:b(s,4,4)],'tallinn-'+name,
                      size=(240,230),origin=(110,110),tiles=17))
    print(preview([lambda s,n=n:townhouse(s,3+n*3,3,2.5,3,2+n%2,n) for n in range(5)],
                  'tallinn-houses',size=(260,220),origin=(70,65),tiles=21))
    import sprites
    from pathlib import Path
    sprite=sprites.kuressaare()
    path=Path(__file__).resolve().parents[2]/'docs/art/capitals/estonia-kuressaare.png'
    sprite.resize((sprite.width*4,sprite.height*4),0).save(path)
    print(path)


if __name__=='__main__':main()
