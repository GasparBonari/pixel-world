"""Tirane: original projected (i, j, z) art, with researched north-up placement.

Run for eight isolated 4× studies and Tirana house/country-sprite studies.
DEVELOPMENT_PLAN.md records two-source coordinates, settings and intentional front turns.
SITES is the capital scene's sole placement source.
"""
import math
from pathlib import Path

from PIL import ImageChops

import iso
from iso import rgb
from landmarks_paris import P, seg, poly, corners, preview, GLASS
from landmarks_iberia import hip_roof, crenellate, stone_courses, arch_opening, palette_of, tones
from landmarks_slovakia import block, band
from landmarks_slovenia import windows, revolve, slab, DOME
from landmarks_bosnia import cylinder

STONE = tones('#F4E6CF', '#DBCCAF', '#C4B193', '#A18B6E', '#766148', '#B5A080', '#493B2C')
WHITE = tones('#FFFDF1', '#F0EBDA', '#DCD5C2', '#BDB49D', '#8C806A', '#CFC3AB', '#514735')
OCHRE = tones('#FFE6AF', '#E9CB85', '#CFAC68', '#AC894D', '#7C6137', '#BE9A5C', '#503D25')
CLAY = tones('#EDAE7F', '#C98252', '#AF673D', '#86462C', '#5C3020', '#9F5834', '#49281D')
LEAD = tones('#B4B9B8', '#929B9B', '#758286', '#56676D', '#3B4B53', '#68787D', '#2B3941')
BLUE = tones('#A4C8E0', '#538DB7', '#3C729F', '#29577F', '#1C3E60', '#32668F', '#142E49')
GOLD = tones('#FFF2B1', '#E5C56A', '#C7A145', '#9A782C', '#6C5322', '#B68D36', '#503E1E')
BRONZE = tones('#A1A08A', '#686D5A', '#505B4A', '#354536', '#243328', '#44523F', '#17251C')
ROCK = tones('#E2D7C0', '#BEB199', '#A3967E', '#83755D', '#5D5443', '#94876C', '#423B30')
CONCRETE = tones('#FFFFFF', '#ECECE2', '#D6D9D1', '#ADB9B5', '#7B8D8B', '#C2CBC5', '#495C5D')
WALLS = [rgb(c) for c in ('#EDCF88', '#D8977C', '#B6CBB2', '#DCC2CE', '#9DBFC7', '#EFE0BB', '#C9BB8C')]
PAVILIONS = [palette_of(rgb(c)) for c in ('#E9B442', '#D86C45', '#B2A1C7', '#60A1BC', '#A2BE75')]
WOOD, IRON, RED = rgb('#735039'), rgb('#35433E'), rgb('#BE4938')
WATER = tuple(rgb(c) for c in ('#5C9690', '#477D79', '#BBDDD0'))
GROUND = {k: rgb(v) for k,v in {
    'square':'#DACDB9', 'joint':'#BDB09C', 'rose':'#C7B2A4', 'grey':'#BEC3B5',
    'cobble':'#B5A58D', 'cobble_joint':'#948773', 'garden':'#8CA969',
    'garden_light':'#AFC386', 'road':'#929790', 'dry':'#C6B694',
}.items()}


def clock(s,i,j,width,z,lit=True):
    """White dial, dressed stone rim, hour marks and dark hands, in its wall plane."""
    def point(u,v):
        return P(s,i+u/8 if lit else i,j if lit else j-u/8,z+v)
    ring=[point(math.cos(n*math.tau/48)*width,math.sin(n*math.tau/48)*width) for n in range(48)]
    poly(s,ring,lambda x,y:WHITE['hi' if lit else 'mid'])
    for a,b in zip(ring,ring[1:]+ring[:1]):seg(s,a,b,STONE['line'])
    for n in range(12):
        a=n*math.tau/12
        seg(s,point(math.cos(a)*(width-1),math.sin(a)*(width-1)),point(math.cos(a)*width,math.sin(a)*width),IRON)
    seg(s,point(0,0),point(-width*.5,width*.18),IRON)
    seg(s,point(0,0),point(width*.12,width*.72),IRON)


def ellipsoid(s,ci,cj,z,ri,rj,rz,material):
    """Closed shaded mesh for solid horse/rider anatomy; height is in art pixels."""
    faces=[]
    for k in range(10):
        a,b=-math.pi/2+k*math.pi/10,-math.pi/2+(k+1)*math.pi/10
        for n in range(20):
            c,d=n*math.tau/20,(n+1)*math.tau/20
            pts=[P(s,ci+ri*math.cos(t)*math.cos(u),cj+rj*math.cos(t)*math.sin(u),z+rz*math.sin(t))
                 for t,u in ((a,c),(a,d),(b,d),(b,c))]
            light=math.sin((c+d)/2)-.6*math.cos((c+d)/2)+.5*math.sin((a+b)/2)
            key='hi' if light>1.1 else 'lit' if light>.35 else 'mid' if light>-.4 else 'dark'
            faces.append((math.cos(c)+math.sin(c)+math.cos(d)+math.sin(d),k,pts,key))
    for _,_,pts,key in sorted(faces,key=lambda f:(f[0],f[1])):
        poly(s,pts,lambda x,y,key=key:material[key])


def flat_roof(s,i,j,w,d,z,material=LEAD):
    band(s,i,j,w,d,z,WHITE,2)
    poly(s,list(corners(s,i+.12,j+.12,w-.24,d-.24,z+2)),
         lambda x,y:material['line'] if (x+2*y)%17==0 else material['mid'])
    for a,b,wi,wj in ((i,j,w,.12),(i,j,.12,d),(i+w-.12,j,.12,d),(i,j+d-.12,w,.12)):
        block(s,a,b,wi,wj,2,WHITE,z=z+2)


def open_arch(s,i,j,width,depth,z,height,material=STONE,along_i=True):
    """Extruded semicircular arch with empty opening; points remain in its wall plane."""
    def point(u,v,back=False):
        return P(s,i+u,j+(0 if back else depth),z+v) if along_i else P(s,i+(0 if back else depth),j+u,z+v)
    spring=height-width*3.5
    spring=max(height*.4,spring)
    for n in range(16):
        a,b=n*math.pi/16,(n+1)*math.pi/16
        outer=[(width/2+width/2*math.cos(t),spring+(height-spring)*math.sin(t)) for t in (a,b)]
        inner=[(width/2+(width/2-.16)*math.cos(t),spring+(height-spring-1.5)*math.sin(t)) for t in (a,b)]
        poly(s,[point(u,v,True) for u,v in outer+inner[::-1]],lambda x,y:material['dark'])
        poly(s,[point(u,v,True) for u,v in inner]+[point(u,v) for u,v in inner[::-1]],lambda x,y:material['deep'])
        pts=[point(u,v) for u,v in outer+inner[::-1]]
        poly(s,pts,lambda x,y,n=n:material['lit' if along_i else 'dark'] if n%3 else material['mid'])
        seg(s,pts[0],pts[-1],material['line'])
    for u in (0,width-.16):
        if along_i:block(s,i+u,j,.16,depth,spring,material,z=z)
        else:block(s,i,j+u,depth,.16,spring,material,z=z)


def museum(scene,i,j,z=0):
    """Long low modernist museum: six open piers and the 13-figure Albanians mosaic.
    South square front is explicitly snapped to SW; mosaic occurs only on that face."""
    W,D,H=12,5,38
    def draw(s):
        def side(u,v,lit):
            c=int(u)%12
            if 4<c<7 and 11<v<32:return LEAD['deep'] if c==5 else GLASS['dark']
            return stone_courses(STONE,6,15)(u,v,lit)
        block(s,i,j,W,D-1.5,H,STONE,side,z=z)
        flat_roof(s,i,j,W,D-1.5,z+H)
        for a in (i,i+W-2):
            block(s,a,j+D-1.6,2,1.7,H,STONE,side,z=z)
            band(s,a,j+D-1.6,2,1.7,z+H,WHITE,2)
        # Recessed glass entrance and balcony behind six genuinely separate piers.
        block(s,i+2,j+D-1.8,8,.15,23,LEAD,
              lambda u,v,lit:WHITE['dark'] if int(u)%7==0 or int(v)%10==0 else GLASS['dark'],z=z+3)
        block(s,i+2,j+D-1.2,8,.8,2,STONE,z=z+17)
        for k in range(6):
            a=i+2.3+k*1.43
            block(s,a,j+D-.8,.36,.9,24,WHITE,stone_courses(WHITE,6,10),z=z+3)
        # Gold tessera field; thirteen individually posed figures and the red banner.
        # u is along the lit face, v height above the panel's own base.
        span=8.4*8
        def mosaic(u,v,lit):
            if not lit:return stone_courses(STONE,5,12)(u,v,lit)
            if u<2 or u>span-2 or v<2 or v>18:return STONE['hi']
            x=u-3; c=int(x/4.65); local=x-c*4.65
            if 34<x<48 and 13<v<18:
                # The banner is Albanian: retain its double-headed eagle even at mural scale.
                eagle={(1,2),(3,2),(0,1),(1,1),(2,1),(3,1),(4,1),(1,0),(2,0),(3,0)}
                if (int(x-39),int(v-14)) in eagle:return IRON
                return RED if int(x+v)%5 else CLAY['dark']
            base=GOLD['lit'] if int(u+2*v)%5 else GOLD['mid']
            if c>=13:return base
            height=10+(c*3)%5; top=height+2
            if 1.2<local<2.9 and top-2<v<top:return OCHRE['dark']
            if 1.6<local<2.4 and top-3<v<=top-2:return OCHRE['mid']
            half=1.5 if v>top-5 else 1 if c!=6 else 1.6
            if abs(local-2)<half and 5<v<top-3:
                if int(v)==6:return RED if c in (3,6,9) else BRONZE['deep']
                return (WHITE,BRONZE,CLAY,BLUE)[c%4]['lit']
            if 6<v<top-2 and abs(local-(.2+(v-6)*.3 if c%2 else 4.4-(v-6)*.3))<.6:
                return WHITE['mid'] if c%3 else BRONZE['dark']
            if 1<local<1.8 and 2<v<5 or 2.6<local<3.3 and 2<v<5:return LEAD['deep']
            if c in (0,2,9,11) and abs(local-(v-5)*.21)<.4 and 5<v<17:return BRONZE['deep']
            return base
        block(s,i+1.8,j+D-.7,8.4,1,21,STONE,mosaic,z=z+27)
        band(s,i+1.8,j+D-.7,8.4,1,z+47,STONE,1)
        for k in range(5):block(s,i+1,j+D+.3+k*.3,10,.35,5-k,STONE,z=z)
    scene.add(i+j+W+D+3,draw)


def culture(scene,i,j,z=0):
    """West-facing long low cultural palace, snapped to SW: deep square-pier colonnade."""
    W,D,H=13,4.5,35
    def draw(s):
        def glazing(u,v,lit):
            if 3<v<31:
                if int(u)%9==0 or int(v) in (11,22):return GOLD['dark']
                if 12<v<22:return STONE['lit' if lit else 'dark']
                return GLASS['dark' if int(u)%9>3 else 'mid']
            return stone_courses(STONE,5,13)(u,v,lit)
        block(s,i,j,W,D-1.1,H,STONE,glazing,z=z+4)
        flat_roof(s,i,j,W,D,z+H+4)
        # Deep soffit and square piers; gaps remain open, unlike a striped facade texture.
        for k in range(11):
            a=i+.2+k*1.24
            block(s,a,j+D-.7,.3,.65,H,STONE,stone_courses(STONE,6,12),z=z+4)
            block(s,a-.06,j+D-.76,.42,.77,1.5,WHITE,z=z+4)
        block(s,i,j+D-.8,W,1,5,STONE,stone_courses(STONE,5,13),z=z+H)
        band(s,i,j+D-.8,W,1,z+H+5,WHITE,2)
        for k in range(5):block(s,i-.1,j+D+.25+k*.22,W+.2,.27,5-k,STONE,z=z)
        # Lateral return has its own windows; no OPERA lettering baked into the image.
        for a in (i+.1,i+W-.4):
            block(s,a,j+.2,.28,D-.7,1.4,WHITE,z=z+H+6)
    scene.add(i+j+W+D+2,draw)


def mosque(scene,i,j,z=0):
    """One lead dome, one stone minaret, clay L-portico and painted landscape spandrels.
    Rotate the building 180° to expose the real N/E porch on visible SW/SE sides."""
    W,D,H=5.8,6.3,28
    def draw(s):
        def prayer(u,v,lit):
            for a,b in ((5,13),(17,23)):
                if a<v<b:
                    opening=arch_opening(int(u)%12,v-a,6,2.2,b-a-2,WOOD)
                    if opening:return opening
            return stone_courses(OCHRE,6,14)(u,v,lit)
        block(s,i+.25,j+.25,W-1.4,D-1.5,H,OCHRE,prayer,z=z)
        band(s,i+.25,j+.25,W-1.4,D-1.5,z+H-2,WHITE,2)
        hip_roof(s,i+.15,j+.15,W-1.2,D-1.3,z+H,5,CLAY)
        ci,cj=i+2.5,j+2.6
        cylinder(s,ci,cj,2.12,2.12,z+H,5,OCHRE,stone_courses(OCHRE,4,12),segments=8)
        revolve(s,ci,cj,2.23,z+H+5,17,DOME,LEAD,ribs=6)
        seg(s,P(s,ci,cj,z+H+22),P(s,ci,cj,z+H+28),GOLD['dark'])
        cylinder(s,ci,cj,.12,.12,z+H+27,2,GOLD)
        # Separate minaret at the NW corner, carried to SE by the documented turn.
        mi,mj=i+W-.35,j+2.15
        block(s,mi-.5,mj-.5,1,1,9,STONE,z=z)
        cylinder(s,mi,mj,.38,.38,z+9,58,STONE,stone_courses(STONE,5,10),segments=12)
        for zz,r,h in ((65,.48,2),(67,.65,2),(69,.64,3),(72,.44,1)):
            cylinder(s,mi,mj,r,r,z+zz,h,WHITE,segments=12)
        for n in range(12):
            a=n*math.tau/12
            seg(s,P(s,mi+.62*math.cos(a),mj+.62*math.sin(a),z+69),P(s,mi+.62*math.cos(a),mj+.62*math.sin(a),z+74),STONE['deep'])
        cylinder(s,mi,mj,.28,.28,z+73,16,STONE,stone_courses(STONE,4,9),segments=12)
        revolve(s,mi,mj,.43,z+89,21,[(0,1),(.15,.9),(1,.02)],LEAD,ribs=4)
        seg(s,P(s,mi,mj,z+110),P(s,mi,mj,z+115),GOLD['dark'])
        # Actual portico along the two visible walls, arches and iron glazing under clay eaves.
        # Distinct landscape panels occupy the spandrels, never spill across an opening.
        def fresco(u,v,lit):
            if int(v) in (0,4):return CLAY['line']
            if int(u)%10 in (1,8) and 1<v<4:return BRONZE['mid']
            if 1<v<3 and 2<int(u)%10<8:return BRONZE['lit'] if int(u)%10<5 else BLUE['lit']
            return OCHRE['lit' if lit else 'dark']
        for a in range(4):
            ai=i+.1+a*1.35
            open_arch(s,ai,j+D-1,1.3,.55,z+3,19,WHITE)
            # Glass/iron screens lie inside the opening in their own plane.
            for t in (.35,.7,.98):
                seg(s,P(s,ai+t,j+D-.48,z+4),P(s,ai+t,j+D-.48,z+16),IRON)
        for b in range(3):open_arch(s,i+W-1,j+.15+b*1.45,1.4,.55,z+3,19,WHITE,False)
        block(s,i,j+D-1.05,W-1,.65,5,OCHRE,fresco,z=z+19)
        block(s,i+W-1.1,j,.65,D-1,5,OCHRE,fresco,z=z+19)
        hip_roof(s,i-.1,j+D-1.2,W-.7,1.5,z+24,6,CLAY)
        hip_roof(s,i+W-1.2,j-.1,1.5,D-.7,z+24,6,CLAY)
        band(s,i,j+D-.95,W-1,.6,z+2,STONE,2)
    scene.add(i+j+W+D+1,draw)


def clock_tower(scene,i,j,z=0):
    """Square rubble shaft, balcony, four dials, open belfry and dark pyramidal cap."""
    W,D=2.8,2.8
    def draw(s):
        def shaft(u,v,lit):
            if 2<v<12:
                opening=arch_opening(u,v-2,W*4,2.7,6,WOOD)
                if opening:return opening
            if 3<int(u)%15<5 and int(v)%25 in range(14,20):return STONE['deep']
            return stone_courses(STONE,5,10)(u,v,lit)
        block(s,i,j,W,D,50,STONE,shaft,z=z)
        band(s,i-.25,j-.25,W+.5,D+.5,z+48,WHITE,3)
        # Balustrade around a projecting viewing gallery.
        for n in range(8):
            a=i-.18+n*.43;b=j-.18+n*.43
            block(s,a,j+D+.1,.13,.15,4.5,WHITE,z=z+51)
            block(s,i+W+.1,b,.15,.13,4.5,WHITE,z=z+51)
        band(s,i-.22,j-.22,W+.44,D+.44,z+55,WHITE,1.5)
        block(s,i+.12,j+.12,W-.24,D-.24,25,WHITE,
              windows(WHITE,25,10,25,arched=True,width=5),z=z+51)
        band(s,i+.1,j+.1,W-.2,D-.2,z+64,STONE,1.5)
        clock(s,i+W/2,j+D-.09,6.3,z+70)
        clock(s,i+W-.09,j+D/2,6.3,z+70,False)
        # Back faces also carry real dials; naturally hidden in this projection.
        band(s,i-.05,j-.05,W+.1,D+.1,z+77,WHITE,2)
        for a,b in ((i+.12,j+.12),(i+W-.38,j+.12),(i+.12,j+D-.38),(i+W-.38,j+D-.38)):
            cylinder(s,a+.13,b+.13,.13,.13,z+79,15,WHITE,segments=8)
            block(s,a-.05,b-.05,.36,.36,1.5,WHITE,z=z+93)
        # Hanging bell is inside the genuinely open loggia.
        revolve(s,i+W/2,j+D/2,.4,z+84,7,[(0,1),(.2,1),(.8,.55),(1,.3)],BRONZE,ribs=4)
        hip_roof(s,i-.15,j-.15,W+.3,D+.3,z+95,17,LEAD)
        seg(s,P(s,i+W/2,j+D/2,z+112),P(s,i+W/2,j+D/2,z+117),GOLD['dark'])
    scene.add(i+j+W+D+1,draw)


def skanderbeg(scene,i,j,z=0):
    """Solid horse with one raised foreleg, armoured rider, horned helm, cape and sword.
    Southward facing snapped to SE (+i); exact real azimuth remains unconfirmed."""
    W,D=5.2,4.2
    def draw(s):
        ci,cj=i+W/2,j+D/2
        for k,(wi,wj,h) in enumerate(((5.2,4.2,5),(4.7,3.9,6),(4.2,3.4,6),(3.8,3.1,5))):
            quad=[(ci-wi/2,cj-wj/2),(ci+wi/2-.25,cj-wj/2-.15),
                  (ci+wi/2,cj+wj/2-.2),(ci-wi/2+.2,cj+wj/2)]
            slab(s,quad,z+k*5,z+k*5+h,ROCK,stone_courses(ROCK,5,15))
            # Small fractures and chipped faces prevent a staircase-like pedestal.
            a,b=quad[2]
            seg(s,P(s,a-.3,b,z+k*5+1),P(s,a-.4,b,z+k*5+4),ROCK['line'])
        before=s.img.copy()
        base=z+22
        # Three load-bearing legs, with shaped hocks and heavy hooves.
        for a,b,back in ((ci-1,cj-.45,True),(ci-1,cj+.45,True),(ci+.95,cj-.45,False)):
            block(s,a-.18,b-.15,.39,.34,2.3,BRONZE,z=base)
            cylinder(s,a,b,.12,.13,base+2,8,BRONZE,segments=12)
            ellipsoid(s,a-.1 if back else a,b,base+10,.19,.18,2.4,BRONZE)
            ellipsoid(s,a-.1 if back else a,b,base+14,.24,.22,5,BRONZE)
        # Heavy tail behind the rump, reaching to the heel.
        for k in range(7):
            ellipsoid(s,ci-1.18-k*.09,cj+.05,base+14-k*1.6,.22-k*.016,.19-k*.012,2.6,BRONZE)
        ellipsoid(s,ci-.2,cj,base+18,1.3,.67,7,BRONZE)
        ellipsoid(s,ci-.95,cj,base+18,.7,.64,6.5,BRONZE)
        ellipsoid(s,ci+.62,cj,base+20,.66,.63,7.3,BRONZE)
        # The lifted visible foreleg bends forward at its knee.
        ellipsoid(s,ci+.8,cj+.49,base+17,.22,.2,5,BRONZE)
        ellipsoid(s,ci+1.05,cj+.52,base+13,.32,.2,2.2,BRONZE)
        ellipsoid(s,ci+1.32,cj+.52,base+13,.2,.18,3.5,BRONZE)
        block(s,ci+1.21,cj+.38,.42,.34,2.1,BRONZE,z=base+10)
        # Arched neck sweeps up out of the chest, then the head turns down at its muzzle.
        for k in range(5):
            ellipsoid(s,ci+.65+k*.11,cj,base+23+k*2.1,.52-k*.045,.43-k*.025,4.1,BRONZE)
        ellipsoid(s,ci+1.16,cj,base+33,.48,.3,3.7,BRONZE)
        ellipsoid(s,ci+1.47,cj+.03,base+31,.42,.26,2,BRONZE)
        for b in (cj-.21,cj+.21):ellipsoid(s,ci+1.02,b,base+37,.1,.08,2.2,BRONZE)
        for k in range(8):
            ellipsoid(s,ci+.35+k*.075,cj-.33,base+22+k*1.7,.18,.15,1.7,BRONZE)
        seg(s,P(s,ci+1.35,cj+.27,base+33),P(s,ci+1.55,cj+.24,base+30),BRONZE['deep'])
        # Saddle and rider. Cape lies behind the rider, leaving the horse's flank visible.
        ellipsoid(s,ci-.12,cj,base+24,.56,.74,2,LEAD)
        slab(s,[(ci-.5,cj-.15),(ci-.25,cj-.4),(ci-1.35,cj-.22),(ci-1.35,cj+.25)],
             base+21,base+37,BRONZE)
        for b in (cj-.73,cj+.73):
            ellipsoid(s,ci,b,base+23,.23,.17,4,BRONZE)
            ellipsoid(s,ci+.14,b,base+18,.16,.16,3.6,BRONZE)
            block(s,ci+.02,b-.12,.48,.25,2,BRONZE,z=base+14)
        ellipsoid(s,ci-.1,cj,base+29,.43,.36,5.5,BRONZE)
        ellipsoid(s,ci-.05,cj,base+34,.5,.35,4.5,BRONZE)
        cylinder(s,ci,cj,.13,.13,base+38,2,BRONZE)
        ellipsoid(s,ci+.04,cj,base+42,.27,.23,3.2,BRONZE)
        ellipsoid(s,ci+.25,cj+.02,base+40.5,.16,.16,2.2,BRONZE)
        revolve(s,ci+.02,cj,.32,base+44,3,[(0,1),(.5,.85),(1,.3)],BRONZE,ribs=0)
        for b in (cj-.23,cj+.23):
            seg(s,P(s,ci,b,base+46),P(s,ci+.24,b,base+49),BRONZE['hi'],2)
            seg(s,P(s,ci+.24,b,base+49),P(s,ci+.39,b,base+47),BRONZE['dark'])
        # Solid bent arms, reins and a low-held curved sword beside the shoulder.
        ellipsoid(s,ci+.25,cj+.39,base+34,.21,.18,3.6,BRONZE)
        ellipsoid(s,ci+.55,cj+.39,base+31,.4,.16,1.8,BRONZE)
        seg(s,P(s,ci+.8,cj+.39,base+31),P(s,ci+1.4,cj+.27,base+32),IRON)
        ellipsoid(s,ci-.31,cj-.42,base+34,.18,.18,4,BRONZE)
        seg(s,P(s,ci-.3,cj+.47,base+31),P(s,ci-.5,cj+.47,base+47),BRONZE['hi'])
        seg(s,P(s,ci-.5,cj+.47,base+47),P(s,ci-.72,cj+.47,base+52),BRONZE['hi'])
        # One silhouette outline around the complete bronze group, without outlining every
        # anatomical mesh seam and turning the small sculpture into a cluster of dark beads.
        changed=ImageChops.difference(before,s.img).convert('RGB')
        box=changed.getbbox()
        if box:
            pixels=changed.load()
            cover={(x,y) for y in range(box[1],box[3]) for x in range(box[0],box[2]) if pixels[x,y]!=(0,0,0)}
            iso.outline(s,cover,BRONZE['outline'])
    scene.add(i+j+W+D+1,draw)


def cathedral(scene,i,j,z=0):
    """Blue-domed rotunda, grand blue-glazed SW arch, and separate SW four-candle tower."""
    W,D=9,9
    def draw(s):
        ci,cj=i+4.9,j+3.6
        cylinder(s,ci,cj,3.5,3.5,z,31,WHITE,windows(WHITE,31,10,16,arched=True),segments=32)
        cylinder(s,ci,cj,3.55,3.55,z+30,9,WHITE,
                 lambda u,v,lit:BLUE['dark'] if 1<int(u)%6<4 and 2<v<8 else stone_courses(WHITE,5,12)(u,v,lit))
        revolve(s,ci,cj,3.65,z+39,26,DOME,BLUE,ribs=6)
        seg(s,P(s,ci,cj,z+65),P(s,ci,cj,z+75),GOLD['dark'],2)
        seg(s,P(s,ci-.32,cj,z+72),P(s,ci+.32,cj,z+72),GOLD['lit'])
        # Gold-copper buttress roofs are separate from the main blue dome.
        for a,b in ((ci-3,cj-.1),(ci+3,cj-.1),(ci,cj-3)):
            cylinder(s,a,b,.65,.65,z,32,WHITE,stone_courses(WHITE,6,13),segments=16)
            revolve(s,a,b,.72,z+32,7,DOME,GOLD,ribs=4)
        fw=7*8
        def entrance(u,v,lit):
            if not lit:return windows(WHITE,43,10,16,arched=True)(u,v,lit)
            dx=(u-fw/2)/(fw/2-3)
            inner=8+25*math.sqrt(max(0,1-dx*dx))
            outer=9+32*math.sqrt(max(0,1-dx*dx))
            if abs(dx)<1 and inner<v<outer:
                return WHITE['mid'] if int(u)%7==0 or int(v)%8==0 else BLUE['dark' if u>fw/2 else 'mid']
            if abs(u-fw/2)<7 and v<17:return BRONZE['mid'] if int(u)%5 else BRONZE['deep']
            return stone_courses(WHITE,9,18)(u,v,lit)
        a,b=i+1.2,j+6.6
        block(s,a,b,7,.6,43,WHITE,entrance,z=z)
        # The grand entrance's outline is a gently curved arch, not a rectangular blank wall.
        for k in range(22):
            u0,u1=k/22,(k+1)/22
            z0,z1=z+40+10*math.sin(u0*math.pi),z+40+10*math.sin(u1*math.pi)
            pts=[P(s,a+7*u0,b,z+40),P(s,a+7*u1,b,z+40),P(s,a+7*u1,b,z1),P(s,a+7*u0,b,z0)]
            poly(s,pts,lambda x,y:WHITE['mid'])
            pts=[P(s,a+7*u0,b+.6,z+40),P(s,a+7*u1,b+.6,z+40),P(s,a+7*u1,b+.6,z1),P(s,a+7*u0,b+.6,z0)]
            poly(s,pts,lambda x,y:WHITE['lit'])
            seg(s,pts[2],pts[3],GOLD['mid'])
        for a0 in (a-.35,a+6.95):block(s,a0,b-.1,.45,.8,45,STONE,z=z)
        # Bronze cross and wheat sprigs on the white inner tympanum.
        c,d=a+3.5,b+.62
        seg(s,P(s,c,d,z+20),P(s,c,d,z+29),GOLD['dark'],2)
        seg(s,P(s,c-.32,d,z+26),P(s,c+.32,d,z+26),GOLD['lit'])
        for direction in (-1,1):
            for k in range(5):
                seg(s,P(s,c+direction*(.5+k*.07),d,z+20+k),P(s,c+direction*(.8+k*.07),d,z+21+k),GOLD['mid'])
        for k in range(6):block(s,i+1,j+7.3+k*.24,7.4,.29,6-k,WHITE,z=z)
        # Detached tower remains SW of the rotunda: +j, with a small gap to its entrance.
        ti,tj=i-.2,j+8.4
        block(s,ti-.85,tj-.85,1.7,1.7,4,STONE,z=z)
        cylinder(s,ti,tj,.24,.24,z+4,71,WHITE,stone_courses(WHITE,8,13),segments=12)
        for di,dj in ((-.55,-.55),(.55,-.55),(-.55,.55),(.55,.55)):
            cylinder(s,ti+di,tj+dj,.2,.2,z+4,94,STONE,stone_courses(STONE,9,12),segments=12)
        for zz in (65,77,89):
            block(s,ti-.78,tj-.78,1.56,1.56,2,WHITE,z=z+zz)
        # Two open stages and visible hanging bells between the four candle shafts.
        for zz in (68,80):
            for di,dj in ((-.3,.35),(.35,.35),(.35,-.3)):
                revolve(s,ti+di,tj+dj,.16,z+zz,5,[(0,1),(.3,1),(.85,.55),(1,.25)],GOLD,ribs=0)
        block(s,ti-.5,tj-.5,1,1,10,WHITE,z=z+90)
        clock(s,ti,tj+.51,3,z+95);clock(s,ti+.51,tj,3,z+95,False)
        revolve(s,ti,tj,.8,z+100,9,DOME,GOLD,ribs=4)
        seg(s,P(s,ti,tj,z+109),P(s,ti,tj,z+116),GOLD['dark'])
        seg(s,P(s,ti-.22,tj,z+114),P(s,ti+.22,tj,z+114),GOLD['lit'])
    scene.add(i+j+W+D+3,draw)


def tanners(scene,i,j,z=0):
    """Humped bridge on dry former channel, one main arch and two small approach arches."""
    W,D=2.1,7.4
    def draw(s):
        # Extruded arch sections along j: top and intrados leave the ground visible below.
        def arch(start,length,rise,base):
            for k in range(22):
                ts=(k/22,(k+1)/22);js=[start+length*t for t in ts]
                low=[base+rise*math.sqrt(max(0,1-(2*t-1)**2)) for t in ts]
                high=[v+4 for v in low]
                for a,lit in ((i,True),(i+W,False)):
                    pts=[P(s,a,js[0],z+low[0]),P(s,a,js[1],z+low[1]),P(s,a,js[1],z+high[1]),P(s,a,js[0],z+high[0])]
                    poly(s,pts,lambda x,y,lit=lit:STONE['line'] if (x+2*y)%11==0 else STONE['lit' if lit else 'dark'])
                    if k%2==0:seg(s,pts[0],pts[3],STONE['line'])
                poly(s,[P(s,i,js[0],z+low[0]),P(s,i+W,js[0],z+low[0]),P(s,i+W,js[1],z+low[1]),P(s,i,js[1],z+low[1])],lambda x,y:STONE['deep'])
                poly(s,[P(s,i,js[0],z+high[0]),P(s,i+W,js[0],z+high[0]),P(s,i+W,js[1],z+high[1]),P(s,i,js[1],z+high[1])],
                     lambda x,y:GROUND['cobble_joint'] if (x+2*y)%5==0 else STONE['mid'])
                for a in (i,i+W-.15):
                    poly(s,[P(s,a,js[0],z+high[0]),P(s,a,js[1],z+high[1]),P(s,a,js[1],z+high[1]+3),P(s,a,js[0],z+high[0]+3)],lambda x,y:STONE['lit' if a==i else 'dark'])
        arch(j+1.25,4.9,18,0)
        arch(j,1.25,5,0);arch(j+6.15,1.25,5,0)
        # Real stone abutments and piers support the separate arches.
        for b in (j-.2,j+1.12,j+6.04,j+D-.05):block(s,i-.1,b,W+.2,.24,5,STONE,z=z)
    scene.add(i+j+W+D+1,draw)


def pyramid(scene,i,j,z=0):
    """2023 cultural centre: low radial shell, stepped concrete ribs, glazing, colourful cubes."""
    W,D=10,10
    def draw(s):
        ci,cj=i+W/2,j+D/2
        # Sixteen radial structural ribs fan from a truncated circular summit.
        # Every horizontal tread is a 3D quad; glazed wedges remain between ribs.
        N=16;R=4.8;top=.85;height=43
        def point(ang,t):
            r=R+(top-R)*t
            return ci+r*math.cos(ang),cj+r*math.sin(ang),z+3+height*t
        order=sorted(range(N),key=lambda n:math.cos((n+.5)*math.tau/N)+math.sin((n+.5)*math.tau/N))
        for n in order:
            a,b=n*math.tau/N,(n+1)*math.tau/N
            pts=[P(s,*point(ang,t)) for ang,t in ((a,0),(b,0),(b,1),(a,1))]
            poly(s,pts,lambda x,y,n=n:BLUE['line'] if (x+2*y)%9==0 else GLASS['dark' if n%3 else 'mid'])
            # Glazing mullions follow the slope and its true cross-sectional rings.
            for step in range(1,4):seg(s,P(s,*point(a,step/4)),P(s,*point(b,step/4)),CONCRETE['mid'])
            for ang in (a+(b-a)*.4,a+(b-a)*.7):seg(s,P(s,*point(ang,0)),P(s,*point(ang,1)),CONCRETE['dark'])
        # Glazing is complete before stairs: adjacent wedge fills cannot erase half a rib.
        for n in order:
            a=n*math.tau/N
            # One broad stair flight per rib, with its vertical risers and parapet edge.
            width=.13
            for step in range(20):
                t,nt=step/20,(step+1)/20
                lo=[point(a+da,t) for da in (-width,width)]
                hi=[point(a+da,nt) for da in (-width,width)]
                tread=[P(s,x,y,hi[0][2]) for x,y,_ in lo]+[P(s,*hi[1]),P(s,*hi[0])]
                poly(s,tread,lambda x,y:CONCRETE['lit'])
                poly(s,[P(s,*lo[0]),P(s,*lo[1]),P(s,lo[1][0],lo[1][1],hi[0][2]),P(s,lo[0][0],lo[0][1],hi[0][2])],lambda x,y:CONCRETE['dark'])
            seg(s,P(s,*point(a-width,0)),P(s,*point(a-width,1)),CONCRETE['hi'])
        cylinder(s,ci,cj,.9,.9,z+45,2,CONCRETE,segments=24)
        cylinder(s,ci,cj,.45,.45,z+47,.8,BLUE,segments=24)
        # Individual climate-controlled cubes: roof and wall tones, glazing and doors.
        for k,(a,b,w,d,zz) in enumerate(((i+.2,j+5,1.5,1.3,0),(i+8,j+6,1.3,1.5,0),
            (i+2,j+8,1.5,1.2,0),(i+5.8,j+.7,1.3,1.2,0),(i+3,j+2.1,1.1,1,26))):
            mat=PAVILIONS[k]
            block(s,a,b,w,d,11,mat,windows(mat,11,7,12,width=4),z=z+zz)
            band(s,a,b,w,d,z+zz+11,mat,1)
    scene.add(i+j+W+D+1,draw)


def townhouse(scene,i,j,wi=2.5,wj=3,floors=2,seed=0,z=0):
    """Tirana painted villas: shutters, dressed panes, iron balconies, clay hips and chimneys."""
    material=palette_of(WALLS[seed%len(WALLS)]);H=floors*11+3
    base=windows(material,H,9,11,hood=True)
    def pattern(u,v,lit):
        c,level=int(u)%9,int(v)%11
        if v<10:
            if 2<=c<=6:
                if c in (2,6) or int(v)==9:return WHITE['lit' if lit else 'dark']
                return WOOD if (int(u)//9+seed)%3==0 else GLASS['dark']
            return material['line'] if int(v)%4==0 else None
        if seed%3 and c in (1,7) and 3<level<9:return BRONZE['mid' if lit else 'dark']
        return base(u,v,lit)
    def draw(s):
        block(s,i,j,wi,wj,H,material,pattern,z=z)
        band(s,i,j,wi,wj,z+1,STONE,2);band(s,i,j,wi,wj,z+H-2,WHITE,2)
        hip_roof(s,i-.2,j-.2,wi+.4,wj+.4,z+H,9+seed%3,CLAY)
        if seed%3==0:
            block(s,i+.45,j+wj,.95,.45,1.5,WHITE,z=z+12)
            for a in range(6):seg(s,P(s,i+.45+a*.19,j+wj+.43,z+14),P(s,i+.45+a*.19,j+wj+.43,z+18),IRON)
            seg(s,P(s,i+.45,j+wj+.43,z+18),P(s,i+1.4,j+wj+.43,z+18),IRON)
            for a in (i+.55,i+1.2):block(s,a,j+wj,.18,.2,3,STONE,z=z+9)
        block(s,i+wi-.7,j+.5,.42,.48,8,STONE,stone_courses(STONE,3,6),z=z+H+3)
        band(s,i+wi-.7,j+.5,.42,.48,z+H+10,CLAY,2)
    scene.add(i+j+wi+wj+1,draw)


def main():
    for name,builder,_,_,_,elevation in SITES:
        print(preview([lambda s,b=builder,z=elevation:b(s,6,6,z=z)],'tirane-'+name,
                      size=(320,280),origin=(160,120),tiles=25))
    print(preview([lambda s,k=k:townhouse(s,3+k*3.6,4,floors=1+k%3,seed=k)
                   for k in range(6)],'tirane-houses',size=(340,240),origin=(80,75),tiles=27))
    import sprites
    im=sprites.kruje()
    path=Path(__file__).resolve().parents[2]/'docs/art/capitals/albania-kruje.png'
    im.resize((im.width*4,im.height*4),0).save(path)
    print(path)


# name, builder, footprint, real longitude/latitude, north-up ground anchor, elevation.
SITES = [
    ('museum',museum,(12,5),(19.817101,41.329418),(135,135),0),
    ('culture',culture,(13,4.5),(19.819638,41.328812),(490,155),0),
    ('mosque',mosque,(5.8,6.3),(19.819329,41.327802),(410,270),0),
    ('skanderbeg',skanderbeg,(5.2,4.2),(19.818557,41.327753),(330,285),0),
    ('clock-tower',clock_tower,(2.8,2.8),(19.819683,41.327703),(555,300),0),
    ('cathedral',cathedral,(9,9),(19.817597,41.326551),(245,375),0),
    ('tanners',tanners,(2.1,7.4),(19.826050,41.326424),(650,390),0),
    ('pyramid',pyramid,(10,10),(19.821536,41.323040),(580,470),0),
]


if __name__=='__main__':
    main()
