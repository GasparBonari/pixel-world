"""Copenhagen: Danish plaster, Renaissance brick and copper in true (i, j, z).

Nine standalone 4× landmark studies precede scene integration. Primary references and
north-up geographic anchors are recorded in DEVELOPMENT_PLAN.md.
"""
import math

import iso
from iso import rgb, h01
from landmarks_paris import P, seg, poly, corners, facade, preview, GLASS
from landmarks_iberia import hip_roof, stone_courses, arch_opening, palette_of, tones
from landmarks_belgium import dome, pediment
from landmarks_italy import cylinder
from landmarks_amsterdam import gable_roof

STONE = tones('#F5E8D0', '#D8C7A7', '#BFAE8F', '#9E8F76', '#71624F', '#AD9A7B', '#493D30')
PALE = tones('#FFF9E6', '#ECE4CE', '#D3CCB6', '#B2AC98', '#827B68', '#C1B69C', '#514837')
BRICK = tones('#DAA07A', '#B56F50', '#98583F', '#773E31', '#502D26', '#8D503B', '#3D2923')
YELLOW = tones('#F3DC96', '#D9B976', '#BCA065', '#9C8155', '#6C593D', '#B49965', '#50412D')
COPPER = tones('#BAD3B0', '#7FA992', '#638B79', '#416958', '#2E4A40', '#557D69', '#263D32')
CLAY = tones('#F0AE77', '#CB7D4D', '#AF613D', '#8A472F', '#603424', '#A25C3D', '#4F2D22')
SLATE = tones('#A5ACAD', '#77888A', '#617376', '#43585E', '#2E4047', '#55686B', '#293B43')
GOLD = tones('#FFF3B5', '#E9C76A', '#C6A047', '#99732E', '#695024', '#AF893B', '#514020')
DARK = tones('#919086', '#5E665D', '#474F48', '#303C36', '#25312C', '#414E42', '#202B25')
BRONZE = tones('#A0A58A', '#6F7961', '#505E49', '#354532', '#243526', '#46583F', '#1C2C21')
GRANITE = tones('#DDD8C7', '#BDBCAA', '#A2A695', '#7C897C', '#566A61', '#929D8C', '#3D5049')
HAIR = tones('#8C9981', '#61745F', '#4B5E4C', '#354A3B', '#293B31', '#445B47', '#25372C')
WALLS = [rgb(c) for c in ('#D8AF55', '#BC6750', '#D8CCAE', '#92ACAE', '#C48759', '#B7BA9C', '#A95343')]
IRON, WOOD = rgb('#343F3B'), rgb('#674A32')
WATER = (rgb('#477F8B'), rgb('#356572'), rgb('#ACD5D4'))


def block(s, i, j, wi, wj, height, material=STONE, pattern=None, z=0):
    cover = facade(s, i, j, wi, wj, height, pattern or stone_courses(material, 4, 9), palette=material, z0=z)
    iso.fill(s, list(corners(s, i, j, wi, wj, z + height)), lambda x, y: material['mid'], cover)
    iso.outline(s, cover, material['outline'])
    return cover


def windows(material, height, bay=9, floor=12, arched=False):
    joints = stone_courses(material, 3 if material == BRICK else 5, 8)
    def pattern(u, v, lit):
        c, v = int(u) % bay, int(v)
        level, trim = v % floor, PALE['lit' if lit else 'dark']
        if v < 2 or v in (height - 1, height - 3) or level == 0:
            return trim
        top = floor - 2 - (abs(c - bay / 2) * .55 if arched else 0)
        if 2 <= c <= bay - 2 and 3 <= level <= top and v < height - 4:
            if c in (2, bay - 2, bay // 2) or level in (3, 6, int(top)):
                return trim
            return GLASS['mid' if lit else 'dark']
        return joints(u, v, lit)
    return pattern


def spire(s, ci, cj, radius, base, height, material=COPPER, onion=False, conical=False):
    """Turned copper spire with square/octagonal sections and projecting collars."""
    profile = [(0, 1), (.12, .82), (.28, .64), (.42, .36), (1, .02)]
    if conical:
        profile = [(0, 1), (1, .11)]
    if onion:
        profile = [(0, .7), (.08, .95), (.18, 1), (.31, .72), (.4, .35), (.48, .33), (.55, .55), (.65, .4), (1, .02)]
    for (z0, r0), (z1, r1) in zip(profile, profile[1:]):
        faces=[]
        for n in range(8):
            a,b=n*math.tau/8,(n+1)*math.tau/8
            pts=[P(s,ci+radius*r*math.cos(t),cj+radius*r*math.sin(t),base+height*z)
                 for z,r,t in ((z0,r0,a),(z0,r0,b),(z1,r1,b),(z1,r1,a))]
            key='lit' if math.sin((a+b)/2)-.5*math.cos((a+b)/2)>.1 else 'dark'
            faces.append((math.cos(a)+math.sin(a)+math.cos(b)+math.sin(b),pts,key))
        for _,pts,key in sorted(faces):
            poly(s,pts,lambda x,y,key=key:material['line'] if int(y)%5==0 else material[key])
            seg(s,pts[0],pts[3],material['hi'] if key=='lit' else material['deep'])
    cylinder(s,ci,cj,.13,.13,base+height,3,GOLD)


def clock(s, i, j, width, z, lit=True):
    """Dial drawn in the supporting wall's plane, with rim, hour marks and two hands."""
    centre=P(s,i,j,z)
    # +j wall runs along i; +i wall runs along j.
    def point(u,v):
        return P(s,i+u/8 if lit else i,j if lit else j-u/8,z+v)
    ring=[point(math.cos(n*math.tau/32)*width,math.sin(n*math.tau/32)*width) for n in range(32)]
    poly(s,ring,lambda x,y:GOLD['lit'] if (int(x)+int(y))%5==0 else DARK['deep'])
    for a,b in zip(ring,ring[1:]+ring[:1]):seg(s,a,b,GOLD['mid'])
    for n in range(12):
        a=n*math.tau/12
        seg(s,point(math.cos(a)*(width-1),math.sin(a)*(width-1)),point(math.cos(a)*width,math.sin(a)*width),PALE['lit'])
    seg(s,centre,point(-width*.55,width*.2),PALE['hi'])
    seg(s,centre,point(width*.1,width*.7),PALE['hi'])


def townhouse(scene,i,j,wi=2.4,wj=2.7,floors=3,seed=0):
    """Danish plaster houses: sash panes, shop doors, cornice, tiles, dormer, chimney."""
    wall,height=palette_of(WALLS[seed%len(WALLS)]),floors*10+3
    def pattern(u,v,lit):
        c,v=int(u)%9,int(v); level=v%10; trim=PALE['lit' if lit else 'dark']
        if v<2:return STONE['dark']
        if v in (height-1,height-3):return trim
        if v<10 and 2<=c<=7 and v<8:
            if c in (2,7) or v==7:return trim
            return WOOD if (int(u)//9+seed)%3==0 else GLASS['dark']
        if v>=10 and 2<=c<=7 and 3<=level<=8 and v<height-4:
            if c in (2,7,4) or level in (3,6,8):return trim
            return GLASS['mid' if lit else 'dark']
        if v>=10 and level==2 and 1<=c<=8:return trim
        if seed%5==0 and level==1 and 1<=c<=8:return IRON
        return wall['line'] if h01(int(u),v,seed)<.025 else None
    def draw(s):
        block(s,i,j,wi,wj,height,wall,pattern)
        roof=SLATE if seed%5==0 else CLAY
        hip_roof(s,i-.08,j-.08,wi+.16,wj+.16,height,10,roof)
        if seed%4==0:
            gable_roof(s,i,j,wi,wj,height,11,roof,wall,'point')
        else:
            di,dj=i+wi*.35,j+wj*.76
            block(s,di,dj,.7,.5,5,PALE,windows(PALE,6,bay=6),z=height+1)
            hip_roof(s,di,dj,.7,.5,height+6,3,roof)
        block(s,i+wi*.7,j+.35,.35,.35,9,BRICK,z=height+5)
        block(s,i+wi*.67,j+.32,.42,.42,1.5,STONE,z=height+13)
    scene.add(i+j+wi+wj,draw)


def rosenborg(scene,i,j):
    """Red-brick Renaissance palace, sandstone bands, scrolled gables, three copper towers."""
    def draw(s):
        block(s,i,j,8,3.5,39,BRICK,windows(BRICK,39))
        hip_roof(s,i,j,8,3.5,39,18,SLATE)
        # Sandstone-edged curving end gables rise above the steep slate ridge.
        for a in (i,i+6.4):
            gable_roof(s,a,j,1.6,3.5,39,18,SLATE,BRICK,'bell')
        for a,b,h,r in ((i+1,j+3.1,55,.9),(i+6.2,j+3.1,55,.9),(i+3,j+2.2,74,1.05)):
            block(s,a,b,1.35,1.35,h,BRICK,windows(BRICK,h,bay=7))
            block(s,a-.12,b-.12,1.59,1.59,3,PALE,z=h-2)
            spire(s,a+.67,b+.67,r,h+1,24,COPPER,onion=True)
        # Dressed central doorway and stair flight at the near wall.
        for k in range(5):block(s,i+3,j+3.5+(4-k)*.2,1.4,.25,k+1,STONE)
        block(s,i+3.2,j+3.5,1,.15,11,PALE,
              lambda u,v,lit:WOOD if 2<int(u)<6 and v<8 else None)
    scene.add(i+j+14,draw)


def round_tower(scene,i,j):
    """Yellow-brick Rundetaarn, attached Trinitatis hall, rebus panel and iron lookout."""
    def draw(s):
        block(s,i+1.8,j-2,3.2,6.8,26,BRICK,windows(BRICK,26,bay=10,floor=22,arched=True))
        hip_roof(s,i+1.8,j-2,3.2,6.8,26,14,CLAY)
        ci,cj=i+1.5,j+3.6
        def tower_lights(u,v,lit):
            c,v=int(u)%15,int(v);level=v%18
            if 5<=c<=8 and 4<=level<=14-abs(c-6.5)*.6:
                return PALE['lit' if lit else 'dark'] if c in (5,8) or level in (4,13) else GLASS['dark']
            return stone_courses(YELLOW,3,8)(u,v,lit)
        cylinder(s,ci,cj,1.6,1.6,0,57,YELLOW,tower_lights)
        cylinder(s,ci,cj,1.72,1.72,55,3,PALE)
        for n in range(36):
            a=n*math.tau/36
            p=P(s,ci+1.63*math.cos(a),cj+1.63*math.sin(a),58)
            q=P(s,ci+1.63*math.cos(a),cj+1.63*math.sin(a),63)
            seg(s,p,q,IRON)
        for z in (60,63):
            pts=[P(s,ci+1.63*math.cos(n*math.tau/48),cj+1.63*math.sin(n*math.tau/48),z) for n in range(49)]
            for a,b in zip(pts,pts[1:]):seg(s,a,b,IRON)
        cylinder(s,ci-.3,cj-.25,.7,.7,58,6,BRICK,windows(BRICK,7,bay=6))
        dome(s,ci-.3,cj-.25,.78,64,6,COPPER)
        # Christian IV's gilded rebus panel, fixed to the visible cylindrical front.
        for di,dz in ((-.3,0),(0,0),(.3,0),(0,3),(-.2,6),(.2,6)):
            block(s,ci+di,cj+1.48,.2,.1,2,GOLD,z=36+dz)
    scene.add(i+j+13,draw)


def marble_church(scene,i,j):
    """Frederik's Church: colossal ribbed copper dome, windowed drum, lantern and portico."""
    def draw(s):
        ci,cj=i+3.6,j+3.6
        cylinder(s,ci,cj,3.4,3.4,0,28,STONE,windows(STONE,28,bay=11,floor=22,arched=True))
        cylinder(s,ci,cj,3.55,3.55,27,3,PALE)
        cylinder(s,ci,cj,2.9,2.9,30,19,STONE,windows(STONE,20,bay=9,floor=18,arched=True))
        # Twelve structural piers on the drum.
        for n in range(12):
            a=n*math.tau/12
            block(s,ci+2.83*math.cos(a)-.12,cj+2.83*math.sin(a)-.12,.24,.24,20,PALE,z=29)
        cylinder(s,ci,cj,3.12,3.12,48,3,PALE)
        dome(s,ci,cj,3.15,51,29,COPPER)
        cylinder(s,ci,cj,.52,.52,79,7,PALE,windows(PALE,8,bay=6))
        dome(s,ci,cj,.64,86,5,COPPER)
        block(s,ci-.08,cj-.08,.16,.16,6,GOLD,z=91)
        block(s,ci-.32,cj-.08,.64,.16,1,GOLD,z=95)
        # Entrance vestibule with four columns, triangular pediment and open portal. The real
        # portico faces east along Frederiksgade towards Amalienborg, so it stands on the shaded
        # +i face (south-east), the visible side closest to east.
        block(s,i+6.2,j+2,1.6,3.2,20,STONE,windows(STONE,20,bay=10,floor=17,arched=True))
        for b in (2.1,2.9,3.7,4.5):
            block(s,i+7.6,j+b,.35,.28,20,PALE,z=2)
            block(s,i+7.53,j+b-.08,.49,.44,2,STONE,z=20)
        gable=[P(s,i+8,j+1.9,23),P(s,i+8,j+5.3,23),P(s,i+8,j+3.6,31)]
        poly(s,gable,lambda x,y:PALE['dark'] if (int(x)+int(y))%7 else PALE['deep'])
        for a,b in zip(gable,gable[1:]+gable[:1]):seg(s,a,b,PALE['lit'],2)
        for n in range(8):
            a=n*math.tau/8
            cylinder(s,ci+3.3*math.cos(a),cj+3.3*math.sin(a),.16,.16,29,4,STONE)
    scene.add(i+j+17,draw)


def horse(s,i,j,z,material=DARK):
    """Small filled equestrian volume: four legs, barrel, neck, head and seated rider."""
    for a,b in ((0,0),(.7,0),(0,.3),(.7,.3)):
        block(s,i+a,j+b,.13,.13,4,material,z=z)
    block(s,i-.1,j-.08,1,.55,3,material,z=z+3)
    block(s,i+.65,j,.23,.3,4,material,z=z+5)
    block(s,i+.65,j-.04,.5,.34,1.7,material,z=z+8)
    block(s,i+.2,j+.03,.3,.3,4,material,z=z+6)
    cylinder(s,i+.35,j+.18,.16,.16,z+10,2,material)
    seg(s,P(s,i-.1,j+.25,z+5),P(s,i-.4,j+.25,z+2),material['dark'],2)


def amalienborg(scene,i,j):
    """Four rococo palace pavilions around an octagonal paved square and Frederik V."""
    def draw(s):
        ground=[P(s,i+a,j+b) for a,b in ((2,0),(7,0),(9,2),(9,7),(7,9),(2,9),(0,7),(0,2))]
        poly(s,ground,lambda x,y:STONE['line'] if (int(x)+2*int(y))%7==0 else STONE['lit'])
        for a,b in ((0,0),(6.1,0),(0,6.1),(6.1,6.1)):
            block(s,i+a,j+b,3.3,3.3,29,STONE,windows(STONE,29,bay=8,floor=13))
            hip_roof(s,i+a,j+b,3.3,3.3,29,11,SLATE)
            # Raised central corps de logis, pediment, dormers and rococo stone dressings.
            block(s,i+a+.85,j+b+2.55,1.6,.8,32,STONE,windows(STONE,32,bay=7,floor=13))
            hip_roof(s,i+a+.85,j+b+2.55,1.6,.8,32,8,SLATE)
            pediment(s,i+a+.65,j+b+3.4,2,33,6,PALE)
            for di in (.2,2.6):
                block(s,i+a+di,j+b+2.8,.55,.45,5,PALE,windows(PALE,6,bay=5),z=30)
                hip_roof(s,i+a+di,j+b+2.8,.55,.45,35,3,SLATE)
            for di in (.25,.8,2.4,3.05):
                block(s,i+a+di,j+b+3.3,.15,.13,24,PALE,z=3)
                block(s,i+a+di,j+b+3.3,.18,.16,3,STONE,z=30)
            for di in (.8,2.4):block(s,i+a+di,j+b+.6,.32,.32,7,BRICK,z=35)
        block(s,i+4,j+4,.95,1,6,PALE)
        horse(s,i+4,j+4,6)
    scene.add(i+j+22,draw)


def sailing_boat(s,i,j,length=3):
    """Moored wooden sailing vessel, projected hull, mast, spars and furled cream sail."""
    pts=[P(s,i,j),P(s,i+length-.3,j),P(s,i+length,j+.4),P(s,i+length-.3,j+.8),P(s,i,j+.8),P(s,i-.3,j+.4)]
    poly(s,pts,lambda x,y:WOOD if int(y)%2 else BRICK['deep'])
    for a,b in zip(pts,pts[1:]+pts[:1]):seg(s,a,b,PALE['dark'])
    for di in (.8,2):
        foot=P(s,i+di,j+.4,1);top=P(s,i+di,j+.4,25)
        seg(s,foot,top,WOOD,2)
        for end in (P(s,i,j+.4,3),P(s,i+length,j+.4,3)):seg(s,top,end,STONE['deep'])
        seg(s,P(s,i+di-.7,j+.4,18),P(s,i+di+.6,j+.4,18),WOOD)
        seg(s,P(s,i+di-.6,j+.4,17),P(s,i+di+.5,j+.4,17),PALE['lit'],2)


def nyhavn(scene,i,j):
    """Colourful narrow townhouses beside the eastward canal and historic sailing ships."""
    for k in range(6):townhouse(scene,i+k*1.9,j,1.85,2.4,2+(k%3!=0),k)
    def draw(s):
        for k in range(12):
            for b in (j+2.5,j+6):
                block(s,i+k,b,.75,.25,2,STONE)
        for k in (1.2,6.5):sailing_boat(s,i+k,j+4.2)
    scene.add(i+j+23,draw)


def christiansborg(scene,i,j):
    """Granite palace wings and courtyard, crowned copper tower, royal entrance and clock."""
    def draw(s):
        for a,b,wi,wj in ((0,0,8.6,2.3),(0,2.3,2.1,4.8),(6.5,2.3,2.1,4.8)):
            block(s,i+a,j+b,wi,wj,34,STONE,windows(STONE,34,bay=9,floor=11))
            hip_roof(s,i+a,j+b,wi,wj,34,11,COPPER)
        block(s,i+3.1,j-.2,2.4,2.6,57,STONE,windows(STONE,57,bay=9))
        block(s,i+2.9,j-.4,2.8,3,3,PALE,z=56)
        clock(s,i+4.3,j+2.4,5,48)
        block(s,i+3.4,j+.1,1.8,2,14,COPPER,windows(COPPER,14,bay=7),z=59)
        spire(s,i+4.3,j+1.1,1.35,73,19,COPPER,onion=True)
        # Distinct three-crown summit; each has a band and solid raised points.
        for di in (-.4,0,.4):
            cylinder(s,i+4.3+di,j+1.1,.2,.2,91,2,GOLD)
            for a in (-.15,.1):block(s,i+4.3+di+a,j+1.05,.1,.1,2,GOLD,z=93)
        block(s,i+3.4,j+6,1.6,1,5,STONE)
        horse(s,i+3.7,j+6.2,5)
        for k in range(4):block(s,i+3,j+2.4+(3-k)*.2,2.5,.2,k+1,STONE)
    scene.add(i+j+21,draw)


def city_hall(scene,i,j):
    """National Romantic red-brick Rådhus, gilded Absalon, crenels and copper clock tower."""
    def draw(s):
        block(s,i,j,8,4.8,31,BRICK,windows(BRICK,31,bay=10,floor=14,arched=True))
        hip_roof(s,i,j,8,4.8,31,16,CLAY)
        # Three steep tiled dormers and an articulated parapet rather than a flat box.
        for di in (1,3.5,6):
            gable_roof(s,i+di,j+3.2,1.1,1.6,31,11,CLAY,BRICK,'point')
        for k in range(12):block(s,i+k*.66,j+4.8,.3,.2,3,PALE,z=30)
        # Paired granite portal, balcony and filled gilded seated Absalon relief.
        block(s,i+3,j+4.8,2,.2,14,STONE,
              lambda u,v,lit:arch_opening(int(u)%8,v,4,2.5,6,BRICK['deep']))
        block(s,i+3.6,j+4.9,.8,.25,2,STONE,z=17)
        block(s,i+3.8,j+4.93,.4,.2,5,GOLD,z=19)
        cylinder(s,i+4,j+5.03,.22,.18,24,2,GOLD)
        a,b=i+6.1,j+.4
        block(s,a,b,1.8,1.8,76,BRICK,windows(BRICK,76,bay=7,floor=17,arched=True))
        block(s,a-.13,b-.13,2.06,2.06,3,PALE,z=60)
        clock(s,a+.9,b+1.81,5.5,67)
        clock(s,a+1.81,b+.9,5.5,67,False)
        block(s,a-.08,b-.08,1.96,1.96,7,STONE,windows(STONE,8,bay=7),z=76)
        spire(s,a+.9,b+.9,1.35,83,19,COPPER)
    scene.add(i+j+20,draw)


def our_saviour(scene,i,j):
    """Cruciform church, tall belfry and four-turn external golden spiral with globe/figure."""
    def draw(s):
        block(s,i+1.2,j,3.2,6.8,26,BRICK,windows(BRICK,26,bay=12,floor=23,arched=True))
        hip_roof(s,i+1.2,j,3.2,6.8,26,17,CLAY)
        block(s,i,j+2.6,5.6,2.3,26,BRICK,windows(BRICK,26,bay=10,floor=23,arched=True))
        hip_roof(s,i,j+2.6,5.6,2.3,26,13,CLAY)
        a,b=i+1.85,j+5.6;ci,cj=a+1,b+1
        block(s,a,b,2,2,40,BRICK,windows(BRICK,40,bay=8,floor=17,arched=True))
        block(s,a-.12,b-.12,2.24,2.24,3,PALE,z=40)
        block(s,a,b,2,2,16,BRICK,windows(BRICK,16,bay=8,floor=16,arched=True),z=43)
        block(s,a-.12,b-.12,2.24,2.24,3,PALE,z=58)
        block(s,a+.1,b+.1,1.8,1.8,12,DARK,windows(DARK,13,bay=7,floor=12,arched=True),z=61)
        spire(s,ci,cj,1.25,73,32,DARK,conical=True)
        # Rear and front helical runs follow the taper in tile space; only near runs are
        # visible over the opaque core. Posts and two rail edges make an actual staircase.
        for n in range(240):
            t=n/239;a=t*math.tau*4;rad=1.28*(1-t)+.14;z=74+t*30
            if math.sin(a)+math.cos(a)<-.2:continue
            p=P(s,ci+rad*math.cos(a),cj+rad*math.sin(a),z)
            q=P(s,ci+(rad+.15)*math.cos(a),cj+(rad+.15)*math.sin(a),z)
            seg(s,p,q,GOLD['lit'])
            r=P(s,ci+(rad+.15)*math.cos(a),cj+(rad+.15)*math.sin(a),z+2)
            if n%4==0:seg(s,q,r,GOLD['mid'])
            s.put(*r,GOLD['hi'])
        dome(s,ci,cj,.3,105,4,GOLD)
        # Filled miniature Saviour on the globe, torso, head and outstretched arms.
        block(s,ci-.12,cj-.1,.24,.2,4,GOLD,z=109)
        cylinder(s,ci,cj,.16,.16,113,2,GOLD)
        block(s,ci-.4,cj-.08,.8,.16,1,GOLD,z=111)
    scene.add(i+j+17,draw)


def little_mermaid(scene, i, j):
    """Seated bronze at Langelinie: bowed head, lap hands and folded legs on a granite boulder."""
    def draw(s):
        faces = []

        def point(u, v, z):
            # u is the figure's left/right profile; v is its depth towards the viewer.
            return i + 1.8 + (u + v) * .7071, j + 1.6 + (v - u) * .7071, z

        def ellipsoid(u, v, z, ru, rv, rz, material, crag=False):
            for row in range(8):
                for col in range(16):
                    vertices = []
                    for rr, cc in ((row, col), (row, col + 1), (row + 1, col + 1), (row + 1, col)):
                        lat, lon = -math.pi / 2 + rr * math.pi / 8, cc * math.tau / 16
                        radius = 1 + .12 * math.sin(cc * 2.3 + rr) if crag else 1
                        vertices.append(point(u + ru * math.cos(lat) * math.cos(lon) * radius,
                                              v + rv * math.cos(lat) * math.sin(lon) * radius,
                                              z + rz * math.sin(lat)))
                    lat, lon = -math.pi / 2 + (row + .5) * math.pi / 8, (col + .5) * math.tau / 16
                    light = -.7 * math.cos(lon) + .25 * math.sin(lon) + .55 * math.sin(lat)
                    tone = 'hi' if light > .75 else 'lit' if light > .1 else 'mid' if light > -.3 else 'dark'
                    faces.append((sum(a + b + h / 8 for a, b, h in vertices) / 4,
                                  [P(s, *p) for p in vertices], material, tone, crag))

        def limb(a, b, radius):
            # Overlapping rounded volumes form a continuous, tapered anatomical limb.
            count = max(3, int(abs(a[2] - b[2]) / 2) + 2)
            for step in range(count):
                t = step / (count - 1)
                u, v, z = [start + (end - start) * t for start, end in zip(a, b)]
                ellipsoid(u, v, z, radius * (1 - .2 * t), radius * .65, 2.1, BRONZE)

        # Uneven granite support, with separate rounded shoreline stones at its foot.
        ellipsoid(0, 0, 5, 1.65, 1.05, 6.5, GRANITE, crag=True)
        ellipsoid(.25, -.1, 11, 1.35, .85, 4.8, GRANITE, crag=True)
        ellipsoid(-1.3, .45, 2, .5, .4, 2.7, GRANITE, crag=True)
        ellipsoid(1.35, .2, 2, .5, .5, 2.8, GRANITE, crag=True)
        # Hips and a gently inclined torso; head and shoulders turn towards screen-left.
        ellipsoid(.4, 0, 17, .6, .4, 4, BRONZE)
        ellipsoid(.2, -.05, 23, .47, .34, 6.1, BRONZE)
        ellipsoid(-.02, -.04, 27.1, .5, .33, 2.5, BRONZE)
        ellipsoid(-.3, -.05, 30.2, .2, .2, 2, BRONZE)
        ellipsoid(-.52, -.05, 34, .34, .28, 4, BRONZE)
        ellipsoid(-.85, .02, 33.5, .18, .13, 1.1, BRONZE)  # nose and downturned profile
        ellipsoid(-.42, -.12, 36.4, .37, .3, 2.2, HAIR)
        ellipsoid(-.12, -.16, 34.2, .23, .24, 1.8, HAIR)  # gathered hair at the nape
        # Two knees point left, lower legs fold back along the rock to the right.
        for depth, lift in ((-.2, 1.5), (.3, 0)):
            limb((.35, depth, 17 + lift), (-1.1, depth, 14.5 + lift), .34)
            limb((-1.1, depth, 14.5 + lift), (.65, depth + .12, 9 + lift), .25)
            ellipsoid(.95, depth + .12, 8.5 + lift, .45, .18, 1.4, BRONZE)
        for depth in (-.3, .36):
            limb((-.02, depth, 27), (-.25, depth + .1, 21), .18)
            limb((-.25, depth + .1, 21), (-.85, depth + .05, 17.7), .16)
            ellipsoid(-.86, depth + .05, 17.3, .25, .16, 1.1, BRONZE)

        # Sort the whole sculpture together, so the near knee/arm occludes the torso naturally.
        visible = {}
        for _, pts, material, tone, crag in sorted(faces, key=lambda face: face[0]):
            for x, y in iso.polygon_pixels(pts):
                color = material[tone]
                if crag and h01(x, y, 179) < .12:
                    color = material['line' if tone in ('hi', 'lit') else 'deep']
                s.put(x, y, color)
                visible[(x, y)] = material
        # One-pixel material-coloured silhouettes, rather than outlines around every mesh facet.
        for (x, y), material in visible.items():
            if any((x + dx, y + dy) not in visible for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                s.put(x, y, material['outline'])
    scene.add(i + j + 7, draw)


if __name__ == '__main__':
    studies=[('rosenborg',rosenborg),('round-tower',round_tower),('marble-church',marble_church),
             ('amalienborg',amalienborg),('nyhavn',nyhavn),('christiansborg',christiansborg),
             ('city-hall',city_hall),('our-saviour',our_saviour),('little-mermaid',little_mermaid)]
    def study(s,builder):
        if builder == little_mermaid:
            for a in range(3,9):
                for b in range(3,9):
                    iso.ground_tile(s,a,b,lambda x,y:WATER[2] if h01(x//3,y,11)<.05 else WATER[(int(x)//6+int(y))%2])
        if builder == nyhavn:
            for a in range(4,17):
                for b in range(7,11):
                    iso.ground_tile(s,a,b,lambda x,y:WATER[2] if h01(x//3,y,11)<.05 else WATER[(int(x)//6+int(y))%2])
        builder(s,4,4)
    for name,builder in studies:
        print(preview([lambda s,b=builder:study(s,b)],'copenhagen-'+name,
                      size=(230,230),origin=(105,100),tiles=19))
    print(preview([lambda s:townhouse(s,4,4,2.5,3,3,0),lambda s:townhouse(s,8,4,2.5,3,3,1),
                   lambda s:townhouse(s,4,9,2.5,3,2,3),lambda s:townhouse(s,8,9,2.5,3,3,4)],
                  'copenhagen-houses',size=(230,210),origin=(105,65),tiles=18))
