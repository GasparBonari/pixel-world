"""Andorra la Vella's mountain valley, with Escaldes and Santa Coloma, in true (i,j,z).

Research, coordinate cross-checks and explicit facade snaps: DEVELOPMENT_PLAN.md, Phase 4.
Run for six isolated 4× landmark studies, Pyrenean houses and the Meritxell country sprite.
"""
import math
from pathlib import Path

import iso
from iso import rgb, h01
from landmarks_paris import P, seg, poly, corners, facade, preview, GLASS
from landmarks_iberia import hip_roof, stone_courses, arch_opening, palette_of, tones
from landmarks_slovakia import block, band
from landmarks_amsterdam import gable_roof
from landmarks_bosnia import cylinder
from landmarks_slovenia import revolve

GRANITE = tones('#E7E2D3', '#BCB9A9', '#A5A696', '#7E877E', '#59635E', '#929B8F', '#394641')
RUBBLE = tones('#D9CFB5', '#B1A58C', '#998C77', '#77725F', '#565443', '#8E826C', '#3C4034')
PALE = tones('#FFFFE9', '#E8E3CD', '#CFCAB4', '#ABA994', '#7E826F', '#BDBCA4', '#4C5345')
SLATE = tones('#B3C2C1', '#778F94', '#5D757D', '#3F5664', '#2C3D49', '#516B77', '#23343E')
MIRROR = tones('#F0F8E7', '#B3DAD5', '#8BB9BC', '#527E91', '#345768', '#72A0A7', '#284955')
STEEL = tones('#FFFFEE', '#DBE5DD', '#B4C5C2', '#829DA1', '#536F7A', '#9CB6B8', '#345260')
WOOD = tones('#D5B286', '#AA8257', '#8B6845', '#655039', '#42392D', '#7B6348', '#302C23')
RED = tones('#E2A488', '#B87862', '#9E614D', '#754333', '#502E25', '#8C5742', '#40281F')
ROCK = tones('#D4CCB2', '#ACAA90', '#919179', '#747760', '#505B46', '#858C71', '#384B36')
WALLS = [rgb(c) for c in ('#D6CDB5', '#BFB9A4', '#E4DBC3', '#C9B59C', '#CDD0BF', '#D7C2B1')]
IRON = rgb('#344440')
GROUND = {k:rgb(v) for k,v in {
    'square':'#D9D7C3', 'joint':'#B4BBAA', 'rose':'#CEC7B6',
    'cobble':'#ADA995', 'cobble_joint':'#898E7D',
    'grass':'#879C65', 'grass_light':'#A7B982', 'rock':'#B4B398',
    'water':'#5D9C9B', 'water_dark':'#3D727D', 'water_hi':'#CAE5D9',
}.items()}


def windows(material, height, bay=12, floor=14, church=False):
    courses = stone_courses(material, 4, 11)
    def pattern(u,v,lit):
        c,k=int(u)%bay,int(v)%floor
        trim=PALE['lit' if lit else 'dark']
        top=floor-3-abs(c-bay/2)*(.75 if church else .12)
        if 3<=c<=bay-3 and 3<=k<=top and v<height-3:
            if c in (3,bay-3,bay//2) or k in (3,6,int(top)):return trim
            return GLASS['mid' if lit else 'dark']
        if k==2 and 2<=c<=bay-2:return trim
        return courses(u,v,lit)
    return pattern


def portal(i,j,width,height,z=0,material=GRANITE,*,s):
    """Recessed voussoir arch belongs only to the SW face, never the return wall."""
    span=width*8
    def pattern(u,v,lit):
        if not lit:return stone_courses(material,4,9)(u,v,lit)
        opening=arch_opening(u,v,span/2,span*.34,height-4,WOOD['dark'])
        if opening:
            return WOOD['lit'] if int(u)%6==0 or int(v)%8==0 else opening
        inner=arch_opening(u,v,span/2,span*.43,height-1,PALE['lit'])
        return inner or stone_courses(material,4,9)(u,v,lit)
    block(s,i,j,width,.35,height,material,pattern,z=z)


def porch(i,j,width,depth,z,height=15,count=3,material=GRANITE,*,s):
    """Extruded round arches, real open intrados and individual piers."""
    spacing=width/count
    for n in range(count+1):
        block(s,i+n*spacing-.15,j,.3,depth,height-5,material,z=z)
        band(s,i+n*spacing-.15,j,.3,depth,z+height-6,PALE,2)
    for n in range(count):
        a=i+n*spacing
        for k in range(12):
            x0=a+spacing*k/12;x1=a+spacing*(k+1)/12
            curve=lambda x:height-6+5*math.sqrt(max(0,1-((x-a-spacing/2)/(spacing/2))**2))
            h0,h1=curve(x0),curve(x1)
            for jj,lit in ((j,False),(j+depth,True)):
                pts=[P(s,x0,jj,z+h0),P(s,x1,jj,z+h1),P(s,x1,jj,z+height+2),P(s,x0,jj,z+height+2)]
                poly(s,pts,lambda x,y,lit=lit:material['lit' if lit else 'dark'])
                seg(s,pts[0],pts[1],PALE['hi' if lit else 'mid'])
                if k%3==0:seg(s,pts[0],pts[-1],material['line'])
            poly(s,[P(s,x0,j,z+h0),P(s,x1,j,z+h1),P(s,x1,j+depth,z+h1),P(s,x0,j+depth,z+h0)],lambda x,y:material['deep'])
    band(s,i-.15,j,width+.3,depth,z+height+2,material,2)


def belfry(i,j,width,depth,z,height=66,tiers=2,material=GRANITE,lights=2,*,s):
    courses=stone_courses(material,4,10)
    def pattern(u,v,lit):
        # Two separate round-headed belfry lights, with dressed voussoirs and central pier.
        span=(width if lit else depth)*8
        for level in range(tiers):
            base=height-20-level*19
            for n in range(lights):
                centre=span*(n+1)/(lights+1)
                aperture=arch_opening(u,v-base,centre,span/(lights*3+2),11,material['deep']) if v>base else None
                if aperture:return aperture
                trim=arch_opening(u,v-base+1,centre,span/(lights*3+2)+1,13,PALE['lit' if lit else 'dark']) if v>base-1 else None
                if trim:return trim
        if int(v)==height-3:return PALE['lit' if lit else 'dark']
        return courses(u,v,lit)
    block(s,i,j,width,depth,height,material,pattern,z=z)
    band(s,i,j,width,depth,z+height-2,material,2)
    hip_roof(s,i-.18,j-.18,width+.36,depth+.36,z+height,8,SLATE)


def casa_de_la_vall(scene,i,j,z=22):
    """Roc de la Vall manor: paired corbelled watch turrets and a rear square tower."""
    w,d,h=8.4,5.5,44
    def draw(s):
        # The northern defensive/dovecote tower rises through, behind the long slate ridge.
        belfry(i+.6,j-.7,2.0,1.9,z,64,1,RUBBLE,1,s=s)
        block(s,i,j,w,d,h,RUBBLE,windows(RUBBLE,h,14,15),z=z+3)
        band(s,i,j,w,d,z+3,GRANITE,4)
        band(s,i,j,w,d,z+h+2,WOOD,2)
        # Long slate gable roof, ridge along i, with the long southern eaves facing the valley.
        T,R,B,L=corners(s,i-.2,j-.2,w+.4,d+.4,z+h+4)
        a=P(s,i-.2,j+d/2,z+h+21);b=P(s,i+w+.2,j+d/2,z+h+21)
        for pts,lit in (([T,R,b,a],False),([L,B,b,a],True)):
            poly(s,pts,lambda x,y,lit=lit:SLATE['line'] if int(y)%3==0 else SLATE['hi'] if (int(x)+int(y)//3)%9==0 else SLATE['lit' if lit else 'dark'])
        poly(s,[R,B,b],lambda x,y:RUBBLE['line'] if int(y)%4==0 else RUBBLE['dark'])
        seg(s,a,b,SLATE['hi']);seg(s,L,B,WOOD['deep'])
        portal(i+2.7,j+d+.04,2.2,19,z+3,RUBBLE,s=s)
        # Shallow projecting machicolation above the arched granite doorway.
        block(s,i+2.8,j+d+.24,1.9,.45,4,RUBBLE,z=z+33)
        for a in (i+2.9,i+3.6,i+4.4):block(s,a,j+d+.23,.15,.42,3,GRANITE,z=z+30)
        # The two front corner turrets are round, with narrow slits and conical slate caps.
        for a in (i+.28,i+w-.28):
            for rr,zz,hh in ((.35,25,2),(.49,27,2),(.63,29,3)):
                cylinder(s,a,j+d+.02,rr,rr,z+zz,hh,RUBBLE,segments=16)
            cylinder(s,a,j+d+.02,.69,.69,z+32,14,RUBBLE,
                     lambda u,v,lit:RUBBLE['deep'] if 5<v<10 and int(u)%9 in (4,5) else stone_courses(RUBBLE,4,10)(u,v,lit),segments=20)
            revolve(s,a,j+d+.02,.82,z+46,11,[(0,1),(1,0)],SLATE,ribs=4,segments=20)
        # Dressed coat-of-arms stone above the doorway; no guessed national flag.
        block(s,i+3.45,j+d+.42,.68,.12,7,PALE,
              lambda u,v,lit:RED['mid'] if int(u)%3==1 and v>2 else None,z=z+24)
        for n in range(3):block(s,i+2.3-n*.12,j+d+.5+n*.28,3+n*.24,.3,3-n,GRANITE,z=z)
        # Deep roof eaves, stone chimneys and narrow upper defensive openings.
        block(s,i+5.7,j+1.0,.65,.65,12,RUBBLE,z=z+h+13)
        band(s,i+5.7,j+1.0,.65,.65,z+h+24,GRANITE,2)
    scene.add(i+j+w+d+4,draw)


def sant_esteve(scene,i,j,z=18):
    """Northern bell tower, crossing roofs, pale southern apses and Lombard arcades."""
    w,d=7.4,8.2
    def draw(s):
        belfry(i+.6,j-.3,2.1,2.1,z,77,2,GRANITE,2,s=s)
        block(s,i+.8,j+1.6,5.9,5.9,37,GRANITE,windows(GRANITE,37,12,30,True),z=z)
        gable_roof(s,i+.65,j+1.45,6.2,6.2,z+37,17,SLATE,GRANITE)
        # Lower crossing wing and three pale apses distinguish the enlarged parish church.
        block(s,i-.4,j+4.1,8.0,2.7,27,GRANITE,windows(GRANITE,27,11,23,True),z=z)
        hip_roof(s,i-.6,j+3.9,8.4,3.1,z+27,11,SLATE)
        for a,b,r,hh,mat in ((i+1.5,j+6.6,1.5,24,PALE),(i+5.3,j+6.6,1.55,25,PALE),
                              (i+7.1,j+3.3,1.55,29,GRANITE)):
            def arcades(u,v,lit,hh=hh,mat=mat):
                c=int(u)%9
                # Blind arches and lesenes, not painted freestanding columns.
                if v>hh-8 and (c in (0,1) or abs(v-(hh-3-3*math.sqrt(max(0,1-((c-4.5)/4.5)**2))))<1):
                    return PALE['hi' if lit else 'mid']
                if 5<v<hh-11 and c in (4,5):return GLASS['dark']
                return stone_courses(mat,4,10)(u,v,lit)
            cylinder(s,a,b,r,r,z,hh,mat,arcades,segments=24)
            cylinder(s,a,b,r+.03,r+.03,z+hh-2,2,mat,segments=24)
            revolve(s,a,b,r+.12,z+hh,12,[(0,1),(.3,.94),(.65,.7),(1,0)],SLATE,ribs=4,segments=24)
        portal(i+2.6,j+7.1,2.3,21,z,GRANITE,s=s)
        band(s,i+.8,j+1.6,5.9,5.9,z+1,GRANITE,2)
    scene.add(i+j+w+d+3,draw)


def pont_de_paris(scene,i,j,z=0):
    """One straight deck plus curved branch, two sphere joints, triangular tubes and fan stays."""
    w,d=9.0,5.2
    def draw(s):
        # Straight crossing along i; river runs on j. One curved slip branch joins upstream.
        block(s,i,j+2.6,w,2.0,4,GRANITE,lambda u,v,lit:STEEL['dark'],z=z+7)
        poly(s,list(corners(s,i,j+2.6,w,2,z+11)),lambda x,y:SLATE['dark'])
        curve=[]
        for k in range(25):
            t=k/24;a=i+w*(1-t);b=j+3.6-3.0*math.sin(t*math.pi/2)
            curve.append((a,b))
        for (a,b),(aa,bb) in zip(curve,curve[1:]):
            pts=[P(s,a,b,z+11),P(s,aa,bb,z+11),P(s,aa,bb+.9,z+11),P(s,a,b+.9,z+11)]
            poly(s,pts,lambda x,y:SLATE['mid'])
            seg(s,P(s,a,b,z+7),P(s,aa,bb,z+7),GRANITE['dark'],2)
        # Two triangular steel frame nodes; connecting upper tie forms the characteristic arch.
        nodes=[(i+2.9,j+2.2,z+52),(i+5.2,j+3.6,z+49)]
        for a,b,zz in nodes:
            for foot in ((i-.2,j+3.6,z+3),(i+w+.2,j+3.6,z+3)):
                seg(s,P(s,*foot),P(s,a,b,zz),STEEL['dark'],3)
                seg(s,P(s,foot[0]-.08,foot[1],foot[2]),P(s,a-.08,b,zz),STEEL['hi'])
        seg(s,P(s,*nodes[0]),P(s,*nodes[1]),STEEL['lit'],3)
        # Individually spaced fan stays run from each sphere to its deck, not an even cage.
        for k in range(1,9):
            a=i+w*k/9
            seg(s,P(s,*nodes[0]),P(s,a,j+2.7,z+13),STEEL['mid'])
        for k in range(2,22,3):
            a,b=curve[k]
            seg(s,P(s,*nodes[1]),P(s,a,b+.55,z+13),STEEL['lit'])
        for a,b,zz in nodes:
            revolve(s,a,b,.45,zz-4,8,[(0,0),(.15,.72),(.5,1),(.85,.72),(1,0)],STEEL,segments=20)
        for jj in (j+2.65,j+4.55):
            for k in range(10):
                a=i+w*k/9;seg(s,P(s,a,jj,z+11),P(s,a,jj,z+17),STEEL['dark'])
            seg(s,P(s,i,jj,z+17),P(s,i+w,jj,z+17),STEEL['hi'])
        for (a,b),(aa,bb) in zip(curve,curve[1:]):
            seg(s,P(s,a,b,z+16),P(s,aa,bb,z+16),STEEL['lit'])
        # Solid bank abutments at the two ends, no invented river pier.
        for a in (i-.35,i+w-.35):block(s,a,j+2.45,.7,2.3,8,GRANITE,z=z)
    scene.add(i+j+w+d+3,draw)


def caldea(scene,i,j,z=0):
    """Jean-Michel Ruols' single mirrored spire and broad faceted crystalline spa halls."""
    w,d=11.8,7.8
    def glass_grid(u,v,lit):
        if int(u)%7==0 or int(v)%7==0:return STEEL['mid' if lit else 'dark']
        if (int(u)//7+int(v)//7*3)%11 in (0,1):return MIRROR['hi' if lit else 'mid']
        return MIRROR['lit' if lit else 'dark']
    def crystal(s,a,b,wi,wj,base,rise,lean=0):
        T,R,B,L=corners(s,a,b,wi,wj,base)
        apex=P(s,a+wi*.48+lean,b+wj*.4,base+rise)
        for pts,lit in (([T,L,apex],True),([T,R,apex],False),([R,B,apex],False),([L,B,apex],True)):
            def glazing(x,y,lit=lit):
                if (int(x)+int(y)//5)%8==0 or int(y)%7==0:return STEEL['lit' if lit else 'dark']
                return MIRROR['hi' if lit and (x//16+y//12)%7==0 else 'lit' if lit else 'dark']
            poly(s,pts,glazing)
            for p,q in zip(pts,pts[1:]+pts[:1]):seg(s,p,q,STEEL['hi' if lit else 'mid'])
    def draw(s):
        block(s,i,j,w,d,18,GRANITE,glass_grid,z=z)
        band(s,i,j,w,d,z+2,GRANITE,3)
        band(s,i,j,w,d,z+18,STEEL,2)
        # Tower at the back/northeast of the lower crystalline halls; 130 px dominates houses.
        a,b=i+6.7,j+1.1
        block(s,a,b,2.9,2.4,73,MIRROR,glass_grid,z=z+18)
        crystal(s,a-.02,b-.02,2.94,2.44,z+91,54,.15)
        crystal(s,i+.1,j+.1,5.8,4.1,z+20,43)
        crystal(s,i+.1,j+4.3,5.8,3.3,z+20,49)
        crystal(s,i+6.1,j+3.8,5.5,3.8,z+20,36)
        # Roof terraces and low glazed entry wing are part of the same spa mass.
        block(s,i+8.6,j+1.8,3.2,2.1,16,MIRROR,glass_grid,z=z+18)
        crystal(s,i+8.6,j+1.8,3.2,2.1,z+34,26)
        # Outdoor thermal basin on the southern terrace, clipped to its own rim.
        a,b=i+7.6,j+7.9
        cylinder(s,a,b,2.0,1.05,z+3,4,GRANITE,segments=32)
        poly(s,[P(s,a+1.8*math.cos(t),b+.88*math.sin(t),z+7) for t in [n*math.tau/48 for n in range(48)]],
             lambda x,y:GROUND['water_hi'] if int(y)%5==0 and int(x)%13<4 else GROUND['water'])
        # Mullioned entry and transparent terrace guards, no signage baked into art.
        block(s,i+3.1,j+d+.1,2.8,.3,12,MIRROR,glass_grid,z=z)
        for k in range(6):
            a=i+k*2.0
            seg(s,P(s,a,j+d,z+20),P(s,a,j+d,z+25),STEEL['mid'])
        seg(s,P(s,i,j+d,z+25),P(s,i+w,j+d,z+25),STEEL['hi'])
    scene.add(i+j+w+d+4,draw)


def sant_pere(scene,i,j,z=6):
    """Granite basilica: one NW tower, three-arch porch, arcaded front, higher nave and lower aisles."""
    w,d=8.2,8.8
    def draw(s):
        # Eastern apse stays behind the long nave, not on the western entrance.
        cylinder(s,i+4.5,j+.5,2.3,2.0,z,30,GRANITE,windows(GRANITE,30,12,26,True),segments=24)
        revolve(s,i+4.5,j+.5,2.45,z+30,12,[(0,1),(.5,.85),(1,0)],SLATE,segments=24)
        for a in (i+.3,i+6.3):
            block(s,a,j+1.4,1.6,6.7,24,GRANITE,windows(GRANITE,24,12,22,True),z=z)
            hip_roof(s,a-.1,j+1.2,1.8,7.1,z+24,10,SLATE)
        block(s,i+1.9,j+1.0,4.4,7.4,43,GRANITE,windows(GRANITE,43,13,36,True),z=z)
        gable_roof(s,i+1.75,j+.9,4.7,7.7,z+43,19,SLATE,GRANITE)
        # NW/-i end of the west front; explicitly not mirrored to the southern/right corner.
        belfry(i-.5,j+4.9,2.1,2.5,z,82,3,GRANITE,3,s=s)
        # The real front has five upper/three lower round-headed lights, not a rose window.
        def front_lights(u,v,lit):
            if not lit:return stone_courses(GRANITE,4,10)(u,v,lit)
            for count,base,hh in ((5,27,11),(3,16,7)):
                for n in range(count):
                    centre=5+(n+1)*25/(count+1)
                    aperture=arch_opening(u,v-base,centre,1.3,hh,GLASS['dark']) if v>base else None
                    if aperture:return aperture
            # Pale sgraffito wall with sampled incised robe/halo fields, no invented lettering.
            if 13<v<42 and (int(u*2+v)//5)%11==0:return GRANITE['line']
            return PALE['lit']
        facade(s,i+1.9,j+8.27,4.4,.15,42,front_lights,palette=GRANITE,z0=z)
        portal(i+3.0,j+8.5,2.2,23,z,GRANITE,s=s)
        porch(i+1.75,j+8.65,4.8,1.2,z,18,3,GRANITE,s=s)
        hip_roof(s,i+1.6,j+8.5,5.1,1.55,z+22,4,SLATE)
        for n in range(4):block(s,i+1.5-n*.1,j+10.1+n*.23,5.3+n*.2,.25,4-n,GRANITE,z=z-1)
        # Lombard lesenes run down the side aisle; stone shoulders below the eaves.
        for b in (j+2.0,j+4.2,j+6.4):block(s,i+7.85,b,.25,.3,25,GRANITE,z=z)
    scene.add(i+j+w+d+4,draw)


def santa_coloma(scene,i,j,z=8):
    """Low pre-Romanesque church and one SE round tower with four paired-window tiers."""
    w,d=8.0,5.4
    def draw(s):
        # Nave extends i (NW/SE); the east apse and tower are at its +i end.
        block(s,i,j,6.6,4.5,22,RUBBLE,stone_courses(RUBBLE,4,10),z=z)
        # True gabled ridge along i, expressed by exchanging the usual roof axes.
        T,R,B,L=corners(s,i-.15,j-.15,6.9,4.8,z+22)
        a=P(s,i-.15,j+2.25,z+35);b=P(s,i+6.75,j+2.25,z+35)
        for pts,lit in (([T,R,b,a],False),([L,B,b,a],True)):
            poly(s,pts,lambda x,y,lit=lit:SLATE['line'] if int(y)%3==0 else SLATE['hi'] if (int(x)+int(y)//3)%11==0 else SLATE['lit' if lit else 'dark'])
        poly(s,[R,B,b],lambda x,y:RUBBLE['dark'] if int(y)%4 else RUBBLE['line'])
        seg(s,a,b,SLATE['hi']);seg(s,L,B,SLATE['outline'])
        block(s,i+6.5,j+1,1.8,2.6,18,RUBBLE,stone_courses(RUBBLE,4,10),z=z)
        hip_roof(s,i+6.4,j+.9,2.0,2.8,z+18,7,SLATE)
        portal(i+1.5,j+4.55,1.9,16,z,RUBBLE,s=s)
        # Low southern timber/stone porch does not hide the eastern tower's base.
        for a in (i+.4,i+2.8,i+4.3):block(s,a,j+5.3,.25,.3,14,RUBBLE,z=z)
        # Single lean-to slate plane, high at the nave wall and lower at the outer posts.
        pts=[P(s,i-.2,j+4.4,z+20),P(s,i+4.9,j+4.4,z+20),P(s,i+4.9,j+5.9,z+15),P(s,i-.2,j+5.9,z+15)]
        poly(s,pts,lambda x,y:SLATE['line'] if int(y)%3==0 else SLATE['lit'])
        for a,b in zip(pts,pts[1:]+pts[:1]):seg(s,a,b,SLATE['outline'])
        ci,cj=i+6.4,j+4.8
        def round_lights(u,v,lit):
            c=u%(math.pi*2*1.12)
            for n in range(4):
                level=13+n*15
                centres=(3.5,) if n==0 and u<7.04 else (2.0,5.0)
                for mid in centres:
                    opening=arch_opening(c,v-level,mid,1.1,9,RUBBLE['deep']) if v>level else None
                    if opening:return opening
                if level+11<v<level+13:return RED['mid' if lit else 'dark'] if n==3 else RUBBLE['hi' if lit else 'mid']
                if c<1 and level<v<level+13:return RUBBLE['hi' if lit else 'mid']
            return stone_courses(RUBBLE,4,9)(u,v,lit)
        cylinder(s,ci,cj,1.12,1.12,z,76,RUBBLE,round_lights,segments=32)
        cylinder(s,ci,cj,1.22,1.22,z+75,2,RUBBLE,segments=32)
        revolve(s,ci,cj,1.4,z+77,12,[(0,1),(.2,.88),(1,0)],SLATE,ribs=4,segments=32)
    scene.add(i+j+w+d+4,draw)


def townhouse(scene,i,j,floors=2,seed=0,z=0):
    """Pyrenean borda/old-town houses: stone, slate, timber balconies and dressed glazing."""
    w,d=2.6,3.0;h=floors*12+5
    material=palette_of(WALLS[seed%len(WALLS)])
    courses=stone_courses(material,4,10)
    def pattern(u,v,lit):
        c,k=int(u)%10,int(v)%12;trim=GRANITE['hi' if lit else 'mid']
        if v<3:return GRANITE['lit' if lit else 'dark']
        if v<13 and 4<c<8:
            if seed%3==0:return trim if c==5 or k in (3,10) else GLASS['dark']
            return WOOD['mid'] if c==6 else WOOD['dark']
        if 2<=c<=8 and 3<=k<=9 and v<h-2:
            if c in (2,5,8) or k in (3,6,9):return trim
            return GLASS['mid' if lit else 'dark']
        if c in (0,1):return GRANITE['lit' if lit else 'dark']
        return courses(u,v,lit)
    def draw(s):
        block(s,i,j,w,d,h,material,pattern,z=z)
        band(s,i,j,w,d,z+1,GRANITE,2)
        band(s,i,j,w,d,z+h-1,WOOD,2)
        hip_roof(s,i-.2,j-.2,w+.4,d+.4,z+h+2,12,SLATE)
        # Frequent traditional timber galleries, occasional iron guards on modern plaster.
        if floors>1:
            for zz in range(16,h,12):
                block(s,i+.3,j+d+.08,2.0,.5,2,WOOD,z=z+zz-2)
                for k in range(7):
                    a=i+.35+k*.3
                    seg(s,P(s,a,j+d+.55,z+zz),P(s,a,j+d+.55,z+zz+5),WOOD['dark'] if seed%3 else IRON)
                seg(s,P(s,i+.3,j+d+.55,z+zz+5),P(s,i+2.3,j+d+.55,z+zz+5),WOOD['lit'])
                for a in (i+.4,i+2.0):seg(s,P(s,a,j+d,z+zz-6),P(s,a,j+d+.45,z+zz-2),WOOD['mid'])
        block(s,i+1.8,j+.5,.45,.5,10,GRANITE,z=z+h+8)
        band(s,i+1.8,j+.5,.45,.5,z+h+18,GRANITE,2)
    scene.add(i+j+w+d,draw)


def main():
    for name,builder in (
        ('casa-de-la-vall',casa_de_la_vall),('sant-esteve',sant_esteve),
        ('pont-de-paris',pont_de_paris),('caldea',caldea),
        ('sant-pere',sant_pere),('santa-coloma',santa_coloma)):
        print(preview([lambda s,b=builder:b(s,5,5,z=0)],f'andorra-{name}',
                      size=(270,245),origin=(130,110),tiles=21))
    print(preview([lambda s:townhouse(s,6,6,3,1),lambda s:townhouse(s,10,5,2,4),
                   lambda s:townhouse(s,10,10,1,3)],'andorra-houses',size=(230,190),origin=(110,30),tiles=19))
    import sprites
    out=Path(__file__).resolve().parents[2]/'docs/art/capitals/andorra-meritxell.png'
    im=sprites.meritxell(0);im.resize((im.width*4,im.height*4),0).save(out);print(out)


if __name__=='__main__':
    main()


# Real longitude/latitude, north-up screen ground anchor and terrain height. Scene/checker source.
SITES = [
    ('Casa de la Vall',casa_de_la_vall,(8.4,5.5),(1.520556,42.506667),(215,415),22),
    ('Sant Esteve',sant_esteve,(7.4,8.2),(1.521657,42.507215),(330,365),18),
    ('Pont de Paris',pont_de_paris,(9,5.2),(1.530667,42.509222),(445,220),0),
    ('Caldea',caldea,(11.8,7.8),(1.536783,42.511694),(545,175),0),
    ('Sant Pere Martir',sant_pere,(8.2,8.8),(1.54165,42.50888),(635,320),6),
    ('Santa Coloma',santa_coloma,(8,5.4),(1.497550,42.494174),(110,475),8),
]
