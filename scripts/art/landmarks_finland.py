"""Helsinki: Empire white, Finnish granite, Jugend plaster and oxidised copper.

All architecture is projected from (i, j, height); +j faces are lit. Run this
file for eight isolated 4× landmark studies and a Helsinki house study.
Geographic anchors and references are recorded in DEVELOPMENT_PLAN.md.
"""
import math

import iso
from iso import rgb, h01
from landmarks_paris import P, seg, poly, corners, facade, preview, GLASS
from landmarks_iberia import hip_roof, stone_courses, arch_opening, palette_of, tones
from landmarks_belgium import dome, pediment
from landmarks_italy import cylinder, cross
from landmarks_denmark import spire, clock
from landmarks_amsterdam import gable_roof

WHITE = tones('#FFFFFF', '#F2F0DD', '#DCDDCB', '#B4BEB4', '#81958E', '#C8CEC0', '#4B625E')
GRANITE = tones('#DDD7CC', '#BCB8A8', '#A09F91', '#7A857B', '#53675D', '#8E9989', '#374C43')
PINK = tones('#E2C4B2', '#C5A08C', '#AD8776', '#8B6C60', '#624E46', '#A18372', '#483A35')
BRICK = tones('#DDA282', '#B67559', '#995D45', '#754433', '#502D25', '#915B46', '#3B2924')
COPPER = tones('#C2D9BE', '#8CB29B', '#6C927E', '#486E5E', '#304D42', '#618773', '#293E35')
SLATE = tones('#A4ADAC', '#768A8B', '#5B7378', '#405A63', '#2B414B', '#536D72', '#263A43')
GOLD = tones('#FFF2B5', '#EBCB70', '#CCA34B', '#9E7935', '#6F5228', '#B48D3F', '#514023')
WOOD = tones('#C5A078', '#9B7855', '#7B5A3E', '#59422F', '#3C3026', '#785B40', '#302820')
WALLS = [rgb(c) for c in ('#E3CD94', '#C2D2BE', '#DCB8B3', '#DCE0CC', '#A9C6CA', '#C9B2CB')]
WATER = (rgb('#477F91'), rgb('#345F76'), rgb('#BEDDDF'))
IRON, BLUE = rgb('#334A46'), rgb('#315D8C')


def block(s, i, j, wi, wj, height, material=GRANITE, pattern=None, z=0):
    cover = facade(s, i, j, wi, wj, height,
                   pattern or stone_courses(material, 4, 9), palette=material, z0=z)
    iso.fill(s, list(corners(s, i, j, wi, wj, z+height)), lambda x,y: material['mid'], cover)
    iso.outline(s, cover, material['outline'])
    return cover


def windows(material, height, bay=10, floor=13, arched=False, plaster=False):
    courses = stone_courses(material, 3 if material == BRICK else 5, 9)
    def pattern(u,v,lit):
        c,v = int(u)%bay,int(v)
        level,trim = v%floor,WHITE['lit' if lit else 'dark']
        if v < 2 or v in (height-1,height-3):
            return material['hi' if lit else 'mid']
        top = floor-3-(abs(c-bay/2)*.7 if arched else 0)
        if 2 <= c <= bay-2 and 3 <= level <= top and v < height-3:
            if c in (2,bay-2,bay//2) or level in (3,6,int(top)):
                return trim
            return GLASS['mid' if lit else 'dark']
        if level == 1:
            return material['line' if lit else 'deep']
        return None if plaster else courses(u,v,lit)
    return pattern


def column(s,i,j,z,height,material=WHITE,radius=.18):
    cylinder(s,i,j,radius*1.6,radius*1.6,z,2,material)
    cylinder(s,i,j,radius,radius,z+2,height-4,material,
             lambda u,v,lit: material['line' if lit else 'deep'] if int(u)%3==0 else None)
    block(s,i-radius*1.6,j-radius*1.6,radius*3.2,radius*3.2,2,material,z=z+height-2)


def flag(s,i,j,z):
    seg(s,P(s,i,j,z),P(s,i,j,z+17),IRON)
    for a,b,low,high,color in ((0,1.7,9,17,WHITE['hi']),(.5,.78,9,17,BLUE),(0,1.7,12,14,BLUE)):
        poly(s,[P(s,i+a,j,z+low),P(s,i+b,j,z+low),P(s,i+b,j,z+high),P(s,i+a,j,z+high)],
             lambda x,y,color=color:color)


def apostle(s,i,j,z):
    """A filled zinc robe, bent arm, separate head and shaded thickness above a plinth."""
    profile=[(-.38,0),(.38,0),(.25,4),(.4,5),(.23,6),(-.2,6),(-.4,4)]
    front=[P(s,i+a,j,z+b) for a,b in profile]
    back=[P(s,i+a,j-.18,z+b) for a,b in profile]
    for k in range(len(front)):
        n=(k+1)%len(front)
        poly(s,[back[k],back[n],front[n],front[k]],lambda x,y:GRANITE['dark'])
    poly(s,front,lambda x,y:GRANITE['lit'] if int(x)%3 else GRANITE['line'])
    cylinder(s,i,j,.18,.18,z+6,3,GRANITE)
    seg(s,P(s,i-.3,j,z+4),P(s,i+.1,j+.12,z+5),GRANITE['hi'],2)


def townhouse(scene,i,j,wi=2.7,wj=3,floors=3,seed=0):
    """Helsinki Jugend: pastel stucco, granite, asymmetrical bays and shaped copper gables."""
    wall,height = palette_of(WALLS[seed%len(WALLS)]),floors*10+4
    def pattern(u,v,lit):
        c,v = int(u)%10,int(v)
        level,trim = v%10,WHITE['lit' if lit else 'dark']
        if v<3:
            return stone_courses(GRANITE,3,7)(u,v,lit)
        if v in (height-1,height-3):
            return trim
        if v<10 and 2<=c<=8 and 2<=v<=8:
            if c in (2,8) or v==8:return trim
            if (int(u)//10+seed)%3==0:
                return WOOD['deep'] if c==5 or v==5 else WOOD['lit' if lit else 'dark']
            return GLASS['mid' if lit else 'dark']
        if v>=10 and 2<=c<=8 and 3<=level<=8 and v<height-4:
            if c in (2,5,8) or level in (3,6,8):return trim
            return GLASS['mid' if lit else 'dark']
        if v>=10 and level==2 and 1<=c<=9:return trim
        # Small plant/curved-stucco accents, rather than continuous balcony bands.
        if seed%3==0 and v>=10 and level==0 and c in (3,4,6,7):return wall['hi' if lit else 'mid']
        return wall['line'] if h01(int(u),v,seed)<.013 else None
    def draw(s):
        block(s,i,j,wi,wj,height,wall,pattern)
        roof = COPPER if seed%3 else SLATE
        hip_roof(s,i-.08,j-.08,wi+.16,wj+.16,height,12,roof)
        if seed%4==0:
            # A projecting polygonal bay, supported by dressed granite at ground level.
            cylinder(s,i+wi*.55,j+wj, .62,.45,9,height-10,wall,
                     windows(wall,height-10,bay=8,floor=10,plaster=True))
            spire(s,i+wi*.55,j+wj,.75,height-1,11,roof,conical=True)
        else:
            gable_roof(s,i+.3,j+wj-.65,wi-.6,.65,height,10,roof,wall,'point')
        # One iron balcony, occasional corner turret, and capped masonry chimney.
        if seed%5==1:
            block(s,i+.6,j+wj,1.3,.35,1,GRANITE,z=13)
            for a in (.65,.95,1.25,1.8):
                seg(s,P(s,i+a,j+wj+.35,14),P(s,i+a,j+wj+.35,18),IRON)
            seg(s,P(s,i+.6,j+wj+.35,18),P(s,i+1.9,j+wj+.35,18),IRON)
        if seed%9==0:
            cylinder(s,i+wi,j+.4,.48,.48,height-4,10,wall,windows(wall,10,bay=7,floor=9))
            spire(s,i+wi,j+.4,.65,height+6,14,roof,conical=True)
        block(s,i+.4,j+.5,.4,.5,8,BRICK,z=height+5)
        block(s,i+.35,j+.45,.5,.6,1.5,GRANITE,z=height+12)
    scene.add(i+j+wi+wj,draw)


def cathedral(scene,i,j):
    """Greek cross, six-column temple portico, broad stairs and five green domes."""
    def draw(s):
        for k in range(8):
            block(s,i+.5,j+6.3+k*.25,7,.28,8-k,GRANITE)
        block(s,i,j,8,6.5,8,GRANITE)
        pattern=windows(WHITE,34,bay=12,floor=20,arched=True,plaster=True)
        block(s,i+2,j,4,6.5,34,WHITE,pattern,z=8)
        block(s,i,j+1.7,8,3.2,34,WHITE,pattern,z=8)
        hip_roof(s,i+2,j,4,6.5,42,9,COPPER)
        hip_roof(s,i,j+1.7,8,3.2,42,9,COPPER)
        # Four real corner bell cupolas, below the great central tambour.
        for a,b in ((.8,1.2),(6,1.2),(.8,4.6),(6,4.6)):
            block(s,i+a,j+b,1.25,1.25,9,WHITE,windows(WHITE,13,bay=7,floor=12),z=40)
            dome(s,i+a+.625,j+b+.625,.77,49,8,COPPER)
            cross(s,i+a+.625,j+b+.625,57,GOLD)
        # Portico is drawn before the high central dome; shafts remain individually open.
        block(s,i+1.4,j+6,5.2,1.2,3,WHITE,z=8)
        for n in range(6):column(s,i+1.7+n*.92,j+7,11,27)
        block(s,i+1.2,j+5.9,5.6,1.5,3,WHITE,z=38)
        pediment(s,i+1.2,j+7.4,5.6,41,12,WHITE)
        # Zinc apostles are filled robed miniatures, individually seated above the cornice.
        for a,b in ((0,2),(0,3.3),(0,4.6),(8,2),(8,3.3),(8,4.6),
                    (1.3,7.35),(3.1,7.35),(4.9,7.35),(6.6,7.35),(2,0),(6,0)):
            apostle(s,i+a,j+b,44)
        def tambour(u,v,lit):
            c,v=int(u)%8,int(v)
            if c in (0,1):return WHITE['hi' if lit else 'mid']
            if 3<=c<=6 and 5<v<20:
                if c in (3,6) or v in (6,19):return WHITE['lit' if lit else 'dark']
                return WHITE['mid'] if v==12 else GLASS['mid' if lit else 'dark']
            return WHITE['line' if lit else 'deep'] if v in (2,22) else None
        cylinder(s,i+4,j+3.2,1.65,1.65,46,24,WHITE,
                 tambour)
        cylinder(s,i+4,j+3.2,1.83,1.83,68,3,WHITE)
        dome(s,i+4,j+3.2,1.9,71,20,COPPER)
        cylinder(s,i+4,j+3.2,.2,.2,91,3,GOLD)
        cross(s,i+4,j+3.2,94,GOLD)
    scene.add(i+j+17,draw)


def uspenski(scene,i,j):
    """Red-brick Russian Revival church: thirteen gilded cupolas, apse and belltower."""
    def cupola(s,a,b,z,radius=.38,rise=7):
        cylinder(s,a,b,radius*.62,radius*.62,z,3,BRICK)
        spire(s,a,b,radius,z+3,rise,GOLD,onion=True)
        cross(s,a,b,z+3+rise,GOLD)
    def draw(s):
        block(s,i-.4,j-.4,6.8,6.3,6,GRANITE)
        brick_windows=windows(BRICK,38,bay=9,floor=18,arched=True)
        block(s,i,j,6,4.8,38,BRICK,brick_windows,z=6)
        hip_roof(s,i-.08,j-.08,6.16,4.96,44,13,COPPER)
        # Deep rounded sanctuary and dressed brick buttresses.
        cylinder(s,i+5.6,j+2.1,1.1,1.3,6,29,BRICK,windows(BRICK,29,bay=9,floor=18,arched=True))
        dome(s,i+5.6,j+2.1,1.25,35,8,COPPER)
        for a in (.1,1.8,4,5.7):
            block(s,i+a,j+4.8,.28,.3,31,BRICK,z=6)
            pediment(s,i+a-.18,j+5.1,.65,37,5,BRICK)
        # Eight smaller pinnacles around the body, then four taller corner domes.
        for a,b in ((.2,.3),(2,.2),(4,.2),(5.8,.3),(.2,4.5),(2,4.5),(4,4.5),(5.8,4.5)):
            cupola(s,i+a,j+b,46,.32,6)
        for a,b in ((1,1),(5,1),(1,3.7),(5,3.7)):
            block(s,i+a-.45,j+b-.45,.9,.9,12,BRICK,
                  windows(BRICK,15,bay=6,floor=13,arched=True),z=44)
            cupola(s,i+a,j+b,56,.47,8)
        # Tall central tent and golden principal dome: 8 + 4 + 1 = thirteen cupolas.
        cylinder(s,i+3,j+2.4,1.2,1.2,48,20,BRICK,
                 windows(BRICK,22,bay=8,floor=22,arched=True))
        spire(s,i+3,j+2.4,1.5,68,20,COPPER,conical=True)
        cupola(s,i+3,j+2.4,88,.57,9)
        # Separate lower western bell tower has a green pyramidal roof, no invented gilt dome.
        block(s,i+.2,j+5,1.6,1.6,46,BRICK,
              windows(BRICK,46,bay=8,floor=16,arched=True),z=6)
        block(s,i+.1,j+4.9,1.8,1.8,2,WHITE,z=50)
        spire(s,i+1,j+5.8,1.15,52,17,COPPER,conical=True)
        cross(s,i+1,j+5.8,69,GOLD)
        for k in range(5):block(s,i+.3,j+6.6+k*.23,1.4,.25,5-k,GRANITE)
    scene.add(i+j+16,draw)


def lantern_man(s,i,j,z):
    """Solid granite Lantern Carrier: coat, face, bent arms and a glowing globe."""
    block(s,i-.23,j-.2,.46,.4,3,PINK,z=z)
    # Coat extruded along j, shoulder-width at top and tapering at the hem.
    front=[P(s,i+a,j+.18,z+b) for a,b in ((-.21,3),(.21,3),(.28,11),(.17,13),(-.2,13),(-.28,11))]
    rear=[(x+2,y-1) for x,y in front]
    for k in range(len(front)-1):poly(s,[front[k],rear[k],rear[k+1],front[k+1]],lambda x,y:PINK['dark'])
    poly(s,front,lambda x,y:PINK['lit'] if int(x)%4 else PINK['line'])
    cylinder(s,i,j,.17,.17,z+13,4,PINK)
    for a in (-.3,.3):
        seg(s,P(s,i+a,j+.15,z+11),P(s,i+a*1.5,j+.45,z+9),PINK['mid'],2)
        seg(s,P(s,i+a*1.5,j+.45,z+9),P(s,i,j+.65,z+10),PINK['lit'],2)
    dome(s,i,j+.65,.31,z+9,4,WHITE)
    cylinder(s,i,j+.65,.31,.31,z+9,1,PINK)


def railway_station(scene,i,j):
    """Saarinen's pink granite, great arched window, four Lantern Carriers and clock tower."""
    def draw(s):
        # Platform canopy behind the station, painted before the entrance and clock tower.
        block(s,i+1,j-2.4,5,2.4,16,SLATE,
              lambda u,v,lit:COPPER['dark'] if int(u)%8==0 or int(v)==15 else GLASS['mid'])
        hip_roof(s,i+1,j-2.4,5,2.4,16,5,COPPER)
        block(s,i,j,9,4.1,30,PINK,windows(PINK,30,bay=9,floor=14))
        hip_roof(s,i,j,9,4.1,30,10,COPPER)
        # Projected barrel/gable entrance with a round window filling the tall arch.
        width=4.4
        def portal(u,v,lit):
            if not lit:return windows(PINK,42,bay=9,floor=16)(u,v,lit)
            centre=width*4
            inner=arch_opening(u,v,centre,13,25,GLASS['dark'])
            outer=arch_opening(u,v,centre,16,26,PINK['hi'])
            if inner:
                return PINK['deep'] if int(u-centre)%5==0 or int(v)%7==0 else GLASS['mid']
            return outer or stone_courses(PINK,4,9)(u,v,lit)
        block(s,i+2.3,j+3.7,width,.8,40,PINK,portal)
        # Round-topped extrusion in i/z, connected by a curved copper roof.
        profile=[(k/24*width,40+12*math.sin(k/24*math.pi)) for k in range(25)]
        front=[P(s,i+2.3+a,j+4.5,z) for a,z in profile]
        back=[P(s,i+2.3+a,j+3.7,z) for a,z in profile]
        for k in range(24):
            poly(s,[front[k],front[k+1],back[k+1],back[k]],lambda x,y:COPPER['lit'] if int(x)%5 else COPPER['line'])
        poly(s,front+[P(s,i+6.7,j+4.5,39),P(s,i+2.3,j+4.5,39)],lambda x,y:PINK['lit'])
        for a,b in zip(front,front[1:]):seg(s,a,b,COPPER['hi'],2)
        # Four distinct, filled stone figures flank the arch in pairs.
        for a in (1.25,2.05,6.9,7.7):lantern_man(s,i+a,j+4.7,3)
        # The tower is offset to the east, not centred above the entrance.
        block(s,i+7.7,j+.4,1.9,1.9,73,PINK,
              windows(PINK,73,bay=9,floor=20))
        block(s,i+7.6,j+.3,2.1,2.1,3,PINK,z=70)
        clock(s,i+8.65,j+2.42,6,64)
        clock(s,i+9.62,j+1.35,6,64,False)
        block(s,i+7.9,j+.6,1.5,1.5,9,COPPER,
              windows(COPPER,12,bay=7,floor=12),z=73)
        spire(s,i+8.65,j+1.35,1.2,82,17,COPPER,onion=True)
    scene.add(i+j+17,draw)


def parliament(scene,i,j):
    """Red-grey Kalvola granite, fourteen fluted columns, five storeys and broad steps."""
    def draw(s):
        def pattern(u,v,lit):
            return windows(PINK,46,bay=9,floor=10)(u,v,lit)
        block(s,i,j,11,5.3,46,PINK,pattern)
        hip_roof(s,i,j,11,5.3,46,4,SLATE)
        # The recessed entrance wall has doors and dressed openings behind the colonnade.
        block(s,i+.6,j+5.2,9.8,.2,38,PINK,pattern,z=3)
        for k in range(7):block(s,i+.6,j+5.3+k*.28,9.8,.3,7-k,GRANITE)
        for n in range(14):column(s,i+.85+n*.72,j+5.75,7,33,PINK,.2)
        block(s,i+.3,j+5.25,10.4,.85,3,PINK,z=40)
        block(s,i+.2,j+5.15,10.6,1,3,PINK,z=44)
        # Individually placed rosette/frieze squares above the columns.
        for n in range(14):
            block(s,i+.65+n*.72,j+6.17,.4,.08,2,GRANITE,z=44)
        flag(s,i+.6,j+1,51)
    scene.add(i+j+19,draw)


def finlandia(scene,i,j):
    """Aalto's white marble concert hall: asymmetric tower, dark base, glazed foyer and terrace."""
    def marble(u,v,lit):
        if int(u)%11==0 or int(v)%9==0:return WHITE['line' if lit else 'deep']
        return WHITE['hi'] if lit and int(u)%11==1 else None
    def glazing(u,v,lit):
        if int(u)%7==0 or int(v)%12==0:return WHITE['dark']
        return GLASS['mid' if lit else 'dark']
    def draw(s):
        block(s,i,j,9.5,5,7,SLATE,windows(SLATE,12,bay=10,floor=12))
        block(s,i+.2,j+.2,9.1,4.6,18,WHITE,glazing,z=7)
        block(s,i-.1,j+2.6,9.7,2.6,2,WHITE,marble,z=25)
        block(s,i+.5,j+.4,5,2.4,24,WHITE,marble,z=24)
        # A genuinely inclined roof/tower volume, using different heights at each corner.
        low=corners(s,i+2.8,j+.6,4.7,2.8,28)
        high=[P(s,i+2.8,j+.6,63),P(s,i+7.5,j+.6,56),
              P(s,i+7.5,j+3.4,49),P(s,i+2.8,j+3.4,55)]
        for a,b,lit in ((0,1,False),(0,3,False),(3,2,True),(2,1,False)):
            foot,end=low[a],low[b]
            def surface(x,y,foot=foot,end=end,lit=lit):
                u=x-foot[0]
                v=foot[1]+u*(end[1]-foot[1])/(end[0]-foot[0] or .001)-y
                return marble(u,v,lit) or WHITE['lit' if lit else 'dark']
            poly(s,[low[a],low[b],high[b],high[a]],surface)
            seg(s,low[a],high[a],WHITE['hi' if lit else 'line'])
        poly(s,high,lambda x,y:SLATE['mid'] if int(x+y)%11 else SLATE['line'])
        # Tall foyer windows below the cantilever and eastern white parapet.
        block(s,i+.3,j+4.5,8.7,.35,14,WHITE,glazing,z=9)
        block(s,i+.15,j+4.85,9,.45,3,WHITE,marble,z=24)
        # Aalto's uneven massing includes a lower north wing and a dark recessed roof gallery.
        block(s,i-.8,j-.9,3.5,2.8,18,WHITE,marble,z=7)
        block(s,i-.8,j-.9,3.5,2.8,1.5,SLATE,z=25)
        block(s,i+.6,j+.1,2.1,.2,7,SLATE,glazing,z=39)
        for n in range(5):
            block(s,i+5.7+n*.45,j+3.8,.13,.9,3,WHITE,z=26)
        for k in range(4):block(s,i+6.5,j+5+k*.25,2.5,.26,4-k,GRANITE)
        flag(s,i+8.5,j+4.2,28)
    scene.add(i+j+17,draw)


def national_museum(scene,i,j):
    """National Romantic granite, steep slate wings, red upper tower and needle copper cap."""
    def draw(s):
        rough=stone_courses(GRANITE,4,8)
        def tower_windows(u,v,lit):
            c,v=int(u)%15,int(v)
            if 5<=c<=8 and v%18 in range(7,13):
                return GRANITE['deep'] if c in (6,7) else GRANITE['hi']
            return rough(u,v,lit)
        block(s,i,j,7.8,4.6,29,GRANITE,windows(GRANITE,29,bay=10,floor=18,arched=True))
        gable_roof(s,i,j,3.5,4.6,29,21,SLATE,GRANITE,'point')
        gable_roof(s,i+4,j,3.8,4.6,29,17,SLATE,GRANITE,'point')
        for a in (i+.7,i+4.7):
            block(s,a,j+2,.65,.7,6,WHITE,windows(WHITE,10,bay=6,floor=10),z=35)
            hip_roof(s,a-.1,j+1.9,.85,.9,41,5,SLATE)
        # Tall rough-granite campanile with slit windows, brick belfry and two cap stages.
        block(s,i+2.8,j+2.6,2.1,2.1,71,GRANITE,tower_windows)
        block(s,i+2.7,j+2.5,2.3,2.3,3,GRANITE,z=69)
        block(s,i+2.8,j+2.6,2.1,2.1,16,BRICK,
              windows(BRICK,19,bay=8,floor=19,arched=True),z=72)
        spire(s,i+3.85,j+3.65,1.55,88,18,COPPER,conical=True)
        block(s,i+3.42,j+3.22,.86,.86,8,BRICK,
              windows(BRICK,11,bay=6,floor=11,arched=True),z=104)
        spire(s,i+3.85,j+3.65,.85,112,23,COPPER,conical=True)
        # Carved portal, stepped entrance and stone bear with a rounded body and head.
        def portal(u,v,lit):
            return arch_opening(u,v,8,5.5,11,WOOD['deep']) or stone_courses(GRANITE,3,7)(u,v,lit)
        block(s,i+5.1,j+4.6,2,.5,19,GRANITE,portal)
        for k in range(4):block(s,i+5,j+5.1+k*.24,2.2,.26,4-k,GRANITE)
        cylinder(s,i+4.75,j+5.3,.42,.27,4,5,GRANITE)
        dome(s,i+4.75,j+5.3,.42,9,4,GRANITE)
        cylinder(s,i+4.65,j+5.65,.26,.26,9,4,GRANITE)
        for a in (-.14,.14):dome(s,i+4.65+a,j+5.65,.1,13,1,GRANITE)
    scene.add(i+j+16,draw)


def market_hall(scene,i,j):
    """Old Market Hall: striped brick/stone, glazed arched gable, ridge lantern and long aisles."""
    def stripes(u,v,lit):
        if int(v)%9 in (0,1):return WHITE['lit' if lit else 'dark']
        return windows(BRICK,25,bay=10,floor=20,arched=True)(u,v,lit)
    def draw(s):
        block(s,i,j,4,8.2,25,BRICK,stripes)
        gable_roof(s,i-.12,j-.12,4.24,8.44,25,14,SLATE,BRICK,'point')
        # Front gable is extruded and carries a dressed round arch with radial voussoirs.
        def entrance(u,v,lit):
            if not lit:return stripes(u,v,lit)
            inner=arch_opening(u,v,16,10,19,GLASS['dark'])
            outer=arch_opening(u,v,16,13,19,WHITE['lit'])
            if inner:
                return WOOD['lit'] if int(u)%6==0 or int(v)%7==0 or v<3 else GLASS['mid']
            if outer:
                return BRICK['dark'] if int(math.atan2(v-19,u-16)*9)%2 else WHITE['lit']
            return WHITE['lit'] if int(v)%8<2 else stone_courses(BRICK,3,7)(u,v,lit)
        block(s,i,j+8,4,.35,31,BRICK,entrance)
        pediment(s,i-.2,j+8.36,4.4,31,10,BRICK)
        for a in (i-.05,i+3.75):
            block(s,a,j+8.4,.3,.18,31,WHITE,stripes)
        block(s,i+1.35,j+3.5,1.3,1.8,6,WOOD,
              lambda u,v,lit:WOOD['deep'] if int(u)%5 in (2,3) else WOOD['lit' if lit else 'dark'],z=37)
        hip_roof(s,i+1.2,j+3.35,1.6,2.1,43,4,SLATE)
        for a in (i,i+4):
            block(s,a-.1,j+8.15,.2,.2,3,WHITE,z=33)
            dome(s,a,j+8.25,.17,36,2,SLATE)
    scene.add(i+j+16,draw)


def suomenlinna(scene,i,j):
    """Kustaanmiekka: grass-topped bastions and the rusticated King's Gate above its landing."""
    def draw(s):
        # Angled bastion faces are actual extruded ground-plane polygons.
        plan=[(0,0),(4.2,-.7),(8.5,.4),(10,2.3),(8,4.9),(5.5,4.4),(3.2,5.5),(.2,3.8)]
        for n,(a,b) in enumerate(zip(plan,plan[1:]+plan[:1])):
            pa,pb=P(s,i+a[0],j+a[1]),P(s,i+b[0],j+b[1])
            lit=(b[0]-a[0])<0
            def stone(x,y,pa=pa,pb=pb,lit=lit):
                u=x-pa[0];v=pa[1]+u*(pb[1]-pa[1])/(pb[0]-pa[0] or .001)-y
                return stone_courses(GRANITE,4,9)(u,v,lit) or GRANITE['lit' if lit else 'dark']
            poly(s,[pa,pb,P(s,i+b[0],j+b[1],22),P(s,i+a[0],j+a[1],22)],stone)
        turf=palette_of(rgb('#7B9D5E'))
        poly(s,[P(s,i+a,j+b,22) for a,b in plan],lambda x,y:turf['mid'] if h01(x,y,204)<.12 else turf['lit'])
        # Concave gate front: central rusticated portal, two slightly advanced return wings.
        def portal(u,v,lit):
            if lit:
                inner=arch_opening(u,v,12,5,11,GRANITE['deep'])
                outer=arch_opening(u,v,12,7.5,11,WHITE['lit'])
                if inner:return GRANITE['outline']
                if outer:return GRANITE['line'] if int(v)%4==0 else WHITE['lit']
                # Marble dedication tablets and round gun ports either side of the opening.
                if 18<u<23 and 16<v<20:return WHITE['lit'] if int(u) in (19,22) else GRANITE['dark']
                if 2<u<6 and 15<v<19:return GRANITE['outline']
            return stone_courses(GRANITE,4,8)(u,v,lit)
        block(s,i+3.5,j+4.2,3,.65,25,GRANITE,portal)
        for a in (2.7,6.5):block(s,i+a,j+4.5,.8,.8,26,GRANITE,windows(GRANITE,26,bay=6,floor=13))
        # Curved return walls make the gate concave: its centre sits behind both wings.
        for a,b in ((2.3,4.9),(2.7,4.65),(6.5,4.65),(6.9,4.9)):
            block(s,i+a,j+b,.45,.4,22,GRANITE,stone_courses(GRANITE,3,7))
        block(s,i+2.6,j+4.15,4.8,1.2,2,WHITE,z=25)
        block(s,i+3.5,j+4.18,3,.8,2,GRANITE,z=27)
        for k in range(6):block(s,i+3.45,j+4.9+k*.3,3.1,.33,6-k,GRANITE)
        # Rounded sandstone landing and its continuous low iron handrail.
        cylinder(s,i+5,j+6.5,2.3,1,0,2,GRANITE,stone_courses(GRANITE,3,8))
        for a in (i+3.3,i+6.7):
            for b in (j+5.6,j+6.2,j+6.8):
                seg(s,P(s,a,b,3),P(s,a,b,6),IRON)
            seg(s,P(s,a,j+5.6,6),P(s,a,j+6.8,6),IRON)
        # Two coast guns: small timber beds, wheels, breeches and projecting iron barrels.
        for a,b in ((1,1.8),(7.5,1.5)):
            block(s,i+a,j+b,.65,.9,3,WOOD,z=22)
            for dj in (.1,.7):
                cylinder(s,i+a+.6,j+b+dj,.18,.18,22,3,SLATE)
            cylinder(s,i+a+.3,j+b+.2,.2,.2,25,3,SLATE)
            seg(s,P(s,i+a+.3,j+b+.2,28),P(s,i+a+.3,j+b-1.2,30),IRON,3)
            seg(s,P(s,i+a+.25,j+b+.2,29),P(s,i+a+.25,j+b-1.2,31),SLATE['lit'])
        flag(s,i+1.3,j+.5,23)
    scene.add(i+j+20,draw)


STUDIES = [('cathedral',cathedral),('uspenski',uspenski),('railway-station',railway_station),
           ('parliament',parliament),('finlandia',finlandia),('national-museum',national_museum),
           ('market-hall',market_hall),('suomenlinna',suomenlinna)]

if __name__ == '__main__':
    for name,builder in STUDIES:
        print(preview([lambda s,b=builder:b(s,4,4)],'helsinki-'+name,
                      size=(250,250),origin=(115,120),tiles=18))
    print(preview([lambda s:townhouse(s,4,4,seed=0),lambda s:townhouse(s,8,4,seed=1),
                   lambda s:townhouse(s,8,8,floors=2,seed=11)],'helsinki-houses',
                  size=(230,190),origin=(105,40),tiles=17))
