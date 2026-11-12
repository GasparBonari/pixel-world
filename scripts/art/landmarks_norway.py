"""Oslo's historic masonry and modern waterfront, projected from (i, j, z).

Run for eight isolated 4× landmark studies and an Oslo house study. Geographic
anchors and architectural references are recorded in DEVELOPMENT_PLAN.md.
"""
import math

import iso
from iso import rgb, h01
from landmarks_paris import P, seg, poly, corners, facade, preview, GLASS
from landmarks_iberia import hip_roof, stone_courses, arch_opening, palette_of, tones
from landmarks_amsterdam import gable_roof
from landmarks_denmark import spire, clock
from landmarks_belgium import pediment
from landmarks_italy import cylinder

GRANITE = tones('#E4DFD0', '#C2BCAB', '#A6A394', '#81877C', '#59655E', '#93998B', '#3B4943')
PALE = tones('#FFF4DE', '#EADFC8', '#CEC3AD', '#AEA18C', '#7C6D5C', '#BCAC93', '#4C4136')
OCHRE = tones('#F4DDA6', '#DDC28C', '#C1A775', '#9D895E', '#736140', '#AF986A', '#51442D')
BRICK = tones('#D3A080', '#AC7056', '#905941', '#704333', '#4D2D26', '#925D49', '#3C2923')
YELLOW_BRICK = tones('#E8CE9C', '#CFB079', '#B49764', '#927B50', '#6B5839', '#A38A5E', '#4B3F2B')
SLATE = tones('#ABB2B3', '#7D8B8F', '#647479', '#465A62', '#2F424B', '#576A71', '#293A43')
COPPER = tones('#B4D4B7', '#7FAA96', '#618E7D', '#416A5B', '#2B4B40', '#557D6A', '#263C33')
MARBLE = tones('#FFFFFF', '#EEF0E6', '#D6DFD8', '#ADBFBD', '#798F92', '#C3CFCA', '#4A6266')
METAL = tones('#CED9CF', '#A0B4AC', '#829D98', '#5F7C7B', '#3D575D', '#718F8D', '#2B444A')
TIMBER = tones('#BD9771', '#99704E', '#7C573C', '#59402F', '#3E2D23', '#73533A', '#30261F')
GOLD = tones('#FFF1B5', '#EACA73', '#CAA34D', '#9A7634', '#6C5127', '#B89043', '#514022')
BRONZE = tones('#A0AC91', '#74886E', '#526C56', '#354E3E', '#24382E', '#4D6650', '#203127')
WALLS = [rgb(c) for c in ('#D9C394', '#C1CBBF', '#BE8E79', '#DAD6C5', '#A6BBC0', '#AE795D')]
WATER = (rgb('#477E8C'), rgb('#345F70'), rgb('#C5DDD9'))
FLAG_RED, FLAG_BLUE = rgb('#BB4851'), rgb('#294968')


def block(s, i, j, wi, wj, height, material=GRANITE, pattern=None, z=0):
    cover = facade(s, i, j, wi, wj, height, pattern or stone_courses(material, 4, 9),
                   palette=material, z0=z)
    iso.fill(s, list(corners(s, i, j, wi, wj, z + height)), lambda x, y: material['mid'], cover)
    iso.outline(s, cover, material['outline'])
    return cover


def windows(material, height, bay=10, floor=13, arched=False, coursed=True):
    courses = stone_courses(material, 3 if material in (BRICK, YELLOW_BRICK) else 5, 9)
    def pattern(u, v, lit):
        c, v = int(u) % bay, int(v)
        level, trim = v % floor, PALE['lit' if lit else 'dark']
        if v < 2 or v in (height - 1, height - 3):
            return trim
        top = floor - 3 - (abs(c - bay / 2) * .7 if arched else 0)
        if 2 <= c <= bay - 2 and 3 <= level <= top and v < height - 4:
            if c in (2, bay - 2, bay // 2) or level in (3, 7, int(top)):
                return trim
            return GLASS['mid' if lit else 'dark']
        if level == 1:
            return material['line' if lit else 'deep']
        return courses(u, v, lit) if coursed else None
    return pattern


def flag(s, i, j, z):
    seg(s, P(s, i, j, z), P(s, i, j, z + 17), SLATE['dark'])
    def panel(a, b, low, high, color):
        poly(s, [P(s, i+a, j, z+low), P(s, i+b, j, z+low),
                 P(s, i+b, j, z+high), P(s, i+a, j, z+high)], lambda x,y: color)
    panel(0, 1.7, 9, 17, FLAG_RED)
    panel(.45, .85, 9, 17, PALE['hi'])
    panel(0, 1.7, 11.5, 14.5, PALE['hi'])
    panel(.58, .72, 9, 17, FLAG_BLUE)
    panel(0, 1.7, 12.5, 13.5, FLAG_BLUE)


def column(s, i, j, height, z=0, material=PALE, radius=.16):
    cylinder(s, i, j, radius*1.5, radius*1.5, z, 2, material)
    cylinder(s, i, j, radius, radius, z+2, height-4, material,
             lambda u,v,lit: material['line' if lit else 'deep'] if int(u)%3 == 0 else None)
    block(s, i-radius*1.5, j-radius*1.5, radius*3, radius*3, 2, material, z=z+height-2)


def figure(s, i, j, z, material=BRONZE):
    """Small solid coat, bent arms, separate legs and a shaded head on a real plinth."""
    x,y=P(s,i,j,z)
    for points,tone in (([(-3,2),(3,2),(2,-5),(0,-9),(-2,-5)],'lit'),
                        ([(0,2),(3,2),(2,-5),(0,-7)],'dark'),
                        ([(-2,-9),(1,-10),(2,-8),(1,-6),(-2,-7)],'hi'),
                        ([(-2,-5),(-4,-2),(-3,0),(-1,-3)],'mid')):
        poly(s,[(x+a,y+b) for a,b in points],lambda x,y,tone=tone:material[tone])
    seg(s,(x-1,y+2),(x-2,y+5),material['dark'])
    seg(s,(x+1,y+2),(x+2,y+5),material['lit'])


def townhouse(scene, i, j, wi=2.6, wj=2.8, floors=3, seed=0):
    """Oslo murbyen: plaster/brick, dressed sash panes, iron balconies and slate dormers."""
    wall, height = palette_of(WALLS[seed % len(WALLS)]), floors*10+3
    def pattern(u,v,lit):
        c,v=int(u)%10,int(v)
        level,trim=v%10,PALE['lit' if lit else 'dark']
        if v<3:
            return GRANITE['lit' if lit else 'dark']
        if v in (height-1,height-3):
            return trim
        if v<10 and 2<=c<=8 and v<8:
            if c in (2,8) or v==7:
                return trim
            if (int(u)//10+seed)%3==0:
                return TIMBER['deep'] if c==5 or v==4 else TIMBER['lit' if lit else 'dark']
            return GLASS['lit' if lit else 'dark'] if c<5 else GLASS['dark']
        if v>=10 and 2<=c<=7 and 3<=level<=8 and v<height-4:
            if seed%4==0 and level==3:
                return SLATE['deep'] if c%2==0 else SLATE['lit']
            if c in (2,4,7) or level in (3,6,8):
                return trim
            return GLASS['mid' if lit else 'dark']
        if v>=10 and level==2 and 1<=c<=8:
            return trim
        if seed%6==0:
            return wall['line' if lit else 'deep'] if v%3==0 or (int(u)+v//3*4)%8==0 else None
        return wall['line'] if h01(int(u),v,seed)<.014 else None
    def draw(s):
        block(s,i,j,wi,wj,height,wall,pattern)
        hip_roof(s,i-.08,j-.08,wi+.16,wj+.16,height,11,SLATE)
        # Dormer, dressed bay on occasional Grünerløkka/Kvadraturen houses.
        block(s,i+.65,j+wj-.65,.65,.5,6,PALE,windows(PALE,10,bay=6),z=height+2)
        hip_roof(s,i+.65,j+wj-.65,.65,.5,height+8,3,SLATE)
        if seed%5==0:
            block(s,i+.7,j+wj,.8,.4,height-12,wall,windows(wall,height-12,bay=6,floor=10),z=10)
            hip_roof(s,i+.65,j+wj,.9,.45,height-2,4,SLATE)
        block(s,i+wi*.75,j+.4,.36,.4,9,BRICK,z=height+5)
        block(s,i+wi*.75-.05,j+.35,.46,.5,1.5,GRANITE,z=height+13)
    scene.add(i+j+wi+wj,draw)


def royal_palace(scene,i,j):
    """Ochre neoclassical palace: wings, six-column temple front and flag above its low roof."""
    def draw(s):
        palace_windows=windows(OCHRE,36,bay=9,floor=11,coursed=False)
        block(s,i,j,10,4,36,OCHRE,palace_windows)
        hip_roof(s,i-.1,j-.1,10.2,4.2,36,8,SLATE)
        for a in (i,i+8):
            block(s,a,j+2.4,2,2.5,36,OCHRE,palace_windows)
            hip_roof(s,a,j+2.4,2,2.5,36,7,SLATE)
        for a in (i+.1,i+1.8,i+8.1,i+9.8):
            block(s,a,j+4.9,.14,.16,34,PALE)
        for k in range(5):
            block(s,i+2.8,j+4+k*.24,4.4,.26,5-k,GRANITE)
        for n in range(6):
            column(s,i+3+n*.8,j+4.45,27,z=5)
        block(s,i+2.6,j+3.9,4.8,.9,3,PALE,z=32)
        pediment(s,i+2.6,j+4.8,4.8,35,10,PALE)
        # Temple tympanum relief remains inside the triangle.
        for x,y in iso.polygon_pixels([P(s,i+2.9,j+4.8,36),P(s,i+7.1,j+4.8,36),P(s,i+5,j+4.8,43)]):
            if h01(x,y,190)<.15:s.put(x,y,OCHRE['line'])
        flag(s,i+5,j+1.8,45)
        block(s,i+4.6,j+6.2,.8,.7,5,GRANITE)
        # Filled equestrian silhouette: body, neck, head, legs and rider.
        x,y=P(s,i+5,j+6.55,12)
        shape=[(-7,-1),(-6,-5),(-2,-6),(3,-5),(4,-9),(3,-12),
               (5,-13),(8,-11),(8,-9),(6,-9),(6,-3),(4,0),(-5,1)]
        poly(s,[(x+a,y+b) for a,b in shape],lambda x,y:BRONZE['lit'])
        poly(s,[(x-5,y-1),(x+4,y-1),(x+3,y-4),(x-3,y-4)],lambda x,y:BRONZE['dark'])
        for dx,dy in ((-5,0),(-2,0),(3,-1),(5,-2)):
            seg(s,(x+dx,y+dy),(x+dx-1,y+6),BRONZE['dark' if dx%2 else 'lit'])
        seg(s,(x-6,y-4),(x-9,y+1),BRONZE['deep'])
        figure(s,i+4.9,j+6.55,20)
    scene.add(i+j+17,draw)


def national_theatre(scene,i,j):
    """Yellow brick, granite dressings, three entrance arches, paired columns and pediment."""
    def draw(s):
        block(s,i,j,6.7,5.5,30,YELLOW_BRICK,windows(YELLOW_BRICK,30,bay=10,floor=13,arched=True))
        hip_roof(s,i,j,6.7,5.5,30,12,COPPER)
        block(s,i+1.4,j+.8,3.9,2.7,11,YELLOW_BRICK,windows(YELLOW_BRICK,11,bay=9),z=32)
        hip_roof(s,i+1.3,j+.7,4.1,2.9,43,8,COPPER)
        def portal(u,v,lit):
            if lit and v<16:
                return arch_opening(int(u)%12,v,6,3.3,9,TIMBER['deep']) or stone_courses(GRANITE)(u,v,lit)
            return windows(YELLOW_BRICK,33,bay=12,floor=14,arched=True)(u,v,lit)
        block(s,i+1,j+5.1,4.7,.8,33,YELLOW_BRICK,portal)
        for a in (i+1.2,i+2.45,i+4.1,i+5.45):
            column(s,a,j+5.95,20,z=13,material=GRANITE,radius=.19)
        block(s,i+.8,j+5.05,5.1,1.1,3,GRANITE,z=33)
        pediment(s,i+.8,j+6.15,5.1,36,11,GRANITE)
        # Bronze roof acroteria and carved frieze panels, individually placed.
        for a,z in ((i+.9,38),(i+3.35,48),(i+5.8,38)):
            block(s,a-.12,j+6,.24,.24,2,GRANITE,z=z)
            figure(s,a,j+6.12,z+7)
        for n in range(3):
            block(s,i+1.5+n*1.35,j+5.93,.8,.1,3,PALE,z=28)
        for k in range(4):
            block(s,i+1,j+6.2+k*.24,4.7,.25,4-k,GRANITE)
        for a in (i-.3,i+6.3):
            block(s,a,j+6,.65,.65,6,GRANITE)
            figure(s,a+.32,j+6.32,12)
        flag(s,i+3.3,j+2,52)
    scene.add(i+j+15,draw)


def storting(scene,i,j):
    """Langlet's yellow-brick parliament: projecting round chamber, arched windows and lions."""
    def draw(s):
        block(s,i,j,7.7,4.8,35,YELLOW_BRICK,windows(YELLOW_BRICK,35,bay=10,floor=14,arched=True))
        hip_roof(s,i,j,7.7,4.8,35,9,SLATE)
        # Chamber rotunda is an actual elliptical volume, projecting out of the front wing.
        ci,cj=i+3.85,j+4.15
        def chamber(u,v,lit):
            c,v=int(u)%10,int(v)
            trim=PALE['lit' if lit else 'dark']
            if v in (1,13,15,32,34):return trim
            if c in (0,1):return YELLOW_BRICK['hi' if lit else 'mid']
            top=29-abs(c-5)*.8
            if 3<=c<=7 and 18<=v<=top:
                if c in (3,5,7) or v in (18,23,int(top)):return trim
                return GLASS['mid' if lit else 'dark']
            if 3<=c<=7 and 3<v<11-abs(c-5)*.5:
                return trim if c in (3,7) or v==4 else TIMBER['deep']
            return stone_courses(YELLOW_BRICK,3,10)(u,v,lit)
        cylinder(s,ci,cj,2.6,2.25,0,35,YELLOW_BRICK,chamber)
        cylinder(s,ci,cj,2.73,2.38,33,3,PALE)
        # Shallow polygonal roof, not a dome.
        for n in range(48):
            a,b=n*math.tau/48,(n+1)*math.tau/48
            poly(s,[P(s,ci+2.73*math.cos(a),cj+2.38*math.sin(a),36),
                    P(s,ci+2.73*math.cos(b),cj+2.38*math.sin(b),36),P(s,ci,cj,40)],
                 lambda x,y,n=n:SLATE['line'] if int(y)%4==0 else SLATE['lit' if 5<n<28 else 'dark'])
        # Small corbels support the projecting round cornice.
        for n in range(19):
            a=n*math.pi/18
            ii,jj=ci+2.6*math.cos(a),cj+2.25*math.sin(a)
            block(s,ii-.08,jj-.08,.16,.16,3,PALE,z=30)
        for a in (i+.1,i+7.1):
            block(s,a,j+4.8,.5,.5,39,YELLOW_BRICK,windows(YELLOW_BRICK,39,bay=6,floor=14,arched=True))
            hip_roof(s,a-.1,j+4.7,.7,.7,39,5,SLATE)
        for k in range(5):
            block(s,i+2,j+6.2+k*.25,3.8,.26,5-k,GRANITE)
        # Two crouching stone lions with solid haunches, mane, muzzle and paws.
        for a in (i+1.1,i+5.9):
            block(s,a,j+6.7,.7,1,4,GRANITE)
            cylinder(s,a+.35,j+7.05,.3,.45,4,4,PALE)
            cylinder(s,a+.35,j+7.35,.23,.23,7,5,PALE)
            block(s,a+.2,j+7.5,.3,.3,2,PALE,z=8)
            block(s,a+.05,j+7.35,.18,.55,1.4,GRANITE,z=4)
            block(s,a+.48,j+7.35,.18,.55,1.4,PALE,z=4)
        flag(s,i+3.85,j+2.8,46)
    scene.add(i+j+17,draw)


def cathedral(scene,i,j):
    """Cruciform brick church, copper roofs and west clock tower with tall Baroque lantern."""
    def church(u,v,lit):
        c,v=int(u)%12,int(v)
        trim=PALE['lit' if lit else 'dark']
        if v in (1,29,31):return trim
        if 3<=c<=9 and 7<=v<=24-abs(c-6)*.7:
            return trim if c in (3,6,9) or v in (7,15,23) else GLASS['mid' if lit else 'dark']
        return stone_courses(BRICK,3,9)(u,v,lit)
    def draw(s):
        block(s,i+.6,j,3.5,6.8,32,BRICK,church)
        gable_roof(s,i+.6,j,3.5,6.8,32,15,COPPER,BRICK)
        block(s,i-.6,j+2.2,5.9,2.1,32,BRICK,church)
        hip_roof(s,i-.6,j+2.2,5.9,2.1,32,14,COPPER)
        ti,tj=i+1.05,j+4.9
        def tower(u,v,lit):
            c,v=int(u)%18,int(v)
            if v in (2,35,60,63):return PALE['lit' if lit else 'dark']
            for lo,hi in ((11,22),(41,55)):
                if 6<=c<=12 and lo<=v<=hi:
                    return PALE['lit' if lit else 'dark'] if c in (6,12) or v in (lo,hi) else TIMBER['deep']
            return stone_courses(BRICK,3,9)(u,v,lit)
        block(s,ti,tj,2.3,2.3,66,BRICK,tower)
        clock(s,ti+1.15,tj+2.32,5,32)
        clock(s,ti+2.32,tj+1.15,4.5,32,False)
        block(s,ti-.1,tj-.1,2.5,2.5,3,PALE,z=63)
        hip_roof(s,ti-.15,tj-.15,2.6,2.6,66,9,COPPER)
        # Open lantern with substantial piers, louvres and a bulbous copper cap.
        block(s,ti+.55,tj+.55,1.2,1.2,16,COPPER,
              lambda u,v,lit:TIMBER['deep'] if 2<int(u)<7 and 3<v<13 else None,z=75)
        spire(s,ti+1.15,tj+1.15,1.05,91,17,COPPER,onion=True)
        block(s,ti+.8,tj+.8,.7,.7,10,COPPER,
              lambda u,v,lit:TIMBER['deep'] if 1<int(u)<4 and 2<v<8 else None,z=108)
        spire(s,ti+1.15,tj+1.15,.58,118,21,COPPER)
        block(s,ti+1.09,tj+1.09,.12,.12,5,GOLD,z=139)
        block(s,ti+.85,tj+1.09,.6,.12,1,GOLD,z=142)
        block(s,ti+.5,tj+2.3,1.3,.23,14,PALE,
              lambda u,v,lit:arch_opening(u,v,5.2,3.2,8,TIMBER['deep']) if lit else None)
    scene.add(i+j+14,draw)


def city_hall(scene,i,j):
    """Functionalist brick hall, unequal twin towers, vast clock, reliefs and carillon slots."""
    def tower(height):
        def pattern(u,v,lit):
            c,v=int(u)%8,int(v)
            if v in (1,height-2):return BRICK['hi' if lit else 'mid']
            if 3<=c<=5 and (10<v<height-28 and 3<=v%10<=7 or height-16<v<height-5):
                if v%10==3:return BRICK['hi' if lit else 'mid']
                return GLASS['mid' if lit else 'dark']
            return stone_courses(BRICK,3,8)(u,v,lit)
        return pattern
    def draw(s):
        block(s,i,j,8.4,5.3,4,GRANITE)
        block(s,i,j,8.4,5.3,37,BRICK,windows(BRICK,37,bay=10,floor=16),z=4)
        hip_roof(s,i,j,8.4,5.3,41,3,COPPER)
        # Western tower slightly shorter; east tower carries the large harbour-facing clock.
        for a,height in ((i+.1,86),(i+5.9,91)):
            block(s,a,j+.3,2.4,2.5,height,BRICK,tower(height))
            block(s,a-.06,j+.24,2.52,2.62,2,BRICK,z=height)
            block(s,a+.1,j+.5,2,2.1,1,COPPER,z=height+2)
        clock(s,i+7.1,j+2.82,8,72)
        # Great hall's long high windows and a central framed sculptural panel.
        def hall(u,v,lit):
            if lit:
                c,v=int(u)%12,int(v)
                if 4<=c<=8 and 13<v<32:
                    return PALE['dark'] if c in (4,8) or v==22 else GLASS['dark']
            return stone_courses(BRICK,3,9)(u,v,lit)
        block(s,i+.3,j+5.3,7.8,.3,38,BRICK,hall,z=3)
        block(s,i+3.3,j+5.63,1.8,.12,18,GRANITE,z=12)
        figure(s,i+4.2,j+5.8,26)
        block(s,i+3.4,j+5.8,1.6,.18,10,GRANITE,
              lambda u,v,lit:TIMBER['deep'] if lit and 2<u<11 and v<8 else None)
        for k in range(4):
            block(s,i+2.7,j+6+k*.25,3,.26,4-k,GRANITE)
    scene.add(i+j+16,draw)


def akershus(scene,i,j):
    """Grey medieval castle, Renaissance wings, Romerike gable and copper-capped towers."""
    def draw(s):
        # Rock and bastion, with irregular stone courses and a low parapet.
        block(s,i-.4,j-.4,10,7.4,7,GRANITE,stone_courses(GRANITE,4,11))
        for a,b,wi,wj in ((i,j,9.2,1.6),(i,j+1.6,1.8,4.8),(i+7.4,j+1.6,1.8,4.8)):
            block(s,a,b,wi,wj,32,GRANITE,windows(GRANITE,32,bay=11,floor=14),z=7)
            hip_roof(s,a,b,wi,wj,39,15,SLATE)
        block(s,i+1.8,j+4.8,5.6,1.6,31,GRANITE,windows(GRANITE,31,bay=11,floor=14),z=7)
        gable_roof(s,i+1.8,j+4.8,5.6,1.6,38,16,SLATE,GRANITE,'step')
        for a,b,width,height in ((i+.2,j+.5,1.8,50),(i+6.8,j+3.8,1.7,45)):
            block(s,a,b,width,width,height,GRANITE,windows(GRANITE,height,bay=10,floor=18),z=7)
            hip_roof(s,a-.1,b-.1,width+.2,width+.2,height+7,8,COPPER)
            block(s,a+.5,b+.5,.8,.8,9,COPPER,
                  lambda u,v,lit:TIMBER['deep'] if 2<int(u)<5 and 2<v<7 else None,z=height+15)
            spire(s,a+width/2,b+width/2,.7,height+24,16,COPPER,onion=True)
        block(s,i+3.7,j+6.3,1.5,.35,19,GRANITE,
              lambda u,v,lit:arch_opening(u,v,6,3.5,11,TIMBER['deep']) if lit else None,z=7)
        # Battered curtain and dressed coping along the open southern bastion.
        block(s,i-.4,j+6.6,10,.4,11,GRANITE)
        block(s,i+9.2,j-.4,.4,7.4,11,GRANITE)
        block(s,i-.45,j+6.55,10.1,.5,2,PALE,z=11)
        flag(s,i+4.8,j+2,28)
    scene.add(i+j+20,draw)


def opera_house(scene,i,j):
    """Walkable Carrara-marble slopes rise from the fjord around a glazed oak foyer."""
    def draw(s):
        block(s,i,j,9.5,6.3,2,MARBLE)
        def glazing(u,v,lit):
            if int(u)%9==0 or int(v)%10==0:return MARBLE['lit' if lit else 'dark']
            # Warm inner oak wall is visible behind the south foyer glass.
            if lit and 13<u<38 and v>7:
                return TIMBER['lit'] if int(u)%6 else TIMBER['line']
            return GLASS['lit' if lit else 'dark']
        block(s,i+1,j+.5,7.8,4.7,20,MARBLE,glazing,z=2)
        # Aluminium fly tower: embossed irregular panels, set behind the roof plateau.
        block(s,i+3.7,j+.6,3.4,2.7,30,METAL,
              lambda u,v,lit:METAL['line' if lit else 'deep'] if int(u)%11==0 or int(v)%8==0
              else METAL['hi' if lit else 'mid'] if h01(int(u)//3,int(v)//3,194)<.12 else None,z=12)
        # Real inclined planes, never a flat white cut-out. Joint lines follow each plane.
        def slope(points, material, z_at):
            def color(x,y):
                # Inverse projection constrained to the plane z=a*i+b*j+c.
                a,b,c=z_at
                d=(x-s.ox)/8
                jj=(y-s.oy-(4-a)*d+c)/(8-a-b)
                ii=jj+d
                seam=abs(ii/.9-round(ii/.9))<.045 or abs(jj/.75-round(jj/.75))<.045
                return material['line'] if seam else material['hi' if h01(math.floor(ii/1.8),math.floor(jj/1.5),195)<.2 else 'lit']
            pts=[P(s,*p) for p in points]
            poly(s,pts,color)
            for a,b in zip(pts,pts[1:]+pts[:1]):seg(s,a,b,material['dark'])
        # Broad southwest ramp, with a stepped fold into the east roof terrace.
        front=j+6.3
        a=-22/5.8;c=2-a*front
        slope([(i,j+.5,24),(i+3.2,j+.5,24),(i+3.2,front,2),(i,front,2)],MARBLE,(0,a,c))
        slope([(i+3.2,j+.5,24),(i+9.5,j+.5,24),(i+9.5,j+3.6,24),(i+3.2,j+3.6,24)],MARBLE,(0,0,24))
        a=-22/2.7;c=2-a*front
        slope([(i+8.7,j+3.6,24),(i+9.5,j+3.6,24),(i+9.5,front,2),(i+8.7,front,2)],MARBLE,(0,a,c))
        # Thin marble eaves on the glazed south face and terrace rail on the rear.
        seg(s,P(s,i+3.2,j+3.6,24),P(s,i+8.7,j+3.6,24),MARBLE['hi'],2)
        for n in range(4):
            ii=i+4+n*1.05
            seg(s,P(s,ii,j+.48,24),P(s,ii,j+.48,28),METAL['dark'])
        seg(s,P(s,i+3.8,j+.48,28),P(s,i+7.4,j+.48,28),METAL['lit'])
    scene.add(i+j+17,draw)


def munch(scene,i,j):
    """Perforated aluminium museum on a three-storey podium, with its leaning upper crown."""
    def skin(u,v,lit):
        u,v=int(u),int(v)
        tone=METAL['lit' if lit else 'dark']
        if v%9==0:return METAL['line' if lit else 'deep']
        if lit and u%26<7 and 2<v%9<7:
            return GLASS['mid'] if u%26<3 else METAL['dark']
        # Sparse staggered perforations and folded metal: avoid a cage of dense stripes.
        if (u+v//9*3)%7==0 and v%3==1:return METAL['mid' if lit else 'deep']
        return METAL['hi' if lit else 'mid'] if u%11==0 else tone
    def draw(s):
        block(s,i-.8,j-.6,5.2,4.2,21,METAL,
              lambda u,v,lit:MARBLE['dark'] if int(u)%9==0 or int(v)%10==0 else GLASS['mid' if lit else 'dark'])
        block(s,i,j,3.2,2.9,82,METAL,skin,z=12)
        # Upper volume leans toward the fjord (+j), modelled with displaced top corners.
        low=corners(s,i,j,3.2,2.9,94)
        high=corners(s,i,j+1.3,3.2,2.9,122)
        for indices,lit in (((0,1),False),((0,3),False),((3,2),True),((2,1),False)):
            a,b=indices
            foot,end=low[a],low[b]
            pts=[foot,end,high[b],high[a]]
            def panel(x,y,lit=lit,foot=foot,end=end):
                # Follow sloping vertical joints and horizontal floor belts on this face.
                v=(foot[1]+(x-foot[0])*(end[1]-foot[1])/(end[0]-foot[0] or .001)-y)
                u=x-foot[0]-(v/28)*(-10.4)
                if 8<v<19:
                    return METAL['lit' if lit else 'dark'] if int(u)%9==0 else GLASS['mid' if lit else 'dark']
                return skin(u,v,lit)
            poly(s,pts,panel)
            seg(s,foot,high[a],METAL['hi' if lit else 'deep'])
        poly(s,list(high),lambda x,y:METAL['mid'] if int(x+y)%13 else METAL['line'])
        for a,b in zip(high,high[1:]+high[:1]):seg(s,a,b,METAL['hi'])
        # Small entrance canopy, deep doorway and projecting terrace at the podium.
        block(s,i+.5,j+3.6,2.7,.55,2,METAL,z=14)
        block(s,i+1.2,j+3.58,1.2,.08,10,METAL,
              lambda u,v,lit:GLASS['dark'] if lit and 1<u<8 else METAL['lit'])
    scene.add(i+j+12,draw)


if __name__ == '__main__':
    studies = [('royal-palace',royal_palace),('national-theatre',national_theatre),
               ('storting',storting),('cathedral',cathedral),('city-hall',city_hall),
               ('akershus',akershus),('opera',opera_house),('munch',munch)]
    for name,builder in studies:
        print(preview([lambda s,b=builder:b(s,4,4)],'oslo-'+name,
                      size=(230,230),origin=(105,110),tiles=17))
    print(preview([lambda s:townhouse(s,4,4,seed=0),lambda s:townhouse(s,8,4,seed=5),
                   lambda s:townhouse(s,8,8,floors=2,seed=12)],'oslo-houses',
                  size=(230,190),origin=(105,40),tiles=17))
