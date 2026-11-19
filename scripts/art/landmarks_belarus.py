"""Minsk's Baroque Upper Town, brick basilica and modern civic silhouettes in (i,j,z).

Two-source building coordinates, setting and explicit local facade turns: DEVELOPMENT_PLAN.md.
Run this module for six isolated 4× studies and the Minsk house study.
"""
import itertools
import math
from pathlib import Path

from iso import rgb
from landmarks_paris import P, seg, poly, corners, preview, GLASS
from landmarks_iberia import hip_roof, stone_courses, arch_opening, palette_of, tones
from landmarks_slovakia import block, band, pediment
from landmarks_bosnia import cylinder
from landmarks_slovenia import revolve, statue, balustrade
from landmarks_greece import column
from landmarks_denmark import clock

WHITE = tones('#FFFFF0','#EFEBDD','#D9D6C6','#B4B7AD','#7C847B','#BEC1B5','#49534C')
STONE = tones('#EEE9D8','#C8C6B4','#ACB0A2','#8A948B','#5D6A61','#9AA494','#394B42')
BRICK = tones('#E6AA88','#BE7655','#A55D43','#824531','#5D3027','#9A533D','#492B25')
RED = tones('#EC9D70','#BE6645','#A65135','#803C2A','#5A2C22','#98452D','#49271F')
GREEN = tones('#C2CFB3','#8BA890','#6E8C78','#4C6D5C','#354C42','#617E68','#2A3B32')
DARK = tones('#B6BFB5','#85958B','#677C70','#496154','#30473D','#5D7664','#273C32')
BRONZE = tones('#BDAD7D','#8C8D65','#6C7753','#485F43','#304331','#5D724D','#23392B')
GOLD = tones('#FFF0AB','#E4C26B','#C7A14D','#A17D34','#6B5325','#B18C40','#4F4124')
BLUE = tones('#DAEFF0','#A2CBCF','#7DAAB5','#527D91','#3B586F','#648D9D','#2B4057')
IRON, WOOD = rgb('#35453F'), rgb('#75523B')
WALLS = [rgb(c) for c in ('#DBD8B4','#D4DFCD','#E1C4AF','#C0D0CC','#E9DDC0','#D0C3CB')]
GROUND = {k:rgb(v) for k,v in {
    'square':'#DBD4BD','joint':'#B5B39F','rose':'#CBB59E','cobble':'#B6B8AA',
    'cobble_joint':'#929C8F','garden':'#8DAF70','garden_hi':'#A9C48A',
    'water':'#4C8F99','water_dark':'#376D81','water_hi':'#B7DEDA',
}.items()}


def windows(material, height, bay=12, floor=14, arched=False):
    courses=stone_courses(material,4,13)
    def pattern(u,v,lit):
        c,k=int(u)%bay,int(v)%floor
        trim=(material if material==BRICK else WHITE)['hi' if lit else 'mid']
        if int(v) in (1,2,height-3,height-2):return trim
        if 3<=c<=bay-3 and 3<=k<=floor-4 and 2<v<height-4:
            if arched and k>floor-5 and abs(c-bay/2)>bay/2-2-(k-floor+5)*.5:return None
            if c in (3,bay-3,bay//2) or k in (3,7,floor-4):return trim
            return BLUE['lit' if lit else 'dark']
        if k==2 and 2<=c<=bay-2:return trim
        return courses(u,v,lit) if material in (STONE,BRICK) else None
    return pattern


def cross(s,i,j,z,size=7):
    seg(s,P(s,i,j,z),P(s,i,j,z+size),GOLD['dark'])
    seg(s,P(s,i-.23,j,z+size*.67),P(s,i+.23,j,z+size*.67),GOLD['hi'])


def cathedral(scene,i,j,z=0):
    """Two equal Baroque bell towers and a shaped central gable; local WNW→SW turn."""
    w,d,h=8.4,8.6,31
    def draw(s):
        block(s,i+.5,j,w-1,d,h,WHITE,windows(WHITE,h,12,20,True),z=z)
        band(s,i+.5,j,w-1,d,z+h-2,WHITE,3)
        hip_roof(s,i+.4,j-.1,w-.8,d+.2,z+h+1,15,GREEN)
        # Pilastered frontage, confined to the actual lit face.
        def front(u,v,lit):
            if not lit:return windows(WHITE,37,12,20,True)(u,v,lit)
            c=int(u)%13
            if c in (0,1):return WHITE['hi']
            if 21<v<31 and 25<u<42:
                return GOLD['dark'] if int(u) in (26,41) or int(v) in (22,30) else BLUE['dark']
            if v<16:
                a=arch_opening(u,v,33.6,4.5,8,WOOD)
                if a:return WHITE['dark'] if abs(u-33.6)>3.4 else a
            return windows(WHITE,37,13,19,True)(u,v,lit)
        block(s,i,j+d-1.6,w,1.6,37,WHITE,front,z=z)
        for a in (i+.15,i+w-2.25):
            b=j+d-2
            def tower_wall(u,v,lit):
                c=int(abs(u))%17
                if c in (0,1,15,16):return WHITE['hi' if lit else 'mid']
                for bottom,top in ((8,19),(27,36),(40,51)):
                    if bottom<v<top:
                        frame=arch_opening(c,v-bottom,8.5,4,top-bottom-4,WHITE['hi' if lit else 'mid'])
                        opening=arch_opening(c,v-bottom-1,8.5,2.7,top-bottom-5,DARK['deep'])
                        if opening:return DARK['lit'] if int(v)%3==0 and v>40 else opening
                        if frame:return frame
                return WHITE['line'] if int(v)%13==0 else None
            block(s,a,b,2.1,2,55,WHITE,tower_wall,z=z)
            for zz in (18,35,51,54):band(s,a,b,2.1,2,z+zz,WHITE,2)
            revolve(s,a+1.05,b+1,1.48,z+57,22,[(0,1),(.18,1),(.32,.7),(.45,.4),(.57,.6),(.72,.48),(1,.02)],DARK,ribs=4,segments=32)
            cross(s,a+1.05,b+1,z+79)
        # Stepped scroll gable is a solid extruded 3D silhouette, not a painted rectangle.
        for n,(ww,hh) in enumerate(((4.3,6),(3.4,5),(2.5,5),(1.6,4))):
            block(s,i+w/2-ww/2,j+d-1.2,ww,.9,hh,WHITE,z=z+36+n*4)
            band(s,i+w/2-ww/2,j+d-1.2,ww,.9,z+36+n*4+hh-1,WHITE)
        cross(s,i+w/2,j+d-.7,z+56,6)
        for n in range(4):block(s,i+2.4-n*.18,j+d+n*.24,3.6+n*.36,.26,4-n,STONE,z=z)
    scene.add(i+j+w+d+2,draw)


def city_hall(scene,i,j,z=0):
    """Low civic hall, four-column portico, one clock tower; NW front locally snapped SW."""
    w,d,h=10,5,25
    def draw(s):
        block(s,i,j,w,d,h,WHITE,windows(WHITE,h,12,18),z=z)
        for zz in (1,h-2):band(s,i,j,w,d,z+zz,WHITE,2)
        hip_roof(s,i-.1,j-.1,w+.2,d+.2,z+h,9,GREEN)
        # Central tower first; porch is shallow enough not to hide its base.
        a,b=i+w/2-1.25,j+d/2-1.25
        block(s,a,b,2.5,2.5,33,WHITE,windows(WHITE,33,10,18),z=z+h+4)
        for zz in (h+5,h+34,h+37):band(s,a,b,2.5,2.5,z+zz,WHITE,2)
        clock(s,a+1.25,b+2.56,4.7,z+h+26)
        hip_roof(s,a-.15,b-.15,2.8,2.8,z+h+39,9,DARK)
        # Weather vane: arrow and pennant, no invented national flag.
        seg(s,P(s,a+1.25,b+1.25,z+h+48),P(s,a+1.25,b+1.25,z+h+57),IRON)
        seg(s,P(s,a+.75,b+1.25,z+h+54),P(s,a+1.8,b+1.25,z+h+54),GOLD['lit'])
        pa,pb=i+2.7,j+d
        block(s,pa-.2,pb,5,1.2,3,STONE,z=z)
        for n in range(4):column(s,pa+.25+n*1.35,pb+.85,z+3,21,.25,WHITE)
        block(s,pa-.2,pb,5,1.2,3,WHITE,z=z+24)
        pediment(s,pa-.3,pb,5.2,1.3,z+27,8,WHITE)
        for n in range(3):block(s,pa-.4-n*.2,pb+1.2+n*.25,5.4+n*.4,.27,3-n,STONE,z=z)
    scene.add(i+j+w+d+3,draw)


def red_church(scene,i,j,z=0):
    """Three unequal towers; local 180° turn exposes the photographed NE transept as SW.

    Real tallest tower SE becomes NW (-i); two altar towers NW become SE (+i).
    """
    def rose(s,i,j,z,r=6):
        """Circular tracery constructed in the SW facade plane, with eight glass petals."""
        centre=P(s,i,j,z)
        # Tangent vector follows the facade (+i); vertical component is actual height.
        for rad,col in ((r+2,BRICK['deep']),(r+1,RED['hi']),(r,BLUE['dark'])):
            pts=[P(s,i+rad/8*math.cos(t*math.tau/40),j,z+rad*math.sin(t*math.tau/40)) for t in range(40)]
            poly(s,pts,lambda x,y,col=col:col)
        for n in range(8):
            t=n*math.tau/8
            seg(s,centre,P(s,i+r/8*math.cos(t),j,z+r*math.sin(t)),BRICK['hi'])
        cylinder(s,i,j,.14,.07,z-1,2,GOLD,segments=12)

    w,d,h=10,5.8,32
    def tower_windows(height):
        base=windows(BRICK,height,10,21,True)
        def pattern(u,v,lit):
            c=int(abs(u))%7
            if height-16<v<height-4:
                frame=arch_opening(c,v-height+16,3.5,2.5,7,BRICK['hi' if lit else 'mid'])
                opening=arch_opening(c,v-height+15,3.5,1.5,6,DARK['deep'])
                if opening:return BRONZE['dark'] if int(v)==height-9 and c==3 else opening
                if frame:return frame
            return base(u,v,lit)
        return pattern

    def draw(s):
        block(s,i,j,w,d,h,BRICK,windows(BRICK,h,11,20,True),z=z)
        band(s,i,j,w,d,z+h-2,RED,2)
        hip_roof(s,i-.1,j-.1,w+.2,d+.2,z+h,18,RED)
        # Two small altar towers at the far +i end after the documented turn.
        for b in (j-.1,j+d-1.45):
            a=i+w-1.7
            block(s,a,b,1.8,1.65,49,BRICK,tower_windows(49),z=z)
            for zz in (19,35,47):band(s,a,b,1.8,1.65,z+zz,RED,2)
            hip_roof(s,a-.15,b-.15,2.1,1.95,z+50,16,RED)
            cross(s,a+.9,b+.8,z+66,5)
        # Tall four-tier tower stands on the opposite end, with broad arched belfries.
        a,b=i-.2,j+d-2.5
        block(s,a,b,2.8,2.8,68,BRICK,tower_windows(68),z=z)
        for zz in (16,33,49,65):band(s,a,b,2.8,2.8,z+zz,RED,2)
        hip_roof(s,a-.12,b-.12,3.04,3.04,z+69,23,RED)
        cross(s,a+1.4,b+1.4,z+92,6)
        # Projecting transept: rose, recessed triple entry and corbelled gable.
        a,b,ww=i+3,j+d-.1,4.3
        def front(u,v,lit):
            if not lit:return windows(BRICK,39,11,20,True)(u,v,lit)
            if v<13:
                for c in (7,17,27):
                    frame=arch_opening(u,v,c,3.8,6,RED['hi'])
                    hole=arch_opening(u,v,c,2.6,5,WOOD)
                    if hole:return hole
                    if frame:return frame
            return stone_courses(BRICK,3,9)(u,v,lit)
        block(s,a,b,ww,1,39,BRICK,front,z=z)
        pediment(s,a-.12,b,ww+.24,1,z+39,18,RED)
        rose(s,a+ww/2,b+1.02,z+29,7)
        for n in range(9):
            u=a+.25+n*(ww-.5)/8
            zz=z+40+17*(1-abs(2*n/8-1))
            block(s,u,b+1,.13,.15,2,BRICK,z=zz)
        for n in range(3):block(s,a-.25-n*.18,b+1+n*.24,ww+.5+n*.36,.26,3-n,STONE,z=z)
    scene.add(i+j+w+d+4,draw)


def opera(scene,i,j,z=0):
    """Broad receding cylindrical tiers, colonnaded SW entry, Apollo/winged Glories."""
    ci,cj=i+5.7,j+5.7
    def draw(s):
        cylinder(s,ci,cj,5.8,5.8,z,4,STONE,segments=64)
        cylinder(s,ci,cj,5.5,5.5,z+4,25,WHITE,windows(WHITE,25,12,22),segments=64)
        cylinder(s,ci,cj,5.65,5.65,z+28,3,WHITE,segments=64)
        cylinder(s,ci,cj,4.6,4.6,z+31,18,WHITE,windows(WHITE,18,10,20),segments=64)
        cylinder(s,ci,cj,4.78,4.78,z+48,3,WHITE,segments=64)
        cylinder(s,ci,cj,3.65,3.65,z+51,10,WHITE,windows(WHITE,10,12,14),segments=64)
        cylinder(s,ci,cj,3.8,3.8,z+60,3,STONE,segments=64)
        for radius,zz in ((5.55,31),(4.68,51),(3.72,63)):
            ring=[P(s,ci+radius*math.cos(n*math.tau/64),cj+radius*math.sin(n*math.tau/64),z+zz) for n in range(64)]
            for p,q in zip(ring,ring[1:]+ring[:1]):seg(s,p,q,WHITE['hi'])
        for n in range(8):
            t=n*math.tau/8
            seg(s,P(s,ci+.6*math.cos(t),cj+.6*math.sin(t),z+63),
                P(s,ci+3.5*math.cos(t),cj+3.5*math.sin(t),z+63),STONE['line'])
        # Flat terrace roofs keep the constructivist drum silhouette; no invented dome.
        a,b=i+2.5,j+9.7
        block(s,a,b,6.4,1.35,5,STONE,z=z)
        for n in range(8):column(s,a+.25+n*.83,b+1.0,z+5,27,.22,WHITE)
        block(s,a-.15,b-.1,6.7,1.6,4,WHITE,z=z+32)
        band(s,a-.15,b-.1,6.7,1.6,z+35,WHITE,2)
        for n in range(5):block(s,a-.2-n*.2,b+1.4+n*.3,6.8+n*.4,.32,5-n,STONE,z=z)
        # Solid bodies, bent arms and full triangular wing silhouettes at roof level.
        for offset in (1.0,3.2,5.4):
            ai,aj=a+offset,b+.8
            statue(s,ai,aj,z+38,13,BRONZE,arm=1 if offset==3.2 else 0)
            if offset!=3.2:
                for sign in (-1,1):
                    pts=[P(s,ai+sign*.1,aj,z+46),P(s,ai+sign*1.0,aj-.2,z+56),P(s,ai+sign*.8,aj,z+47)]
                    poly(s,pts,lambda x,y:BRONZE['lit'] if (x+y)%3 else BRONZE['dark'])
    scene.add(i+j+24,draw)


def victory(scene,i,j,z=0):
    """One granite obelisk, relief/sword pedestal, Order of Victory star and SW flame."""
    def draw(s):
        for n in range(3):block(s,i+n*.3,j+n*.3,4.8-n*.6,4.8-n*.6,3,STONE,z=z+n*3)
        block(s,i+1,j+1,2.8,2.8,17,STONE,stone_courses(STONE,4,12),z=z+9)
        for zz in (10,24):band(s,i+1,j+1,2.8,2.8,z+zz,STONE,2)
        # Relief panels are bounded to their own facade planes, with tiny raised figures.
        block(s,i+1.35,j+3.82,2.1,.12,10,BRONZE,
              lambda u,v,lit:BRONZE['hi'] if (int(u)%6==3 and int(v) in (7,8) or int(u)%6 in (2,3,4) and 4<int(v)<7 or int(u)%6 in (2,4) and 1<int(v)<4) else None,z=z+12)
        seg(s,P(s,i+2.4,j+3.98,z+13),P(s,i+2.4,j+3.98,z+23),GOLD['lit'],2)
        # Taper in 3D rather than a front-facing polygon.
        low=corners(s,i+1.45,j+1.45,1.9,1.9,z+26)
        high=corners(s,i+1.78,j+1.78,1.24,1.24,z+91)
        for indices,lit in (((3,2),True),((2,1),False)):
            a,b=indices
            poly(s,[low[a],low[b],high[b],high[a]],lambda x,y,lit=lit:STONE['line'] if y%9==0 else STONE['lit' if lit else 'dark'])
            seg(s,low[a],high[a],STONE['hi' if lit else 'deep'])
        hip_roof(s,i+1.76,j+1.76,1.28,1.28,z+91,6,STONE)
        # Ruby five-point order with a gold surround, lying in the visible SW plane.
        for radius,material in ((8,GOLD),(6,RED)):
            pts=[]
            for n in range(10):
                t=math.pi/2+n*math.pi/5;r=radius*(1 if n%2==0 else .45)
                pts.append(P(s,i+2.4+r/8*math.cos(t),j+2.4,z+103+r*math.sin(t)))
            poly(s,pts,lambda x,y,m=material:m['lit'] if (x+y)%3 else m['hi'])
        x,y=P(s,i+2.4,j+2.4,z+103)
        for dx in (-1,0,1):s.put(x+dx,y,BLUE['hi'])
        for a,b in ((i+2.4,j+.8),(i+.8,j+2.4),(i+4,j+2.4),(i+2.4,j+4)):
            ring=[P(s,a+.45*math.cos(n*math.tau/24),b+.45*math.sin(n*math.tau/24),z+9) for n in range(24)]
            for p,q in zip(ring,ring[1:]+ring[:1]):seg(s,p,q,BRONZE['lit'],2)
        # Eternal flame in its own inset brazier southwest of the obelisk.
        cylinder(s,i+2.1,j+5.25,.6,.45,z,2,BRONZE,segments=24)
        for n in range(5):
            x,y=P(s,i+2.1,j+5.25,z+2+n)
            s.put(x+(n%2),y,RED['hi']);s.put(x,y,GOLD['hi'])
    scene.add(i+j+11,draw)


def library(scene,i,j,z=0):
    """Actual 26-face rhombicuboctahedral mesh: six axial, twelve diagonal squares, eight triangles."""
    def draw(s):
        ci,cj=i+5,j+5
        cylinder(s,ci,cj,5.3,5.3,z,9,STONE,windows(STONE,9,10,12),segments=64)
        cylinder(s,ci,cj,5.45,5.45,z+8,3,WHITE,segments=64)
        block(s,i+3,j+8.7,4,1.4,9,BLUE,
              lambda u,v,lit:WHITE['mid'] if int(u)%6==0 or int(v)==7 else BLUE['dark'],z=z)
        a=1+math.sqrt(2)
        vertices=sorted({p for x in (-1,1) for y in (-1,1) for t in (-1,1) for p in itertools.permutations((x,y,t*a))})
        # Supporting planes select the six axial and twelve diagonal squares, then eight triangles.
        normals=[]
        for axis in range(3):
            for sign in (-1,1):normals.append((tuple(sign if k==axis else 0 for k in range(3)),a))
        for zero in range(3):
            for p,q in itertools.product((-1,1),repeat=2):
                n=[p,q];n.insert(zero,0);normals.append((tuple(n),a+1))
        normals += [(n,a+2) for n in itertools.product((-1,1),repeat=3)]
        faces=[]
        for normal,dist in normals:
            pts=[v for v in vertices if abs(sum(x*y for x,y in zip(v,normal))-dist)<1e-6]
            assert len(pts) in (3,4)
            if normal[0]+normal[1]+normal[2]*.9<=0:continue
            centre=[sum(v[k] for v in pts)/len(pts) for k in range(3)]
            # Basis on the face plane, then angular ordering of its actual vertices.
            ref=(1,0,0) if abs(normal[0])<.9 else (0,1,0)
            crossprod=lambda u,v:(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])
            u=crossprod(normal,ref);v=crossprod(normal,u)
            pts.sort(key=lambda p:math.atan2(sum((p[k]-centre[k])*v[k] for k in range(3)),sum((p[k]-centre[k])*u[k] for k in range(3))))
            faces.append((centre[0]+centre[1]+centre[2]*.9,normal,pts))
        def project(v):return P(s,ci+v[0]*1.45,cj+v[1]*1.45,z+51+v[2]*15)
        for _,normal,pts in sorted(faces):
            screen=[project(p) for p in pts]
            key='lit' if normal[2]>0 or normal[1]>0 and normal[0]<=0 else 'dark'
            poly(s,screen,lambda x,y,key=key:BLUE[key])
            # Mullions follow each face's own 3D edges, never screen-aligned noise.
            if len(pts)==4:
                for n in range(1,7):
                    t=n/7
                    for a0,a1,b0,b1 in ((0,1,3,2),(0,3,1,2)):
                        p=tuple(pts[a0][k]*(1-t)+pts[a1][k]*t for k in range(3));q=tuple(pts[b0][k]*(1-t)+pts[b1][k]*t for k in range(3))
                        seg(s,project(p),project(q),BLUE['mid' if key=='hi' else 'deep'])
            else:
                for n in range(1,4):
                    t=n/4
                    p=tuple(pts[0][k]*(1-t)+pts[1][k]*t for k in range(3));q=tuple(pts[0][k]*(1-t)+pts[2][k]*t for k in range(3))
                    seg(s,project(p),project(q),BLUE['mid'])
            for p,q in zip(screen,screen[1:]+screen[:1]):seg(s,p,q,BLUE['hi'] if key!='dark' else BLUE['outline'])
        # Flat rooftop observation rail, fitted to the top face.
        balustrade(s,(ci-1.4,cj+1.4),(ci+1.4,cj+1.4),z+51+a*15,2,WHITE)
    scene.add(i+j+22,draw)


def townhouse(scene,i,j,wi=2.8,wj=3,floors=2,seed=0,z=0):
    """Upper Town stucco / avenue classicism: rusticated shops, pilasters and metal hip roofs."""
    material=palette_of(WALLS[seed%len(WALLS)]);height=floors*12+5
    base=windows(material,height,10,12)
    def pattern(u,v,lit):
        c=int(u)%10
        trim=WHITE['lit' if lit else 'dark']
        if c in (0,1):return trim if v>9 else material['line']
        if v<9:
            if 3<=c<=7:return trim if c in (3,7) or int(v)==8 else WOOD if (int(u)//10+seed)%3==0 else GLASS['dark']
            return material['line'] if int(v)%3==0 else None
        if seed%3==0 and 11<=v<=14 and 2<=c<=8:return IRON if int(v) in (11,14) or c%2==0 else None
        return base(u,v,lit)
    def draw(s):
        block(s,i,j,wi,wj,height,material,pattern,z=z)
        band(s,i,j,wi,wj,z+1,STONE,2);band(s,i,j,wi,wj,z+height-2,WHITE,2)
        roof=RED if seed%4==0 else GREEN if seed%2==0 else DARK
        hip_roof(s,i-.08,j-.08,wi+.16,wj+.16,z+height,10,roof)
        block(s,i+wi-.7,j+.4,.4,.45,9,STONE,z=z+height+3)
        band(s,i+wi-.7,j+.4,.4,.45,z+height+11,DARK,2)
        if seed%4==1:
            pediment(s,i+.15,j+wj-.3,wi-.3,.45,z+height,7,WHITE)
    scene.add(i+j+wi+wj,draw)


def main():
    for name,builder,_,_,_,elevation in SITES:
        print(preview([lambda s,b=builder,e=elevation:b(s,4,4,z=e)],'minsk-'+name,
                      size=(280,250),origin=(140,115),tiles=22))
    import sprites
    im=sprites.mir_castle()
    path=Path(__file__).resolve().parents[2]/'docs/art/capitals/belarus-mir-castle.png'
    im.resize((im.width*4,im.height*4),0).save(path)
    print(path)
    print(preview([lambda s,n=n:townhouse(s,2+n*3.4,3,floors=2+n%2,seed=n) for n in range(6)],
                  'minsk-houses',size=(300,220),origin=(90,70),tiles=25))


# name, builder, footprint, actual building (longitude,latitude), north-up scene anchor, elevation.
SITES = [
    ('library',library,(10.8,10.8),(27.6462283,53.93122865),(598,148),0),
    ('opera',opera,(11.6,13.4),(27.561761,53.9105266),(394,225),6),
    ('victory',victory,(4.8,5.8),(27.57508705,53.90867375),(540,297),0),
    ('holy-spirit',cathedral,(8.4,9.6),(27.5561848,53.90502955),(280,344),10),
    ('city-hall',city_hall,(10,7),(27.5561119,53.90356085),(254,465),10),
    ('red-church',red_church,(10,7.5),(27.5476028,53.89647835),(86,476),0),
]

if __name__=='__main__':
    main()
