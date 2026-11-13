"""Bratislava's coronation city in true projected (i, j, z), with native pixel textures.

Eight isolated landmark studies and an Old Town house study, each rendered at 4×.
Real geographic anchors and architectural sources are recorded in DEVELOPMENT_PLAN.md.
"""
import math

import iso
from iso import rgb
from landmarks_paris import P, seg, poly, corners, facade, mansard, preview, GLASS
from landmarks_iberia import hip_roof, stone_courses, arch_opening, palette_of, tones
from landmarks_amsterdam import gable_roof
from landmarks_italy import cylinder, ellipse
from landmarks_denmark import spire, clock

STONE = tones('#F6EDDB', '#DCCEB3', '#C5B498', '#A39277', '#75654F', '#B3A080', '#493C2C')
WHITE = tones('#FFFCF0', '#EEE8D7', '#D8D0BC', '#B9AF99', '#837863', '#CBC0A8', '#514634')
CLAY = tones('#F5B182', '#CF7950', '#B3603D', '#8D452F', '#613021', '#A65336', '#51291F')
SLATE = tones('#A6ADA6', '#7D8880', '#626F69', '#46534F', '#303D39', '#5A6861', '#293630')
COPPER = tones('#B9D7BE', '#81AF98', '#64917E', '#416B5D', '#2C4C42', '#577F6E', '#263E34')
PINK = tones('#F7D8C7', '#DFB1AA', '#C69592', '#A27577', '#754D56', '#B18486', '#563A40')
BLUE = tones('#E1F4F0', '#A6D4DF', '#81B6CC', '#5A8FAE', '#3E657F', '#729CB5', '#304D67')
CERAMIC = tones('#B9E7EB', '#76B9D0', '#5299B8', '#367495', '#24516F', '#4887A8', '#263F5A')
STEEL = tones('#F3F1DD', '#C3CBC6', '#A2B0AE', '#778F91', '#4C656D', '#90A2A1', '#344A55')
GOLD = tones('#FFF2AA', '#E8C461', '#C89D3F', '#A2782B', '#6E5022', '#B88B32', '#514022')
ROCK = tones('#D6C5A3', '#B4A27F', '#988562', '#776449', '#584A35', '#8D7959', '#453B2C')
WALLS = [rgb(c) for c in ('#E4C68E', '#DBCDB0', '#D7A9A0', '#B8C8B9', '#D6B372', '#C2B3CC')]
IRON, WOOD = rgb('#354139'), rgb('#70513A')
WATER = (rgb('#4E8991'), rgb('#376D7C'), rgb('#C3DFD9'))


def block(s, i, j, wi, wj, height, material=STONE, pattern=None, z=0):
    cover = facade(s, i, j, wi, wj, height,
                   pattern or stone_courses(material, 4, 10), palette=material, z0=z)
    iso.fill(s, list(corners(s, i, j, wi, wj, z+height)), lambda x,y:material['mid'], cover)
    iso.outline(s, cover, material['outline'])
    return cover


def band(s, i, j, wi, wj, z, material=WHITE, height=1):
    facade(s,i-.06,j-.06,wi+.12,wj+.12,height,
           lambda u,v,lit:material['hi' if lit else 'dark'],palette=material,z0=z)
    _,r,b,l=corners(s,i-.06,j-.06,wi+.12,wj+.12,z+height)
    seg(s,l,b,material['hi']);seg(s,b,r,material['deep'])


def windows(material, height, bay=10, floor=12, gothic=False, pilasters=False):
    courses=stone_courses(material,5,11)
    def pattern(u,v,lit):
        c,level=int(u)%bay,int(v)%floor
        trim=WHITE['lit' if lit else 'dark']
        if v<2 or int(v) in (height-1,height-3) or pilasters and c in (0,1):return trim
        top=floor-3-abs(c-bay/2)*(1.1 if gothic else .1)
        if 2<=c<=bay-2 and 3<=level<=top and v<height-3:
            if c in (2,bay-2,bay//2) or level in (3,6,int(top)):return trim
            return GLASS['mid' if lit else 'dark']
        return courses(u,v,lit) if material in (STONE,ROCK) else None
    return pattern


def pediment(s,i,j,width,depth,base,rise,material=WHITE):
    front=[P(s,i,j+depth,base),P(s,i+width,j+depth,base),P(s,i+width/2,j+depth,base+rise)]
    back=[P(s,i,j,base),P(s,i+width,j,base),P(s,i+width/2,j,base+rise)]
    poly(s,back,lambda x,y:material['mid'])
    for a,b in ((0,2),(2,1)):
        poly(s,[back[a],back[b],front[b],front[a]],lambda x,y:material['dark'])
    poly(s,front,lambda x,y:material['lit'] if (int(x)+int(y))%7 else material['mid'])
    for a,b in zip(front,front[1:]+front[:1]):seg(s,a,b,material['hi'],2)


def cross(s,i,j,z,material=GOLD):
    seg(s,P(s,i,j,z),P(s,i,j,z+8),material['dark'])
    seg(s,P(s,i-.25,j,z+5),P(s,i+.25,j,z+5),material['lit'])


SLOVAK_ARMS = ("rrWrr",
               "rWWWr",     # shorter upper bar of the double cross
               "rrWrr",
               "WWWWW",     # longer lower bar
               "rrWrr",
               "bbbbb",     # three blue hills
               " bbb ")


def flag(s,i,j,z):
    """Slovak flag: white, blue and red stripes with the coat of arms (white double cross on three
    blue hills, red shield, white border) toward the hoist, so it never reads as a plain tricolour."""
    seg(s,P(s,i,j,z),P(s,i,j,z+16),IRON)
    for n,c in enumerate((WHITE['hi'],rgb('#3B62A8'),rgb('#D2463C'))):
        poly(s,[P(s,i+a,j,z+15-n*3-b) for a,b in ((0,0),(1.7,0),(1.7,3),(0,3))],lambda x,y,c=c:c)
    x0,y0=P(s,i+.3,j,z+14)
    colours={'W':WHITE['hi'],'r':rgb('#C8322E'),'b':rgb('#2F55A0')}
    for dy,row in enumerate(SLOVAK_ARMS):
        for dx,ch in enumerate(row):
            if ch!=' ':
                s.put(x0+dx,y0+dy+int(dx*.5),colours[ch])


def townhouse(scene,i,j,wi=2.5,wj=3,floors=3,seed=0):
    """Pressburg stucco: dressed divided windows, shop arches, iron guards and clay roofs."""
    wall,H=palette_of(WALLS[seed%len(WALLS)]),floors*10+3
    base=windows(wall,H,9,10)
    def pattern(u,v,lit):
        c,level=int(u)%9,int(v)%10
        trim=WHITE['lit' if lit else 'dark']
        if v<9 and 1<=c<=7:
            if c in (1,7) or int(v) in (1,8):return trim
            return WOOD if (int(u)//9+seed)%3==0 else GLASS['dark']
        if seed%3==0 and v>=10 and level in (1,2) and 1<=c<=7:
            return IRON if level==1 or c%3==1 else base(u,v,lit)
        return base(u,v,lit)
    def draw(s):
        block(s,i,j,wi,wj,H,wall,pattern)
        band(s,i,j,wi,wj,1,STONE,2);band(s,i,j,wi,wj,H-1)
        if seed%5==0:mansard(s,i,j,wi,wj,H,11,.4,roof=SLATE,dormers=6)
        else:
            gable_roof(s,i,j,wi,wj,H,12,CLAY,wall,'point')
            if seed%2==0:
                block(s,i+.8,j+wj-.65,.65,.55,5,WHITE,windows(WHITE,8,5),z=H+3)
                hip_roof(s,i+.75,j+wj-.7,.75,.65,H+8,3,CLAY)
        block(s,i+wi-.65,j+.4,.4,.45,8,STONE,z=H+7)
        band(s,i+wi-.65,j+.4,.4,.45,H+14,CLAY,2)
        if seed%7==0:
            block(s,i+.65,j+wj,1.15,.42,1.5,STONE,z=13)
            for a in range(6):seg(s,P(s,i+.7+a*.2,j+wj+.4,14),P(s,i+.7+a*.2,j+wj+.4,18),IRON)
            seg(s,P(s,i+.65,j+wj+.4,18),P(s,i+1.8,j+wj+.4,18),IRON)
    scene.add(i+j+wi+wj,draw)


def castle(scene,i,j):
    """White quadrangle, four red capped towers, taller Crown Tower, open court and terrace."""
    W,D,H,Z=10,8,43,9
    def draw(s):
        block(s,i-.7,j-.7,W+1.4,D+1.4,Z,ROCK)
        for a in range(3):block(s,i+3,j+D+.2+a*.35,4,.4,7-a*2,STONE)
        # Far wings and far towers, court paving, then near wings/towers.
        parts=[(i,j,W,1.6,H),(i,j+1.5,1.6,D-1.5,H),
               (i+W-1.6,j+1.5,1.6,D-1.5,H),(i+1.5,j+D-1.6,W-3,1.6,H)]
        for a,b in ((i-.35,j-.35),(i+W-1.45,j-.35),(i-.35,j+D-1.45),(i+W-1.45,j+D-1.45)):
            parts.append((a,b,1.8,1.8,61 if a<i and b>j else 56))
        poly(s,list(corners(s,i+1.6,j+1.6,W-3.2,D-3.2,Z)),lambda x,y:WHITE['dark'] if (x+y)%5 else STONE['line'])
        for a,b,w,d,h in sorted(parts,key=lambda p:p[0]+p[1]+p[2]+p[3]):
            pat=windows(WHITE,h,10,12)
            block(s,a,b,w,d,h,WHITE,pat,z=Z)
            for z in (Z+3,Z+H-2):band(s,a,b,w,d,z)
            hip_roof(s,a-.06,b-.06,w+.12,d+.12,Z+h,13 if h>H else 10,CLAY)
            if h>H:
                band(s,a,b,w,d,Z+h-3,WHITE,2)
                cross(s,a+w/2,b+d/2,Z+h+13)
        # Carved central gate on the lit south façade, flanked by dressed columns.
        fj=j+D+.03
        for a in (4.1,5.7):block(s,i+a,fj,.2,.25,14,WHITE,z=Z)
        block(s,i+4.3,fj,1.4,.08,11,STONE,
              lambda u,v,lit:arch_opening(u,v,5.6,4.5,7,WOOD) or WHITE['lit'],z=Z)
        band(s,i+4,fj,2,.4,Z+14,WHITE,2)
        flag(s,i+5,j+1,Z+H+12)
    scene.add(i+j+W+D+3,draw)


def cathedral(scene,i,j):
    """St Martin: long Gothic nave, buttresses, west clock tower and crowned copper spire."""
    W,D,H=5,8,35
    def draw(s):
        block(s,i+.3,j,W-.6,D,H,STONE,windows(STONE,H,11,23,True))
        gable_roof(s,i+.3,j,W-.6,D,H,23,CLAY,STONE,'point')
        for b in (.4,2.3,4.3,6.3):
            block(s,i+W-.35,j+b,.5,.45,26,STONE)
            seg(s,P(s,i+W-.15,j+b,25),P(s,i+W-.65,j+b,35),WHITE['lit'],2)
        # West tower is visibly higher than all surrounding Old Town houses.
        ti,tj=i+.9,j+D-1.8
        block(s,ti,tj,2.6,2.6,64,STONE,windows(STONE,64,11,17,True))
        for z in (11,38,53,63):band(s,ti,tj,2.6,2.6,z)
        clock(s,ti+1.3,tj+2.65,5,51)
        clock(s,ti+2.65,tj+1.3,5,51,False)
        spire(s,ti+1.3,tj+1.3,1.65,65,16,COPPER,onion=True)
        cylinder(s,ti+1.3,tj+1.3,.55,.55,77,10,COPPER,windows(COPPER,12,5,10,True))
        spire(s,ti+1.3,tj+1.3,.85,87,27,COPPER)
        # Crown replica: solid golden cushion, open diadem lobes and central cross.
        cylinder(s,ti+1.3,tj+1.3,.38,.38,114,3,GOLD)
        for a in range(5):
            t=a*math.tau/5
            seg(s,P(s,ti+1.3+.38*math.cos(t),tj+1.3+.38*math.sin(t),117),
                P(s,ti+1.3,tj+1.3,121),GOLD['lit'],2)
        cross(s,ti+1.3,tj+1.3,119)
        # Deep pointed portal and splayed stone surround on the tower face.
        fj=tj+2.68
        pts=[P(s,ti+.65,fj,2),P(s,ti+1.95,fj,2),P(s,ti+1.95,fj,12),P(s,ti+1.3,fj,18),P(s,ti+.65,fj,12)]
        poly(s,pts,lambda x,y:WOOD)
        for a,b in zip(pts[1:],pts[2:]):seg(s,a,b,WHITE['hi'],2)
    scene.add(i+j+W+D+3,draw)


def michael_gate(scene,i,j):
    """Gate passage, white medieval shaft, clocks, double onion copper lantern and St Michael."""
    def draw(s):
        W,D=3.8,3.5
        shaft_windows=windows(WHITE,42,10,14)
        def gate(u,v,lit):
            opening=arch_opening(u,v,15.2,6,10,STONE['deep']) if lit else None
            return opening or shaft_windows(u,v,lit)
        block(s,i,j,W,D,42,WHITE,gate)
        for z in (2,16,30,41):band(s,i,j,W,D,z)
        block(s,i+.4,j+.4,3,2.7,15,WHITE,windows(WHITE,15,10,15),z=42)
        clock(s,i+1.9,j+3.15,4,50)
        clock(s,i+3.45,j+1.75,4,50,False)
        band(s,i+.4,j+.4,3,2.7,57)
        spire(s,i+1.9,j+1.75,1.7,58,22,COPPER,onion=True)
        cylinder(s,i+1.9,j+1.75,.5,.5,76,10,COPPER,windows(COPPER,10,5,8))
        spire(s,i+1.9,j+1.75,.85,86,16,COPPER,onion=True)
        # Filled miniature figure: cloak, head, wings and a diagonal sword.
        cylinder(s,i+1.9,j+1.75,.16,.16,103,5,COPPER)
        ellipse(s,i+1.9,j+1.75,.17,.17,109,GOLD['mid'])
        for sign in (-1,1):
            poly(s,[P(s,i+1.9,j+1.75,106),P(s,i+1.9+sign*.65,j+1.75,110),P(s,i+1.9+sign*.3,j+1.75,105)],lambda x,y:COPPER['lit'])
        seg(s,P(s,i+2.1,j+1.75,106),P(s,i+2.5,j+1.75,112),GOLD['dark'])
    scene.add(i+j+8,draw)


def town_hall(scene,i,j):
    """Old Town Hall: open courtyard, Gothic arcaded wing, patterned tiles and clock tower."""
    W,D=8,6
    def draw(s):
        for a,b,w,d in ((i,j,8,1.6),(i,j+1.6,1.6,4.4),(i+6.4,j+1.6,1.6,4.4),(i+1.6,j+4.4,4.8,1.6)):
            block(s,a,b,w,d,29,WHITE,windows(WHITE,29,10,14,True))
            gable_roof(s,a,b,w,d,29,16,CLAY,WHITE,'point')
        # Distinct diamond tiles on the long front slope, clipped to that roof plane.
        outer=corners(s,i+1.6,j+4.4,4.8,1.6,29)
        ridge=[P(s,i+2.4,j+5.2,45),P(s,i+5.6,j+5.2,45)]
        poly(s,[outer[3],outer[2],ridge[1],ridge[0]],
             lambda x,y:CERAMIC['lit'] if ((int(x)//3+int(y)//3)%5)==0 else CLAY['dark'] if int(y)%3==0 else CLAY['lit'])
        ti,tj=i-.2,j+3.7
        block(s,ti,tj,2.25,2.5,65,STONE,windows(STONE,65,9,15,True))
        for z in (3,20,42,56,64):band(s,ti,tj,2.25,2.5,z)
        clock(s,ti+1.12,tj+2.55,5,52)
        clock(s,ti+2.3,tj+1.25,5,52,False)
        spire(s,ti+1.12,tj+1.25,1.45,66,23,COPPER,onion=True)
        cross(s,ti+1.12,tj+1.25,89)
        # Gothic balcony gallery and carved entrance on the south face.
        for a in (2.4,3.5,4.6,5.7):
            block(s,i+a,j+D,.18,.25,13,STONE,z=12)
        band(s,i+2.2,j+D,4,.4,11,STONE,2)
        band(s,i+2.2,j+D,4,.3,25,STONE,2)
        block(s,i+2.5,j+D,.9,.12,10,STONE,
              lambda u,v,lit:arch_opening(u,v,3.6,3,7,WOOD) or STONE['lit'])
    scene.add(i+j+W+D+2,draw)


def primatial_palace(scene,i,j):
    """Pink Classicist palace: giant pilasters, triangular pediment, arms, cardinal's hat."""
    W,D,H=8.5,3.5,43
    def draw(s):
        block(s,i,j,W,D,H,PINK,windows(PINK,H,11,14,pilasters=True))
        hip_roof(s,i,j,W,D,H,11,SLATE)
        for z in (2,14,28,42):band(s,i,j,W,D,z)
        for a in (0,2.7,5.4,8.15):
            block(s,i+a,j+D,.27,.2,38,WHITE,z=3)
            band(s,i+a,j+D,.27,.2,40,WHITE,2)
        fj=j+D+.23
        # Pediment is a volumetric triangular prism attached to the central bay.
        pediment(s,i+2.35,fj-.25,3.8,.65,44,12,WHITE)
        # Filled allegorical figures and urns stand above the parapet.
        for a in (.5,1.6,6.7,7.8):
            block(s,i+a-.18,fj-.1,.36,.3,2,STONE,z=43)
            cylinder(s,i+a,fj,.17,.16,45,5,WHITE)
            cylinder(s,i+a,fj,.22,.18,49,2,WHITE)
            cylinder(s,i+a,fj,.15,.15,51,2,WHITE)
            seg(s,P(s,i+a-.25,fj,48),P(s,i+a+.25,fj,50),STONE['lit'],2)
        for a in (2.1,6.2):
            cylinder(s,i+a,fj,.2,.2,44,4,WHITE)
        # Carved coat of arms: rounded shield, scrolls and a broad cardinal's hat.
        cylinder(s,i+4.25,fj+.05,.32,.15,48,7,GOLD)
        ellipse(s,i+4.25,fj,.9,.32,58,IRON)
        cylinder(s,i+4.25,fj,.45,.28,58,3,palette_of(IRON))
        for sign in (-1,1):
            for n in range(3):
                seg(s,P(s,i+4.25+sign*(.5+n*.2),fj,57),P(s,i+4.25+sign*(.6+n*.2),fj,52-n),GOLD['dark'])
        block(s,i+3.2,j+D,2.1,.55,2,STONE,z=17)
        for a in range(10):seg(s,P(s,i+3.25+a*.22,j+D+.52,19),P(s,i+3.25+a*.22,j+D+.52,23),IRON)
        seg(s,P(s,i+3.2,j+D+.52,23),P(s,i+5.3,j+D+.52,23),IRON)
        for a in (3.35,4.4):
            block(s,i+a,j+D,.75,.1,13,WHITE,lambda u,v,lit:WOOD if 1<u<5 and v<11 else WHITE['lit'])
    scene.add(i+j+W+D+2,draw)


def grassalkovich(scene,i,j):
    """Rococo presidential palace: symmetrical wings, taller central pavilion, mansards, fence."""
    W,D=11,3.5
    def draw(s):
        block(s,i,j,W,D,27,WHITE,windows(WHITE,27,10,13,pilasters=True))
        mansard(s,i,j,W,D,27,13,.6,roof=SLATE,dormers=8)
        for z in (2,13,26):band(s,i,j,W,D,z)
        block(s,i+4,j-.25,3,4,36,WHITE,windows(WHITE,36,9,16,pilasters=True))
        mansard(s,i+4,j-.25,3,4,36,11,.5,roof=SLATE,dormers=7)
        pediment(s,i+4,j+D+.02,3,.6,37,9,WHITE)
        for a in (4.1,5.35,6.6):block(s,i+a,j+D,.18,.22,29,STONE,z=4)
        flag(s,i+5.5,j+1.7,48)
        # Palace's gilded gates and dressed piers leave the front elevation readable.
        for a in (0,3.2,7.8,10.8):
            block(s,i+a,j+D+1.1,.3,.35,10,STONE)
            cylinder(s,i+a+.15,j+D+1.28,.18,.18,10,2,GOLD)
        for a in range(42):
            x=i+.2+a*.26
            seg(s,P(s,x,j+D+1.25,2),P(s,x,j+D+1.25,9),IRON)
            if a%4==0:ellipse(s,x,j+D+1.25,.08,.08,10,GOLD['lit'])
        for z in (3,8):seg(s,P(s,i+.2,j+D+1.25,z),P(s,i+10.8,j+D+1.25,z),IRON)
    scene.add(i+j+W+D+2,draw)


def blue_church(scene,i,j):
    """St Elisabeth: blue glazed roof, round bell tower, white tendrils and mosaic medallion."""
    W,D,H=5,6,29
    def ceramic_windows(u,v,lit):
        c=int(u)%12
        if int(v)%9==0 or c in (0,1):return WHITE['lit' if lit else 'dark']
        if 3<=c<=8 and 8<v<23:
            if c in (3,8) or int(v) in (8,21) or abs(c-5.5)>2.5-(v-19)*.4 and v>19:
                return WHITE['hi' if lit else 'mid']
            return GLASS['dark']
        return BLUE['lit' if lit else 'dark']
    def draw(s):
        block(s,i,j,W,D,H,BLUE,ceramic_windows)
        gable_roof(s,i,j,W,D,H,18,CERAMIC,BLUE,'point')
        for z in (3,6,27):band(s,i,j,W,D,z,WHITE)
        # White scrolls are drawn in the plane of the blue south façade.
        fj=j+D+.05
        for a in (.5,1.7,3,4.3):
            prev=None
            for n in range(25):
                t=n*math.tau/24
                pt=P(s,i+a+.28*math.cos(t),fj,30+2.5*math.sin(t))
                if prev:seg(s,prev,pt,WHITE['lit'])
                prev=pt
        # Round tower rises beside the entrance, with white bands and arched belfry.
        ci,cj=i+.55,j+D-.4
        cylinder(s,ci,cj,1.1,1.1,0,65,BLUE,ceramic_windows)
        for z in (3,8,42,52,63):cylinder(s,ci,cj,1.16,1.16,z,1.5,WHITE)
        cylinder(s,ci,cj,1,1,53,10,BLUE,windows(BLUE,12,8,12,True))
        spire(s,ci,cj,1.25,65,19,CERAMIC,onion=True)
        cross(s,ci,cj,85,STEEL)
        clock(s,ci,cj+1.12,4,47)
        # Round mosaic medallion above the entrance, framed by a white ceramic ring.
        for radius,color in ((.68,WHITE['hi']),(.48,GOLD['mid']),(.3,PINK['lit'])):
            pts=[P(s,i+3.3+radius*math.cos(n*math.tau/32),fj,24+radius*8*math.sin(n*math.tau/32)) for n in range(32)]
            poly(s,pts,lambda x,y,c=color:c)
        block(s,i+2.6,fj,.25,.25,12,WHITE)
        block(s,i+3.8,fj,.25,.25,12,WHITE)
        block(s,i+2.85,fj,.9,.1,11,BLUE,lambda u,v,lit:arch_opening(u,v,3.6,3,7,WOOD) or WHITE['lit'])
        for a in range(3):block(s,i+2.5,fj+.2+a*.25,1.7,.3,3-a,STONE)
    scene.add(i+j+W+D+3,draw)


def snp_bridge(scene,i,j):
    """Single asymmetric cable-stayed span, south A-pylon and glazed saucer restaurant."""
    W,D,deck=2.8,22,10
    def draw(s):
        # Deck spans j, crossing a Danube reach along i at right angles.
        block(s,i,j,W,D,3,STEEL,z=deck)
        poly(s,list(corners(s,i+.25,j,W-.5,D,deck+3)),lambda x,y:SLATE['dark'])
        for a in (.25,W-.25):
            seg(s,P(s,i+a,j,deck+4),P(s,i+a,j+D,deck+4),STEEL['hi'])
        for b in range(1,22,3):
            seg(s,P(s,i+1.4,j+b,deck+3.2),P(s,i+1.4,j+b+.9,deck+3.2),WHITE['lit'])
        # Both inclined pylon legs are true tapered prisms with visible return faces.
        cj=j+D-3
        for a in (.15,2.65):
            bottom=corners(s,i+a-.25,cj-.35,.5,.7,0)
            top=corners(s,i+1.15+(a-1.4)*.28,cj-.15,.5,.7,91)
            for p,q,key in ((0,1,'mid'),(3,2,'lit'),(2,1,'dark')):
                poly(s,[bottom[p],bottom[q],top[q],top[p]],lambda x,y,k=key:STEEL[k])
                seg(s,bottom[p],top[p],STEEL['hi'] if key=='lit' else STEEL['deep'])
        for b in (1,4,7,10,13):
            for a in (.2,2.6):
                seg(s,P(s,i+1.4,cj+.1,88),P(s,i+a,j+b,deck+4),STEEL['lit'])
        # Saucer is a layered elliptical volume, with a continuous band of glazing.
        ci=i+1.4
        cylinder(s,ci,cj,1.2,1.2,88,5,STEEL)
        cylinder(s,ci,cj,2.4,2.4,93,4,STEEL)
        cylinder(s,ci,cj,2.25,2.25,97,6,STEEL,
                 lambda u,v,lit:STEEL['lit'] if int(u)%5==0 else GLASS['dark' if not lit else 'mid'])
        cylinder(s,ci,cj,2.55,2.55,103,2,STEEL)
        ellipse(s,ci,cj,1.6,1.6,107,STEEL['hi'])
        # Stair/observation room emerges from the roof as a solid low volume.
        cylinder(s,ci,cj,.7,.7,107,3,STEEL)
        for a in (.45,2.35):block(s,i+a-.2,j,.4,.8,deck,STONE)
    scene.add(i+j+W+D+4,draw)


if __name__=='__main__':
    studies=[('castle',castle),('st-martin',cathedral),('michael-gate',michael_gate),
             ('town-hall',town_hall),('primatial-palace',primatial_palace),
             ('grassalkovich',grassalkovich),('blue-church',blue_church),('snp-bridge',snp_bridge)]
    for name,builder in studies:
        print(preview([lambda s,b=builder:b(s,4,3)],'bratislava-'+name,
                      size=(350,280) if name=='snp-bridge' else (250,250),
                      origin=(230,125) if name=='snp-bridge' else (125,125),tiles=25))
    print(preview([lambda s:townhouse(s,3,3,seed=0),lambda s:townhouse(s,7,3,seed=7),
                   lambda s:townhouse(s,5,8,floors=2,seed=4)],'bratislava-houses',
                  size=(230,220),origin=(115,60),tiles=20))

    from pathlib import Path
    import sprites
    icon=sprites.spis_castle()
    path=Path(__file__).resolve().parents[2]/'docs/art/capitals/slovakia-spis-castle.png'
    icon.resize((icon.width*4,icon.height*4),0).save(path)
    print(path)
