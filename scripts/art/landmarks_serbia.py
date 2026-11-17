"""Belgrade's confluence city in true (i, j, z): six researched landmark studies.

Two-source coordinates, compass/front decisions and setting: DEVELOPMENT_PLAN.md, Phase 4.
Run this file for isolated 4× studies; SITES is the source of the integrated scene's placements.
"""
import math
from pathlib import Path

import iso
from iso import rgb, h01
from landmarks_paris import P, seg, poly, corners, preview, GLASS
from landmarks_iberia import hip_roof, stone_courses, arch_opening, palette_of, tones
from landmarks_italy import ellipse
from landmarks_bosnia import cylinder
from landmarks_slovakia import block, band, pediment
from landmarks_slovenia import windows, revolve, slab, DOME, HELMET, balustrade, lamp
from landmarks_denmark import clock

STONE = tones('#F3EBDD', '#DCCEB6', '#C8B89C', '#AA9679', '#786A54', '#B8A58A', '#493E30')
WHITE = tones('#FFFCF2', '#F0EADD', '#DBD4C6', '#BDB7A9', '#898476', '#CBC2B2', '#524D41')
RED = tones('#E6A18C', '#C7745D', '#AD5E49', '#884636', '#603226', '#9D513D', '#45271F')
CLAY = tones('#DEA57C', '#B67C55', '#9B6241', '#77492F', '#533323', '#895439', '#412B20')
COPPER = tones('#B6D8C1', '#86B59C', '#6D9D83', '#4D7765', '#345345', '#5D8B76', '#263E34')
DARK_ROOF = tones('#A5B6A8', '#788F7F', '#617666', '#465C50', '#304238', '#566D5E', '#25372D')
SLATE = tones('#B2B8BB', '#8A949A', '#717E86', '#53616D', '#394954', '#65717B', '#29353E')
BRONZE = tones('#ACC0A0', '#7F9C80', '#63846A', '#46614F', '#2C4538', '#58795F', '#20372C')
GOLD = tones('#FFF0B0', '#E1C367', '#C4A04D', '#97732D', '#6A5125', '#B18C3B', '#4D3B1F')
ROCK = tones('#D1C8B2', '#AFA38A', '#95896F', '#756C56', '#554E3F', '#897D65', '#3C372D')
GRANITE = tones('#D9B7A9', '#BC8F80', '#A4796A', '#825C50', '#5B4038', '#92685A', '#432F29')
WOOD = rgb('#684732')
IRON = rgb('#343D3D')
WALLS = [rgb(c) for c in ('#D9C4A0', '#E5D9BE', '#C7CFBD', '#D3ACA0', '#BDC9CD', '#CBB894')]
WATER = tuple(rgb(c) for c in ('#537F88', '#3C6574', '#B6D6D2'))
GROUND = {k: rgb(v) for k, v in {
    'square': '#D6CBB7', 'joint': '#BAAF98', 'cobble': '#B5AA98', 'cobble_joint': '#978D7D',
    'garden': '#91AC66', 'garden_light': '#B2C582', 'flower': '#C9817F',
}.items()}


def cross(s, i, j, z, size=7):
    seg(s, P(s, i, j, z), P(s, i, j, z+size), GOLD['dark'], 2)
    seg(s, P(s, i-.24, j, z+size*.66), P(s, i+.24, j, z+size*.66), GOLD['hi'])


def victor(scene, i, j, z=0):
    """Upper Town's western artillery rampart and Victor: Doric column, nude bronze man,
    falcon in left hand and lowered sword in right, facing west/north-west."""
    W, D = 9, 7
    def draw(s):
        # The west rampart is low and broad, without an invented fairytale castle's towers.
        block(s, i, j, W, D, 4, ROCK, stone_courses(ROCK, 3, 9), z=z)
        poly(s, list(corners(s, i+.25, j+.25, W-.5, D-.5, z+4)),
             lambda x, y: GROUND['square'] if (x+2*y) % 9 else GROUND['joint'])
        for a, b, w, d in ((i, j+D-.7, W, .7), (i, j, .65, D)):
            block(s, a, b, w, d, 6, ROCK, stone_courses(ROCK, 3, 9), z=z+4)
            band(s, a, b, w, d, z+9, STONE)
        ci, cj = i+4, j+3.2
        for w, h, zz in ((2.2, 2, 4), (1.8, 3, 6), (1.25, 5, 9)):
            block(s, ci-w/2, cj-w/2, w, w, h, STONE, z=z+zz)
        cylinder(s, ci, cj, .56, .56, z+14, 34, STONE,
                 lambda u, v, lit: STONE['line' if lit else 'deep'] if int(u) % 3 == 0 else None)
        for base, r, h in ((14, .67, 2), (46, .7, 2), (48, .85, 2)):
            cylinder(s, ci, cj, r, r, z+base, h, STONE)
        # Sculpted, dimensional limbs and torso, rather than a post topped by an antenna.
        foot = z+50
        for a, b in ((ci-.23, cj+.05), (ci+.18, cj-.05)):
            block(s, a-.12, b-.12, .29, .4, 1.4, BRONZE, z=foot)
            cylinder(s, a, b, .14, .13, foot+1, 6, BRONZE)
            cylinder(s, a, b, .19, .17, foot+7, 5, BRONZE)
        cylinder(s, ci, cj, .36, .25, foot+11, 4, BRONZE)
        cylinder(s, ci, cj, .29, .23, foot+15, 3, BRONZE)
        cylinder(s, ci, cj, .41, .27, foot+18, 4, BRONZE)
        seg(s, P(s, ci-.18, cj+.23, foot+17), P(s, ci+.18, cj+.23, foot+17), BRONZE['deep'])
        cylinder(s, ci-.08, cj, .13, .13, foot+22, 2, BRONZE)
        cylinder(s, ci-.16, cj+.06, .22, .2, foot+24, 4, BRONZE)
        ellipse(s, ci-.16, cj+.06, .23, .2, foot+28, BRONZE['dark'])
        # Left elbow bends out to a solid-bodied falcon, westward (screen left).
        slab(s, [(ci-.4,cj+.1),(ci-.6,cj+.22),(ci-.8,cj+.45),(ci-.57,cj+.54)], foot+17, foot+21, BRONZE)
        slab(s, [(ci-.8,cj+.42),(ci-.57,cj+.5),(ci-.74,cj+.8),(ci-.95,cj+.71)], foot+17, foot+19, BRONZE)
        cylinder(s, ci-.9, cj+.75, .25, .16, foot+19, 3.5, BRONZE)
        cylinder(s, ci-1.03, cj+.78, .13, .12, foot+22, 2, BRONZE)
        seg(s, P(s,ci-1.05,cj+.85,foot+23),P(s,ci-1.25,cj+.95,foot+23),GOLD['dark'])
        poly(s, [P(s,ci-.8,cj+.7,foot+20),P(s,ci-.5,cj+.52,foot+18),P(s,ci-.6,cj+.56,foot+22)],
             lambda x,y: BRONZE['dark'])
        # Right arm and the sword hang beside the right thigh.
        cylinder(s, ci+.45, cj-.08, .13, .12, foot+13, 8, BRONZE)
        seg(s,P(s,ci+.48,cj-.08,foot+13),P(s,ci+.45,cj-.05,foot+1),BRONZE['hi'],2)
        seg(s,P(s,ci+.25,cj-.05,foot+13),P(s,ci+.7,cj-.05,foot+13),BRONZE['dark'])
    scene.add(i+j+W+D, draw)


def cathedral(scene, i, j, z=0):
    """One western clock/bell tower, copper Baroque helm, long nave and eastern apse.
    West front is explicitly snapped to the visible SW face; the altar remains opposite."""
    W, D, H = 5.4, 9, 29
    def draw(s):
        cylinder(s, i+W/2, j+.8, W*.46, 1.2, z, H-3, WHITE,
                 windows(WHITE,H-3,11,12,arched=True))
        revolve(s,i+W/2,j+.8,W*.48,z+H-3,10,DOME,DARK_ROOF,ribs=5)
        block(s,i,j+1,W,D-2,H,WHITE,windows(WHITE,H,11,12,arched=True,pilasters=True),z=z)
        for zz in (2, H-3): band(s,i,j+1,W,D-2,z+zz,STONE,2)
        hip_roof(s,i-.1,j+.9,W+.2,D-1.8,z+H,16,DARK_ROOF)
        # The nave side is closed, with cornice, tall windows and pilaster buttresses.
        for b in (j+1.8,j+3.8,j+5.8,j+7.4):
            block(s,i+W,b,.22,.32,H-2,STONE,z=z)
        # West narthex at +j. Masonry front with painted gold/blue icon panels.
        def front(u,v,lit):
            if not lit:return windows(WHITE,35,10,12,arched=True)(u,v,lit)
            span=W*8
            if v < 17:
                opening=arch_opening(u,v,span/2,3.8,10,WOOD)
                if opening:return opening
            if 19<v<29 and 3<int(u)%14<10:
                c=int(u)%14
                if c in (4,9) or int(v) in (20,28):return GOLD['lit']
                return GOLD['mid'] if c in (6,7) and v<26 else rgb('#455D72')
            return stone_courses(WHITE,5,13)(u,v,lit)
        block(s,i-.15,j+D-1.6,W+.3,1.8,35,WHITE,front,z=z)
        band(s,i-.15,j+D-1.6,W+.3,1.8,z+33,STONE,2)
        pediment(s,i-.2,j+D-.15,W+.4,.25,z+35,9,WHITE)
        # Central tower over the west entrance; no second tower.
        a,b=i+W/2-1.05,j+D-2
        block(s,a,b,2.1,2.1,34,WHITE,windows(WHITE,34,8,13,arched=True,pilasters=True),z=z+35)
        band(s,a,b,2.1,2.1,z+64,STONE,2)
        clock(s,a+1.05,b+2.13,3.6,z+59)
        clock(s,a+2.13,b+1.05,3.4,z+59,False)
        band(s,a,b,2.1,2.1,z+69,STONE,2)
        revolve(s,a+1.05,b+1.05,1.1,z+71,27,HELMET,COPPER,ribs=3)
        cylinder(s,a+1.05,b+1.05,.27,.27,z+98,5,COPPER,
                 lambda u,v,lit:IRON if int(u)%3 else None)
        revolve(s,a+1.05,b+1.05,.45,z+103,6,DOME,COPPER,ribs=4)
        cross(s,a+1.05,b+1.05,z+109)
        for k in range(4):
            block(s,i+.65,j+D+.2+k*.3,W-1.3,.35,4-k,STONE,z=z)
    scene.add(i+j+W+D+2,draw)


def residence(scene,i,j,z=0):
    """White two-storey konak, broad clay hip, deep eaves and the curved garden divanhana."""
    W,D,H=8,5,23
    def draw(s):
        def panes(u,v,lit):
            c,level=int(u)%7,int(v)%11
            if v<2:return ROCK['lit' if lit else 'dark']
            if 2<=c<=5 and 3<=level<=9:
                if c in (2,5) or level in (3,6,9):return WOOD
                return GLASS['mid' if lit else 'dark']
            return WHITE['line'] if int(v)==11 else None
        block(s,i,j,W,D,H,WHITE,panes,z=z)
        band(s,i,j,W,D,z+1,ROCK,2);band(s,i,j,W,D,z+H-2,WHITE,2)
        hip_roof(s,i-.3,j-.3,W+.6,D+.6,z+H,11,CLAY)
        # Ground-floor central garden entry and the projecting rounded upper bay.
        block(s,i+W/2-.55,j+D,.95,.15,9,STONE,
              lambda u,v,lit:WOOD if 1<u<6 and v<8 else None,z=z)
        cylinder(s,i+W/2,j+D-.1,1.22,.88,z+11,12,WHITE,panes,segments=20)
        cylinder(s,i+W/2,j+D-.1,1.3,.94,z+22,1.3,WHITE)
        revolve(s,i+W/2,j+D-.1,1.43,z+23.3,7,[(0,1),(.45,.75),(1,.1)],CLAY,ribs=4)
        for a,b in ((i+1.1,j+1.2),(i+6.2,j+1.1),(i+1.2,j+3.5),(i+6.2,j+3.4)):
            block(s,a,b,.55,.6,10,WHITE,stone_courses(WHITE,3,6),z=z+H+4)
            band(s,a,b,.55,.6,z+H+12,WHITE,2)
            for di in (0,.38):block(s,a+di,b,.16,.6,2,WHITE,z=z+H+14)
    scene.add(i+j+W+D+1,draw)


def museum(scene,i,j,z=0):
    """Red academic palace: SE square front, cream rustication, paired windows,
    three copper domes, central clock/cartouche, lantern, pilasters and balustrade."""
    W,D,H=4.8,12,33
    def draw(s):
        base=windows(RED,H,10,12,pilasters=True,hood=True)
        def pattern(u,v,lit):
            if v<10:
                opening=arch_opening(int(u)%12,v,6,3,5,WOOD)
                return opening or stone_courses(STONE,3,11)(u,v,lit)
            return base(u,v,lit)
        block(s,i,j,W,D,H,RED,pattern,z=z)
        for zz in (9,11,H-2):band(s,i,j,W,D,z+zz,STONE,2)
        hip_roof(s,i-.05,j-.05,W+.1,D+.1,z+H,7,SLATE)
        # South-east-facing +i façade. End pavilions and middle bay project only a little.
        for off,width in ((.15,2.05),(D/2-1.5,3),(D-2.2,2.05)):
            a,b=i+W-.65,j+off
            block(s,a,b,1,width,H+4,RED,windows(RED,H+4,9,12,pilasters=True,hood=True),z=z)
            band(s,a,b,1,width,z+9,STONE,2)
            band(s,a,b,1,width,z+H+3,STONE,2)
        # Facade centre's framed entrance, double pilasters and cartouche with clock.
        front=i+W+.37
        for b in (j+D/2-1.1,j+D/2+1.1):
            block(s,front-.03,b,.18,.18,22,WHITE,z=z+11)
        ci,cj=i+W-1.05,j+D/2
        for off,r,rise in ((1.25,1.22,12),(D/2,1.65,18),(D-1.25,1.22,12)):
            aa,bb=i+W-1.05,j+off
            cylinder(s,aa,bb,r,r,z+H+5,3,STONE)
            revolve(s,aa,bb,r*1.1,z+H+8,rise,DOME,COPPER,ribs=3)
            if off==D/2:
                cylinder(s,aa,bb,.29,.29,z+H+8+rise,5,COPPER,
                         lambda u,v,lit:IRON if int(u)%2 else None)
                revolve(s,aa,bb,.42,z+H+13+rise,4,DOME,COPPER,ribs=4)
                seg(s,P(s,aa,bb,z+H+17+rise),P(s,aa,bb,z+H+23+rise),GOLD['dark'])
            else:seg(s,P(s,aa,bb,z+H+8+rise),P(s,aa,bb,z+H+14+rise),IRON)
        # Cartouche sits on the SE face, not accidentally on the visible SW flank.
        slab(s,[(front-.1,cj-.52),(front+.12,cj-.52),(front+.12,cj+.52),(front-.1,cj+.52)],z+H+1,z+H+9,WHITE)
        clock(s,front+.13,cj,2.9,z+H+5,False)
        balustrade(s,(i+W+.34,j+.2),(i+W+.34,j+D-.2),z+H+3,3,STONE,step=5)
        # Tall sculpted central clock crest stands above the balustrade, as on the square front.
        slab(s,[(front-.12,cj-.48),(front+.15,cj-.48),(front+.15,cj+.48),(front-.12,cj+.48)],
             z+H+3,z+H+12,WHITE)
        clock(s,front+.17,cj,3.2,z+H+8,False)
        # Scroll shoulders and a carved crest, kept off the side-wall texture.
        for off in (-.6,.6):
            cylinder(s,front-.04,cj+off,.16,.16,z+H+5,2,STONE)
        block(s,front-.1,cj-.17,.25,.34,2,WHITE,z=z+H+12)
    scene.add(i+j+W+D+1,draw)


def horse(s,i,j,z,facing=1):
    """Bronze horse-and-handler group: volumetric body, four legs, bent neck, head and tail."""
    block(s,i-.55,j-.45,1.4,.95,2,STONE,z=z)
    for a,b in ((-.3,-.2),(.3,-.2),(-.3,.2),(.3,.2)):
        cylinder(s,i+a,j+b,.075,.075,z+2,4,BRONZE)
    cylinder(s,i,j,.49,.3,z+6,2.7,BRONZE)
    slab(s,[(i+.25*facing,j-.15),(i+.53*facing,j-.15),(i+.65*facing,j+.16),(i+.38*facing,j+.16)],z+7,z+12,BRONZE)
    block(s,i+.45*facing,j-.17,.48,.34,2.4,BRONZE,z=z+11)
    seg(s,P(s,i-.4*facing,j,z+8),P(s,i-.75*facing,j+.1,z+4),BRONZE['dark'],2)
    cylinder(s,i,j+.53,.14,.13,z+2,6,BRONZE)
    cylinder(s,i,j+.53,.12,.11,z+8,2,BRONZE)
    seg(s,P(s,i,j+.53,z+7),P(s,i+.5*facing,j+.2,z+10),BRONZE['lit'],2)


def assembly(scene,i,j,z=0):
    """Long stone parliamentary palace, SW portico and pediment, octagonal dome drum,
    copper dome/lantern and two Black Horses groups at the stairs."""
    W,D,H=12,5.4,29
    def draw(s):
        pat=windows(STONE,H,11,12,arched=True,pilasters=True,hood=True)
        block(s,i,j,W,D,H,STONE,pat,z=z)
        for zz in (2,12,H-2):band(s,i,j,W,D,z+zz,WHITE,2)
        hip_roof(s,i-.06,j-.06,W+.12,D+.12,z+H,9,SLATE)
        # Long wings retain their low silhouette; both terminal pavilions are visible.
        for a in (i,i+W-2.1):
            block(s,a,j+D-2.4,2.1,2.65,H+5,STONE,windows(STONE,H+5,8,12,pilasters=True),z=z)
            band(s,a,j+D-2.4,2.1,2.65,z+H+3,WHITE,2)
            hip_roof(s,a-.05,j+D-2.45,2.2,2.75,z+H+5,5,SLATE)
            cylinder(s,a+1.05,j+D-1.05,.74,.74,z+H+7,3,STONE,segments=8)
            revolve(s,a+1.05,j+D-1.05,.9,z+H+10,8,DOME,COPPER,ribs=3)
            seg(s,P(s,a+1.05,j+D-1.05,z+H+18),P(s,a+1.05,j+D-1.05,z+H+22),COPPER['dark'])
        # Drum/dome before the portico: a central dominant volume, no invented roof statues.
        ci,cj=i+W/2,j+D/2
        cylinder(s,ci,cj,1.65,1.65,z+H+1,12,STONE,windows(STONE,12,8,11,arched=True),segments=8)
        cylinder(s,ci,cj,1.76,1.76,z+H+12,2,WHITE,segments=8)
        revolve(s,ci,cj,1.85,z+H+14,19,DOME,COPPER,ribs=3)
        cylinder(s,ci,cj,.3,.3,z+H+33,6,COPPER,
                 lambda u,v,lit:IRON if int(u)%3 else None)
        revolve(s,ci,cj,.48,z+H+39,5,DOME,COPPER,ribs=3)
        seg(s,P(s,ci,cj,z+H+44),P(s,ci,cj,z+H+49),COPPER['dark'])
        a,b,w=i+3.9,j+D-.4,4.2
        block(s,a,b,w,.8,H+2,STONE,windows(STONE,H+2,9,12,arched=True),z=z)
        # Recess behind a real open columned portico, rather than painted vertical stripes.
        for k in range(4):
            aa=a+.3+k*1.2
            block(s,aa-.19,b+.85,.38,.38,2,WHITE,z=z+7)
            cylinder(s,aa,b+1.02,.13,.13,z+9,18,WHITE,
                     lambda u,v,lit:STONE['line'] if int(u)%3==0 else None)
            block(s,aa-.24,b+.78,.48,.48,2,WHITE,z=z+27)
        block(s,a-.12,b+.7,w+.24,.7,3,STONE,z=z+29)
        pediment(s,a-.2,b+.65,w+.4,.8,z+32,9,WHITE)
        # Entrance stair, paired bronze sculptures and lamps.
        for k in range(5):
            block(s,a-.2,b+1.5+k*.27,w+.4,.32,6-k,STONE,z=z)
        horse(s,a-.85,b+1.9,z,1);horse(s,a+w+.85,b+1.9,z,-1)
        for aa in (i+2.7,i+9.3):lamp(s,aa,b+2.1,z,12)
    scene.add(i+j+W+D+3,draw)


def half_dome(s,ci,cj,r,base,rise,direction):
    """Half of a hemisphere; flat inner cut abuts the crossing, with its outward apse wall."""
    start={'i':-math.pi/2,'j':0,'-i':math.pi/2,'-j':math.pi}[direction]
    faces=[]
    for k in range(6):
        t,nt=k/6,(k+1)/6
        for n in range(16):
            a,b=start+n*math.pi/16,start+(n+1)*math.pi/16
            pts=[P(s,ci+r*math.cos(tt*math.pi/2)*math.cos(ang),cj+r*math.cos(tt*math.pi/2)*math.sin(ang),base+rise*math.sin(tt*math.pi/2))
                 for tt,ang in ((t,a),(t,b),(nt,b),(nt,a))]
            lit=math.sin((a+b)/2)-.5*math.cos((a+b)/2)>0
            faces.append((math.cos(a)+math.sin(a)+math.cos(b)+math.sin(b),n,pts,lit))
    for _,n,pts,lit in sorted(faces):
        poly(s,pts,lambda x,y,lit=lit:DARK_ROOF['line'] if int(y)%5==0 else DARK_ROOF['lit' if lit else 'dark'])
        if n%4==0:seg(s,pts[0],pts[3],COPPER['hi' if lit else 'deep'])


def saint_sava(scene,i,j,z=0):
    """White marble Greek cross, four half-domes, four capped bell towers and dominant
    green dome. West is snapped to SW; the four principal turrets are counted explicitly."""
    W,D=9.5,8.5
    def draw(s):
        ci,cj=i+W/2,j+D/2
        def sava_windows(u,v,lit):
            c=int(u)%9
            for low,high in ((8,20),(24,31)):
                if low<v<high:
                    opening=arch_opening(c,v-low,4.5,1.6,high-low-3,IRON)
                    if opening:return opening
                    if c in (2,7):return WHITE['hi' if lit else 'mid']
            return stone_courses(WHITE,6,15)(u,v,lit)
        a,b=i+.75,j+.55
        block(s,a,b,1.45,1.45,44,WHITE,sava_windows,z=z)
        revolve(s,a+.725,b+.725,.85,z+44,10,DOME,DARK_ROOF,ribs=3)
        cross(s,a+.725,b+.725,z+54,5)
        # Central crossing and four arms share closed walls down to the plateau.
        wall=sava_windows
        block(s,i+1.7,j+1.35,W-3.4,D-2.7,49,WHITE,sava_windows,z=z)
        arms=[(i+1.85,j,5.8,2.6,'-j'),(i,j+1.6,2.9,5.3,'-i'),
              (i+W-2.9,j+1.6,2.9,5.3,'i'),(i+1.85,j+D-2.6,5.8,2.6,'j')]
        for a,b,w,d,di in arms:
            block(s,a,b,w,d,35,WHITE,wall,z=z)
            band(s,a,b,w,d,z+32,GRANITE,2)
            ac,bc=(ci,b+d-.2) if di=='-j' else (ci,b+.2) if di=='j' else (a+w-.2,cj) if di=='-i' else (a+.2,cj)
            half_dome(s,ac,bc,2.65,z+35,20,di)
        # Windowed drum and vast shallow hemispherical dome, with reddish granite cornice.
        cylinder(s,ci,cj,2.65,2.65,z+49,15,WHITE,
                 lambda u,v,lit: arch_opening(int(u)%7,v,3.5,1.5,8,IRON) if v>3 else None,segments=32)
        cylinder(s,ci,cj,2.8,2.8,z+62,2.5,GRANITE)
        revolve(s,ci,cj,2.92,z+64.5,30,DOME,DARK_ROOF,ribs=4)
        cross(s,ci,cj,z+94.5,11)
        # Rear tower is naturally hidden by the main dome. Draw the three nearer belfries
        # after it so the central drum cannot erase their caps (a real depth relation).
        for a,b in ((i+.75,j+.55),(i+W-2.2,j+.55),(i+.75,j+D-2),(i+W-2.2,j+D-2)):
            def belfry(u,v,lit):
                if 33<v<43:
                    return arch_opening(int(u)%8,v-33,4,2,6,IRON) or WHITE['lit' if lit else 'dark']
                return stone_courses(WHITE,5,12)(u,v,lit)
            if a<i+1 and b<j+1:
                continue  # the far north-east bell tower is completely behind the central roof
            block(s,a,b,1.45,1.45,44,WHITE,belfry,z=z)
            band(s,a,b,1.45,1.45,z+42,GRANITE,2)
            revolve(s,a+.725,b+.725,.85,z+44,10,DOME,DARK_ROOF,ribs=3)
            cross(s,a+.725,b+.725,z+54,5)
        # Lower chapel turrets at the western outside corners; these are not extra belfries.
        for a in (i+.15,i+W-1.15):
            block(s,a,j+D-1.05,1,1.05,26,WHITE,sava_windows,z=z)
            band(s,a,j+D-1.05,1,1.05,z+24,GRANITE,2)
            revolve(s,a+.5,j+D-.52,.58,z+26,6,DOME,DARK_ROOF,ribs=3)
            cross(s,a+.5,j+D-.52,z+32,4)
        pediment(s,i+1.9,j+D-.05,W-3.8,.2,z+29,8,WHITE)
        # Carved west oculus in the pediment, using the actual face's plane.
        xx,yy=P(s,i+W/2,j+D+.17,z+33)
        for dx in range(-2,3):
            for dy in range(-2,3):
                if dx*dx+dy*dy<=5:s.put(xx+dx,yy+dy,IRON if dx*dx+dy*dy<3 else GRANITE['lit'])
        # Three arched western entrances under separate moulded archivolts.
        for a in (i+2.2,i+W/2-.45,i+W-3.1):
            def portal(u,v,lit):
                if lit:
                    hole=arch_opening(u,v,4,2.8,11,WOOD)
                    if hole:return hole
                return stone_courses(WHITE,4,10)(u,v,lit)
            block(s,a,j+D+.04,.95,.25,20,WHITE,portal,z=z)
            band(s,a-.05,j+D,.95,.35,z+2,GRANITE)
        for k in range(4):block(s,i+2,j+D+.4+k*.25,W-4,.3,4-k,WHITE,z=z)
    scene.add(i+j+W+D+3,draw)


def townhouse(scene,i,j,wi=2.5,wj=3,floors=3,seed=0):
    """Belgrade academic stucco: rusticated shop base, framed panes, iron balconies,
    window hoods, deep cornice, clay/slate hip roof, dormer and capped chimneys."""
    wall,H=palette_of(WALLS[seed%len(WALLS)]),floors*10+3
    base=windows(wall,H,9,10,hood=True,pilasters=seed%4==0)
    roof=CLAY if seed%3 else SLATE
    def pattern(u,v,lit):
        c,level=int(u)%9,int(v)%10
        if v<9:
            if 2<=c<=6:
                if c in (2,6) or int(v)==8:return WHITE['lit' if lit else 'dark']
                return WOOD if (int(u)//9+seed)%3==0 else GLASS['dark']
            return wall['line'] if int(v)%3==0 else None
        if seed%3==1 and 10<v<H-5 and level in (1,2) and 1<=c<=7:
            return IRON if level==1 or c%2 else WHITE['mid']
        return base(u,v,lit)
    def draw(s):
        block(s,i,j,wi,wj,H,wall,pattern)
        band(s,i,j,wi,wj,1,ROCK,2);band(s,i,j,wi,wj,H-2,WHITE,2)
        hip_roof(s,i-.13,j-.13,wi+.26,wj+.26,H,10+seed%3,roof)
        # Deep balcony, supported by corbels, on selected academic fronts.
        if seed%4==0:
            block(s,i+.5,j+wj,.9,.42,1.5,WHITE,z=13)
            for a in range(5):seg(s,P(s,i+.5+a*.225,j+wj+.4,15),P(s,i+.5+a*.225,j+wj+.4,19),IRON)
            seg(s,P(s,i+.5,j+wj+.4,19),P(s,i+1.4,j+wj+.4,19),IRON)
        block(s,i+.65,j+wj-.6,.6,.55,5,wall,windows(wall,5,5,6),z=H+2)
        hip_roof(s,i+.6,j+wj-.65,.7,.65,H+7,3,roof)
        block(s,i+wi-.65,j+.4,.4,.45,8,STONE,z=H+5)
        band(s,i+wi-.65,j+.4,.4,.45,H+12,roof,2)
    scene.add(i+j+wi+wj+1,draw)


def main():
    for name,builder,(wi,wj),_,_,elevation in SITES:
        def study(s,b=builder,z=elevation,wi=wi,wj=wj):
            if z:
                for a in range(5,math.ceil(7+wi)):
                    for c in range(5,math.ceil(7+wj)):
                        iso.ground_tile(s,a,c,lambda x,y:GROUND['garden'],z,iso.stone_wall(ROCK['mid']))
            b(s,6,6,z=z)
        print(preview([study],'belgrade-'+name,size=(340,300),origin=(170,120),tiles=25))
    print(preview([lambda s,k=k:townhouse(s,3+k*3.5,4,floors=2+k%2,seed=k)
                   for k in range(6)],'belgrade-houses',size=(340,240),origin=(80,75),tiles=27))
    import sprites
    image=sprites.golubac()
    path=Path(__file__).resolve().parents[2]/'docs/art/capitals/serbia-golubac.png'
    image.resize((image.width*4,image.height*4),0).save(path)
    print(path)


# name, builder, footprint, real (longitude, latitude), north-up ground anchor, elevation.
SITES = [
    ('victor',victor,(9,7),(20.447694,44.823028),(130,155),22),
    ('cathedral',cathedral,(5.4,9),(20.452160,44.818060),(270,250),0),
    ('residence',residence,(8,5),(20.452270,44.817120),(280,335),0),
    ('museum',museum,(4.8,12),(20.459400,44.816700),(410,340),0),
    ('assembly',assembly,(12,5.4),(20.465830,44.811670),(490,430),0),
    ('saint-sava',saint_sava,(9.5,8.5),(20.4685389,44.798060),(640,480),12),
]


if __name__ == '__main__':
    main()
