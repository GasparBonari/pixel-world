"""Sofia's Byzantine brick, gilded domes and ceramic Secession in projected (i,j,z).

Two-source facts, explicit facade turns and the north-up layout: DEVELOPMENT_PLAN.md, Phase 4.
Run directly for seven isolated native-pixel studies enlarged exactly 4×, plus Sofia houses.
"""
import math
from pathlib import Path

from iso import rgb
from landmarks_paris import P, seg, poly, corners, preview, GLASS
from landmarks_iberia import hip_roof, stone_courses, arch_opening, palette_of, tones
from landmarks_slovakia import block, band, pediment
from landmarks_bosnia import cylinder
from landmarks_slovenia import revolve, DOME, balustrade
from landmarks_greece import column, figure

IVORY = tones('#FFFBE9', '#EEE1C2', '#D8C7A5', '#B7A17F', '#846E50', '#C7B18C', '#504332')
WHITE = tones('#FFFFF2', '#F5EDD9', '#DED4BF', '#BFB29A', '#8C7E66', '#D0C1A8', '#554A39')
BRICK = tones('#E5A07A', '#BD7456', '#A55C44', '#804532', '#5A3025', '#C78C6B', '#482A23')
RED = tones('#E7AC8D', '#B9664D', '#A3533F', '#7C3A30', '#542A24', '#954836', '#45271F')
OCHRE = tones('#FFF0B8', '#EDD18B', '#D5B36B', '#AF8C4B', '#7D6134', '#C39F58', '#544126')
CLAY = tones('#E8AB7A', '#CA8555', '#B06A42', '#8A4E32', '#603523', '#9E5C3A', '#4E2D21')
GREEN = tones('#B2D8A7', '#7CAD89', '#5E9476', '#3D6B58', '#2B4B3D', '#527C60', '#253D32')
LEAD = tones('#BDC3BA', '#929F99', '#778782', '#576A67', '#3C4B4A', '#697B75', '#2C3939')
GOLD = tones('#FFF4B4', '#ECCC6D', '#CCA84C', '#A17B31', '#72551E', '#B79038', '#584225')
BRONZE = tones('#B9BB9A', '#7B846C', '#64715C', '#425342', '#2E3C30', '#56674F', '#253127')
CERAMIC = tones('#C2E1CD', '#80B7A2', '#5F9986', '#3D7568', '#285349', '#4E897A', '#263F35')
ROCK = tones('#D8CBB0', '#B9A88B', '#A08F72', '#817056', '#5B4E3A', '#927D5E', '#433B2E')
WALLS = [rgb(c) for c in ('#E8D3A5', '#E6B6A0', '#C6CFB3', '#ECDCC2', '#D2BDCF', '#B9CCCE')]
IRON, WOOD = rgb('#35423D'), rgb('#705039')
GROUND = {k:rgb(v) for k,v in {
    'yellow':'#DAC17A', 'yellow_hi':'#E9D493', 'yellow_joint':'#B29A5E',
    'square':'#DDD2B9', 'joint':'#B9AB91', 'rose':'#CDB59E',
    'cobble':'#BCAF96', 'cobble_joint':'#94856D',
    'garden':'#92A873', 'garden_hi':'#AFBF89', 'earth':'#A68E69',
}.items()}
ONION = [(0,.72),(.12,.97),(.34,1),(.55,.8),(.75,.45),(.9,.18),(1,.03)]


def windows(material, height, bay=11, floor=14, arched=False):
    """Dressed divided glass, lintels/sills and restrained masonry courses in local wall space."""
    joints = stone_courses(material, 4, 13)
    def pattern(u,v,lit):
        c,k=int(u)%bay,int(v)%floor
        trim=WHITE['lit' if lit else 'dark']
        if arched:
            # Narrow round-headed stone/brick church openings; no domestic blue window grid.
            centre=bay/2
            if 3<=k and v<height-2:
                outer=arch_opening(c,k-3,centre,2.7,floor-9,trim)
                inner=arch_opening(c,k-4,centre,1.7,floor-10,IRON)
                if inner:return inner if k%7 else IVORY['dark']
                if outer:return outer
        elif 3<=c<=bay-3 and 3<=k<=floor-4 and v<height-3:
            if c in (3,bay-3,bay//2) or k in (3,6,floor-4):return trim
            return GLASS['mid' if lit else 'dark']
        if k==2 and 2<=c<=bay-2:return WHITE['hi' if lit else 'mid']
        if int(v) in (1,height-2):return trim
        return joints(u,v,lit) if material in (BRICK,IVORY,ROCK) else None
    return pattern


def cross(s,i,j,z,size=7):
    seg(s,P(s,i,j,z),P(s,i,j,z+size),GOLD['dark'])
    seg(s,P(s,i-.24,j,z+size*.68),P(s,i+.24,j,z+size*.68),GOLD['hi'])
    seg(s,P(s,i-.13,j,z+size*.85),P(s,i+.13,j,z+size*.85),GOLD['lit'])


def drum(s,ci,cj,r,z,height,material=IVORY,bay=10):
    def openings(u,v,lit):
        c=int(u)%bay
        if 4<v<height-3:
            a=arch_opening(c,v-4,bay/2,2,height-10,WHITE['mid' if lit else 'line'])
            b=arch_opening(c,v-5,bay/2,1,height-11,GLASS['dark'])
            if b:return b
            if a:return a
        return stone_courses(material,4,13)(u,v,lit)
    # Paint the base collar BEFORE the shaft: its horizontal cap must not cover the windows.
    cylinder(s,ci,cj,r+.08,r+.08,z,2,WHITE,segments=32)
    cylinder(s,ci,cj,r,r,z,height,material,openings,segments=32)
    for zz,rr in ((height-2,r+.13),(height,r+.2)):
        cylinder(s,ci,cj,rr,rr,z+zz,2,WHITE,segments=32)


def portrait(s,ci,cj,z,r=3):
    """Small bounded gold mosaic with solid head/robe tesserae in the facade's own plane."""
    pts=[P(s,ci+math.cos(t*math.tau/24)*r/8,cj,z+math.sin(t*math.tau/24)*r) for t in range(24)]
    poly(s,pts,lambda x,y:GOLD['lit'] if (x+y)%3 else GOLD['dark'])
    for a,b in zip(pts,pts[1:]+pts[:1]):seg(s,a,b,GOLD['outline'])
    x,y=P(s,ci,cj,z)
    for dx,dy in ((0,-1),(0,0),(-1,1),(0,1),(1,1),(0,2)):
        s.put(x+dx,y+dy,IVORY['hi'] if dx<1 else RED['dark'])


def gable_roof(s,i,j,w,d,z,rise,material=BRICK,roof=CLAY):
    """Plain basilica gable with actual extruded brick end, not a classical pediment."""
    a,b=P(s,i+w/2,j,z+rise),P(s,i+w/2,j+d,z+rise)
    T,R,B,L=corners(s,i,j,w,d,z)
    for pts,lit in (([T,a,b,L],True),([a,R,B,b],False)):
        poly(s,pts,lambda x,y,lit=lit:roof['line'] if y%3==0 else roof['lit' if lit else 'dark'])
    pts=[L,B,b]
    poly(s,pts,lambda x,y:material['line'] if y%3==0 else material['lit'])
    for p,q in ((L,b),(b,B),(a,b)):seg(s,p,q,roof['hi'])


def nevsky(scene,i,j,z=8):
    """Two gold crowns, cascading copper apses, south/north entrance domes, western belfry."""
    w,d=9.2,12.5
    def draw(s):
        # Apse/aisles, with their own ribbed green roofs, before the higher crossing.
        block(s,i+.5,j+.3,w-1,d-1,24,IVORY,windows(IVORY,24,12,18,True),z=z)
        for a,b,r,h in ((i+4.6,j+1.9,2.6,27),(i+2.0,j+5.8,2.2,29),(i+7.2,j+5.8,2.2,29)):
            drum(s,a,b,r,z+14,14)
            revolve(s,a,b,r+.2,z+h,17,DOME,GREEN,ribs=4,segments=32)
        # Lower side entrance domes are north/south; both remain below the great gold dome.
        for a,b in ((i+.35,j+7.2),(i+8.85,j+7.2)):
            block(s,a-.7,b-.75,1.4,1.5,26,IVORY,windows(IVORY,26,10,17,True),z=z)
            drum(s,a,b,.82,z+26,6)
            revolve(s,a,b,.97,z+32,9,DOME,GREEN,ribs=3)
            cross(s,a,b,z+41,4)
        ci,cj=i+4.6,j+5.7
        block(s,i+2,j+3.1,5.2,5.2,35,IVORY,windows(IVORY,35,13,20,True),z=z)
        band(s,i+2,j+3.1,5.2,5.2,z+34,WHITE,3)
        drum(s,ci,cj,2.65,z+36,15)
        revolve(s,ci,cj,2.95,z+51,18,DOME,GOLD,ribs=3,segments=48)
        cross(s,ci,cj,z+69,7)
        # Visible southern transept: rounded window gallery and copper half-dome in front
        # of the crossing, as in the actual cascading silhouette, not buried under its walls.
        a,b=i+8.25,j+5.4
        drum(s,a,b,2.05,z+15,19,IVORY,11)
        revolve(s,a,b,2.3,z+34,15,DOME,GREEN,ribs=3,segments=32)
        hip_roof(s,i+1.8,j+7.0,5.6,3.6,z+29,10,GREEN)
        # West narthex and taller western bell tower: snapped W to SW (+j).
        block(s,i+1.5,j+8.4,6.2,3.9,27,IVORY,windows(IVORY,27,11,17,True),z=z)
        hip_roof(s,i+1.4,j+8.3,6.4,4.1,z+27,9,GREEN)
        def front(u,v,lit):
            c=int(u)%12
            if lit and v<20:
                a=arch_opening(c,v,6,3,13,WHITE['mid'])
                b=arch_opening(c,v,6,2,12,WOOD)
                if b:return b
                if a:return a
            return stone_courses(IVORY,4,14)(u,v,lit)
        block(s,i+2.3,j+11,4.6,1.45,27,IVORY,front,z=z)
        for n in range(3):block(s,i+2.1-n*.15,j+12.5+n*.25,4.9+n*.3,.3,3-n,WHITE,z=z)
        ci,cj=i+4.6,j+10.0
        block(s,ci-1.45,cj-1.45,2.9,2.9,43,IVORY,windows(IVORY,43,11,16,True),z=z)
        for zz in (25,39,43):band(s,ci-1.45,cj-1.45,2.9,2.9,z+zz,WHITE,2)
        # Open bell chamber: four corner piers, lintels, hanging bronze bells.
        for a,b in ((ci-1,cj-1),(ci+1,cj-1),(ci-1,cj+1),(ci+1,cj+1)):
            column(s,a,b,z+45,16,.2,WHITE)
        for a,b in ((ci-.55,cj+.85),(ci+.55,cj+.85)):
            seg(s,P(s,a,b,z+61),P(s,a,b,z+55),IRON)
            revolve(s,a,b,.28,z+51,5,[(0,1),(.6,.5),(1,.3)],GOLD,ribs=0)
        block(s,ci-1.45,cj-1.45,2.9,2.9,3,WHITE,z=z+61)
        drum(s,ci,cj,1.55,z+64,5)
        revolve(s,ci,cj,1.8,z+69,14,DOME,GOLD,ribs=3,segments=32)
        cross(s,ci,cj,z+83,7)
        portrait(s,ci,cj+1.48,z+34,4)
    scene.add(i+j+w+d+3,draw)


def sophia(scene,i,j,z=8):
    """Long brick basilica, lower side aisles, stepped crossing and clay gables; no modern towers."""
    w,d=5.8,11.4
    def draw(s):
        # Eastern apse is NE/back, western narthex on visible SW side.
        cylinder(s,i+w/2,j+1,1.9,1.4,z,21,BRICK,windows(BRICK,21,11,16,True),segments=24)
        revolve(s,i+w/2,j+1,2,z+21,7,DOME,CLAY,ribs=0)
        block(s,i,j+1,w,d-1,20,BRICK,windows(BRICK,20,13,17,True),z=z)
        gable_roof(s,i-.05,j+.95,w+.1,d-.9,z+20,7)
        block(s,i+1.25,j+.8,w-2.5,d-1,34,BRICK,windows(BRICK,34,13,20,True),z=z)
        gable_roof(s,i+1.2,j+.75,w-2.4,d-.9,z+34,9)
        # Broad crossing shoulders, deliberately lower than the nave's main ridge.
        block(s,i-.6,j+3.8,w+1.2,3.2,29,BRICK,windows(BRICK,29,12,19,True),z=z)
        hip_roof(s,i-.65,j+3.75,w+1.3,3.3,z+29,7,CLAY)
        block(s,i+1.2,j+3.6,w-2.4,3.5,36,BRICK,windows(BRICK,36,12,28,True),z=z)
        gable_roof(s,i+1.15,j+3.55,w-2.3,3.6,z+36,9)
        def entrance(u,v,lit):
            if lit:
                # Three west portals correspond to the basilica's three-bay narthex.
                for centre in (8.5,w*4,w*8-8.5):
                    a=arch_opening(u,v,centre,3.2,12,IVORY['mid'])
                    b=arch_opening(u,v,centre,2.1,11,WOOD)
                    if b:return b
                    if a:return a
                return stone_courses(BRICK,3,11)(u,v,lit)
            return windows(BRICK,21,12,17,True)(u,v,lit)
        block(s,i,j+d-.7,w,.8,21,BRICK,entrance,z=z)
        gable_roof(s,i-.05,j+d-.75,w+.1,.9,z+21,8)
        for k in range(3):block(s,i+1.6-k*.1,j+d+.25+k*.23,2.6+k*.2,.3,3-k,ROCK,z=z)
    scene.add(i+j+w+d+2,draw)


def russian(scene,i,j,z=0):
    """Five gilded onion domes, tall green tent, ceramic kokoshniks and south porch."""
    w,d=6.5,7.2
    def draw(s):
        block(s,i+.3,j+.5,w-.6,d-1,31,WHITE,windows(WHITE,31,12,18,True),z=z)
        for zz in (1,24,30):band(s,i+.3,j+.5,w-.6,d-1,z+zz,IVORY,2)
        hip_roof(s,i+.2,j+.4,w-.4,d-.8,z+32,8,GREEN)
        ci,cj=i+w/2,j+3.4
        # Rear corner bulbs first; front pair after the central tower.
        def bulb(a,b,base,r=.72,rise=10):
            drum(s,a,b,r*.65,z+base,8,WHITE,8)
            revolve(s,a,b,r,z+base+8,rise,ONION,GOLD,ribs=3,segments=24)
            cross(s,a,b,z+base+8+rise,6)
        for a,b in ((i+.7,j+1.1),(i+w-.7,j+1.1)):bulb(a,b,34)
        drum(s,ci,cj,1.6,z+33,18,WHITE,12)
        # Tall tiled tent tapers to a narrow white lantern below central onion dome.
        revolve(s,ci,cj,1.9,z+51,27,[(0,1),(1,.35)],GREEN,ribs=3,segments=24)
        drum(s,ci,cj,.65,z+78,8,WHITE,8)
        revolve(s,ci,cj,1.05,z+86,13,ONION,GOLD,ribs=3,segments=32)
        cross(s,ci,cj,z+99,7)
        for a,b in ((i+.7,j+5.7),(i+w-.7,j+5.7)):bulb(a,b,34)
        # Ceramic scalloped gables along visible eaves, each a real extruded arch.
        for a in (i+.65,i+2.2,i+3.75,i+5.3):
            pediment(s,a,j+6.05,1.3,.25,z+31,5,WHITE)
            portrait(s,a+.65,j+6.32,z+33,1.5)
        block(s,i+1.5,j+6.25,3.5,1.6,20,WHITE,
              lambda u,v,lit:WOOD if lit and 8<u<20 and v<15 else windows(WHITE,20,10,16,True)(u,v,lit),z=z)
        hip_roof(s,i+1.35,j+6.1,3.8,1.9,z+21,9,GREEN)
        band(s,i+1.4,j+6.2,3.7,1.7,z+19,GOLD,1)
        portrait(s,i+3.25,j+7.87,z+19,2.6)
        for k in range(4):block(s,i+1.6-k*.1,j+7.9+k*.25,3.3+k*.2,.3,4-k,IVORY,z=z)
    scene.add(i+j+w+d+4,draw)


def baths(scene,i,j,z=0):
    """Low ceramic-striped Secession wings, arched bays, curving central/corner pavilion roofs."""
    w,d=13.5,5.8
    def ceramic(u,v,lit):
        c=int(u)%12
        if 21<v<26:
            if (c-6)**2+(int(v)-23)**2<5:return CERAMIC['lit' if lit else 'dark']
            return OCHRE['lit' if lit else 'dark'] if c%3 else RED['mid']
        if int(v)%7 in (0,1):return RED['lit' if lit else 'dark']
        return windows(OCHRE,28,12,21,True)(u,v,lit)
    def draw(s):
        block(s,i,j,w,d,27,OCHRE,ceramic,z=z)
        band(s,i,j,w,d,z+1,ROCK,3)
        band(s,i,j,w,d,z+27,IVORY,2)
        hip_roof(s,i-.1,j-.1,w+.2,d+.2,z+29,9,CLAY)
        # Projecting low end pavilions and taller central entry, all roofed in curved green metal.
        for a,ww,hh in ((i,2.7,32),(i+5.05,3.4,39),(i+w-2.7,2.7,32)):
            block(s,a,j+2.6,ww,3.7,hh,OCHRE,ceramic,z=z)
            for zz in (4,hh-4,hh):band(s,a,j+2.6,ww,3.7,z+zz,IVORY,1)
            # Rounded oval pavilion caps follow a three-dimensional Secession roof profile.
            ci,cj=a+ww/2,j+4.45
            profile=[(0,1),(.16,.99),(.4,.9),(.65,.68),(.85,.35),(1,.08)]
            faces=[]
            for (t,r),(tt,rr) in zip(profile,profile[1:]):
                for n in range(32):
                    aa,bb=n*math.tau/32,(n+1)*math.tau/32
                    pts=[P(s,ci+ww*.55*rad*math.cos(ang),cj+2.05*rad*math.sin(ang),z+hh+1+level*14)
                         for level,rad,ang in ((t,r,aa),(t,r,bb),(tt,rr,bb),(tt,rr,aa))]
                    lit=math.sin((aa+bb)/2)-.5*math.cos((aa+bb)/2)>0
                    faces.append((math.cos(aa)+math.sin(aa)+math.cos(bb)+math.sin(bb),n,pts,lit))
            for _,n,pts,lit in sorted(faces,key=lambda f:(f[0],f[1])):
                poly(s,pts,lambda x,y,lit=lit:GREEN['line'] if y%5==0 else GREEN['lit' if lit else 'dark'])
                if n%4==0:seg(s,pts[0],pts[3],GREEN['hi' if lit else 'deep'])
        # Ceramic portrait panels flank the central arched doorway on its lit front only.
        for a in (i+5.35,i+8.1):portrait(s,a,j+6.34,z+22,2.4)
        centre=i+6.75
        block(s,centre-.6,j+6.32,1.2,.12,16,IVORY,
              lambda u,v,lit:WOOD if 1<u<9 and v<13 else None,z=z)
        # Round arched entrance crown, extruded 0.35 tiles with concentric ceramic bands.
        for n in range(20):
            aa,bb=n*math.pi/20,(n+1)*math.pi/20
            x0,x1=centre+1.5*math.cos(aa),centre+1.5*math.cos(bb)
            h0,h1=z+31+9*math.sin(aa),z+31+9*math.sin(bb)
            front=[P(s,x0,j+6.66,z+30),P(s,x1,j+6.66,z+30),P(s,x1,j+6.66,h1),P(s,x0,j+6.66,h0)]
            poly(s,front,lambda x,y:OCHRE['lit'])
            poly(s,[front[3],front[2],P(s,x1,j+6.31,h1),P(s,x0,j+6.31,h0)],lambda x,y:IVORY['dark'])
            seg(s,front[3],front[2],IVORY['hi'],2)
            seg(s,P(s,x0,j+6.68,h0-3),P(s,x1,j+6.68,h1-3),CERAMIC['dark'])
        for k in range(3):block(s,centre-1.25-k*.12,j+6.7+k*.24,2.5+k*.24,.3,3-k,IVORY,z=z)
    scene.add(i+j+w+d+4,draw)


def mosque(scene,i,j,z=0):
    """One broad lead dome, western single-balcony minaret, three small NW porch domes."""
    w,d=6,6
    def masonry(u,v,lit):
        if int(v)%8 in (0,1):return BRICK['lit' if lit else 'dark']
        return windows(IVORY,31,13,21,True)(u,v,lit)
    def draw(s):
        # NW entrance lies on hidden -i. Three porch roofs project west of the prayer hall.
        for k in range(3):
            a,b=i-.7,j+.9+k*1.8
            column(s,a-.55,b,z,14,.15,WHITE)
            block(s,a-.65,b-.75,1.3,1.5,3,IVORY,z=z+14)
            revolve(s,a,b,.86,z+17,6,DOME,LEAD,ribs=0)
        block(s,i,j,w,d,30,IVORY,masonry,z=z)
        band(s,i,j,w,d,z+29,WHITE,2)
        drum(s,i+3,j+3,2.8,z+31,7,IVORY,12)
        revolve(s,i+3,j+3,3.15,z+38,21,DOME,LEAD,ribs=4,segments=40)
        seg(s,P(s,i+3,j+3,z+59),P(s,i+3,j+3,z+65),GOLD['dark'])
        # Crescent is a tiny crescent-shaped volume, not a cross.
        x,y=P(s,i+3,j+3,z+65)
        for dx,dy in ((0,-2),(-1,-1),(-1,0),(0,1),(1,1)):s.put(x+dx,y+dy,GOLD['lit'])
        # Western corner: -i,+j. Octagonal brick shaft, one corbelled gallery, lead cone.
        a,b=i-.6,j+5.8
        block(s,a-.5,b-.5,1,1,11,IVORY,stone_courses(IVORY,4,8),z=z)
        cylinder(s,a,b,.42,.42,z+11,47,BRICK,stone_courses(BRICK,3,8),segments=12)
        for zz,r in ((54,.48),(56,.59),(58,.76)):
            cylinder(s,a,b,r,r,z+zz,2,IVORY,segments=16)
        for n in range(12):
            ang=n*math.tau/12
            seg(s,P(s,a+.7*math.cos(ang),b+.7*math.sin(ang),z+60),
                P(s,a+.7*math.cos(ang),b+.7*math.sin(ang),z+64),IRON)
        cylinder(s,a,b,.32,.32,z+60,13,IVORY,segments=12)
        revolve(s,a,b,.53,z+73,16,[(0,1),(1,.03)],LEAD,ribs=3,segments=16)
        seg(s,P(s,a,b,z+89),P(s,a,b,z+94),GOLD['dark'])
    scene.add(i+j+w+d+3,draw)


def rotunda(scene,i,j,z=-6):
    """Red-brick rotunda, low tiled cone, cruciform shoulders and excavated Serdica walls."""
    w,d=7,7
    def draw(s):
        # Low ruin courses sit on the excavated courtyard floor, not on street level.
        for a,b,ww,dd in ((i-.7,j+5.3,2.3,.35),(i+4.7,j+6.4,2.5,.4),(i+6.4,j+4.2,.4,2.6)):
            block(s,a,b,ww,dd,3,BRICK,stone_courses(BRICK,2,7),z=z)
        block(s,i+.5,j+.5,6,6,18,BRICK,windows(BRICK,18,13,15,True),z=z)
        hip_roof(s,i+.45,j+.45,6.1,6.1,z+18,5,CLAY)
        ci,cj=i+3.5,j+3.5
        cylinder(s,ci,cj,2.65,2.65,z,27,BRICK,windows(BRICK,27,14,21,True),segments=40)
        cylinder(s,ci,cj,2.35,2.35,z+25,17,BRICK,windows(BRICK,17,15,15,True),segments=40)
        cylinder(s,ci,cj,2.5,2.5,z+42,1,CLAY,segments=40)
        revolve(s,ci,cj,2.7,z+43,10,[(0,1),(1,.03)],CLAY,ribs=3,segments=40)
        # Western rectangular vestibule, with a real recessed doorway, snapped SW.
        block(s,i+2.4,j+5.45,2.2,1.35,17,BRICK,
              lambda u,v,lit:WOOD if lit and arch_opening(u,v,8.8,2.2,10,WOOD) else
              stone_courses(BRICK,3,10)(u,v,lit),z=z)
        hip_roof(s,i+2.3,j+5.35,2.4,1.55,z+17,5,CLAY)
    scene.add(i+j+w+d+3,draw)


def theatre(scene,i,j,z=0):
    """Six-column white portico, Apollo/Muses pediment, paired red chariot-topped towers."""
    w,d=12.6,6.1
    def chariot(s,a,b,zz):
        # Solid two-horse group and broad standing figure, with wheels and raised arm.
        for off in (-.3,.3):
            cylinder(s,a+off,b,.14,.14,zz+1,2,BRONZE,segments=12)
            block(s,a+off-.16,b-.2,.32,.7,2,BRONZE,z=zz+3)
            block(s,a+off-.13,b-.42,.24,.25,3,BRONZE,z=zz+4)
            for dj in (-.14,.3):block(s,a+off-.1,b+dj,.12,.12,3,BRONZE,z=zz)
        block(s,a-.4,b+.45,.8,.55,3,BRONZE,z=zz+2)
        figure(s,a,b+.6,zz+5,BRONZE,height=9)
        poly(s,[P(s,a-.1,b+.6,zz+11),P(s,a+.45,b+.55,zz+14),P(s,a+.55,b+.55,zz+13),P(s,a+.1,b+.6,zz+9)],lambda x,y:BRONZE['lit'])
    def draw(s):
        block(s,i,j,w,d,38,RED,windows(RED,38,12,16,True),z=z)
        for zz in (2,17,36,38):band(s,i,j,w,d,z+zz,WHITE,2)
        hip_roof(s,i-.1,j-.1,w+.2,d+.2,z+40,7,LEAD)
        # Symmetric roof towers, each with moulded corner dressings and curved dark cap.
        for a in (i+.25,i+w-2.8):
            block(s,a,j+2.3,2.55,2.55,55,RED,windows(RED,55,10,15,True),z=z)
            for zz in (37,48,54):band(s,a,j+2.3,2.55,2.55,z+zz,WHITE,2)
            for aa in (a,a+2.3):block(s,aa,j+4.8,.22,.2,15,WHITE,z=z+38)
            hip_roof(s,a-.1,j+2.2,2.75,2.75,z+57,6,LEAD)
            chariot(s,a+1.27,j+3.6,z+63)
        # Recessed entry wall remains behind the open colonnade.
        block(s,i+3.1,j+5.7,6.4,.6,33,RED,
              lambda u,v,lit:WOOD if lit and int(u)%16 in range(4,13) and v<23 else windows(RED,33,16,18,True)(u,v,lit),z=z)
        for k in range(6):column(s,i+3.15+k*1.26,j+7,z+4,34,.3,WHITE,'ionic')
        block(s,i+2.7,j+6.5,7.2,1.2,5,WHITE,z=z+38)
        pediment(s,i+2.55,j+5.95,7.5,1.85,z+44,13,WHITE)
        # The relief stays in its own triangular tympanum; seven full small draped volumes.
        for k in range(7):
            height=4+max(0,3-abs(k-3))*1.4
            figure(s,i+3.4+k*.95,j+7.82,z+45,GOLD,height=height)
        for n in range(4):block(s,i+2.7-n*.16,j+7.2+n*.26,7.2+n*.32,.3,4-n,WHITE,z=z)
        balustrade(s,(i+.2,j+6.12),(i+2.6,j+6.12),z+40,3,WHITE,3)
        balustrade(s,(i+10,j+6.12),(i+12.4,j+6.12),z+40,3,WHITE,3)
    scene.add(i+j+w+d+5,draw)


def townhouse(scene,i,j,wi=2.5,wj=3,floors=2,seed=0,z=0):
    """Sofia plaster townhouses: ceramic eave friezes, oriel bays, iron balconies and clay hips."""
    material=palette_of(WALLS[seed%len(WALLS)]);h=floors*12+3
    dressed=windows(material,h,10,12)
    def pattern(u,v,lit):
        c=int(u)%10
        if v<10:
            if 3<=c<=7:return WOOD if seed%2 else GLASS['dark']
            if c in (2,8):return WHITE['lit' if lit else 'dark']
        if h-6<v<h-3:return CERAMIC['lit' if lit else 'dark'] if c in (2,5,8) else OCHRE['lit' if lit else 'dark']
        return dressed(u,v,lit)
    def draw(s):
        block(s,i,j,wi,wj,h,material,pattern,z=z)
        band(s,i,j,wi,wj,z,ROCK,3)
        band(s,i,j,wi,wj,z+h-1,WHITE,2)
        if floors>1:
            if seed%3==0:
                block(s,i+.55,j+wj-.1,1.4,.55,11,material,windows(material,11,9,11),z=z+13)
                band(s,i+.55,j+wj-.1,1.4,.55,z+24,WHITE,1)
            else:
                block(s,i+.4,j+wj,1.7,.65,1.5,WHITE,z=z+13)
                for a in (i+.4,i+1.9):block(s,a,j+wj,.15,.45,3,IVORY,z=z+10)
                for k in range(9):seg(s,P(s,i+.4+k*.2,j+wj+.65,z+15),P(s,i+.4+k*.2,j+wj+.65,z+20),IRON)
                seg(s,P(s,i+.4,j+wj+.65,z+20),P(s,i+2.05,j+wj+.65,z+20),IRON)
        hip_roof(s,i-.16,j-.16,wi+.32,wj+.32,z+h+2,8+seed%3,CLAY)
        block(s,i+wi-.6,j+.5,.4,.45,7,IVORY,stone_courses(IVORY,3,7),z=z+h+5)
        band(s,i+wi-.6,j+.5,.4,.45,z+h+12,CLAY,2)
    scene.add(i+j+wi+wj+2,draw)


def main():
    for name,builder,_,_,_,z in SITES:
        print(preview([lambda s,b=builder,z=z:b(s,7,7,z=z)],'sofia-'+name,
                      size=(340,285),origin=(170,110),tiles=29))
    print(preview([lambda s,k=k:townhouse(s,3+k*3.6,4,floors=1+k%3,seed=k)
                   for k in range(6)],'sofia-houses',size=(340,240),origin=(80,75),tiles=27))
    import sprites
    im=sprites.rila();path=Path(__file__).resolve().parents[2]/'docs/art/capitals/bulgaria-rila.png'
    im.resize((im.width*4,im.height*4),0).save(path);print(path)


# name, builder, footprint, independently verified lon/lat, north-up scene anchor, ground elevation.
SITES = [
    ('mosque',mosque,(6,6),(23.3225614,42.6995055),(100,115),0),
    ('baths',baths,(13.5,5.8),(23.3238787,42.6992879),(280,155),0),
    ('rotunda',rotunda,(7,7),(23.3228560,42.6969088),(150,255),-6),
    ('sophia',sophia,(5.8,11.4),(23.3314339,42.6965492),(480,270),8),
    ('nevsky',nevsky,(9.2,12.5),(23.3327954,42.6958183),(605,395),8),
    ('russian',russian,(6.5,7.2),(23.3289372,42.6956956),(405,410),0),
    ('theatre',theatre,(12.6,6.1),(23.3265503,42.6941792),(285,462),0),
]


if __name__=='__main__':
    main()
