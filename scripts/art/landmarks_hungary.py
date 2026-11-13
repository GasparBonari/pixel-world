"""Budapest: original isometric architecture, projected from (i, j, z).

Eight landmark studies and Pest apartment houses. See DEVELOPMENT_PLAN.md for
real anchors and architectural references. Run this file for isolated 4× plots.
"""
import math

import iso
from iso import rgb
from landmarks_paris import P, seg, poly, corners, facade, mansard, preview, GLASS
from landmarks_iberia import hip_roof, stone_courses, arch_opening, palette_of, tones
from landmarks_italy import cylinder, ellipse
from landmarks_denmark import spire, clock

STONE = tones('#FFF5DE', '#E5D3AC', '#CDBB96', '#A99776', '#7A6B50', '#B9A783', '#50422F')
WHITE = tones('#FFFFED', '#F0E8D0', '#D8CEB5', '#B7AD94', '#877B63', '#C5BA9E', '#534B38')
RED = tones('#F1AF8C', '#B86B54', '#9A5144', '#743C36', '#512A29', '#87453B', '#442728')
COPPER = tones('#C2D8B7', '#8EAF93', '#70977F', '#4E7163', '#355044', '#60836E', '#2C4339')
SLATE = tones('#AFB6BA', '#849299', '#6D7B85', '#4D5D6B', '#34424E', '#5D6E7B', '#2A3743')
OCHRE = tones('#FFF0BF', '#E6C47F', '#D0AC68', '#AC8B53', '#7B603B', '#BD995E', '#55442C')
GOLD = tones('#FFF5AF', '#EBCB6A', '#C7A14C', '#9A7635', '#695327', '#B68D3C', '#504023')
BRONZE = tones('#ABB59A', '#7F9275', '#61795E', '#3F5946', '#2A4134', '#536B51', '#24372B')
TILE_GREEN = rgb('#638F78')
WALLS = [rgb(c) for c in ('#DFCAA4', '#D6B16F', '#D4AC9A', '#B5C1AD', '#C5B5CA', '#E8DCC4')]
IRON, WOOD = rgb('#354548'), rgb('#765139')
WATER = (rgb('#497F91'), rgb('#376879'), rgb('#BBDCD9'))
POOL = (rgb('#64ABB5'), rgb('#438D9D'), rgb('#BBDCD9'))
HILL_GRASS = rgb('#88AB58')


def block(s,i,j,wi,wj,height,material=STONE,pattern=None,z=0):
    cover=facade(s,i,j,wi,wj,height,pattern or stone_courses(material,4,10),palette=material,z0=z)
    iso.fill(s,list(corners(s,i,j,wi,wj,z+height)),lambda x,y:material['mid'],cover)
    iso.outline(s,cover,material['outline'])
    return cover


def band(s,i,j,wi,wj,z,material=WHITE,height=1):
    facade(s,i-.05,j-.05,wi+.1,wj+.1,height,
           lambda u,v,lit:material['hi' if lit else 'dark'],palette=material,z0=z)
    _,r,b,l=corners(s,i-.05,j-.05,wi+.1,wj+.1,z+height)
    seg(s,l,b,material['hi']);seg(s,b,r,material['deep'])


def windows(material,height,bay=10,floor=13,gothic=False):
    courses=stone_courses(material,5,12)
    def pattern(u,v,lit):
        c,level=int(u)%bay,int(v)%floor
        trim=WHITE['lit' if lit else 'dark']
        if v<2 or int(v) in (height-1,height-3):return trim
        top=floor-3-abs(c-bay/2)*(1.2 if gothic else .15)
        if 2<=c<=bay-2 and 3<=level<=top and v<height-3:
            if c in (2,bay-2,bay//2) or level in (3,6,int(top)):return trim
            return GLASS['mid' if lit else 'dark']
        return courses(u,v,lit)
    return pattern


def pediment(s,i,j,w,d,z,rise,material=WHITE):
    front=[P(s,i,j+d,z),P(s,i+w,j+d,z),P(s,i+w/2,j+d,z+rise)]
    back=[P(s,i,j,z),P(s,i+w,j,z),P(s,i+w/2,j,z+rise)]
    poly(s,back,lambda x,y:material['mid'])
    for a,b in ((0,2),(2,1)):
        poly(s,[back[a],back[b],front[b],front[a]],lambda x,y:material['dark'])
    poly(s,front,lambda x,y:material['lit'])
    for a,b in zip(front,front[1:]+front[:1]):seg(s,a,b,material['hi'],2)


def cross(s,i,j,z):
    block(s,i-.06,j-.06,.12,.12,7,GOLD,z=z)
    block(s,i-.28,j-.06,.56,.12,1.3,GOLD,z=z+4)


def dome(s,i,j,r,base,height,material=COPPER,pointed=False):
    """Revolved ribbed roof mesh, shaded and depth sorted around its full volume."""
    profile=[(0,1),(.12,1.05),(.35,.94),(.60,.72),(.82,.40),(1,.12)]
    if pointed:profile=[(0,1),(.16,.98),(.40,.82),(.70,.46),(1,.09)]
    faces=[]
    for (a,ra),(b,rb) in zip(profile,profile[1:]):
        for n in range(24):
            t,u=n*math.tau/24,(n+1)*math.tau/24
            pts=[P(s,i+r*rr*math.cos(v),j+r*rr*math.sin(v),base+height*h)
                 for h,rr,v in ((a,ra,t),(a,ra,u),(b,rb,u),(b,rb,t))]
            key='lit' if math.sin((t+u)/2)-.5*math.cos((t+u)/2)>.1 else 'dark'
            faces.append((r*(math.cos(t)+math.sin(t)+math.cos(u)+math.sin(u)),pts,key,n))
    for _,pts,key,n in sorted(faces):
        poly(s,pts,lambda x,y,k=key:material['line'] if int(y)%7==0 else material[k])
        if n%2==0:seg(s,pts[0],pts[3],material['hi' if key=='lit' else 'deep'])
    cylinder(s,i,j,.23,.23,base+height,5,GOLD)


def townhouse(scene,i,j,wi=2.5,wj=3,floors=3,seed=0):
    """Pest Historicist stucco: rustication, window crowns, iron balconies, roof dormers."""
    wall,H=palette_of(WALLS[seed%len(WALLS)]),floors*11+4
    base=windows(wall,H,10,11)
    def pattern(u,v,lit):
        c,level=int(u)%10,int(v)%11
        trim=WHITE['lit' if lit else 'dark']
        if v<11:
            if 2<=c<=8 and 1<v<9:
                return trim if c in (2,8) or int(v)==8 else WOOD if seed%3==0 else GLASS['dark']
            return wall['line' if lit else 'deep'] if int(v)%4==0 else None
        if level==10 and 2<=c<=8:return trim
        if seed%2 and level in (1,2) and 2<=c<=8:return IRON if level==1 or c%3==0 else None
        return base(u,v,lit)
    def draw(s):
        block(s,i,j,wi,wj,H,wall,pattern)
        for z in (1,11,H-1):band(s,i,j,wi,wj,z)
        if seed%3==0:hip_roof(s,i,j,wi,wj,H,12,RED)
        else:mansard(s,i,j,wi,wj,H,13,.45,roof=SLATE,dormers=6)
        block(s,i+wi-.6,j+.4,.4,.5,9,STONE,z=H+7)
        band(s,i+wi-.6,j+.4,.4,.5,H+15,RED,2)
        if seed%4==0:
            block(s,i+.65,j+wj,1.2,.45,1.5,WHITE,z=16)
            for a in range(6):seg(s,P(s,i+.7+a*.2,j+wj+.4,17),P(s,i+.7+a*.2,j+wj+.4,21),IRON)
            seg(s,P(s,i+.65,j+wj+.4,21),P(s,i+1.85,j+wj+.4,21),IRON)
        if seed%5==0:
            block(s,i+.8,j+wj-.6,.8,.65,6,wall,windows(wall,9,6),z=H+3)
            pediment(s,i+.7,j+wj-.65,1,.75,H+9,5)
    scene.add(i+j+wi+wj,draw)


def parliament(scene,i,j):
    """Long Gothic riverfront, red roofs, central ribbed dome, pinnacles and traceried bays."""
    W,D,H=12,5,39
    def draw(s):
        block(s,i,j,W,D,H,STONE,windows(STONE,H,10,18,True))
        hip_roof(s,i,j,W,D,H,16,RED)
        for z in (3,19,37):band(s,i,j,W,D,z)
        # Projecting gabled end pavilions and central entrance bay.
        for a,w,h in ((0,2.1,47),(4.7,2.6,48),(9.9,2.1,47)):
            block(s,i+a,j+3.1,w,2.5,h,STONE,windows(STONE,h,9,20,True))
            hip_roof(s,i+a,j+3.1,w,2.5,h,17,RED)
            pediment(s,i+a,j+5.55,w,.18,h-1,12)
            for di in (.15,w-.15):
                block(s,i+a+di-.13,j+5.6,.26,.26,12,WHITE,z=h-4)
                spire(s,i+a+di,j+5.7,.25,h+8,9,WHITE)
        # Buttress strips and pinnacles remain separated, avoiding a fence texture.
        for a in (.35,2.8,4.1,7.9,9.2,11.65):
            block(s,i+a,j+D,.22,.4,37,WHITE)
            spire(s,i+a+.1,j+D+.2,.30,38,16,WHITE)
        ci,cj=i+6,j+2.5
        cylinder(s,ci,cj,1.8,1.8,45,17,STONE,windows(STONE,17,9,17,True))
        cylinder(s,ci,cj,1.88,1.88,61,2,WHITE)
        dome(s,ci,cj,1.85,63,35,RED,True)
        spire(s,ci,cj,.25,101,12,GOLD)
        for n in range(8):
            t=n*math.tau/8
            spire(s,ci+1.85*math.cos(t),cj+1.85*math.sin(t),.18,62,15,WHITE)
        # A dark pointed portal with carved surround on the central front pavilion.
        block(s,i+5.35,j+5.66,1.3,.10,16,STONE,
              lambda u,v,lit:arch_opening(u,v,5.2,3.5,11,WOOD) or WHITE['lit'])
        for a in range(3):block(s,i+4.8,j+5.8+a*.22,2.4,.25,4-a,STONE)
    scene.add(i+j+W+D+3,draw)


def matthias_church(scene,i,j):
    """Asymmetric Gothic towers, open spire tracery, rose window and Zsolnay diamond roof."""
    W,D,H=5,7,36
    def draw(s):
        block(s,i,j,W,D,H,WHITE,windows(WHITE,H,11,25,True))
        hip_roof(s,i,j,W,D,H,28,RED)
        # Tile mosaic lives only on the two visible roof slopes.
        t,r,b,l=corners(s,i,j,W,D,H)
        ridge0=P(s,i+W/2,j+W/2,H+28)
        ridge1=P(s,i+W/2,j+D-W/2,H+28)
        for pts in ([l,b,ridge1,ridge0],[b,r,ridge0,ridge1]):
            poly(s,pts,lambda x,y:TILE_GREEN if (int(x)//3+int(y)//3)%5==0 else GOLD['mid'] if (int(x)//3-int(y)//3)%5==0 else RED['lit'] if int(y)%3 else RED['dark'])
        for a,bj in ((.1,1),(4.7,1),(4.7,3.2),(4.7,5.3)):
            block(s,i+a,j+bj,.3,.5,30,STONE)
            spire(s,i+a+.15,j+bj+.25,.25,30,13,WHITE)
        # Dominant southwestern Matthias tower: successive open belfry stages.
        ti,tj=i-.3,j+D-1.8
        block(s,ti,tj,2.1,2.3,61,WHITE,windows(WHITE,61,9,20,True))
        for z in (3,24,43,59):band(s,ti,tj,2.1,2.3,z)
        clock(s,ti+1.05,tj+2.36,4,40)
        cylinder(s,ti+1.05,tj+1.15,.85,.85,61,12,WHITE,windows(WHITE,12,7,13,True))
        spire(s,ti+1.05,tj+1.15,1.0,74,34,WHITE)
        for a,bj in ((0,0),(1.9,0),(0,2.1),(1.9,2.1)):
            spire(s,ti+a,tj+bj,.20,60,15,WHITE)
        cross(s,ti+1.05,tj+1.15,110)
        # Lower Béla tower has a tiled tent cap, deliberately much shorter.
        block(s,i+3.4,j+D-1.6,1.8,1.9,42,WHITE,windows(WHITE,42,8,18,True))
        spire(s,i+4.3,j+D-.65,1.2,43,16,RED,conical=True)
        # Portal and rose face west/south; return face keeps its own lancets.
        fj=j+D+.04
        block(s,i+1.9,fj,1.4,.1,17,STONE,
              lambda u,v,lit:arch_opening(u,v,5.6,4,12,WOOD) or WHITE['lit'])
        center=(i+2.6,fj,26)
        ring=[P(s,center[0]+.57*math.cos(n*math.tau/32),fj,26+4.6*math.sin(n*math.tau/32)) for n in range(32)]
        poly(s,ring,lambda x,y:GLASS['dark'])
        for a,bj in zip(ring,ring[1:]+ring[:1]):seg(s,a,bj,STONE['lit'])
        for n in range(8):seg(s,P(s,*center),ring[n*4],WHITE['lit'])
    scene.add(i+j+W+D+3,draw)


def fishermans_bastion(scene,i,j):
    """Seven pale conical turrets, open Romanesque arcades, parapets and stair terraces."""
    W,D=11,4.5
    def draw(s):
        block(s,i-.3,j-.2,W+.6,D+.4,8,STONE)
        # Open galleries built from individual piers and curved voussoir rings.
        for a in range(10):
            block(s,i+a+.1,j+3.25,.25,.65,16,WHITE,z=8)
            for n in range(10):
                t,u=n*math.pi/10,(n+1)*math.pi/10
                pts=[P(s,i+a+.62+rr*math.cos(v),j+3.93,19+rr*9*math.sin(v))
                     for rr,v in ((.52,t),(.52,u),(.36,u),(.36,t))]
                poly(s,pts,lambda x,y:WHITE['lit'])
        band(s,i,j+3.2,W,.8,28,WHITE,3)
        for a in range(0,11,2):block(s,i+a,j+3.75,.16,.16,5,WHITE,z=31)
        # Seven turrets: two rear, four along the terrace, one taller main tower.
        for a,bj,r,h in ((.3,.35,.48,25),(10.3,.35,.48,25),(.2,3.4,.52,29),
                         (3,3.4,.42,25),(5.8,3.4,.42,25),(8.6,3.4,.42,25),(10.8,3.4,.7,39)):
            cylinder(s,i+a,j+bj,r,r,8,h,WHITE,windows(WHITE,h,8,15,True))
            cylinder(s,i+a,j+bj,r+.1,r+.1,h+7,2,STONE)
            spire(s,i+a,j+bj,r+.2,h+10,17 if h<40 else 24,WHITE,conical=True)
        for a in range(5):block(s,i+3,j+4.1+a*.4,3,.45,8-a*1.4,STONE)
    scene.add(i+j+W+D+5,draw)


def buda_castle(scene,i,j):
    """Royal Palace terrace, long Baroque wings, pedimented pavilions and green central dome."""
    W,D,H=12,4.5,40
    def draw(s):
        block(s,i-.5,j-.4,W+1,D+1,12,STONE)
        block(s,i,j,W,D,H,OCHRE,windows(OCHRE,H,10,13),z=12)
        hip_roof(s,i,j,W,D,H+12,14,SLATE)
        for z in (14,26,39,51):band(s,i,j,W,D,z)
        for a in (0,4.8,9.6):
            block(s,i+a,j+2.2,2.4,2.7,44,OCHRE,windows(OCHRE,44,10,14),z=12)
            hip_roof(s,i+a,j+2.2,2.4,2.7,56,15,SLATE)
            pediment(s,i+a,j+4.8,2.4,.25,55,8)
            for di in (.1,2.1):block(s,i+a+di,j+4.92,.2,.15,29,WHITE,z=25)
        cylinder(s,i+6,j+2.1,1.6,1.6,60,16,STONE,windows(STONE,16,9,16))
        cylinder(s,i+6,j+2.1,1.7,1.7,76,2,WHITE)
        dome(s,i+6,j+2.1,1.8,78,25,COPPER)
        # Grand terrace stair, balustrade and dressed retaining wall.
        for a in range(5):block(s,i+4.4,j+D+.7+a*.35,3.2,.4,11-a*2,STONE)
        for a in (1,2.7,8.6,10.5):
            block(s,i+a,j+D+.4,.22,.22,7,WHITE,z=12)
        band(s,i,j+D+.2,4,.3,19,WHITE)
        band(s,i+8,j+D+.2,4,.3,19,WHITE)
    scene.add(i+j+W+D+6,draw)


def chain_bridge(scene,i,j):
    """Two stone portal towers, paired sagging iron chains, hangers, four lions and deck."""
    W,D,Z=18,2.5,10
    def chain_height(a):
        if a<4:return Z+5+(a/4)**2*36
        if a>14:return Z+5+((18-a)/4)**2*36
        return Z+14+27*((a-9)/5)**2
    def draw(s):
        # Far chain is behind the roadway and piers.
        def chains(bj):
            for off in (0,2.2):
                for n in range(180):
                    a,b=n/10,(n+1)/10
                    seg(s,P(s,i+a,j+bj,chain_height(a)+off),P(s,i+b,j+bj,chain_height(b)+off),IRON)
            for a in range(1,18):seg(s,P(s,i+a,j+bj,Z+3),P(s,i+a,j+bj,chain_height(a)),SLATE['lit'])
        chains(.12)
        block(s,i,j,W,D,3,SLATE,z=Z)
        for a in (4,14):
            block(s,i+a-.6,j-.3,1.2,D+.6,10,STONE)
            # Towers are piers plus a semicircular voussoir arch, not a painted black cut-out.
            for bj in (-.2,2.15):
                block(s,i+a-.45,j+bj,.9,.55,37,STONE,z=Z+3)
            for n in range(14):
                t,u=n*math.pi/14,(n+1)*math.pi/14
                pts=[P(s,i+a+.48,j+1.25+rr*math.cos(v),Z+26+rr*8*math.sin(v))
                     for rr,v in ((1.48,t),(1.48,u),(.9,u),(.9,t))]
                poly(s,pts,lambda x,y:STONE['dark'])
                pts2=[(x-7.4,y-3.7) for x,y in pts]
                poly(s,pts2,lambda x,y:STONE['lit'])
            block(s,i+a-.5,j-.25,1,D+.5,7,STONE,z=Z+37)
            band(s,i+a-.5,j-.25,1,D+.5,Z+44,WHITE,2)
            for bj in (.05,2.1):block(s,i+a-.15,j+bj,.3,.3,3,WHITE,z=Z+46)
        chains(D-.12)
        for bj in (0,D):seg(s,P(s,i,j+bj,Z+4),P(s,i+W,j+bj,Z+4),SLATE['hi'])
        # Each entrance has a pair of crouching stone lions on separate pedestals.
        for a in (.5,17.1):
            for bj in (-.6,2.9):
                block(s,i+a-.35,j+bj-.22,.7,.44,4,STONE,z=Z)
                cylinder(s,i+a,j+bj,.4,.22,Z+4,3,STONE)
                cylinder(s,i+a-.3,j+bj,.22,.22,Z+6,3,WHITE)
                for da in (-.25,.25):block(s,i+a+da,j+bj+.15,.12,.12,2,STONE,z=Z+3)
    scene.add(i+j+W+D+3,draw)


def st_stephen(scene,i,j):
    """Basilica's twin bell towers, columned pedimented portico, drum and ribbed dome."""
    W,D,H=7,6,40
    def draw(s):
        block(s,i,j,W,D,H,STONE,windows(STONE,H,11,18))
        hip_roof(s,i,j,W,D,H,12,SLATE)
        ci,cj=i+3.5,j+2
        cylinder(s,ci,cj,1.65,1.65,45,21,STONE,windows(STONE,21,10,21))
        cylinder(s,ci,cj,1.8,1.8,65,2,WHITE)
        dome(s,ci,cj,1.85,67,27,SLATE)
        cylinder(s,ci,cj,.3,.3,97,6,STONE,windows(STONE,6,5,8))
        cross(s,ci,cj,104)
        # Open columned porch and sculpted triangular tympanum.
        for a in (1.8,2.8,4,5):
            cylinder(s,i+a,j+D+.35,.14,.14,3,24,WHITE)
            band(s,i+a-.2,j+D+.15,.4,.4,3,WHITE,2)
        pediment(s,i+1.4,j+D-.1,4.2,.9,28,12)
        for a in (.0,5.3):
            block(s,i+a,j+D-1.9,1.7,2,65,STONE,windows(STONE,65,8,19))
            for z in (3,38,51,64):band(s,i+a,j+D-1.9,1.7,2,z)
            clock(s,i+a+.85,j+D+.15,3.5,44)
            dome(s,i+a+.85,j+D-.9,1.0,66,14,SLATE)
            cross(s,i+a+.85,j+D-.9,83)
        block(s,i+3,j+D+.03,1,.1,15,STONE,
              lambda u,v,lit:arch_opening(u,v,4,3,11,WOOD) or STONE['lit'])
        for a in range(4):block(s,i+1.3,j+D+.9+a*.23,4.4,.3,4-a,STONE)
    scene.add(i+j+W+D+4,draw)


def figure(s,i,j,z,height=11,winged=False):
    """Filled bronze cloak, head and arms; wings have a broad feathered silhouette."""
    spire(s,i,j,.27,z,height*.65,BRONZE,conical=True)
    cylinder(s,i,j,.19,.19,z+height*.65,height*.18,BRONZE)
    for sign in (-1,1):
        poly(s,[P(s,i,j,z+height*.55),P(s,i+sign*.5,j,z+height*.73),
                P(s,i+sign*.65,j,z+height*.95),P(s,i+sign*.2,j,z+height*.65)],lambda x,y:BRONZE['lit'])
        if winged:
            poly(s,[P(s,i,j,z+height*.65),P(s,i+sign*.85,j,z+height*1.12),
                    P(s,i+sign*.7,j,z+height*.65),P(s,i+sign*.2,j,z+height*.45)],lambda x,y:BRONZE['dark' if sign>0 else 'lit'])


def heroes_square(scene,i,j):
    """Millennium column/Gabriel, seven mounted chieftains and two curved king colonnades."""
    W,D=11,7
    def draw(s):
        block(s,i,j,W,D,2,WHITE)
        # Two separate quarter-circle colonnades with independent columns and entablature.
        for start in (3.3,5.0):
            previous=None
            for n in range(8):
                t=start+n*.16
                a,b=i+5.5+4.4*math.cos(t),j+2.8+2.8*math.sin(t)
                cylinder(s,a,b,.15,.15,3,27,STONE)
                cylinder(s,a,b,.24,.24,28,3,WHITE)
                if previous:
                    for z in (30,31,33):seg(s,P(s,*previous,z),P(s,a,b,z),WHITE['lit'],2)
                    # Seven historical figures in the seven bays of each colonnade.
                    figure(s,(a+previous[0])/2,(b+previous[1])/2,3,10)
                if n in (0,7):figure(s,a,b,34,8)
                if (start<4 and n==7) or (start>4 and n==0):
                    # War and Peace ride bronze chariots at the inner ends.
                    for delta in (-.25,.25):
                        cylinder(s,a+.45,b+delta,.35,.13,35,3,BRONZE)
                        cylinder(s,a+.75,b+delta,.12,.12,37,3,BRONZE)
                        for step in (.2,.65):block(s,a+step,b+delta,.08,.08,3,BRONZE,z=33)
                    cylinder(s,a-.15,b,.3,.3,34,2,BRONZE)
                previous=(a,b)
        ci,cj=i+5.5,j+5
        block(s,ci-.8,cj-.8,1.6,1.6,7,STONE,z=2)
        cylinder(s,ci,cj,.35,.35,9,52,WHITE,
                 lambda u,v,lit:STONE['line'] if int(u)%3==0 else None)
        cylinder(s,ci,cj,.55,.55,59,3,WHITE)
        figure(s,ci,cj,63,14,True)
        cross(s,ci-.65,cj,74)
        # Seven horse bodies, heads/necks, legs and seated riders around the pedestal.
        for n in range(7):
            t=n*math.tau/7;a,b=ci+1.4*math.cos(t),cj+1.15*math.sin(t)
            cylinder(s,a,b,.42,.22,5,3,BRONZE)
            cylinder(s,a-.33,b,.16,.16,7,4,BRONZE)
            cylinder(s,a-.45,b,.21,.13,10,2,BRONZE)
            for da in (-.25,.25):
                for db in (-.13,.13):block(s,a+da,b+db,.09,.09,4,BRONZE,z=2)
            figure(s,a+.05,b,8,6)
    scene.add(i+j+W+D+3,draw)


def szechenyi_baths(scene,i,j):
    """Ochre Neo-Baroque courtyard wings, three open-air turquoise pools and domed entrance."""
    W,D,H=11,8,26
    def draw(s):
        block(s,i,j,W,D,2,WHITE)

        def wing(a,b,w,d,height=H):
            block(s,a,b,w,d,height,OCHRE,windows(OCHRE,height,10,13))
            hip_roof(s,a,b,w,d,height,12 if height==H else 8,SLATE)
            for z in sorted({2,13,height-1}):band(s,a,b,w,d,z)

        wing(i,j,W,1.6)
        wing(i,j+1.6,1.5,6.4)
        # Long central swimming pool and two rounded thermal pools, bordered in stone.
        for a,b,ri,rj in ((5.2,4.5,1.25,2.4),(2.7,4.5,.8,1.9),(7.7,4.5,.8,1.9)):
            ellipse(s,i+a,j+b,ri,rj,2.25,WHITE['hi'])
            ellipse(s,i+a,j+b,ri-.1,rj-.1,2.2,STONE['dark'])
            ellipse(s,i+a,j+b,ri-.18,rj-.18,2.1,
                    lambda x,y:POOL[2] if iso.h01(int(x)//3,int(y),1909)<.045
                    else POOL[1] if iso.h01(int(x)//6,int(y)//2,1910)<.22 else POOL[0])
        # Central garden-side entrance mass and lateral domed roof pavilions.
        block(s,i+4.2,j-.3,2.6,2,34,OCHRE,windows(OCHRE,34,10,16))
        pediment(s,i+4.2,j+1.7,2.6,.25,34,9)
        cylinder(s,i+5.5,j+.65,1,1,37,7,OCHRE,windows(OCHRE,7,6,10))
        dome(s,i+5.5,j+.65,1.2,44,18,SLATE)
        # Ladders belong behind the foreground wing, along with the water.
        for a in (4,6.4):
            for b in (3,6):
                seg(s,P(s,i+a,j+b,3),P(s,i+a,j+b,7),SLATE['hi'])
                seg(s,P(s,i+a,j+b,7),P(s,i+a+.25,j+b,7),SLATE['hi'])
        # The low courtyard wing stands in front of the basins. Its walls/roof
        # occlude water and ladders; the taller corner pavilion remains behind it.
        wing(i+9.5,j+1.6,1.5,6.4,height=14)
        for a in (.8,10.2):
            cylinder(s,i+a,j+.8,.7,.7,29,5,OCHRE)
            dome(s,i+a,j+.8,.9,34,11,SLATE)
        for a in range(2,10,2):block(s,i+a,j+7.8,.15,.18,4,WHITE,z=2)
        band(s,i+1.5,j+7.8,8,.2,6,WHITE)
    scene.add(i+j+W+D+3,draw)


STUDIES=[('parliament',parliament),('matthias-church',matthias_church),
         ('fishermans-bastion',fishermans_bastion),('buda-castle',buda_castle),
         ('chain-bridge',chain_bridge),('st-stephen',st_stephen),
         ('heroes-square',heroes_square),('szechenyi-baths',szechenyi_baths)]

if __name__=='__main__':
    for name,builder in STUDIES:
        print(preview([lambda s,b=builder:b(s,3,3)],'budapest-'+name,
                      size=(280,270),origin=(120,135),tiles=25))
    print(preview([lambda s:townhouse(s,3,3,seed=0),lambda s:townhouse(s,7,3,seed=4),
                   lambda s:townhouse(s,5,8,floors=2,seed=5)],'budapest-houses',
                  size=(230,230),origin=(115,65),tiles=20))

    from pathlib import Path
    import sprites
    icon=sprites.tihany_abbey()
    path=Path(__file__).resolve().parents[2]/'docs/art/capitals/hungary-tihany-abbey.png'
    icon.resize((icon.width*4,icon.height*4),0).save(path)
    print(path)
