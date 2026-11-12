"""Stockholm's brick, ochre plaster and copper, built from projected (i, j, z).

Run for eight isolated 4× landmark plots and a Gamla Stan house study.
Coordinates and architectural references are recorded in DEVELOPMENT_PLAN.md.
"""
import math

import iso
from iso import rgb, h01
from landmarks_paris import P, seg, poly, corners, facade, preview, GLASS
from landmarks_iberia import hip_roof, stone_courses, arch_opening, palette_of, tones
from landmarks_amsterdam import gable_roof
from landmarks_denmark import spire, clock
from landmarks_italy import cylinder

STONE = tones('#F2DFC1', '#D6BE99', '#BAA27D', '#998363', '#6F5C44', '#AE9471', '#483B2C')
PALE = tones('#FFF4DD', '#EBDDC1', '#D3C6AA', '#B0A185', '#7D705A', '#C0AF8E', '#514533')
BRICK = tones('#CB9270', '#A5684C', '#874F3A', '#693C30', '#492B24', '#8F5C44', '#38261F')
OCHRE = tones('#F3DAA2', '#D9B775', '#BD9A5E', '#987847', '#705333', '#B09158', '#503C26')
ROSE = tones('#E5BDA2', '#D0A58B', '#B98C74', '#98745F', '#6F5040', '#B58D74', '#4E382C')
COPPER = tones('#B5D0B4', '#80AA94', '#628C79', '#416856', '#2B493D', '#557B65', '#263D32')
CLAY = tones('#E6A878', '#BD744E', '#A45C3C', '#7F422D', '#592E23', '#985839', '#48271F')
IRON = tones('#9B9D98', '#6C7772', '#515E59', '#35443D', '#26352E', '#48594F', '#202D26')
GOLD = tones('#FFF1AD', '#EAC669', '#C8A047', '#99722C', '#6D5024', '#B28C3B', '#534022')
TIMBER = tones('#B7886D', '#8A5B44', '#704533', '#52352A', '#39271F', '#684332', '#30221C')
WALLS = [rgb(c) for c in ('#D5AE64', '#AD654A', '#D8BD8C', '#BC855B', '#D4A38A', '#C6B69B')]
WATER = (rgb('#477E8A'), rgb('#35616F'), rgb('#BDDAD7'))
WOOD = rgb('#634431')
FLAG_BLUE = rgb('#35628A')


def block(s, i, j, wi, wj, height, material=STONE, pattern=None, z=0):
    cover = facade(s, i, j, wi, wj, height, pattern or stone_courses(material, 4, 9), palette=material, z0=z)
    iso.fill(s, list(corners(s, i, j, wi, wj, z + height)), lambda x, y: material['mid'], cover)
    iso.outline(s, cover, material['outline'])
    return cover


def windows(material, height, bay=10, floor=13, arched=False):
    courses = stone_courses(material, 3 if material == BRICK else 5, 9)
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
        return courses(u, v, lit)
    return pattern


def church_lights(material, height, bay=11):
    courses = stone_courses(material, 3, 8)
    def pattern(u, v, lit):
        c, v = int(u) % bay, int(v)
        trim = PALE['lit' if lit else 'dark']
        top = height - 4 - abs(c - bay / 2) * 1.1
        if c == 0 or v in (1, height - 1):
            return trim
        if 3 <= c <= bay - 2 and 7 <= v <= top:
            if c in (3, bay - 2, bay // 2) or v in (7, 14, int(top)):
                return trim
            return GLASS['mid' if lit else 'dark']
        return courses(u, v, lit)
    return pattern


def tower_windows(material, height, bay, belfry):
    """Keep solid masonry below the belfry; tower openings are separate storeys."""
    courses = stone_courses(material, 3, 9)
    def pattern(u, v, lit):
        c, v = int(u) % bay, int(v)
        trim = PALE['lit' if lit else 'dark']
        if v in (1, height - 2) or c in (0, bay - 1):
            return trim
        for low, high in ((9, 17), (29, 37), belfry):
            if low <= v <= high and bay * .3 <= c <= bay * .7:
                if v in (low, high) or c in (int(bay*.3)+1, int(bay*.7)):
                    return trim
                if low != belfry[0] and (c == bay // 2 or v == (low + high) // 2):
                    return trim
                return IRON['deep'] if low == belfry[0] else GLASS['dark']
        return courses(u, v, lit)
    return pattern


def cross(s, i, j, z):
    block(s, i - .08, j - .08, .16, .16, 6, GOLD, z=z)
    block(s, i - .29, j - .08, .58, .16, 1.2, GOLD, z=z + 3.5)


def townhouse(scene, i, j, wi=2.3, wj=2.8, floors=3, seed=0):
    """Gamla Stan plaster: dressed sash windows, iron guards, shops and steep clay roofs."""
    wall, height = palette_of(WALLS[seed % len(WALLS)]), floors * 10 + 3
    def pattern(u, v, lit):
        c, v = int(u) % 9, int(v)
        level, trim = v % 10, PALE['lit' if lit else 'dark']
        if v < 2:
            return STONE['dark']
        if v in (height - 1, height - 3):
            return trim
        if v < 10 and 2 <= c <= 7 and v < 8:
            if c in (2, 7) or v == 7:
                return trim
            return WOOD if (int(u) // 9 + seed) % 3 == 0 else GLASS['dark']
        if v >= 10 and 2 <= c <= 7 and 3 <= level <= 8 and v < height - 4:
            if c in (2, 4, 7) or level in (3, 6, 8):
                return trim
            return GLASS['mid' if lit else 'dark']
        if v >= 10 and level == 2 and 1 <= c <= 8:
            return trim
        if seed % 4 == 0 and level == 3 and v >= 10 and 2 <= c <= 7:
            return IRON['dark']
        return wall['line'] if h01(int(u), v, seed) < .02 else None
    def draw(s):
        block(s, i, j, wi, wj, height, wall, pattern)
        roof = IRON if seed % 5 == 0 else CLAY
        if seed % 3 == 0:
            gable_roof(s, i, j, wi, wj, height, 13, roof, wall, 'bell' if seed % 6 == 0 else 'point')
        else:
            hip_roof(s, i - .08, j - .08, wi + .16, wj + .16, height, 13, roof)
            block(s, i + .65, j + wj - .7, .65, .5, 5, PALE, windows(PALE, 8, bay=6), z=height + 2)
            hip_roof(s, i + .65, j + wj - .7, .65, .5, height + 7, 3, roof)
        block(s, i + wi * .7, j + .4, .34, .4, 10, BRICK, z=height + 6)
        block(s, i + wi * .7 - .04, j + .36, .42, .48, 1.5, STONE, z=height + 15)
    scene.add(i + j + wi + wj, draw)


def city_hall(scene, i, j):
    """Brick courtyard, waterfront colonnade and massive tower with three separate gold crowns."""
    def draw(s):
        block(s, i, j, 8.4, 5.4, 3, STONE)
        for a, b, wi, wj in ((i,j,8.4,1.3),(i,j+1.3,1.3,4.1),(i+7.1,j+1.3,1.3,4.1)):
            block(s,a,b,wi,wj,31,BRICK,windows(BRICK,31,bay=9,floor=12),z=3)
            hip_roof(s,a,b,wi,wj,34,13,COPPER)
        # A genuinely open colonnade: quays and the courtyard show between the columns.
        for a in range(8):
            block(s,i+.25+a,j+4.45,.28,.7,13,STONE,z=3)
        block(s,i,j+4.4,8.4,1,16,BRICK,windows(BRICK,16,bay=9),z=16)
        hip_roof(s,i,j+4.4,8.4,1,32,12,COPPER)
        ti,tj=i+6.4,j+3.5
        block(s,ti,tj,2,2,84,BRICK,tower_windows(BRICK,84,16,(67,78)))
        block(s,ti-.1,tj-.1,2.2,2.2,3,STONE,z=82)
        # Open copper lantern, four pillars and a little tent roof.
        for a,b in ((ti,tj),(ti+1.7,tj),(ti,tj+1.7),(ti+1.7,tj+1.7)):
            block(s,a,b,.3,.3,13,COPPER,z=85)
        hip_roof(s,ti-.1,tj-.1,2.2,2.2,98,7,COPPER)
        cylinder(s,ti+1,tj+1,.15,.15,105,9,GOLD)
        for di,dj in ((-.55,.18),(.55,.18),(0,-.52)):
            ci,cj=ti+1+di,tj+1+dj
            block(s,ci-.25,cj-.1,.5,.2,1.8,GOLD,z=114)
            for offset in (-.25,0,.25):
                block(s,ci+offset-.06,cj-.1,.12,.2,3,GOLD,z=115)
        for a,b in ((i+.5,j+.7),(i+3,j+.5)):
            spire(s,a,b,.35,46,11,COPPER)
    scene.add(i+j+15,draw)


def royal_palace(scene,i,j):
    """Tessin's low-roofed Baroque quadrangle: courtyard, rustication, pilasters and relief attic."""
    def draw(s):
        block(s,i,j,9,7,3,STONE)
        for a,b,wi,wj in ((i,j,9,1.7),(i,j+1.7,1.7,3.6),(i+7.3,j+1.7,1.7,3.6),(i,j+5.3,9,1.7)):
            block(s,a,b,wi,wj,40,OCHRE,windows(OCHRE,40,bay=9,floor=12),z=3)
            # Heavy upper cornice, projecting quoins and a moulded parapet.
            block(s,a-.08,b-.08,wi+.16,wj+.16,2,STONE,z=41)
            hip_roof(s,a,b,wi,wj,43,4,IRON)
        block(s,i+3,j+6.65,3,.6,43,STONE,windows(STONE,43,bay=8,floor=12))
        for a in (i+3,i+3.9,i+5.1,i+5.9):
            block(s,a,j+7.18,.18,.2,23,PALE,z=12)
        # Three deep portals and a carved attic panel belong only to the lit wall.
        def centre(u,v,lit):
            if lit and v<12:
                return arch_opening(int(u)%8,v,4,2.4,7,IRON['deep'])
            if lit and 34<v<40 and 4<int(u)<20:
                return OCHRE['line'] if (int(u)+int(v))%4 else PALE['hi']
            return windows(STONE,43,bay=8,floor=12)(u,v,lit)
        block(s,i+3.15,j+7.02,2.7,.2,43,STONE,centre)
        for k in range(4):
            block(s,i+3,j+7.3+k*.22,3,.23,4-k,STONE)
        # Swedish flag above the roof, with a projected gold Nordic cross.
        seg(s,P(s,i+4.5,j+3,45),P(s,i+4.5,j+3,60),PALE['lit'])
        flag=[P(s,i+4.5,j+3,59),P(s,i+5.8,j+3,59),P(s,i+5.8,j+3,53),P(s,i+4.5,j+3,53)]
        poly(s,flag,lambda x,y:FLAG_BLUE)
        seg(s,P(s,i+4.5,j+3,56),P(s,i+5.8,j+3,56),GOLD['lit'])
        seg(s,P(s,i+4.95,j+3,53),P(s,i+4.95,j+3,59),GOLD['lit'])
    scene.add(i+j+17,draw)


def storkyrkan(scene,i,j):
    """Warm plaster nave, pale pilasters and square clock tower with a Baroque lantern."""
    def draw(s):
        block(s,i,j,4.3,6.3,34,ROSE,church_lights(ROSE,34,bay=11))
        gable_roof(s,i,j,4.3,6.3,34,15,COPPER,ROSE)
        for a in (i+.1,i+1.35,i+2.75,i+4):
            block(s,a,j+6.3,.22,.25,34,PALE)
        ti,tj=i+1.1,j+4.5
        block(s,ti,tj,2.2,2.2,65,OCHRE,tower_windows(OCHRE,65,17,(38,46)))
        block(s,ti-.1,tj-.1,2.4,2.4,3,PALE,z=61)
        clock(s,ti+1.1,tj+2.22,5,53)
        clock(s,ti+2.22,tj+1.1,4,53,False)
        hip_roof(s,ti-.15,tj-.15,2.5,2.5,65,8,COPPER)
        block(s,ti+.65,tj+.65,.9,.9,11,IRON,church_lights(IRON,11,bay=6),z=73)
        spire(s,ti+1.1,tj+1.1,.8,84,13,COPPER,onion=True)
        cross(s,ti+1.1,tj+1.1,99)
        block(s,i+1.4,j+6.35,1.4,.25,13,PALE,
              lambda u,v,lit:arch_opening(u,v,5.5,3.5,8,WOOD) if lit else None)
    scene.add(i+j+12,draw)


def riddarholmen(scene,i,j):
    """Medieval brick nave, burial chapels and the restored cast-iron openwork spire."""
    def draw(s):
        block(s,i,j,3.6,6.5,31,BRICK,church_lights(BRICK,31))
        gable_roof(s,i,j,3.6,6.5,31,19,COPPER,BRICK)
        for b in (j+1,j+3,j+5):
            block(s,i+3.6,b,.38,.35,26,STONE)
            hip_roof(s,i+3.6,b,.38,.35,26,4,COPPER)
        cylinder(s,i+3.1,j+5,1.65,1.5,0,21,STONE,church_lights(STONE,21,bay=10))
        spire(s,i+3.1,j+5,1.7,21,14,COPPER,onion=True)
        ti,tj=i+.8,j+4.8
        block(s,ti,tj,2,2,63,BRICK,tower_windows(BRICK,63,16,(48,59)))
        clock(s,ti+1,tj+2.02,4.5,40)
        block(s,ti-.08,tj-.08,2.16,2.16,3,STONE,z=62)
        # Hollow octagonal lattice, including the rear ribs visible through the gaps.
        ci,cj=ti+1,tj+1
        for n in sorted(range(8),key=lambda n:math.cos(n*math.tau/8)+math.sin(n*math.tau/8)):
            a,b=n*math.tau/8,(n+1)*math.tau/8
            for z in range(66,111,7):
                r0,r1=1.05*(114-z)/48,1.05*(114-z-7)/48
                p0,p1=P(s,ci+r0*math.cos(a),cj+r0*math.sin(a),z),P(s,ci+r1*math.cos(a),cj+r1*math.sin(a),z+7)
                q0,q1=P(s,ci+r0*math.cos(b),cj+r0*math.sin(b),z),P(s,ci+r1*math.cos(b),cj+r1*math.sin(b),z+7)
                tone=IRON['lit' if math.sin(a)>.1 else 'dark']
                for aa,bb in ((p0,p1),(p0,q0),(p0,q1),(q0,p1)):
                    seg(s,aa,bb,tone)
        for di,dj in ((0,0),(2,0),(0,2),(2,2)):
            spire(s,ti+di,tj+dj,.28,64,14,IRON,conical=True)
        cross(s,ci,cj,114)
    scene.add(i+j+13,draw)


def german_church(scene,i,j):
    """St Gertrude's steep nave and high copper steeple, clocks, galleries and corner pinnacles."""
    def draw(s):
        block(s,i,j,4,5.8,33,BRICK,church_lights(BRICK,33,bay=11))
        gable_roof(s,i,j,4,5.8,33,20,COPPER,BRICK)
        for b in (j+.8,j+2.5,j+4.3):
            block(s,i+3.9,b,.35,.35,30,PALE)
        ti,tj=i+.8,j+3.8
        block(s,ti,tj,2.4,2.4,67,OCHRE,tower_windows(OCHRE,67,19,(39,48)))
        for z in (48,65,73):
            block(s,ti-.15,tj-.15,2.7,2.7,2,PALE if z==48 else COPPER,z=z)
        block(s,ti+.2,tj+.2,2,2,12,COPPER,church_lights(COPPER,12,bay=8),z=67)
        spire(s,ti+1.2,tj+1.2,1.35,79,46,COPPER)
        for di,dj in ((0,0),(2.4,0),(0,2.4),(2.4,2.4)):
            spire(s,ti+di,tj+dj,.38,74,15,COPPER)
        clock(s,ti+1.2,tj+2.43,5,57)
        clock(s,ti+2.43,tj+1.2,4.5,57,False)
        cross(s,ti+1.2,tj+1.2,127)
        block(s,i+1.25,j+5.85,1.5,.3,13,PALE,
              lambda u,v,lit:arch_opening(u,v,6,4,8,WOOD) if lit else None)
    scene.add(i+j+13,draw)


def nationalmuseum(scene,i,j):
    """Renaissance stone palazzo: round-headed windows, central relief front and glazed roof lanterns."""
    def draw(s):
        block(s,i,j,7.8,5,40,STONE,windows(STONE,40,bay=10,floor=13,arched=True))
        hip_roof(s,i,j,7.8,5,40,7,COPPER)
        block(s,i+2.4,j+4.7,3,.65,47,STONE,windows(STONE,47,bay=8,floor=13,arched=True))
        hip_roof(s,i+2.3,j+4.65,3.2,.85,47,5,COPPER)
        for a in (i+2.4,i+3.2,i+4.5,i+5.25):
            block(s,a,j+5.36,.15,.17,19,PALE,z=17)
        for z in (13,26,39):
            block(s,i-.08,j+4.95,7.96,.16,1.5,PALE,z=z)
        # Sculptural metopes under the attic cornice, on the lit face alone.
        for a in (i+2.8,i+3.7,i+4.6):
            block(s,a,j+5.36,.45,.16,5,PALE,
                  lambda u,v,lit:STONE['line'] if lit and (int(u)+int(v))%3==0 else None,z=39)
        for b in (j+1,j+3):
            block(s,i+1.3,b,5,.65,3,COPPER,z=45)
            hip_roof(s,i+1.3,b,5,.65,48,2,palette_of(GLASS['mid']))
        for k in range(5):
            block(s,i+2.5,j+5.5+k*.2,2.8,.22,5-k,STONE)
    scene.add(i+j+14,draw)


def vasa_museum(scene,i,j):
    """Modern red timber hall with folded copper roofs and three rigged ship masts above it."""
    def draw(s):
        def boarding(u,v,lit):
            if int(u)%4==0:return TIMBER['line' if lit else 'deep']
            if 6<v<13 and int(u)%12<9:return GLASS['dark']
            return None
        block(s,i,j,7.5,5,24,TIMBER,boarding)
        for a,b,wi,wj,z,h in ((i,j,2.4,5,24,12),(i+2.4,j,2.7,5,26,16),(i+5.1,j,2.4,5,24,10)):
            if z>24:block(s,a,b,wi,wj,z,TIMBER,boarding)
            gable_roof(s,a,b,wi,wj,z,h,COPPER,TIMBER)
        block(s,i+1,j+5,5.5,1,12,TIMBER,windows(TIMBER,12,bay=8,floor=12))
        hip_roof(s,i+1,j+5,5.5,1,12,5,COPPER)
        # Only the replica upper masts project above the building; the ship stays indoors.
        for a,b,base,height in ((i+1.4,j+2.3,34,35),(i+3.8,j+2.3,40,48),(i+6,j+2.3,32,34)):
            block(s,a-.08,b-.08,.16,.16,height,TIMBER,z=base)
            for zz,span in ((base+height*.42,1.3),(base+height*.7,1),(base+height*.88,.65)):
                seg(s,P(s,a-span,b,zz),P(s,a+span,b,zz),TIMBER['lit'])
                seg(s,P(s,a-span,b,zz),P(s,a,b,base+height),IRON['mid'])
                seg(s,P(s,a+span,b,zz),P(s,a,b,base+height),IRON['dark'])
            for di,dj in ((-1,-1),(1,1)):
                seg(s,P(s,a,b,base+height),P(s,a+di,b+dj,base),IRON['dark'])
            block(s,a-.3,b-.25,.6,.5,2,TIMBER,z=base+height*.45)
    scene.add(i+j+15,draw)


def nordiska(scene,i,j):
    """Castle-like museum hall, sculpted end gable, turrets and two staged copper spires."""
    def draw(s):
        block(s,i,j,5.2,8.5,41,STONE,windows(STONE,41,bay=10,floor=13,arched=True))
        gable_roof(s,i,j,5.2,8.5,41,29,IRON,STONE,'bell')
        # Sandstone dressings and tall projecting buttresses down the long wall.
        for b in (j+.4,j+2.3,j+4.2,j+6.2,j+8):
            block(s,i+5.18,b,.24,.3,40,PALE)
        for a,b in ((i+.1,j+7.1),(i+3.8,j+.6)):
            block(s,a,b,1.3,1.3,65,STONE,windows(STONE,65,bay=8,floor=13,arched=True))
            spire(s,a+.65,b+.65,1,65,49,COPPER,onion=True)
            block(s,a-.1,b-.1,1.5,1.5,2,COPPER,z=72)
            block(s,a-.02,b-.02,1.34,1.34,2,COPPER,z=85)
            for di,dj in ((0,0),(1.3,0),(0,1.3),(1.3,1.3)):
                spire(s,a+di,b+dj,.16,73,11,COPPER)
        # Raised gable cartouche, three traceried lights and a dressed round entrance.
        block(s,i+1.1,j+8.61,3,.16,2,PALE,z=46)
        cylinder(s,i+2.6,j+8.65,.35,.08,54,5,PALE)
        block(s,i+1.7,j+8.5,1.8,.4,15,PALE,
              lambda u,v,lit:arch_opening(u,v,7,5,10,WOOD) if lit else None)
        for k in range(5):
            block(s,i+1.4,j+8.9+k*.2,2.4,.21,5-k,STONE)
        for a,b in ((i+.2,j+.1),(i+4.8,j+8.3)):
            spire(s,a,b,.45,44,23,COPPER)
        # The broad sculpted end gable rises in rounded steps above the hall roof.
        profile=[(0,0),(.06,.2),(.18,.24),(.18,.43),(.3,.48),(.3,.7),
                 (.4,.74),(.4,.9),(.47,1),(.53,1),(.6,.9),(.6,.74),
                 (.7,.7),(.7,.48),(.82,.43),(.82,.24),(.94,.2),(1,0)]
        front=[P(s,i+.2+u*4.8,j+8.66,41+v*35) for u,v in profile]
        back=[P(s,i+.2+u*4.8,j+8.5,41+v*35) for u,v in profile]
        for a in range(len(profile)-1):
            poly(s,[back[a],back[a+1],front[a+1],front[a]],lambda x,y:STONE['dark'])
        foot=P(s,i+.2,j+8.66,41)
        joints=stone_courses(STONE,4,9)
        poly(s,front,lambda x,y:joints(x-foot[0],foot[1]+(x-foot[0])*.5-y,True) or STONE['lit'])
        for a,b in zip(front,front[1:]):
            seg(s,a,b,PALE['lit'])
        for z,width in ((46,2.5),(53,1.7),(62,.8)):
            block(s,i+2.6-width/2,j+8.68,width,.1,1.5,PALE,z=z)
        for a,z in ((i+1.7,47),(i+3,47),(i+2.35,57)):
            block(s,a,j+8.7,.45,.1,5,PALE,
                  lambda u,v,lit:GLASS['dark'] if lit and 1<int(u)<3 and 1<v<4 else None,z=z)
    scene.add(i+j+16,draw)


STUDIES = [('city-hall',city_hall),('royal-palace',royal_palace),('storkyrkan',storkyrkan),
           ('riddarholmen',riddarholmen),('german-church',german_church),
           ('nationalmuseum',nationalmuseum),('vasa',vasa_museum),('nordiska',nordiska)]

if __name__ == '__main__':
    for name,builder in STUDIES:
        print(preview([lambda s,b=builder:b(s,4,4)],'stockholm-'+name,
                      size=(240,250),origin=(110,115),tiles=20))
    print(preview([lambda s:townhouse(s,4,4,2.4,3,3,0),lambda s:townhouse(s,8,4,2.4,3,3,1),
                   lambda s:townhouse(s,4,9,2.4,3,2,2),lambda s:townhouse(s,8,9,2.4,3,3,3)],
                  'stockholm-houses',size=(230,220),origin=(105,70),tiles=18))
