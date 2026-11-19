"""Chișinău's limestone, Empire porticoes and decorated Bessarabian houses in (i,j,z).

Two-source coordinates, photographed silhouettes and deliberate facade turns: Phase 4.
Run directly to regenerate eight isolated 4× landmark studies and a house study.
"""
import math
from pathlib import Path

import iso
from iso import rgb
from landmarks_paris import P, seg, poly, corners, preview, GLASS
from landmarks_iberia import hip_roof, stone_courses, arch_opening, palette_of, tones
from landmarks_slovakia import block, band, pediment
from landmarks_bosnia import cylinder
from landmarks_slovenia import revolve, DOME, balustrade
from landmarks_greece import column
from landmarks_denmark import clock

STONE = tones('#FFF8DE', '#E5D7B4', '#CEBE98', '#AD9C78', '#7D6C4C', '#B6A37C', '#51432D')
WHITE = tones('#FFFFF2', '#F4EDDA', '#DED5BE', '#BFB49A', '#8B7F64', '#CFC2A8', '#514735')
OCHRE = tones('#FFF1BC', '#E9C776', '#CFA85D', '#A88748', '#745E32', '#BA954D', '#534023')
BRICK = tones('#E7B18B', '#BE805A', '#A66A48', '#835034', '#5D3725', '#A16A49', '#4A3024')
CLAY = tones('#F0AD79', '#C78251', '#AE663E', '#88492F', '#603323', '#A25A39', '#4C2B20')
METAL = tones('#C0C7BA', '#939F91', '#758578', '#54665D', '#394C43', '#65766A', '#2B3B33')
DARK_DOME = tones('#CEC19B', '#9A9274', '#7D785D', '#5B5D49', '#3D4336', '#6B6B53', '#30372D')
BRONZE = tones('#B9BD92', '#84916B', '#657654', '#42583F', '#2B3C2E', '#596F4D', '#233328')
GOLD = tones('#FFF1A5', '#EAC76C', '#CBA047', '#A0782E', '#6D501F', '#B48B38', '#514023')
REDSTONE = tones('#D4A38B', '#A36C58', '#895341', '#653B31', '#4B2B25', '#81513E', '#3B2723')
TIMBER = tones('#DBBA8B', '#AB8859', '#8E6B45', '#6A4E32', '#493726', '#85613E', '#382C22')
ROCK = tones('#D9C9A8', '#B5A17F', '#9B8767', '#79674C', '#564A37', '#8E7959', '#433B2D')
IRON, WOOD = rgb('#36423D'), rgb('#70503A')
FLAG_BLUE, FLAG_RED = rgb('#31559A'), rgb('#C74736')
WALLS = [rgb(c) for c in ('#E7D7AC', '#D5DFBF', '#E5BEA1', '#C6D4CF', '#ECDDBE', '#C6B9CD')]
GROUND = {k: rgb(v) for k, v in {
    'square':'#DED2B7', 'joint':'#BAAD92', 'rose':'#CDB99F',
    'cobble':'#BCAF98', 'cobble_joint':'#968972',
    'garden':'#93AE70', 'garden_hi':'#B1C48A', 'flower':'#D5AD73',
    'water':'#649A94', 'water_dark':'#4C7F80', 'water_hi':'#C8E0D5',
}.items()}


def windows(material, height, bay=12, floor=15, arched=False):
    joints = stone_courses(material, 4, 13)
    def pattern(u, v, lit):
        c, k = int(u) % bay, int(v) % floor
        trim = WHITE['lit' if lit else 'dark']
        if arched and 2 < v < height-3:
            a = arch_opening(c, k-3, bay/2, 3.2, floor-10, trim)
            b = arch_opening(c, k-4, bay/2, 2.1, floor-11, GLASS['dark'])
            if b:
                return trim if c == bay//2 or k == 7 else b
            if a:
                return a
        elif 3 <= c <= bay-3 and 3 <= k <= floor-4 and 2 < v < height-3:
            if c in (3, bay-3, bay//2) or k in (3, 7, floor-4):
                return trim
            return GLASS['mid' if lit else 'dark']
        if k == 2 and 2 <= c <= bay-2 or int(v) in (1, height-2):
            return trim
        return joints(u, v, lit)
    return pattern


def cross(s, i, j, z, size=7, material=GOLD):
    seg(s, P(s,i,j,z), P(s,i,j,z+size), material['dark'])
    seg(s, P(s,i-.23,j,z+size*.65), P(s,i+.23,j,z+size*.65), material['hi'])


def flag(s, i, j, z):
    """Vertical Moldovan tricolour with a miniature eagle/aurochs shield on yellow."""
    seg(s,P(s,i,j,z),P(s,i,j,z+18),IRON)
    for k, c in enumerate((FLAG_BLUE,GOLD['lit'],FLAG_RED)):
        poly(s,[P(s,i+a,j,z+17-b) for a,b in ((k*.65,0),((k+1)*.65,0),
                                                           ((k+1)*.65,9),(k*.65,9))],lambda x,y,c=c:c)
    x,y=P(s,i+.97,j,z+13)
    # Spread eagle wings, red breast shield, gold aurochs head; not a Romanian plain tricolour.
    for dx,dy in ((-2,-1),(-1,0),(0,-1),(1,0),(2,-1),(0,1),(0,2)):
        s.put(x+dx,y+dy,REDSTONE['deep'])
    s.put(x,y,FLAG_RED);s.put(x,y+1,GOLD['hi'])


def portico(s, i, j, w, d, z, height, count=6, material=WHITE):
    block(s,i-.12,j-.1,w+.24,d+.2,3,STONE,z=z)
    for k in range(count):
        column(s,i+.35+k*(w-.7)/(count-1),j+d-.25,z+3,height,.21,material)
    block(s,i-.1,j-.1,w+.2,d+.2,3,material,z=z+height+3)
    pediment(s,i-.12,j-.12,w+.24,d+.24,z+height+6,7,material)


def cathedral(scene, i, j, z=0):
    """One great dark dome and four six-column porticoes; SW/SE porticoes visible."""
    w=d=7.8
    def draw(s):
        block(s,i,j,w,d,31,WHITE,windows(WHITE,31,16,24,True),z=z+3)
        band(s,i,j,w,d,z+4,STONE,3)
        band(s,i,j,w,d,z+31,WHITE,3)
        hip_roof(s,i-.1,j-.1,w+.2,d+.2,z+34,8,METAL)
        # Rear NE and NW porticoes remain behind the naos, rather than becoming extra towers.
        # The SE portico is rotated in its local tile frame, preserving its true six columns.
        a,b=i+w+.05,j+1.6
        block(s,a,b,1.5,4.6,3,STONE,z=z)
        for n in range(6):column(s,a+1.22,b+.3+n*.8,z+3,24,.21,WHITE)
        block(s,a,b,1.5,4.6,3,WHITE,z=z+27)
        # Extruded triangular pediment on the shaded +i face.
        pts=[P(s,a+1.5,b,z+30),P(s,a+1.5,b+4.6,z+30),P(s,a+1.5,b+2.3,z+37)]
        poly(s,pts,lambda x,y:WHITE['dark'])
        for p,q in zip(pts,pts[1:]+pts[:1]):seg(s,p,q,WHITE['mid'])
        ci,cj=i+w/2,j+d/2
        cylinder(s,ci,cj,2.25,2.25,z+39,15,WHITE,windows(WHITE,15,10,18,True),segments=40)
        cylinder(s,ci,cj,2.4,2.4,z+53,2,WHITE,segments=40)
        revolve(s,ci,cj,2.48,z+55,20,DOME,DARK_DOME,ribs=4,segments=40)
        cross(s,ci,cj,z+75,7)
        # Main southwest front is genuinely southwest: no orientation turn.
        def entrance(u,v,lit):
            if lit:
                a=arch_opening(u,v,18.4,4,15,WOOD)
                if a:return a
            return windows(WHITE,28,14,25,True)(u,v,lit)
        block(s,i+1.6,j+d-.12,4.6,.2,28,WHITE,entrance,z=z+3)
        portico(s,i+1.6,j+d,4.6,1.5,z,24)
        for n in range(3):block(s,i+1.4-n*.15,j+d+1.5+n*.23,5+n*.3,.26,3-n,WHITE,z=z)
    scene.add(i+j+w+d+3,draw)


def vault(s, i, j, w, d, z, height, half, spring, material=WHITE):
    """Four-pier open cross vault. Spandrels and intrados are projected, openings stay empty."""
    pier=(w*8/2-half)/8
    for a,b in sorted(((i,j),(i+w-pier,j),(i,j+d-pier),(i+w-pier,j+d-pier)),key=sum):
        shadow = dict(material,lit=material['mid'],dark=material['deep']) if a==i and b==j else material
        block(s,a,b,pier,pier,height,shadow,z=z)
    # Back spandrels first; the ground remains visible through the crossed passages.
    for start,end,lit in ((P(s,i,j+d,z),P(s,i+w,j+d,z),True),
                          (P(s,i+w,j+d,z),P(s,i+w,j,z),False)):
        width=abs(end[0]-start[0]);slope=(end[1]-start[1])/(end[0]-start[0])
        pts=[start,end,(end[0],end[1]-height),(start[0],start[1]-height)]
        for x,y in iso.polygon_pixels(pts):
            u=x-start[0];v=start[1]+u*slope-y
            centre=(end[0]-start[0])/2
            if abs(u-centre)<half:
                crown=spring+math.sqrt(max(0,half**2-(u-centre)**2))
                if v<crown:
                    # Only shade masonry actually seen through the opening. Empty pixels
                    # retain the plot/plaza; interior stone never spills below the arch.
                    px,py=int(x),int(y)
                    if 0<=px<s.w and 0<=py<s.h and s.px[px,py][:3] in material.values():
                        s.put(x,y,material['deep'])
                    continue
                c=material['hi' if lit else 'mid'] if v<crown+2 else material['lit' if lit else 'dark']
            else:c=stone_courses(material,4,12)(u,v,lit) or material['lit' if lit else 'dark']
            s.put(x,y,c)
        # Voussoirs follow the arc in its own wall plane, never a screen-facing semicircle.
        for k in range(13):
            t=k*math.pi/12
            u=width/2+half*math.cos(t)
            base_y=start[1]+u*slope
            seg(s,(start[0]+u,base_y-spring-half*math.sin(t)),
                (start[0]+u+2*math.cos(t),base_y-spring-(half+2)*math.sin(t)),material['line'])


def belfry(scene, i, j, z=0):
    def draw(s):
        block(s,i-.35,j-.35,4.7,4.7,3,STONE,z=z)
        block(s,i,j,4,4,20,WHITE,windows(WHITE,20,16,24,True),z=z+3)
        band(s,i,j,4,4,z+22,WHITE,3)
        vault(s,i+.4,j+.4,3.2,3.2,z+25,17,6.8,7)
        band(s,i+.4,j+.4,3.2,3.2,z+42,WHITE,3)
        vault(s,i+.7,j+.7,2.6,2.6,z+45,17,5.3,7)
        # Bell is physically within the opening, entirely above its sill.
        seg(s,P(s,i+2,j+2,z+60),P(s,i+2,j+2,z+53),IRON)
        revolve(s,i+2,j+2,.34,z+49,5,[(0,1),(.2,.9),(.7,.5),(1,.4)],BRONZE,ribs=0)
        band(s,i+.65,j+.65,2.7,2.7,z+62,WHITE,3)
        cylinder(s,i+2,j+2,1.17,1.17,z+65,5,WHITE,segments=32)
        revolve(s,i+2,j+2,1.35,z+70,10,DOME,DARK_DOME,ribs=4,segments=32)
        cross(s,i+2,j+2,z+80,6)
        portico(s,i+.9,j+3.8,2.2,.7,z+3,10,count=2)
        for n in range(3):block(s,i+.7-n*.15,j+4.6+n*.22,2.6+n*.3,.24,3-n,WHITE,z=z)
    scene.add(i+j+12,draw)


def arch(scene, i, j, z=0):
    def draw(s):
        vault(s,i,j,5.4,5.4,z,30,11,12)
        band(s,i,j,5.4,5.4,z+29,WHITE,3)
        block(s,i,j,5.4,5.4,13,WHITE,stone_courses(WHITE,4,14),z=z+32)
        band(s,i,j,5.4,5.4,z+43,WHITE,3)
        band(s,i+.1,j+.1,5.2,5.2,z+46,STONE,2)
        # Paired Doric pilasters, not extra arches or a solid dark cut-out.
        for a,b in ((i+.15,j+5.44),(i+4.85,j+5.44)):
            block(s,a,b,.4,.18,28,WHITE,z=z)
            band(s,a,b,.4,.18,z+26,STONE,2)
        clock(s,i+2.7,j+5.48,4.3,z+38)
    scene.add(i+j+11,draw)


def stephen(scene, i, j, z=0):
    """Crowned bronze ruler with raised LEFT cross and sword, turned NE→SW for visibility."""
    def draw(s):
        for n in range(4):block(s,i+n*.25,j+n*.25,4-n*.5,4-n*.5,3,WHITE,z=z+n*3)
        block(s,i+.8,j+.8,2.4,2.4,23,STONE,z=z+12)
        for zz in (12,29,34):band(s,i+.75,j+.75,2.5,2.5,z+zz,WHITE,2)
        # Carved belt, shield and bounded garland reliefs in the plinth's SW plane.
        for n in range(7):
            a=i+.95+n*.3
            cylinder(s,a,j+3.23,.1,.07,z+28,2,WHITE,segments=8)
        shield=[P(s,i+1.65,j+3.23,z+25),P(s,i+2.35,j+3.23,z+25),
                P(s,i+2.3,j+3.23,z+20),P(s,i+2,j+3.23,z+18),P(s,i+1.7,j+3.23,z+20)]
        poly(s,shield,lambda x,y:WHITE['mid'] if (x+y)%4 else STONE['dark'])
        ci,cj=i+2,j+2
        # Substantial boots, flared cloak, torso, crown and bent arms, not a stick statue.
        for a in (-.28,.18):block(s,ci+a,cj-.1,.18,.35,6,BRONZE,z=z+37)
        for k in range(5):
            w=1.05-k*.09
            block(s,ci-w/2,cj-.3,w,.65,3.4,BRONZE,
                  lambda u,v,lit:BRONZE['line'] if int(u)%3==0 else None,z=z+42+k*3.2)
        block(s,ci-.35,cj-.25,.7,.5,7,BRONZE,z=z+54)
        cylinder(s,ci,cj,.26,.24,z+61,5,BRONZE,segments=16)
        cylinder(s,ci,cj,.32,.29,z+66,2,BRONZE,segments=12)
        for a in (-.23,0,.23):block(s,ci+a,cj,.08,.12,2,BRONZE,z=z+68)
        # Left hand on the figure's own left, the SE/viewer's-right end of the SW frontage.
        for a,b,h,zz in ((.38,.02,7,54),(.65,.02,8,60),(.87,.02,10,67)):
            block(s,ci+a,cj+b,.2,.2,h,BRONZE,z=z+zz)
        cross(s,ci+.97,cj+.08,z+77,8,BRONZE)
        # Right forearm bent to sword hilt across the chest; sheathed sword reaches the boots.
        seg(s,P(s,ci-.5,cj+.2,z+57),P(s,ci-.1,cj+.4,z+54),BRONZE['hi'],2)
        seg(s,P(s,ci-.35,cj+.38,z+56),P(s,ci-.6,cj+.43,z+39),BRONZE['dark'],2)
        seg(s,P(s,ci-.6,cj+.4,z+56),P(s,ci-.1,cj+.4,z+56),BRONZE['lit'])
    scene.add(i+j+8,draw)


def city_hall(scene, i, j, z=0):
    """Two long yellow wings, ONE corner clock tower; NE/SE street fronts turned SE/SW."""
    w,d=12,8
    def draw(s):
        # Open L-shaped rear courtyard; shallow wings keep the corner and windows legible.
        parts=[(i,j+5.4,w,2.6),(i+9.4,j,2.6,5.4)]
        for a,b,wi,wj in parts:
            block(s,a,b,wi,wj,33,OCHRE,windows(OCHRE,33,12,16,True),z=z)
            for zz in (1,16,31):band(s,a,b,wi,wj,z+zz,WHITE,2)
            hip_roof(s,a-.05,b-.05,wi+.1,wj+.1,z+34,8,METAL)
            for k in range(int(wi*8)//12):
                aa=a+.3+k*1.5
                block(s,aa,b+wj,.12,.15,32,WHITE,z=z)
            # Dormer-like facade gables, in three rhythmically separated bays.
            if wi>5:
                for aa in (a+.5,a+4.4,a+8):pediment(s,aa,b+wj-.3,2.1,.4,z+32,7,WHITE)
        # Corner turret at the junction of the two street elevations.
        a,b=i+9.3,j+5.2
        block(s,a,b,2.9,2.9,48,OCHRE,windows(OCHRE,48,11,17,True),z=z)
        for zz in (1,16,33,46):band(s,a,b,2.9,2.9,z+zz,WHITE,2)
        clock(s,a+1.45,b+2.97,5,z+41)
        clock(s,a+2.97,b+1.45,5,z+41,False)
        # Actual small clock-tower cap/lantern, not a church dome.
        hip_roof(s,a-.1,b-.1,3.1,3.1,z+49,9,METAL)
        block(s,a+1.1,b+1.1,.7,.7,7,WHITE,windows(WHITE,7,5,10,True),z=z+58)
        hip_roof(s,a+1,b+1,.9,.9,z+65,6,METAL)
        flag(s,a+1.45,b+1.45,z+71)
        # Projecting civic balcony over the corner entrance, with iron rail and brackets.
        block(s,a+.35,b+2.91,2.15,.08,14,WHITE,
              lambda u,v,lit:arch_opening(u,v,8.6,4.8,8,WOOD) or WHITE['lit'],z=z)
        block(s,a+.25,b+2.9,2.4,.55,2,WHITE,z=z+16)
        for k in range(9):
            aa=a+.3+k*.27
            seg(s,P(s,aa,b+3.42,z+18),P(s,aa,b+3.42,z+23),IRON)
        seg(s,P(s,a+.25,b+3.42,z+23),P(s,a+2.65,b+3.42,z+23),IRON)
    scene.add(i+j+w+d+2,draw)


def history_museum(scene, i, j, z=8):
    """Broad classical wings, four Corinthian columns, curving central pavilion and Wolf."""
    w,d=13.6,5.5
    def draw(s):
        block(s,i,j,w,d,30,STONE,windows(STONE,30,12,14,True),z=z)
        for zz in (1,14,28):band(s,i,j,w,d,z+zz,WHITE,2)
        hip_roof(s,i-.05,j-.05,w+.1,d+.1,z+31,7,METAL)
        for a,b,wi,wj in ((i,j+d,w,.12),(i+w,j,.12,d)):
            balustrade(s,(a,b),(a+wi,b+wj),z+32,4,WHITE)
        # Shallow central pavilion and stepped broad approach, turned NE→SW.
        a,b=i+4.25,j+3.1
        block(s,a,b,5.1,3.3,36,WHITE,windows(WHITE,36,14,18,True),z=z)
        for n in range(5):block(s,a-.2-n*.18,b+3.3+n*.3,5.5+n*.36,.34,6-n,STONE,z=z)
        for n in range(4):
            ca=a+.4+n*1.43
            column(s,ca,b+3.2,z+5,29,.28,WHITE,order='corinthian')
            for off in (-.22,0,.22):
                block(s,ca+off-.08,b+3.42,.16,.18,3,WHITE,z=z+30)
        block(s,a-.15,b+2.2,5.4,1.3,4,WHITE,z=z+35)
        band(s,a-.15,b+2.2,5.4,1.3,z+39,STONE,2)
        # Concave mansard slopes with a round coat-of-arms cartouche on the visible face.
        # Concave pavilion roof, rising steeply to a small flat lantern seat.
        rings=[(0,4.8,2.9),(.28,3.7,2.15),(.62,2.7,1.6),(1,1.5,1.05)]
        for (t,wi,wj),(nt,nwi,nwj) in zip(rings,rings[1:]):
            low=corners(s,a+2.55-wi/2,b+1.6-wj/2,wi,wj,z+40+t*24)
            high=corners(s,a+2.55-nwi/2,b+1.6-nwj/2,nwi,nwj,z+40+nt*24)
            for aa,bb,lit in ((0,1,False),(0,3,True),(3,2,True),(2,1,False)):
                poly(s,[low[aa],low[bb],high[bb],high[aa]],
                     lambda x,y,lit=lit:METAL['line'] if y%3==0 else METAL['lit' if lit else 'dark'])
                seg(s,low[aa],high[aa],METAL['hi' if lit else 'deep'])
        ci,cj=a+2.55,b+2.98
        centre=P(s,ci,cj,z+46)
        ring=[P(s,ci+math.cos(k*math.tau/32)*.58,cj,z+46+math.sin(k*math.tau/32)*5) for k in range(32)]
        poly(s,ring,lambda x,y:WHITE['lit'])
        for p,q in zip(ring,ring[1:]+ring[:1]):seg(s,p,q,STONE['dark'])
        for dx,dy in ((-2,-1),(-1,0),(0,-1),(1,0),(2,-1),(0,1),(0,2)):
            s.put(centre[0]+dx,centre[1]+dy,BRONZE['dark'])
        s.put(centre[0],centre[1],FLAG_RED)
        cylinder(s,a+2.55,b+1.6,.65,.65,z+64,7,TIMBER,windows(TIMBER,7,6,10),segments=8)
        hip_roof(s,a+1.8,b+.85,1.5,1.5,z+71,5,METAL)
        # Capitoline Wolf: solid horizontal animal, muzzle, tail, four legs and nursing twins.
        aa,bb=i+3.1,j+d+1.5
        block(s,aa-.4,bb-.35,1.6,.85,9,REDSTONE,z=z)
        band(s,aa-.4,bb-.35,1.6,.85,z+9,REDSTONE,2)
        for xx in (aa-.15,aa+.65):
            for yy in (bb-.12,bb+.25):block(s,xx,yy,.12,.12,4,BRONZE,z=z+11)
        block(s,aa-.2,bb-.17,1.1,.52,4,BRONZE,z=z+15)
        block(s,aa-.45,bb-.17,.35,.37,5,BRONZE,z=z+17)
        block(s,aa-.7,bb-.17,.3,.3,2,BRONZE,z=z+18)
        for xx in (aa+.2,aa+.5):cylinder(s,xx,bb+.33,.12,.1,z+12,2,BRONZE,segments=8)
        seg(s,P(s,aa+.9,bb,z+17),P(s,aa+1.15,bb,z+12),BRONZE['dark'])
    scene.add(i+j+w+d+5,draw)


def ethnography(scene, i, j, z=10):
    """Long Moorish wings, horseshoe openings, ceramic friezes and stepped parapets."""
    w,d=12.6,5.6
    def decorated(u,v,lit):
        if int(v) in (3,4,24,25,28):
            return OCHRE['lit'] if (int(u)+int(v))%4<2 else REDSTONE['dark']
        c=int(u)%12
        a=arch_opening(c,v-6,6,3.8,11,WHITE['lit' if lit else 'dark'])
        b=arch_opening(c,v-7,6,2.6,10,GLASS['dark'])
        if b:return WHITE['dark'] if c==6 or int(v)==14 else b
        if a:return a
        return stone_courses(STONE,4,13)(u,v,lit)
    def draw(s):
        block(s,i,j,w,d,29,STONE,decorated,z=z)
        band(s,i,j,w,d,z+1,WHITE,3)
        hip_roof(s,i-.05,j-.05,w+.1,d+.1,z+29,10,CLAY)
        # End risalits stay low and square; no invented minarets or domes.
        for aa in (i,i+w-2.5):
            block(s,aa,j+d-1.2,2.5,1.3,33,OCHRE,decorated,z=z)
            band(s,aa,j+d-1.2,2.5,1.3,z+32,WHITE,2)
            for k in range(6):block(s,aa+k*.44,j+d-.05,.24,.2,3,OCHRE,z=z+34)
        a,b=i+4.4,j+3.1
        def front(u,v,lit):
            if lit:
                # Tall horseshoe opening framed with alternating ochre/cream voussoirs.
                c=17.0;dist=abs(u-c)
                top=29+math.sqrt(max(0,7.2**2-(u-c)**2))
                if dist<7.2 and 17<v<top:
                    return WHITE['mid'] if abs(u-c)<1 or int(v) in (22,29) else GLASS['dark']
                if dist<8.8 and 16<v<top+2:return OCHRE['dark'] if (int(u)+int(v))%4 else WHITE['hi']
                door=arch_opening(u,v,c,4.7,9,WOOD)
                if door:return WHITE['mid'] if int(u)==17 else door
            if int(v) in (2,15,16,38,39,42):return REDSTONE['dark'] if int(u)%4<2 else WHITE['hi']
            return stone_courses(OCHRE,4,14)(u,v,lit)
        block(s,a,b,4.25,3.1,44,OCHRE,front,z=z)
        for zz in (1,15,40,44):band(s,a,b,4.25,3.1,z+zz,WHITE,2)
        for k in range(10):block(s,a+k*.45,b+3.06,.24,.25,4,OCHRE,z=z+46)
        # Higher, narrow rear crest steps up as on the photographed central roofline.
        block(s,a+.8,b+.1,2.65,1.2,5,OCHRE,z=z+46)
        for k in range(7):block(s,a+.8+k*.4,b+1.2,.22,.2,3,OCHRE,z=z+51)
        for n in range(4):block(s,a-.25-n*.14,b+3.2+n*.26,4.75+n*.28,.3,4-n,WHITE,z=z)
        for aa in (a+.15,a+3.85):block(s,aa,b+3.13,.18,.2,39,WHITE,z=z)
    scene.add(i+j+w+d+3,draw)


def water_tower(scene, i, j, z=18):
    """Octagonal stone shaft, brick string courses and projecting timber/glazed tank room."""
    def draw(s):
        ci,cj=i+2.1,j+2.1
        cylinder(s,ci,cj,2.25,2.25,z,4,STONE,segments=8)
        def masonry(u,v,lit):
            if int(v) in (1,2,19,20,37,38,55,56):return BRICK['lit' if lit else 'dark']
            c=int(u)%11;k=int(v)%18
            a=arch_opening(c,k-4,5.5,2.9,6,WHITE['lit' if lit else 'dark']) if v<55 else None
            b=arch_opening(c,k-5,5.5,1.8,5,GLASS['dark']) if v<55 else None
            if b:return WHITE['dark'] if int(v)%18==9 else b
            if a:return a
            return stone_courses(STONE,4,13)(u,v,lit)
        # Build the shaft upwards in stages. Capped ring cylinders drawn after a full shaft
        # would paint opaque discs across the windows above them in this painter.
        for base,height in ((4,19),(25,16),(43,15)):
            cylinder(s,ci,cj,1.7,1.7,z+base,height,STONE,
                     lambda u,v,lit,base=base:masonry(u,v+base-4,lit),segments=8)
            cylinder(s,ci,cj,1.82,1.82,z+base+height,1,BRICK,segments=8)
            cylinder(s,ci,cj,1.82,1.82,z+base+height+1,1,WHITE,segments=8)
        # Corbelled projecting room: broad brackets before the glazing, eight true facets.
        for k in range(8):
            a=k*math.tau/8+math.pi/8
            aa,bb=ci+1.85*math.cos(a),cj+1.85*math.sin(a)
            block(s,aa-.12,bb-.12,.24,.24,6,WHITE,z=z+55)
        cylinder(s,ci,cj,2.08,2.08,z+60,3,WHITE,segments=8)
        cylinder(s,ci,cj,2.0,2.0,z+63,13,TIMBER,windows(TIMBER,13,10,17),segments=8)
        cylinder(s,ci,cj,2.25,2.25,z+76,2,TIMBER,segments=8)
        revolve(s,ci,cj,2.55,z+78,11,[(0,1),(.8,.22),(1,.02)],CLAY,ribs=1,segments=8)
        # Existing exterior entrance/approach, with stone landing and a short stair.
        for n in range(4):block(s,i+3.2+n*.25,j+1.6,.3,1.1,4-n,STONE,z=z)
    scene.add(i+j+9,draw)


def townhouse(scene,i,j,wi=2.5,wj=3,floors=2,seed=0,z=0):
    """Bessarabian limestone/plaster: carved hoods, veranda ironwork and clay/metal hips."""
    wall=palette_of(WALLS[seed%len(WALLS)]);height=12*floors+3
    base=windows(wall,height,10,12)
    def pattern(u,v,lit):
        c,k=int(u)%10,int(v)%12
        if v<10 and 2<=c<=8:
            if c in (2,8) or int(v) in (1,9):return WHITE['lit' if lit else 'dark']
            return WOOD if (int(u)//10+seed)%3==0 else GLASS['dark']
        if k==10 and v>12 and 2<=c<=8:return WHITE['hi' if lit else 'mid']
        if c in (0,1) and int(v)%4==0:return STONE['lit' if lit else 'dark']
        return base(u,v,lit)
    def draw(s):
        block(s,i,j,wi,wj,height,wall,pattern,z=z)
        band(s,i,j,wi,wj,z+1,STONE,2);band(s,i,j,wi,wj,z+height-1,WHITE,2)
        roof=METAL if seed%4==0 else CLAY
        hip_roof(s,i-.08,j-.08,wi+.16,wj+.16,z+height+1,9,roof)
        if seed%3==0:
            block(s,i+.6,j+wj-.35,1.3,.45,5,wall,windows(wall,5,8,8),z=z+height)
            pediment(s,i+.55,j+wj-.4,1.4,.55,z+height+5,4,WHITE)
        block(s,i+wi-.7,j+.35,.4,.45,7,STONE,z=z+height+6)
        band(s,i+wi-.7,j+.35,.4,.45,z+height+12,BRICK,2)
        if seed%3==1 and floors>1:
            block(s,i+.4,j+wj,1.7,.55,2,STONE,z=z+13)
            for n in range(7):seg(s,P(s,i+.45+n*.25,j+wj+.5,z+15),P(s,i+.45+n*.25,j+wj+.5,z+19),IRON)
            seg(s,P(s,i+.4,j+wj+.5,z+19),P(s,i+2.1,j+wj+.5,z+19),IRON)
    scene.add(i+j+wi+wj,draw)


def main():
    for name,builder,_,_,_,z in SITES:
        print(preview([lambda s,b=builder,z=z:b(s,7,7,z=z)],'chisinau-'+name,
                      size=(300,285),origin=(145,105),tiles=25))
    print(preview([lambda s,k=k:townhouse(s,3+k*3.6,4,floors=1+k%2,seed=k)
                   for k in range(6)],'chisinau-houses',size=(320,230),origin=(75,65),tiles=27))
    import sprites
    im=sprites.soroca();path=Path(__file__).resolve().parents[2]/'docs/art/capitals/moldova-soroca.png'
    im.resize((im.width*4,im.height*4),0).save(path);print(path)


# name, builder, footprint, verified building lon/lat, north-up scene anchor, ground elevation.
SITES = [
    ('cathedral',cathedral,(9.5,9.5),(28.8345281,47.0260628),(635,145),0),
    ('belfry',belfry,(4.7,5.2),(28.833824,47.025575),(525,220),0),
    ('stephen',stephen,(4,4),(28.8303111,47.02550915),(365,240),0),
    ('arch',arch,(5.4,5.4),(28.83259695,47.02473035),(480,305),0),
    ('ethnography',ethnography,(12.6,6.8),(28.82001575,47.02339345),(105,340),10),
    ('city-hall',city_hall,(12.4,8.7),(28.83440715,47.0226975),(605,392),0),
    ('history',history_museum,(13.6,8),(28.8280886,47.0225926),(330,420),8),
    ('water-tower',water_tower,(4.5,4.5),(28.82242625,47.0193307),(190,485),18),
]


if __name__=='__main__':
    main()
