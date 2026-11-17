"""Podgorica: researched north-up sites, original projected (i, j, z) landmark studies.

Run this module for the isolated 4× studies. Coordinate sources and compass decisions are
recorded in DEVELOPMENT_PLAN.md. SITES is the sole placement source for the capital scene.
"""
import math

import iso
from iso import rgb
from landmarks_paris import P, seg, poly, corners, preview, GLASS
from landmarks_iberia import hip_roof, stone_courses, arch_opening, palette_of, tones
from landmarks_slovakia import block, band, pediment
from landmarks_slovenia import windows, revolve, slab, DOME
from landmarks_bosnia import cylinder
from landmarks_denmark import clock

STONE = tones('#F4EAD7', '#DCCDB2', '#C4B394', '#A28F73', '#77654F', '#B2A083', '#493D2E')
WHITE = tones('#FFFCF1', '#F0EADD', '#D9D2C1', '#B9B1A1', '#857D70', '#C8BEAA', '#514A3D')
PEACH = tones('#FFE0B6', '#E6BA8F', '#D4A47B', '#AF805E', '#805B43', '#C39570', '#523B2C')
CLAY = tones('#E4A17C', '#C27A54', '#A66040', '#81432E', '#583022', '#975337', '#48291E')
ROOF = tones('#B3B4B0', '#858D8C', '#6A7778', '#4D5D62', '#34444C', '#5F6D70', '#2C383E')
STEEL = tones('#FFFFFF', '#E6EBE4', '#CAD8D5', '#96B2B3', '#5F7F87', '#B6C9C8', '#3D5964')
GOLD = tones('#FFF3B6', '#DFC36E', '#BF9C46', '#92702A', '#695021', '#AE8A39', '#4D3B1F')
ROCK = tones('#DFD5BF', '#BBAF97', '#A0937B', '#80735D', '#5C5243', '#92836C', '#423C32')
WALLS = [rgb(c) for c in ('#DDD3B8', '#E5C39D', '#E8DFCE', '#C6CBB2', '#D4ABA0', '#C3CDCA')]
WOOD, IRON = rgb('#70503B'), rgb('#354447')
WATER = tuple(rgb(c) for c in ('#598E88', '#3E726E', '#BEDBD2'))
GROUND = {k: rgb(v) for k, v in {
    'square': '#DBCFB7', 'joint': '#BCB097', 'cobble': '#BBAF9A', 'cobble_joint': '#9B907D',
    'garden': '#91AA68', 'garden_light': '#B3C38A', 'flower': '#CC8D85', 'road': '#8C9390',
}.items()}


def cross(s, i, j, z, height=7):
    seg(s, P(s,i,j,z), P(s,i,j,z+height), GOLD['dark'], 2)
    seg(s, P(s,i-.22,j,z+height*.65), P(s,i+.22,j,z+height*.65), GOLD['hi'])


def arcade(s, i, j, width, depth, base, height, material=WHITE):
    """A genuine open, extruded semicircular arch; a bell can hang inside its opening."""
    # Ring voussoirs on the lit front, plus a shaded intrados and rear surface.
    for n in range(12):
        a,b=n*math.pi/12,(n+1)*math.pi/12
        outer=[(i+width/2+width/2*math.cos(t),base+height*.48+height*.52*math.sin(t)) for t in (a,b)]
        inner=[(i+width/2+(width/2-.18)*math.cos(t),base+height*.48+(height*.52-2)*math.sin(t)) for t in (a,b)]
        pts=[P(s,u,j+depth,v) for u,v in outer+inner[::-1]]
        poly(s,pts,lambda x,y,n=n:material['lit' if n%3 else 'mid'])
        seg(s,pts[0],pts[-1],material['line'])
        poly(s,[P(s,u,j,v) for u,v in inner]+[P(s,u,j+depth,v) for u,v in inner[::-1]],
             lambda x,y:material['dark'])
    for a in (i,i+width-.18):block(s,a,j,.18,depth,height*.5,material,z=base)
    # Bronze bell with a flared mouth, hung from the apex, visible through the arch.
    ci,cj=i+width/2,j+depth*.55
    seg(s,P(s,ci,cj,base+height-2),P(s,ci,cj,base+height*.52),IRON)
    revolve(s,ci,cj,.18,base+height*.39,height*.27,[(0,1),(.2,1),(.75,.55),(1,.25)],GOLD,ribs=2)


def cathedral(scene,i,j,z=0):
    """Rough limestone base, twin western square bell towers, monumental mosaic arch,
    one dark central dome, eastern apse and a 2+1 western bell gable."""
    W,D,H=10,10,39
    def draw(s):
        # Eastern altar apse, followed by the broad nave and rounded lateral arms.
        cylinder(s,i+5,j+.8,2.6,1.7,z,H-5,WHITE,windows(WHITE,H-5,11,16,arched=True))
        revolve(s,i+5,j+.8,2.7,z+H-5,12,DOME,ROOF,ribs=6)
        def masonry(u,v,lit):
            return stone_courses(STONE,8,15)(u,v,lit) if v<16 else windows(WHITE,H,12,18,arched=True)(u,v,lit)
        block(s,i+1,j+1,W-2,D-2,H,WHITE,masonry,z=z)
        hip_roof(s,i+.8,j+.8,W-1.6,D-1.6,z+H,10,ROOF)
        for a in (i+.9,i+W-.9):
            cylinder(s,a,j+4.3,1.6,2,z,29,WHITE,windows(WHITE,29,10,17,arched=True))
            revolve(s,a,j+4.3,1.7,z+29,9,DOME,ROOF,ribs=4)
        # One broad central drum and dark metal dome with meridional ribs.
        cylinder(s,i+5,j+4.1,2.5,2.5,z+H+4,16,WHITE,
                 windows(WHITE,16,9,16,arched=True,width=5))
        revolve(s,i+5,j+4.1,2.7,z+H+20,24,DOME,ROOF,ribs=4)
        cross(s,i+5,j+4.1,z+H+44,9)
        # West front: the Resurrection mosaic is confined to its great arch.
        fw=7*8
        def entrance(u,v,lit):
            if not lit:return masonry(u,v,lit)
            dx=(u-fw/2)/(fw/2-3)
            crown=13+19*math.sqrt(max(0,1-dx*dx))
            if abs(dx)<1 and v<crown:
                if v<12:
                    return WOOD if any(abs(u-c)<4.5 for c in (14,28,42)) else WHITE['dark']
                # Gold-ground icon, clothed central Christ and two groups of figures.
                if abs(dx)<.14 and 18<v<29:return WHITE['hi'] if v<26 else GOLD['hi']
                if .25<abs(dx)<.8 and 15<v<24:
                    return ROOF['mid'] if (int(u)//4+int(v)//5)%3 else WHITE['lit']
                return GOLD['lit' if lit else 'dark']
            if abs(v-crown)<2 and abs(dx)<1.1:return WHITE['hi']
            return masonry(u,v,lit)
        block(s,i+1.5,j+8.5,7,1.1,39,WHITE,entrance,z=z)
        band(s,i+1.4,j+8.5,7.2,1.15,z+37,WHITE,2)
        # Distinctive central 2+1 bell gable sits above the semicircular front gallery.
        cylinder(s,i+5,j+8,1.7,1.3,z+39,12,WHITE,
                 windows(WHITE,12,8,12,arched=True,width=5))
        revolve(s,i+5,j+8,1.8,z+51,6,DOME,ROOF,ribs=4)
        block(s,i+3.55,j+7.8,2.9,.5,17,WHITE,z=z+48)
        for a in (i+3.65,i+5.15):arcade(s,a,j+8.05,1.2,.5,z+56,12)
        pediment(s,i+3.5,j+8.05,3,.5,z+68,5,WHITE)
        arcade(s,i+4.4,j+8.15,1.2,.5,z+72,12)
        pediment(s,i+4.25,j+8.1,1.5,.6,z+84,5,WHITE)
        cross(s,i+5,j+8.4,z+89)
        # Matched western towers: open bell stages and flat dentilled eaves, no domed caps.
        for a in (i-.15,i+8.1):
            block(s,a,j+7.7,2.05,2.5,56,WHITE,
                  lambda u,v,lit:stone_courses(STONE if v<18 else WHITE,7 if v<18 else 5,12)(u,v,lit),z=z)
            for zz in (17,36,54):band(s,a,j+7.7,2.05,2.5,z+zz,WHITE,2)
            def belfry(u,v,lit):
                centre=8.2 if lit else 10
                dark=arch_opening(u,v-2,centre,5.4,8,IRON)
                if dark:
                    if abs(u-centre)<2 and 4<v<10:return GOLD['lit' if lit else 'dark']
                    return dark
                rim=arch_opening(u,v-1,centre,6.7,8,WHITE['hi' if lit else 'mid'])
                return rim or stone_courses(WHITE,5,10)(u,v,lit)
            block(s,a,j+7.7,2.05,2.5,18,WHITE,belfry,z=z+56)
            block(s,a-.15,j+7.6,2.35,2.8,3,WHITE,z=z+74)
            for off in (.1,.6,1.1,1.6):block(s,a+off,j+10.25,.18,.18,2,WHITE,z=z+73)
            cross(s,a+1,j+8.9,z+78,9)
            # Small paired pierced windows stay on the tower's front face.
            for off in (.45,1.2):
                block(s,a+off,j+10.22,.4,.08,12,WHITE,
                      lambda u,v,lit:IRON if 2<v<10 and int(v)%3 else None,z=z+38)
        for k in range(5):block(s,i+2,j+9.7+k*.3,6,.35,5-k,STONE,z=z)
    scene.add(i+j+W+D+3,draw)


def st_george(scene,i,j,z=0):
    """Small limestone single nave; western open 2+1 bell gable, clay roof, eastern apse."""
    W,D,H=4.3,7,24
    def draw(s):
        cylinder(s,i+W/2,j+.5,1.7,1.1,z,18,STONE,stone_courses(STONE,4,10))
        revolve(s,i+W/2,j+.5,1.8,z+18,7,DOME,CLAY,ribs=4)
        block(s,i,j+1,W,D-1,H,STONE,windows(STONE,H,11,14,arched=True),z=z)
        band(s,i,j+1,W,D-1,z+H-1,WHITE,2)
        hip_roof(s,i-.1,j+.9,W+.2,D-.8,z+H,10,CLAY)
        def front(u,v,lit):
            if lit:
                door=arch_opening(u,v,W*4,5,11,WOOD)
                if door:return door
            return stone_courses(STONE,4,10)(u,v,lit)
        block(s,i,j+D-.25,W,.4,H,STONE,front,z=z)
        # Broad central pier and the three actual bell openings above the western entrance.
        a=i+W/2-1.25;b=j+D-.1
        block(s,a,b,2.5,.48,8,WHITE,z=z+H-2)
        for off in (.04,1.29):arcade(s,a+off,b,1.17,.48,z+H+6,13)
        band(s,a-.1,b,2.7,.5,z+H+19,WHITE,2)
        arcade(s,a+.65,b,1.2,.48,z+H+21,12)
        pediment(s,a+.52,b,1.46,.5,z+H+33,5,WHITE)
        cross(s,a+1.25,b+.3,z+H+38)
        for off in (.1,2.4):cross(s,a+off,b+.3,z+H+20,5)
        for k in range(3):block(s,i+1,j+D+.2+k*.25,2.3,.3,3-k,STONE,z=z)
    scene.add(i+j+W+D+1,draw)


def millennium(scene,i,j,z=0):
    """Single eastern pylon; twelve main stays and twenty-four eastern backstays, long deck."""
    W,D=15,2.4
    def draw(s):
        block(s,i,j,W,D,4,STEEL,z=z+7)
        poly(s,list(corners(s,i,j+.35,W,D-.7,z+11)),lambda x,y:GROUND['road'])
        for k in range(1,15,2):seg(s,P(s,i+k,j+D/2,z+11.1),P(s,i+k+.7,j+D/2,z+11.1),WHITE['hi'])
        for b in (j+.08,j+D-.08):
            for a in range(16):seg(s,P(s,i+a,b,z+11),P(s,i+a,b,z+15),STEEL['dark'])
            seg(s,P(s,i,b,z+15),P(s,i+W,b,z+15),STEEL['lit'])
        # Pylon at +i = eastern/SE abutment, not at the western riverbank.
        pi,pj=i+11.9,j+D/2
        slab(s,[(pi-.38,pj-.28),(pi+.38,pj-.28),(pi+.19,pj+.28),(pi-.19,pj+.28)],z+11,z+99,STEEL)
        band(s,pi-.4,pj-.32,.8,.64,z+97,WHITE,2)
        for plane,b in enumerate((j+.15,j+D-.15)):
            for n in range(12):
                top=z+96-n*3.5
                if n % 2 == plane:  # six per plane: twelve main stays in total
                    seg(s,P(s,pi,pj,top),P(s,i+.4+n*.85,b,z+12),STEEL['lit' if b>pj else 'mid'])
                seg(s,P(s,pi,pj,top),P(s,i+12.7+n*.17,b,z+12),STEEL['mid'])
        # Twenty-four shorter backstays remain in the two eastern anchor planes.
        for n in range(0,15,4):
            a=i+n
            seg(s,P(s,a,j+D,z+12),P(s,a,j+D,z+25),IRON)
            seg(s,P(s,a,j+D,z+25),P(s,a+.35,j+D-.3,z+27),STEEL['lit'])
    scene.add(i+j+W+D+1,draw)


def ribnica(scene,i,j,z=0):
    """One humped stone arch and real open intrados, crossing the smaller river on +j."""
    W,D=1.9,8
    def draw(s):
        # Arch voussoirs are extruded in i; empty space below them shows the actual scene water.
        for n in range(24):
            t0,t1=n/24,(n+1)/24
            js=[j+D*t for t in (t0,t1)]
            low=[z+24*math.sqrt(max(0,1-(2*t-1)**2)) for t in (t0,t1)]
            high=[h+5 for h in low]
            for a,tone in ((i,STONE['mid']),(i+W,STONE['lit'])):
                pts=[P(s,a,js[0],low[0]),P(s,a,js[1],low[1]),P(s,a,js[1],high[1]),P(s,a,js[0],high[0])]
                poly(s,pts,lambda x,y,tone=tone: tone if (x+y)%7 else STONE['line'])
                seg(s,pts[0],pts[3],STONE['line'])
            poly(s,[P(s,i,js[0],high[0]),P(s,i,js[1],high[1]),P(s,i+W,js[1],high[1]),P(s,i+W,js[0],high[0])],
                 lambda x,y:GROUND['cobble'] if (x+2*y)%5 else GROUND['cobble_joint'])
            poly(s,[P(s,i,js[0],low[0]),P(s,i,js[1],low[1]),P(s,i+W,js[1],low[1]),P(s,i+W,js[0],low[0])],
                 lambda x,y:STONE['deep'])
            for a in (i,i+W):seg(s,P(s,a,js[0],high[0]+1),P(s,a,js[1],high[1]+1),STONE['hi'])
        for b in (j-.4,j+D):block(s,i-.15,b,W+.3,.5,4,ROCK,stone_courses(ROCK,3,8),z=z)
        for n in range(3):block(s,i-.2,j+D+.5+n*.3,W+.4,.35,3-n,STONE,z=z)
    scene.add(i+j+W+D+1,draw)


def palace(scene,i,j,z=0):
    """Long two-storey peach palace, white dressings/shutters, west balcony and curved attic."""
    W,D,H=11,5,32
    def draw(s):
        pat=windows(PEACH,H,14,16,hood=True,width=6)
        def shutters(u,v,lit):
            c,lv=int(u)%14,int(v)%16
            if v>3 and 3<lv<13 and c in (2,3,10,11):return WHITE['lit' if lit else 'dark'] if int(v)%2 else WHITE['line']
            return pat(u,v,lit)
        block(s,i,j,W,D,H,PEACH,shutters,z=z)
        for zz in (1,15,H-1):band(s,i,j,W,D,z+zz,WHITE,2)
        for a in (i+.1,i+W-.3):block(s,a,j+D,.25,.15,H,WHITE,z=z)
        hip_roof(s,i-.15,j-.15,W+.3,D+.3,z+H,12,CLAY)
        # Three real attic dormers; little clay gables, divided glass and white surrounds.
        for off in (2.3,5.2,8.1):
            block(s,i+off,j+D-1.1,.7,.65,7,WHITE,windows(WHITE,9,6,9,width=4),z=z+H+4)
            pediment(s,i+off-.05,j+D-.5,.8,.2,z+H+11,3,WHITE)
        for a in (i+1.1,i+8.7):
            block(s,a,j+.8,.5,.6,8,STONE,z=z+H+5)
            band(s,a,j+.8,.5,.6,z+H+12,WHITE,2)
        # Front entrance risalit, arched opening, shallow balcony with dressed balusters.
        a,b=i+4.2,j+D-.05
        block(s,a,b,2.6,.4,29,WHITE,
              lambda u,v,lit: arch_opening(u,v,10.4,7,8,WOOD) if lit and v<14 else None,z=z)
        for off in (.1,2.3):block(s,a+off,b+.4,.2,.2,28,WHITE,z=z)
        block(s,a-.15,b+.2,2.9,.8,2,WHITE,z=z+15)
        for n in range(9):block(s,a+n*.3,b+.87,.11,.11,4,WHITE,z=z+17)
        seg(s,P(s,a,b+.9,z+21),P(s,a+2.6,b+.9,z+21),WHITE['hi'],2)
        # Rounded attic crest above the central window; three-dimensional shallow extrusion.
        for n in range(14):
            a0,a1=n*math.pi/14,(n+1)*math.pi/14
            pts=[P(s,i+5.5+1.4*math.cos(t),j+D+.38,z+H+3+10*math.sin(t)) for t in (a0,a1)]
            poly(s,[P(s,i+5.5,j+D+.38,z+H+3),*pts],lambda x,y:PEACH['lit'])
            seg(s,*pts,WHITE['hi'],2)
        for n in range(4):block(s,i+4.3,j+D+.8+n*.3,2.4,.35,4-n,STONE,z=z)
    scene.add(i+j+W+D+2,draw)


def clock_tower(scene,i,j,z=0):
    """Single tall Ottoman rubble-stone shaft, slits, arched belfry, dial and low dark cap."""
    W,D,H=3.4,3.4,67
    def draw(s):
        def wall(u,v,lit):
            if 8<v<44 and int(u)%14 in (6,7) and int(v)%18 in (7,8,9):return IRON
            if v<10:
                door=arch_opening(u,v,13.6,3.5,6,WOOD)
                if door and lit:return door
            if 49<v<63:
                opening=arch_opening(u,v-49,13.6,6,7,IRON)
                if opening:return opening
            return stone_courses(STONE,4,9)(u,v,lit)
        block(s,i,j,W,D,H,STONE,wall,z=z)
        band(s,i,j,W,D,z+1,ROCK,2)
        band(s,i,j,W,D,z+H-1,WHITE,2)
        clock(s,i+W/2,j+D+.035,4,z+45)
        # Photograph/OSM roof tags disagree; select the restrained low charcoal hip, no dome.
        hip_roof(s,i-.1,j-.1,W+.2,D+.2,z+H,5,ROOF)
        seg(s,P(s,i+W/2,j+D/2,z+H+5),P(s,i+W/2,j+D/2,z+H+12),IRON)
        seg(s,P(s,i+W/2-.18,j+D/2,z+H+9),P(s,i+W/2+.18,j+D/2,z+H+9),IRON)
    scene.add(i+j+W+D,draw)


def townhouse(scene,i,j,wi=2.6,wj=3,floors=2,seed=0,z=0):
    """Low Podgorica limestone/stucco house: shutters, sills, shops, clay hip and iron balcony."""
    H=floors*11+2;wall=palette_of(WALLS[seed%len(WALLS)])
    base=windows(wall,H,10,11,width=5)
    def pattern(u,v,lit):
        c,lv=int(u)%10,int(v)%11
        if v<9 and 2<=c<=7:
            if c in (2,7) or int(v)==8:return STONE['lit' if lit else 'dark']
            return WOOD if seed%3 else GLASS['dark']
        if v>10 and 3<lv<9 and c in (1,8):return ROOF['lit' if lit else 'dark']
        return base(u,v,lit)
    def draw(s):
        block(s,i,j,wi,wj,H,wall,pattern,z=z)
        band(s,i,j,wi,wj,z+1,STONE,2);band(s,i,j,wi,wj,z+H-1,WHITE,2)
        hip_roof(s,i-.12,j-.12,wi+.24,wj+.24,z+H,9+seed%3,CLAY)
        block(s,i+.5,j+.5,.38,.45,7,STONE,z=z+H+5)
        band(s,i+.5,j+.5,.38,.45,z+H+11,CLAY,2)
        if seed%3==0 and floors>1:
            block(s,i+.55,j+wj,1.4,.48,1.5,WHITE,z=z+12)
            for off in range(7):seg(s,P(s,i+.6+off*.2,j+wj+.45,z+13),P(s,i+.6+off*.2,j+wj+.45,z+18),IRON)
            seg(s,P(s,i+.55,j+wj+.45,z+18),P(s,i+1.95,j+wj+.45,z+18),IRON)
    scene.add(i+j+wi+wj,draw)


def main():
    from pathlib import Path
    import sprites
    icon = sprites.ostrog()
    icon.resize((icon.width*4,icon.height*4),0).save(
        Path(__file__).resolve().parents[2]/'docs/art/capitals/podgorica-ostrog.png')
    for name,builder,(wi,wj),_,_,z in SITES:
        def study(s,b=builder,z=z,wi=wi,wj=wj):
            if z:
                for a in range(3,math.ceil(5+wi)):
                    for c in range(3,math.ceil(5+wj)):
                        iso.ground_tile(s,a,c,lambda x,y:GROUND['garden'],z,iso.stone_wall(ROCK['mid']))
            b(s,4,4,z=z)
        print(preview([study],'podgorica-'+name,
                      size=(290,250),origin=(95 if name == 'millennium' else 130,95),tiles=21))
    print(preview([lambda s:townhouse(s,4,4,seed=0),lambda s:townhouse(s,8,3,floors=1,seed=3),
                   lambda s:townhouse(s,9,8,floors=3,seed=4)],'podgorica-houses',
                  size=(230,190),origin=(110,35),tiles=17))


# (name, builder, footprint, real (longitude, latitude), scene anchor, elevation)
SITES = [
    ('cathedral', cathedral, (10,10), (19.248250,42.445694), (135,150), 12),
    ('st-george', st_george, (4.3,7), (19.267143,42.445424), (615,180), 20),
    ('millennium', millennium, (15,2.4), (19.258100,42.445200), (350,260), 0),
    ('ribnica', ribnica, (1.9,8), (19.258785,42.439474), (380,395), 0),
    ('palace', palace, (11,5), (19.250280,42.437780), (170,410), 12),
    ('clock-tower', clock_tower, (3.4,3.4), (19.260014,42.435557), (510,465), 12),
]

if __name__ == '__main__':
    main()
