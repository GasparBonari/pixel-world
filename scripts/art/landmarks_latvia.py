"""Riga: Baltic brick Gothic, sculpted merchant gables and copper lanterns in (i,j,z).

Eight isolated 4× studies precede integration. Geographic anchors and sources:
DEVELOPMENT_PLAN.md, Phase 4. All art is original, rendered at native pixel resolution.
"""
import math
from pathlib import Path

import iso
from iso import rgb
from landmarks_paris import P, seg, poly, corners, preview, GLASS
from landmarks_iberia import hip_roof, stone_courses, arch_opening, palette_of, tones
from landmarks_amsterdam import gable_roof
from landmarks_italy import cylinder, ellipse, column
from landmarks_denmark import spire, clock
from landmarks_slovakia import block, band, pediment

STONE = tones('#F3E8D0', '#D6C7AA', '#BDAC90', '#988970', '#70604C', '#AC9A7E', '#483D30')
PALE = tones('#FFF9E6', '#EDE3CA', '#D5C9AE', '#B2A68D', '#81735C', '#C0B498', '#514634')
BRICK = tones('#E8AE90', '#BD765A', '#A15B44', '#7C4235', '#552F28', '#95503E', '#412B25')
CLAY = tones('#F1B17C', '#CE7C4F', '#AF603D', '#88442F', '#5D3026', '#A45336', '#4C2A23')
COPPER = tones('#BCD6C0', '#83AD98', '#628F7D', '#416A5E', '#2A4B40', '#557C6C', '#243D33')
SLATE = tones('#AEBBB7', '#7E9592', '#647C79', '#455F5D', '#2E4443', '#566E6C', '#293B3A')
PINK = tones('#EBD5CE', '#C5A69C', '#AD8B82', '#896C65', '#634C46', '#9E7F75', '#483A34')
GOLD = tones('#FFF3B0', '#EBCB70', '#CCA248', '#9B792F', '#6C5223', '#B08C3D', '#514022')
YELLOW = tones('#FFF1CB', '#E5CB93', '#CFB079', '#AB8E60', '#786144', '#BD9D6A', '#53432F')
WALLS = [rgb(c) for c in ('#D7BC82', '#C39787', '#B2C5B2', '#E0D5BB', '#B8C8CD', '#B77B60', '#CDC1A4')]
IRON, WOOD = rgb('#35433D'), rgb('#6C4B37')
WATER = (rgb('#4C8490'), rgb('#376577'), rgb('#BDDADD'))


def windows(material, height, bay=10, floor=12, gothic=False):
    joints = stone_courses(material, 3 if material == BRICK else 5, 10)
    def pattern(u,v,lit):
        c,level=int(u)%bay,int(v)%floor
        trim=PALE['lit' if lit else 'dark']
        if v<2 or int(v) in (height-1,height-3):return trim
        top=floor-3-abs(c-bay/2)*(.9 if gothic else .1)
        if 2<=c<=bay-2 and 3<=level<=top and v<height-4:
            if c in (2,bay-2,bay//2) or level in (3,6,int(top)):return trim
            return GLASS['mid' if lit else 'dark']
        return joints(u,v,lit)
    return pattern


def rooster(s,i,j,z):
    """A filled golden rooster vane: belly, raised tail, neck, head and beak."""
    seg(s,P(s,i,j,z),P(s,i,j,z+6),GOLD['dark'])
    profile=[(-.55,2),(-.8,6),(-.55,5),(-.35,7),(-.2,4),(.2,4),(.3,7),
             (.55,8),(.7,7),(.95,7),(.7,6),(.6,3),(.3,1),(-.2,1)]
    poly(s,[P(s,i+a,j,z+b) for a,b in profile],lambda x,y:GOLD['lit'])
    seg(s,P(s,i-.5,j,z+3),P(s,i+.4,j,z+3),GOLD['hi'])


def figure(s,i,j,z,height=12,material=COPPER,arms=False):
    """Draped, solid sculpture with shoulders and head; relief scale at the base."""
    cylinder(s,i,j,.22,.18,z,height*.13,material)
    # Tapered robe is an extruded volume rather than a stick silhouette.
    for a,b,wi,wj,h,zz in ((i-.25,j-.16,.5,.32,height*.55,z+1),
                           (i-.34,j-.2,.68,.4,height*.18,z+height*.55)):
        block(s,a,b,wi,wj,h,material,z=zz)
    cylinder(s,i,j,.2,.18,z+height*.78,height*.17,material)
    ellipse(s,i,j,.21,.19,z+height*.95,material['hi'])
    if arms:
        for sign in (-1,1):
            a=P(s,i+sign*.23,j,z+height*.68);b=P(s,i+sign*.65,j,z+height*1.12)
            seg(s,a,b,material['dark'],3);seg(s,(a[0]-1,a[1]),(b[0]-1,b[1]),material['lit'])
    else:
        seg(s,P(s,i-.3,j,z+height*.65),P(s,i-.45,j,z+height*.3),material['dark'],2)


def townhouse(scene,i,j,wi=2.5,wj=3,floors=3,seed=0):
    """Riga merchant/Art Nouveau houses: sculpted lintels, occasional bays, copper or clay roofs."""
    wall,height=palette_of(WALLS[seed%len(WALLS)]),floors*10+3
    base=windows(wall,height,9,10)
    def pattern(u,v,lit):
        c,level=int(u)%9,int(v)%10
        if v<9 and 1<=c<=7:
            if c in (1,7) or int(v) in (1,8):return PALE['lit' if lit else 'dark']
            return WOOD if (int(u)//9+seed)%3==0 else GLASS['dark']
        if seed%3==0 and v>=10 and level==2 and 1<=c<=7:return IRON
        if level==9 and c in (3,6):return PALE['hi' if lit else 'mid']
        return base(u,v,lit)
    def draw(s):
        block(s,i,j,wi,wj,height,wall,pattern)
        band(s,i,j,wi,wj,1,STONE,2);band(s,i,j,wi,wj,height-1,PALE)
        roof=COPPER if seed%4==0 else CLAY
        if seed%4==0:
            hip_roof(s,i,j,wi,wj,height,14,roof)
            # Projecting polygonal bay and decorated attic in Riga's later streets.
            cylinder(s,i+wi*.5,j+wj+.12,.52,.32,11,height-12,wall,windows(wall,height,6,10))
            spire(s,i+wi*.5,j+wj+.12,.58,height,9,COPPER)
            pediment(s,i+.4,j+wj-.04,wi-.8,.18,height,8,PALE)
        else:
            gable_roof(s,i,j,wi,wj,height,17,roof,wall,'step' if seed%5==0 else 'point')
            fj=j+wj+.15
            block(s,i+wi/2-.15,fj,.3,.15,6,palette_of(WOOD),z=height+5)
            seg(s,P(s,i+wi/2,fj,height+12),P(s,i+wi/2,fj+.6,height+12),IRON,2)
        block(s,i+wi-.65,j+.35,.45,.5,9,BRICK,z=height+6)
        band(s,i+wi-.65,j+.35,.45,.5,height+14,STONE,2)
    scene.add(i+j+wi+wj,draw)


def riga_castle(scene,i,j):
    """Pale convent quadrangle, two great round corner towers and Latvian standard."""
    def draw(s):
        # The courtyard remains open between four textured, red-roofed ranges.
        for a,b,w,d,h in ((i,j,10,2,30),(i,j+2,2,4,31),(i+8,j+2,2,4,30),(i+2,j+5,6,1.8,29)):
            block(s,a,b,w,d,h,PALE,windows(PALE,h,10,12))
            hip_roof(s,a,b,w,d,h,13,CLAY)
            for z in (2,h-2):band(s,a,b,w,d,z,STONE)
        for ci,cj,h in ((i+.7,j+5.8,48),(i+9,j+.7,42)):
            cylinder(s,ci,cj,1.35,1.35,0,h,PALE,windows(PALE,h,11,14))
            ellipse(s,ci,cj,1.44,1.44,h,STONE['hi'])
            if h==48:
                ellipse(s,ci,cj,1.2,1.2,h+.2,STONE['deep'])
                for n in range(12):
                    angle=n*math.tau/12
                    block(s,ci+1.28*math.cos(angle)-.15,cj+1.28*math.sin(angle)-.15,.3,.3,4,PALE,z=h)
            else:spire(s,ci,cj,1.5,h+1,19,CLAY,conical=True)
        # Gate surround and the two historic sculptural plaques above its entry.
        fj=j+6.84
        block(s,i+4.1,fj,1.8,.18,15,STONE,
              lambda u,v,lit:arch_opening(u,v,7,4.5,9,WOOD) or None)
        for a in (4.35,5.3):figure(s,i+a,fj+.2,18,6,PALE)
        ci,cj=i+.7,j+5.8
        seg(s,P(s,ci,cj,52),P(s,ci,cj,72),IRON)
        for offset,h,col in ((0,3,BRICK['deep']),(3,1.5,PALE['hi']),(4.5,3,BRICK['deep'])):
            poly(s,[P(s,ci+a,cj,71-offset-b) for a,b in ((0,0),(1.4,0),(1.4,h),(0,h))],lambda x,y,c=col:c)
    scene.add(i+j+20,draw)


def three_brothers(scene,i,j):
    """White stepped Gothic, ochre Dutch Renaissance, narrow green Baroque merchant houses."""
    def draw(s):
        for n,(w,h,wall,style) in enumerate(((2.5,35,PALE,'step'),(3,40,YELLOW,'bell'),(1.8,34,palette_of(WALLS[2]),'neck'))):
            a=i+(0,2.6,5.7)[n]
            block(s,a,j,w,4,h,wall,windows(wall,h,10,12))
            gable_roof(s,a,j,w,4,h,20,CLAY,wall,style)
            band(s,a,j,w,4,2,STONE,2)
            if n==1:
                for z in (15,28,h-1):band(s,a,j,w,4,z,PALE)
                for u in (.15,w-.35):block(s,a+u,j+4.08,.2,.18,h-3,PALE,z=2)
                pediment(s,a+.65,j+4.12,1.7,.28,12,5,PALE)
            fj=j+4.15
            poly(s,[P(s,a+w/2+u,fj,z) for u,z in ((-.4,1),(.4,1),(.4,9),(0,12),(-.4,9))],lambda x,y:WOOD)
            if n==0:
                for u in (.25,2):block(s,a+u,fj+.1,.25,.7,4,STONE)
                for u in (.6,1.8):seg(s,P(s,a+u,fj,h+3),P(s,a+u,fj,h+11),IRON)
            block(s,a+w-.6,j+.5,.4,.5,7,BRICK,z=h+9)
    scene.add(i+j+15,draw)


def cathedral(scene,i,j):
    """Brick Gothic cathedral, south cloister and broad Baroque tower cap with rooster."""
    def draw(s):
        block(s,i,j,6,8,38,BRICK,windows(BRICK,38,13,28,True))
        gable_roof(s,i,j,6,8,38,24,CLAY,BRICK)
        for b in (.4,2.4,4.4,6.4):
            block(s,i+5.75,j+b,.65,.5,29,STONE)
            block(s,i+5.9,j+b,.4,.5,34,BRICK)
        # Cloister arcades on the south side, with an open central grass court.
        for a,b,w,d in ((i+6,j+1,3,.8),(i+8.2,j+1,.8,6),(i+6,j+6.2,3,.8)):
            block(s,a,b,w,d,12,BRICK,
                  lambda u,v,lit:arch_opening(u%8,v,4,2.3,7,BRICK['deep']) or stone_courses(BRICK,3,9)(u,v,lit))
            hip_roof(s,a,b,w,d,12,7,CLAY)
        ti,tj=i+.5,j+5.6
        block(s,ti,tj,3.6,3.6,64,BRICK,windows(BRICK,64,14,19,True))
        for z in (2,24,46,62):band(s,ti,tj,3.6,3.6,z,STONE,2)
        clock(s,ti+1.8,tj+3.65,4.5,54);clock(s,ti+3.65,tj+1.8,4.5,54,False)
        spire(s,ti+1.8,tj+1.8,2.35,66,22,SLATE,onion=True)
        cylinder(s,ti+1.8,tj+1.8,.48,.48,86,9,SLATE,
                 lambda u,v,lit:SLATE['deep'] if int(u)%5 in (2,3) else None)
        spire(s,ti+1.8,tj+1.8,.8,95,21,SLATE,conical=True)
        rooster(s,ti+1.8,tj+1.8,118)
        fj=tj+3.68
        for n in range(3):
            a=.5+n*.18
            seg(s,P(s,ti+a,fj,3),P(s,ti+a,fj,14),PALE['hi'])
            seg(s,P(s,ti+3.1-n*.18,fj,3),P(s,ti+3.1-n*.18,fj,14),STONE['dark'])
        poly(s,[P(s,ti+a,fj+.02,z) for a,z in ((1,0),(2.6,0),(2.6,12),(1.8,18),(1,12))],lambda x,y:WOOD)
    scene.add(i+j+20,draw)


def st_peter(scene,i,j):
    """Brick basilica, three Baroque portals and the skyline's stacked open copper lanterns."""
    def draw(s):
        block(s,i,j,5.8,8,40,BRICK,windows(BRICK,40,12,30,True))
        gable_roof(s,i,j,5.8,8,40,26,SLATE,BRICK)
        for b in (.3,2.2,4.1,6):
            block(s,i+5.6,j+b,.6,.45,33,BRICK)
            block(s,i+5.8,j+b,.35,.45,38,STONE)
        ti,tj=i+.95,j+5.5
        block(s,ti,tj,3.5,3.5,68,STONE,windows(STONE,68,14,22,True))
        for z in (2,26,48,66):band(s,ti,tj,3.5,3.5,z,PALE)
        clock(s,ti+1.75,tj+3.55,4,57)
        ci,cj=ti+1.75,tj+1.75
        # Three diminishing open belfries, each seated between bulbous copper collars.
        for z,r,h in ((69,2.15,14),(94,1.5,12),(117,.95,10)):
            spire(s,ci,cj,r,z,h,COPPER,onion=True)
            cylinder(s,ci,cj,r*.45,r*.45,z+h-2,2,COPPER)
            for a in range(8):
                t=a*math.tau/8
                block(s,ci+r*.55*math.cos(t)-.08,cj+r*.55*math.sin(t)-.08,.16,.16,9,COPPER,z=z+h)
            ellipse(s,ci,cj,r*.7,r*.7,z+h+9,COPPER['lit'])
        spire(s,ci,cj,.85,136,27,COPPER,conical=True)
        rooster(s,ci,cj,165)
        fj=j+9.08
        # Three sculpted Baroque entry portals, each with paired columns and pediment.
        for a in (.2,2.2,4.2):
            block(s,i+a,fj,1.5,.4,14,STONE,
                  lambda u,v,lit:arch_opening(u,v,6,3.6,8,WOOD) or None)
            for u in (.05,1.3):column(s,i+a+u,fj+.4,0,15,PALE,.22)
            pediment(s,i+a-.15,fj+.25,1.8,.4,15,4,PALE)
            figure(s,i+a+.75,fj+.45,20,6,PALE)
    scene.add(i+j+20,draw)


def blackheads(scene,i,j):
    """Red Dutch Renaissance guildhall: sculpted stepped gables, astronomical clock, four figures."""
    def draw(s):
        for a,w,h,rise in ((i,3.5,35,29),(i+3.7,5.3,43,38)):
            block(s,a,j,w,5.5,h,BRICK,windows(BRICK,h,12,15,True))
            gable_roof(s,a,j,w,5.5,h,rise,CLAY,BRICK,'step')
            for z in (2,16,31,h-1):band(s,a,j,w,5.5,z,PALE)
            fj=j+5.65
            # Projected pilasters and vertical stone tracery continue up the main gable.
            for u in (.22,w/3,2*w/3,w-.22):
                top=h+rise*(1-abs(u/w-.5)*2)
                block(s,a+u-.07,fj,.14,.15,top-18,PALE,z=18)
                ellipse(s,a+u,fj+.1,.18,.08,top+1,GOLD['lit'])
            # Scroll cartouches and ornamental finials on the sculpted gable steps.
            for u,z in ((.3,h+8),(w-.3,h+8),(.9,h+19),(w-.9,h+19)):
                ellipse(s,a+u,fj+.05,.22,.08,z,PALE['hi'])
                block(s,a+u-.06,fj,.12,.12,5,PALE,z=z)
            for u in (.5,w-1.35):
                block(s,a+u,fj,.85,.25,13,STONE,
                      lambda u,v,lit:arch_opening(u,v,3.4,2.6,8,WOOD) or None)
            if w>4:
                # Blue astronomical dial, twelve zodiac divisions and gold solar hands.
                ci=a+w/2
                rim=[P(s,ci+math.cos(n*math.tau/32)*.65,fj+.05,66+math.sin(n*math.tau/32)*5.2)
                     for n in range(33)]
                poly(s,rim,lambda x,y:GLASS['dark'])
                for left,right in zip(rim,rim[1:]):seg(s,left,right,GOLD['lit'])
                for n in range(12):
                    t=n*math.tau/12
                    seg(s,P(s,ci+math.cos(t)*.5,fj+.06,66+math.sin(t)*4),
                        P(s,ci+math.cos(t)*.65,fj+.06,66+math.sin(t)*5.2),GOLD['hi'])
                seg(s,P(s,ci,fj+.07,66),P(s,ci+.3,fj+.07,69),GOLD['lit'])
                seg(s,P(s,ci,fj+.07,66),P(s,ci-.4,fj+.07,65),GOLD['lit'])
                # Small sun cartouche below the dial.
                cylinder(s,ci,fj+.07,.18,.06,56,2,GOLD)
                for u in (.6,1.95,3.3,4.65):
                    block(s,a+u-.3,fj+.1,.6,.4,2,PALE,z=20)
                    figure(s,a+u,fj+.25,22,10,PALE)
                figure(s,a+w/2,fj,88,8,GOLD)
    scene.add(i+j+20,draw)


def freedom(scene,i,j):
    """Stepped granite relief plinth, travertine column, full copper Milda and three gold stars."""
    def draw(s):
        for inset,z,h in ((0,0,3),(.35,3,3),(.8,6,13),(1.5,19,10)):
            block(s,i+inset,j+inset,6-2*inset,6-2*inset,h,PINK,z=z)
            band(s,i+inset,j+inset,6-2*inset,6-2*inset,z+h-1,STONE)
        for a,b in ((1.2,5.1),(3,5.1),(4.8,5.1),(5.1,1.4),(5.1,3.3)):
            figure(s,i+a,j+b,7,10,STONE)
        block(s,i+2.05,j+2.05,1.9,1.9,54,PALE,
              lambda u,v,lit:PALE['line'] if int(v)%18==0 or int(u)==7 else None,z=29)
        band(s,i+2.05,j+2.05,1.9,1.9,81,STONE,2)
        figure(s,i+3,j+3,84,22,COPPER,True)
        # Exactly three five-pointed gold stars, with filled extruded backs.
        for u,z in ((-1.1,111),(0,115),(1.1,111)):
            front=[]
            for n in range(10):
                t=-math.pi/2+n*math.pi/5;r=3 if n%2==0 else 1.35
                front.append(P(s,i+3+u+math.cos(t)*r/8,j+3, z-math.sin(t)*r))
            back=[(x+1,y+1) for x,y in front]
            poly(s,back,lambda x,y:GOLD['dark']);poly(s,front,lambda x,y:GOLD['lit'])
    scene.add(i+j+15,draw)


def opera(scene,i,j):
    """White neoclassical opera: six columns, pediment relief, roof sculpture and stairs."""
    def draw(s):
        block(s,i,j,10,5,34,PALE,windows(PALE,34,11,13))
        hip_roof(s,i,j,10,5,34,13,SLATE)
        for z in (2,17,32):band(s,i,j,10,5,z,STONE)
        block(s,i+1.8,j+4.9,6.4,1.6,4,STONE)
        for a in range(6):column(s,i+2.1+a*1.15,j+6,4,25,PALE,.45)
        band(s,i+1.7,j+4.9,6.6,1.5,29,PALE,3)
        pediment(s,i+1.6,j+4.9,6.8,1.6,32,12,PALE)
        # Pediment group is kept within the triangle, with a central Apollo/lyre figure.
        for a,h in ((3.1,4),(4.1,7),(5.2,7),(6.4,4)):
            figure(s,i+a,j+6.55,33,h,STONE)
        figure(s,i+5,j+5.6,47,12,PALE)
        for a in (-1,1):
            poly(s,[P(s,i+5+a*u,j+5.6,52+z) for u,z in ((.2,0),(1.5,3),(1.2,5),(.4,3))],lambda x,y:PALE['lit'])
        for n in range(5):block(s,i+1.5,j+6.4+n*.25,7,.3,5-n,STONE)
    scene.add(i+j+20,draw)


def market_hall(s,i,j,wi=2.3,wj=6,base=13,rise=13):
    """Long barrel vault with steel ribs and a glazed semicircular end in its own plane."""
    block(s,i,j,wi,wj,base,YELLOW,windows(YELLOW,base,9,12))
    # Roof cross-section swept along j. Mesh facets use material ramps and raised ribs.
    for n in range(16):
        a,b=n*math.pi/16,(n+1)*math.pi/16
        profile=lambda t,k:P(s,i+wi/2+wi/2*math.cos(t),j+k,base+rise*math.sin(t))
        pts=[profile(a,0),profile(a,wj),profile(b,wj),profile(b,0)]
        lit=n>=8
        poly(s,pts,lambda x,y,lit=lit:SLATE['line'] if int(y)%5==0 else SLATE['lit' if lit else 'dark'])
        if n%4==0:seg(s,pts[0],pts[1],SLATE['hi' if lit else 'deep'])
    fj=j+wj+.03
    pts=[P(s,i+wi/2+wi/2*math.cos(n*math.pi/24),fj,base+rise*math.sin(n*math.pi/24)) for n in range(25)]
    foot=P(s,i,fj,base)
    def glazing(x,y):
        u=x-foot[0];v=foot[1]+u*.5-y
        return STONE['lit'] if int(u)%5==0 or int(v)%5==0 else GLASS['mid']
    poly(s,pts,glazing)
    for a,b in zip(pts,pts[1:]):seg(s,a,b,YELLOW['hi'],2)
    band(s,i,j,wi,wj,base-1,STONE)


def central_market(scene,i,j):
    """Five former hangar roof pavilions: four parallel barrels and the separate transverse hall."""
    def draw(s):
        # One crosswise hall, then four parallel halls, as at the real market.
        block(s,i,j,9.5,2.3,13,YELLOW,windows(YELLOW,13,9,12))
        for n in range(16):
            a,b=n*math.pi/16,(n+1)*math.pi/16
            def pt(t,k):return P(s,i+k,j+1.15+1.15*math.cos(t),13+13*math.sin(t))
            pts=[pt(a,0),pt(a,9.5),pt(b,9.5),pt(b,0)]
            poly(s,pts,lambda x,y,n=n:SLATE['line'] if int(y)%5==0 else SLATE['lit' if n<8 else 'dark'])
        # The four parallel vaults have narrow open pedestrian aisles.
        for n in range(4):market_hall(s,i+n*2.7,j+3,2.3,6)
        for n in range(8):
            a=i+.3+n*1.3;b=j+9.8
            block(s,a,b,1,.6,3,palette_of(WOOD))
            hip_roof(s,a-.1,b-.1,1.2,.8,3,2,CLAY if n%2 else PALE)
    scene.add(i+j+25,draw)


# name, builder, footprint, real lon/lat, compressed north-up ground anchor.
SITES = [
    ('freedom', freedom, (6,6), (24.11338,56.95143), (550,145)),
    ('castle', riga_castle, (10.5,8), (24.100636,56.95095), (150,205)),
    ('three-brothers', three_brothers, (7.5,4.5), (24.10429,56.95031), (285,220)),
    ('opera', opera, (10,8), (24.11439,56.94929), (610,290)),
    ('cathedral', cathedral, (9,9.5), (24.104444,56.949167), (305,360)),
    ('st-peter', st_peter, (6,10), (24.1087,56.947499), (535,400)),
    ('blackheads', blackheads, (9,6), (24.10685,56.94726), (400,465)),
    ('central-market', central_market, (10.5,11), (24.115,56.94386), (620,467)),
]


def main():
    for name,builder,_,_,_ in SITES:
        print(preview([lambda s,b=builder:b(s,4,4)],'riga-'+name,
                      size=(280,310),origin=(130,175),tiles=20))
    print(preview([lambda s,n=n:townhouse(s,3+n*3,3,2.5,3,2+n%2,n) for n in range(5)],
                  'riga-houses',size=(280,230),origin=(70,80),tiles=22))
    import sprites
    sprite=sprites.rundale()
    path=Path(__file__).resolve().parents[2]/'docs/art/capitals/latvia-rundale.png'
    sprite.resize((sprite.width*4,sprite.height*4),0).save(path)
    print(path)


if __name__=='__main__':main()
