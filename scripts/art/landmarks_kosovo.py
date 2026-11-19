"""Pristina's old town and university campus, in original projected (i, j, z) pixels.

Run for six isolated 4× studies and the local house types. Two-source fact sheets,
hidden fronts and explicit local turns are recorded in DEVELOPMENT_PLAN.md.
"""
import math

import iso
from iso import rgb
from landmarks_paris import P, seg, poly, corners, preview, GLASS
from landmarks_iberia import hip_roof, stone_courses, arch_opening, palette_of, tones
from landmarks_slovakia import block, band
from landmarks_slovenia import windows as framed_windows, revolve
from landmarks_bosnia import cylinder, crescent

STONE = tones('#FFF1D7', '#E4D5B8', '#CCBA97', '#AE9875', '#7E6C51', '#BAA581', '#51412F')
WHITE = tones('#FFFDF0', '#F2EDDB', '#DFD8C4', '#BFB7A1', '#8D836B', '#CEC3AB', '#514938')
BRICK = tones('#E3B08A', '#C38A63', '#AC6E4B', '#865038', '#5D3728', '#9F6548', '#4C2D24')
CLAY = tones('#DF9C73', '#BF724D', '#A65B3C', '#80412D', '#592E23', '#955134', '#49271E')
DARK_CLAY = tones('#BC9B7B', '#947253', '#7B5A42', '#5F422F', '#422F25', '#694B35', '#35281F')
LEAD = tones('#CFD1C3', '#A7AEA4', '#87958E', '#63766F', '#42574F', '#758980', '#31473E')
CONCRETE = tones('#E8E1CB', '#CFC5AA', '#B7AB8C', '#958B71', '#685F4D', '#AA9F81', '#454335')
MESH = tones('#EEE9BF', '#C9C493', '#ABA77B', '#85845E', '#585C40', '#99986C', '#3C4836')
YELLOW = tones('#FFF1A1', '#E9C95B', '#CEAA40', '#A37D29', '#765821', '#B99536', '#58401C')
GOLD = tones('#FFF4BA', '#E4C976', '#C4A14C', '#96732F', '#6A5124', '#B48F3F', '#4D3B21')
MARBLE = tones('#FFFEF5', '#EEECE1', '#DCDDD3', '#B5BDB6', '#818E86', '#CFD0C4', '#525E57')
RED_TILE = tones('#E5A08A', '#BC634E', '#A24D3B', '#7B382D', '#542B24', '#92503F', '#492923')
SKYLIGHT = tones('#FFFFF5', '#E8EEEE', '#CCD9DB', '#A3B8BD', '#728C94', '#91A7AD', '#4B6872')
ROOF_GRAVEL = rgb('#777C6E')
WOOD, IRON = rgb('#634A35'), rgb('#36413C')
WALLS = [rgb(c) for c in ('#E3D5B7', '#E4C29F', '#D0D4B9', '#D1BCAB', '#C4CFCD', '#EDE5D1')]
GROUND = {k: rgb(v) for k, v in {
    'pave': '#D4CABB', 'joint': '#B8AF9F', 'square': '#E5DCC7',
    'cobble': '#BFB39E', 'cobble_joint': '#9E927E', 'rose': '#CFB4A2',
    'grass': '#91AD69', 'grass_light': '#B2C48B', 'rock': '#A99B82',
    'flower': '#C38C8E', 'path': '#DBC9AA',
}.items()}


def windows(material, height, *args, **kwargs):
    framed = framed_windows(material,height,*args,**kwargs)
    courses = stone_courses(material,5,12)
    def pattern(u,v,lit):
        return framed(u,v,lit) or (courses(u,v,lit) if material in (STONE,CONCRETE,BRICK) else None)
    return pattern


def cross(s, i, j, z, height=7):
    seg(s, P(s,i,j,z), P(s,i,j,z+height), GOLD['dark'], 2)
    seg(s, P(s,i-.22,j,z+height*.65), P(s,i+.22,j,z+height*.65), GOLD['hi'])


def opening(u, v, centre, bottom, half, spring, material, lit, grille=False):
    """Bounded round arch with its dressed frame; v is measured from the actual wall foot."""
    if v < bottom:
        return None
    inner=arch_opening(u,v-bottom,centre,half,spring,IRON)
    if inner:
        return material['mid'] if grille and (int(u)%3==0 or int(v)%4==0) else IRON
    return arch_opening(u,v-bottom+.7,centre,half+1,spring,material['hi' if lit else 'mid'])


def nave_roof(s, i, j, wi, wj, base, rise, roof=RED_TILE, wall=MARBLE):
    """Two gabled roof slopes along j; no hip running across the nave's gable end."""
    t,r,b,l=corners(s,i,j,wi,wj,base)
    rear,front=P(s,i+wi/2,j,base+rise),P(s,i+wi/2,j+wj,base+rise)
    poly(s,[t,r,rear],lambda x,y:wall['mid'])
    for pts,key in (([t,l,front,rear],'lit'),([rear,front,b,r],'dark')):
        poly(s,pts,lambda x,y,key=key:roof['line'] if int(y)%3==0 else
             roof['hi'] if (int(x)+int(y)//3*2)%13==0 else roof[key])
    poly(s,[l,b,front],lambda x,y:wall['lit'])
    for a,b in ((rear,front),(l,front),(front,b)):
        seg(s,a,b,roof['hi'] if a==rear else wall['hi'])


def metal_roof(s, ci, cj, radius, base, rise, conical=False):
    """Lead standing seams follow meridians; no horizontal stripes across a dome."""
    profile=[(0,1),(1,0)] if conical else [(math.sin(n*math.pi/12),math.cos(n*math.pi/12)) for n in range(7)]
    faces,seams=[],[]
    for (t,r),(nt,nr) in zip(profile,profile[1:]):
        for n in range(24):
            a,b=n*math.tau/24,(n+1)*math.tau/24
            points=[(ci+rr*radius*math.cos(angle),cj+rr*radius*math.sin(angle),base+tt*rise)
                    for tt,rr,angle in ((t,r,a),(t,r,b),(nt,nr,b),(nt,nr,a))]
            light=math.sin((a+b)/2)-.4*math.cos((a+b)/2)+t*.4
            key='hi' if light>1 else 'lit' if light>.35 else 'mid' if light>-.35 else 'dark'
            faces.append((sum(p[0]+p[1] for p in points),n,points,key))
            if n%2==0 and ((math.cos(a)+math.sin(a))*(1-t)/radius+8*t/rise)>0:
                seams.append((points[0],points[3],key))
    for _,n,points,key in sorted(faces,key=lambda f:f[0]):
        pts=[P(s,*p) for p in points]
        poly(s,pts,lambda x,y,key=key:LEAD[key])
    for a,b,key in seams:seg(s,P(s,*a),P(s,*b),LEAD['line' if key in ('hi','lit') else 'deep'])


def townhouse(scene, i, j, wi=2.6, wj=3, floors=2, seed=0, z=0):
    """Pristina plaster houses: timber oriels, deep tiled eaves and occasional iron guards."""
    wall, H = palette_of(WALLS[seed%len(WALLS)]), floors*12+2
    base = windows(wall,H,10,12,width=6)
    def pattern(u,v,lit):
        c,level = int(u)%10,int(v)%12
        if v<10 and 2<=c<=8:
            if c in (2,8) or int(v)==9:return STONE['lit' if lit else 'dark']
            return WOOD if seed%3 else GLASS['dark']
        if seed%2==0 and v>10 and (c==0 or level==0):return WOOD
        return base(u,v,lit)
    def draw(s):
        block(s,i,j,wi,wj,H,wall,pattern,z=z)
        band(s,i,j,wi,wj,z+1,STONE,2)
        band(s,i,j,wi,wj,z+H-1,WHITE,2)
        if seed%4==0 and floors>1:
            # A supported timber bay, rather than an unattached front rectangle.
            block(s,i+.5,j+wj,wi-1,.45,11,wall,
                  windows(wall,11,7,12,width=5),z=z+13)
            for off in (.55,wi-.6):
                seg(s,P(s,i+off,j+wj+.4,z+13),P(s,i+off,j+wj,z+8),WOOD)
            hip_roof(s,i+.4,j+wj-.1,wi-.8,.8,z+24,3,DARK_CLAY)
        hip_roof(s,i-.22,j-.22,wi+.44,wj+.44,z+H,8+seed%3,
                 DARK_CLAY if seed%3 else CLAY)
        block(s,i+.4,j+.6,.42,.5,7,STONE,stone_courses(STONE,3,6),z=z+H+4)
        band(s,i+.4,j+.6,.42,.5,z+H+10,DARK_CLAY,2)
        if seed%4==1 and floors>1:
            block(s,i+.6,j+wj,1.3,.45,1.5,STONE,z=z+13)
            for k in range(6):seg(s,P(s,i+.65+k*.22,j+wj+.4,z+14),P(s,i+.65+k*.22,j+wj+.4,z+19),IRON)
            seg(s,P(s,i+.6,j+wj+.4,z+19),P(s,i+1.9,j+wj+.4,z+19),IRON)
    scene.add(i+j+wi+wj+1,draw)


def emin_gjiku(scene, i, j, z=0):
    """Two unequal hipped wings, recessed courtyard stair and the glazed SE loggia."""
    def draw(s):
        H=36
        def joinery(u,v,lit,loggia=False):
            level=v%18
            c=u%(8 if loggia else 9)
            trim=WOOD
            if loggia and v>4 and 4<level<15:
                if int(c) in (0,4,7) or int(level) in (5,9,14):return trim
                return SKYLIGHT['mid' if lit else 'deep']
            if not loggia and 2<=c<=7 and 4<=level<=15:
                if int(c) in (2,7) or int(level) in (4,9,14):return trim
                return SKYLIGHT['lit' if lit else 'dark']
            if loggia and int(level)==15 and int(c)%4==0:return WOOD
            if v<3:return STONE['lit' if lit else 'dark']
            return None
        # The family house has a concave courtyard front, not a single large
        # pyramid roof. These separate hip ridges meet at an actual L-shaped plan.
        block(s,i,j,3.6,8,H,WHITE,joinery,z=z)
        band(s,i,j,3.6,8,z+1,WHITE,2)
        hip_roof(s,i-.25,j-.25,4.1,8.5,z+H,12,DARK_CLAY)
        block(s,i+3.6,j,5.4,4.3,H,WHITE,joinery,z=z)
        block(s,i+4.8,j+4.3,4.2,2.4,H,WHITE,
              lambda u,v,lit:joinery(u,v,lit,loggia=True),z=z)
        # Smooth white floor bands and scalloped white valances frame the brown
        # loggia glazing, rather than timber stripes crossing every plaster wall.
        band(s,i+4.8,j+4.3,4.2,2.4,z+17,WHITE,3)
        for level in (15,33):
            for k in range(8):
                a=i+4.9+k*.5
                poly(s,[P(s,a,j+6.73,z+level+2),P(s,a+.5,j+6.73,z+level+2),
                        P(s,a+.25,j+6.73,z+level)],lambda x,y:WHITE['lit'])
        hip_roof(s,i+3.35,j-.25,5.9,7.2,z+H,12,DARK_CLAY)
        # Courtyard entrance is recessed between the solid wing and glazed wing.
        block(s,i+3.6,j+4.3,1.2,.15,14,WHITE,
              lambda u,v,lit:WOOD if 1<u<8 and 1<v<12 else None,z=z+4)
        for k in range(6):block(s,i+3.6,j+4.5+k*.42,1.2,.45,7-k,STONE,z=z)
        for b in (j+4.5,j+6.8):
            seg(s,P(s,i+4.7,b,z+5),P(s,i+4.7,b,z+12),WOOD)
        seg(s,P(s,i+4.7,j+4.5,z+12),P(s,i+4.7,j+6.8,z+7),WOOD)
        for a,b in ((i+1.2,j+2),(i+6.7,j+1.2)):
            block(s,a,b,.42,.5,7,STONE,stone_courses(STONE,3,6),z=z+H+7)
            band(s,a,b,.42,.5,z+H+13,DARK_CLAY,2)
        block(s,i-.5,j+9,10,.25,3,WHITE,z=z)
        block(s,i-.5,j+7.5,.25,1.7,3,WHITE,z=z)
    scene.add(i+j+21,draw)


def imperial_mosque(scene, i, j, z=0):
    """One main lead dome, three NW porch crowns and one western balconied minaret."""
    def draw(s):
        # NW portico (-i face). Its arches are behind the hall in this view;
        # do not put a second, invented entrance on either visible southern wall.
        for b in (j+1.2,j+3.4,j+5.6,j+7.8):
            cylinder(s,i+.35,b,.18,.18,z,14,STONE,segments=8)
        for b in (j+2.3,j+4.5,j+6.7):
            # Extruded voussoir rings on the hidden NW front, with open intrados.
            for n in range(12):
                a0,a1=n*math.pi/12,(n+1)*math.pi/12
                outer=[(b+1.1*math.cos(t),z+14+7*math.sin(t)) for t in (a0,a1)]
                inner=[(b+.94*math.cos(t),z+14+5.4*math.sin(t)) for t in (a0,a1)]
                poly(s,[P(s,i+.2,u,v) for u,v in outer+inner[::-1]],
                     lambda x,y:STONE['mid'] if (x+y)%4 else STONE['line'])
                poly(s,[P(s,i+.2,u,v) for u,v in inner]+[P(s,i+1.9,u,v) for u,v in inner[::-1]],
                     lambda x,y:STONE['deep'])
            block(s,i+.2,b-1.0,2.0,2.0,3,STONE,z=z+18)
            metal_roof(s,i+1.2,b,1.1,z+21,9)
        H=35
        def hall_windows(u,v,lit):
            # Small dark grilles in dressed arches, rather than the previous
            # repeating blue domestic sash windows. The upper row is smaller.
            c=(int(u)//18)*18+9
            for bottom,half,spring in ((4,3.4,9),(23,2.3,4)):
                col=opening(u,v,c,bottom,half,spring,STONE,lit,grille=True)
                if col:return col
            return stone_courses(STONE,5,13)(u,v,lit)
        block(s,i+2,j+1,7,7,H,STONE,
              hall_windows,z=z)
        for zz in (1,18,H-1):band(s,i+2,j+1,7,7,z+zz,STONE,2)
        cylinder(s,i+5.5,j+4.5,3.25,3.25,z+H,8,STONE,
                 windows(STONE,8,10,10,arched=True,width=4),segments=12)
        metal_roof(s,i+5.5,j+4.5,3.4,z+H+8,24)
        crescent(s,(i+5.5,j+4.5,z+H+32))
        # Western minaret is at -i,+j, not on the eastern corner.
        a,b=i+1,j+7.8
        block(s,a-.65,b-.65,1.3,1.3,13,STONE,stone_courses(STONE,4,9),z=z)
        cylinder(s,a,b,.55,.55,z+13,61,STONE,
                 lambda u,v,lit: STONE['line' if lit else 'deep'] if int(v)%6==0 else None,segments=12)
        revolve(s,a,b,.58,z+66,8,[(0,1),(.4,1.7),(1,1.9)],STONE,ribs=0)
        cylinder(s,a,b,1.1,1.1,z+74,4,STONE,segments=12)
        for n in range(12):
            t=n*math.tau/12
            seg(s,P(s,a+.95*math.cos(t),b+.95*math.sin(t),z+75),
                P(s,a+.95*math.cos(t),b+.95*math.sin(t),z+80),STONE['deep'])
        cylinder(s,a,b,.46,.46,z+78,13,STONE,segments=12)
        metal_roof(s,a,b,.58,z+91,19,conical=True)
        crescent(s,(a,b,z+110))
    scene.add(i+j+19,draw)


def sahat_kulla(scene, i, j, z=0):
    """Hexagonal stone shaft, open clock arcade, six pediments/medallions and a lead belfry."""
    def draw(s):
        ci,cj=i+1.7,j+1.7
        span=3.3*math.pi*4/6
        def shaft(u,v,lit):
            col=opening(u%span,v,span/2,52,1.0,4,STONE,lit)
            if col:return col
            return stone_courses(STONE,12,20)(u,v,lit)
        cylinder(s,ci,cj,1.65,1.65,z,65,STONE,shaft,segments=6)
        cylinder(s,ci,cj,1.75,1.75,z+64,2,WHITE,segments=6)
        def clock_arcade(u,v,lit):
            col=opening(u%span,v,span/2,1,2.1,10,BRICK,lit)
            if col:
                if col==IRON and v<5 and (int(u*2)%3==0 or int(v)==4):return LEAD['mid']
                return col
            return stone_courses(BRICK,3,8)(u,v,lit)
        cylinder(s,ci,cj,1.65,1.65,z+66,16,BRICK,clock_arcade,segments=6)
        # Pediments are on the hexagon's real faces. Rectangular-wall pediments
        # had floated off the shaft and omitted the circular inset medallions.
        faces=[]
        for n in range(6):
            a,b=(n+.5)*math.tau/6,(n+1.5)*math.tau/6
            va,vb=(ci+1.65*math.cos(a),cj+1.65*math.sin(a)),(ci+1.65*math.cos(b),cj+1.65*math.sin(b))
            faces.append((sum(va+vb),a,b,va,vb))
        for _,a,b,va,vb in sorted(faces):
            lit=math.sin((a+b)/2)-.5*math.cos((a+b)/2)>0
            mid=((va[0]+vb[0])/2,(va[1]+vb[1])/2)
            front=[P(s,*va,z+82),P(s,*vb,z+82),P(s,*mid,z+88)]
            poly(s,front,lambda x,y,lit=lit:BRICK['lit' if lit else 'dark'])
            for pa,pb in ((front[0],front[2]),(front[2],front[1])):seg(s,pa,pb,LEAD['dark'])
            def point(u,v):
                t=.5+u
                return P(s,va[0]+(vb[0]-va[0])*t,va[1]+(vb[1]-va[1])*t,z+v)
            ring=[point(.13*math.cos(t*math.tau/16),85+1.3*math.sin(t*math.tau/16)) for t in range(16)]
            poly(s,ring,lambda x,y:LEAD['mid'])
        def belfry(u,v,lit):
            local_span=1.7*math.pi*4/6
            col=opening(u%local_span,v,local_span/2,2,.85,6,BRICK,lit)
            return col or stone_courses(BRICK,3,8)(u,v,lit)
        cylinder(s,ci,cj,.85,.85,z+86,12,BRICK,belfry,segments=6)
        cylinder(s,ci,cj,1.02,1.02,z+97,2,BRICK,segments=6)
        revolve(s,ci,cj,1.15,z+99,5,[(0,1),(1,0)],LEAD,ribs=1,segments=6)
        seg(s,P(s,ci,cj,z+104),P(s,ci,cj,z+107),IRON)
        # The photographed finial is a small weather vane, not a national flag.
        poly(s,[P(s,ci,cj,z+107),P(s,ci+.36,cj,z+106),P(s,ci,cj,z+105)],lambda x,y:LEAD['dark'])
        for a,b in ((math.pi/2,5*math.pi/6),(-math.pi/6,math.pi/6),(math.pi/6,math.pi/2)):
            ax,ay=ci+1.65*math.cos(a),cj+1.65*math.sin(a)
            bx,by=ci+1.65*math.cos(b),cj+1.65*math.sin(b)
            def point(u,v):
                t=.5+u*.34
                return P(s,ax+(bx-ax)*t,ay+(by-ay)*t,z+76+v*5)
            ring=[point(math.cos(n*math.tau/32),math.sin(n*math.tau/32)) for n in range(32)]
            poly(s,ring,lambda x,y:IRON)
            for p,q in zip(ring,ring[1:]+ring[:1]):seg(s,p,q,WHITE['hi'])
            for n in range(12):
                t=n*math.tau/12
                seg(s,point(.76*math.cos(t),.76*math.sin(t)),point(.98*math.cos(t),.98*math.sin(t)),WHITE['hi'])
            seg(s,point(0,0),point(0,.7),WHITE['hi'])
            seg(s,point(0,0),point(.65,-.25),WHITE['hi'])
    scene.add(i+j+7,draw)


# The monument is a sculpture, so each filled cell is a genuinely extruded steel prism.
# Open counters in B/O/R reveal the ground; no flat text texture or painted background.
LETTER_CELLS = {
    'N': ('10001','11001','11001','10101','10011','10011','10001'),
    'E': ('11111','10000','10000','11110','10000','10000','11111'),
    'W': ('10001','10001','10001','10101','10101','11011','10001'),
    'B': ('11110','10001','10001','11110','10001','10001','11110'),
    'O': ('01110','10001','10001','10001','10001','10001','01110'),
    'R': ('11110','10001','10001','11110','10100','10010','10001'),
}


def newborn(scene, i, j, z=0):
    """Seven freestanding DIN-like steel capitals in the documented original 2008 yellow."""
    def draw(s):
        block(s,i-.3,j-.25,15.5,1.2,1.5,STONE,z=z)
        for n,letter in enumerate('NEWBORN'):
            cells=LETTER_CELLS[letter]
            for row,line in enumerate(cells):
                for col,filled in enumerate(line):
                    if filled!='1':continue
                    a=i+n*2.15+col*.36
                    low=z+1.5+(6-row)*2.2
                    top=low+2.2
                    # Only external contours get seams. Joining every pixel cell
                    # would turn a smooth steel letter into a striped brick wall.
                    front=[P(s,a,j+.48,low),P(s,a+.36,j+.48,low),
                           P(s,a+.36,j+.48,top),P(s,a,j+.48,top)]
                    poly(s,front,lambda x,y:YELLOW['lit'])
                    if col==4 or line[col+1]=='0':
                        poly(s,[P(s,a+.36,j,low),P(s,a+.36,j+.48,low),
                                P(s,a+.36,j+.48,top),P(s,a+.36,j,top)],lambda x,y:YELLOW['dark'])
                        seg(s,front[1],front[2],YELLOW['outline'])
                    if row==0 or cells[row-1][col]=='0':
                        poly(s,list(corners(s,a,j,.36,.48,top)),lambda x,y:YELLOW['hi'])
                        seg(s,front[2],front[3],YELLOW['mid'])
                    if col==0 or line[col-1]=='0':seg(s,front[0],front[3],YELLOW['deep'])
                    if row==6 or cells[row+1][col]=='0':seg(s,front[0],front[1],YELLOW['dark'])
    scene.add(i+j+17,draw)


# The two dominant reading/atrium domes and unequal surrounding roof volumes are
# follow aerial photographs. Small skylights are compressed onto this plan;
# their total follows the conservation paper's 99, not eleven invented 3×3 groups.
LIBRARY_MODULES = (
    (1.4,5.3,4.2,4.2,40,1.75), (6.0,1.8,4.5,4.5,44,1.9),
    (1.0,1.0,2.2,2.2,33,.88), (3.4,1.0,2.1,2.1,36,.82),
    (1.0,3.4,2.2,1.6,28,.65), (6.0,7.0,2.2,2.2,31,.9),
    (8.5,7.0,2.2,2.2,34,.9), (3.2,9.8,2.2,2.2,29,.88),
    (8.0,9.6,2.2,2.2,30,.9), (10.6,3.7,1.4,1.6,28,.5),
)


def national_library(scene, i, j, z=0):
    """Two dominant geodesic crowns, unequal smaller lights and external metal diamonds."""
    def draw(s):
        def dome(ci,cj,r,base):
            # A convex triangulated hemisphere. The previous horizontal tiered
            # profile produced pointed/conical caps instead of acrylic geodesics.
            faces=[]
            segments=12
            for row in range(4):
                a,b=row*math.pi/8,(row+1)*math.pi/8
                for n in range(segments):
                    t0,t1=n*math.tau/segments,(n+1)*math.tau/segments
                    vertices=[(ci+r*math.cos(h)*math.cos(t),cj+r*math.cos(h)*math.sin(t),
                               base+(r*8.5+1)*math.sin(h)) for h,t in ((a,t0),(a,t1),(b,t1),(b,t0))]
                    for ids in (((0,1,2),(0,2,3)) if (n+row)%2 else ((0,1,3),(1,2,3))):
                        pts=[vertices[k] for k in ids]
                        light=.55+.25*math.cos((a+b)/2)+.22*(math.sin((t0+t1)/2)-.4*math.cos((t0+t1)/2))
                        key='hi' if light>.85 else 'lit' if light>.66 else 'mid' if light>.45 else 'dark'
                        faces.append((sum(p[0]+p[1] for p in pts),pts,key))
            for _,pts,key in sorted(faces,key=lambda f:f[0]):
                projected=[P(s,*p) for p in pts]
                poly(s,projected,lambda x,y,key=key:SKYLIGHT[key])
                if r>.6:
                    for a,b in zip(projected,projected[1:]+projected[:1]):seg(s,a,b,SKYLIGHT['line'])
        def metal_net(ai,bj,w,d,base,H):
            # Project the metal members on planes just outside both real walls.
            # Only their endpoints are clipped; nothing is painted onto a roof.
            for lit,length in ((True,w),(False,d)):
                span=length*8
                def at(u,v):
                    return P(s,ai+u/8 if lit else ai+w+.08,
                             bj+d+.08 if lit else bj+d-u/8,base+v)
                for slope in (-1,1):
                    for c in range(-math.ceil(span),math.ceil(H+span),7):
                        hits=[]
                        for u in (0,span):
                            v=slope*u+c
                            if 0<=v<=H:hits.append((u,v))
                        for v in (0,H):
                            u=(v-c)/slope
                            if 0<=u<=span:hits.append((u,v))
                        if len(hits)>=2:seg(s,at(*hits[0]),at(*hits[-1]),MESH['lit' if lit else 'dark'])
        # Central circulation base; high reading rooms stand on exposed piers.
        block(s,i+.3,j+.3,11.4,11.4,9,CONCRETE,
              lambda u,v,lit:IRON if 1<v<7 and int(u)%14>2 else None,z=z)
        modules=list(LIBRARY_MODULES)
        candidates=[]
        for row in range(18):
            for col in range(18):
                a,b=.05+col*.65,.05+row*.65
                if any(a+.55>u-.08 and a<u+w+.08 and b+.55>v-.08 and b<v+d+.08
                       for u,v,w,d,H,r in modules):continue
                candidates.append((a,b))
        # The miniature leaves roof terraces between lights. Its precise small-
        # light spacing is illustrative; the two main crowns carry the silhouette.
        chosen=sorted(candidates,key=lambda p:iso.h01(*p,9491))[:89]
        for a,b in chosen:
            modules.append((a,b,.55,.55,16+int(iso.h01(a,b,9492)*3),.20))
        assert len(modules)==99
        for a,b,w,d,H,r in sorted(modules,key=lambda m:m[0]+m[1]+m[2]+m[3]):
            ai,bj=i+a,j+b
            if w>1:
                for u,v in ((.15,.15),(w-.35,.15),(.15,d-.35),(w-.35,d-.35)):
                    block(s,ai+u,bj+v,.22,.22,14,CONCRETE,z=z)
            def glazing(u,v,lit):
                if int(v)%13 in (0,1):return CONCRETE['lit' if lit else 'dark']
                if lit and int(v)%13==11:return SKYLIGHT['deep']
                return IRON if int(u)%11>1 else CONCRETE['mid']
            block(s,ai,bj,w,d,H-12,CONCRETE,glazing,z=z+12)
            if w>1:metal_net(ai,bj,w,d,z+12,H-12)
            band(s,ai,bj,w,d,z+H-1,MESH,1)
            poly(s,list(corners(s,ai+.04,bj+.04,w-.08,d-.08,z+H+.1)),
                 lambda x,y:ROOF_GRAVEL)
            dome(ai+w/2,bj+d/2,r,z+H+.3)
        # Public entry on the west, locally snapped to the SW display face.
        block(s,i+2.3,j+11.7,2.3,.1,9,CONCRETE,
              lambda u,v,lit:IRON if 1<u<17 and 1<v<8 else None,z=z+2)
        for k in range(5):block(s,i+2,j+11.8+k*.25,2.9,.3,5-k,STONE,z=z)
    scene.add(i+j+27,draw)


def mother_teresa(scene, i, j, z=0):
    """White basilica with its photographed front shown by an explicit local 180° turn.

    Real entrance NNE / apse SSW; here entrance +j (SW), apse -j (NE).
    Campaniles flank the transept, inset from the apse, outside both aisles.
    Geographic SITES placement stays north-up.
    """
    W,D=8,15
    def draw(s):
        # Paving continues through the porch; the study's grass must not appear
        # inside the entrance opening.
        poly(s,list(corners(s,i+1.9,j+D,4.2,1.5,z+1)),lambda x,y:MARBLE['mid'])
        def marble(u,v,lit):
            if int(v)%7==0:return MARBLE['line']
            return None
        def dial(a,b,base,lit=True):
            def point(u,v):return P(s,a+u/8 if lit else a,b if lit else b-u/8,base+v)
            ring=[point(4*math.cos(n*math.tau/32),4*math.sin(n*math.tau/32)) for n in range(32)]
            poly(s,ring,lambda x,y:MARBLE['lit' if lit else 'mid'])
            for p,q in zip(ring,ring[1:]+ring[:1]):seg(s,p,q,MARBLE['deep'])
            for n in range(12):
                t=n*math.tau/12
                seg(s,point(3*math.cos(t),3*math.sin(t)),point(3.7*math.cos(t),3.7*math.sin(t)),IRON)
            seg(s,point(0,0),point(0,2.8),IRON)
            seg(s,point(0,0),point(2,-1),IRON)
        # Tower stages are individually modelled: two lower lancets, a solid clock
        # storey, one large opening above it, then paired openings at the crown.
        def tower(a):
            b=j+3.5
            def shaft(u,v,lit):
                centre=7.6 if lit else 8
                for bottom in (25,43):
                    col=opening(u,v,centre,bottom,2.6,7,MARBLE,lit)
                    if col:return col
                if v<21:
                    col=opening(u,v,centre,4,3,10,MARBLE,lit)
                    if col:return MARBLE['mid'] if col==IRON else col
                return marble(u,v,lit)
            block(s,a,b,1.9,2,70,MARBLE,shaft,z=z)
            for level in (1,22,39,54,69):band(s,a,b,1.9,2,z+level,MARBLE,2)
            dial(a+.95,b+2.03,z+61)
            dial(a+1.93,b+1,z+61,lit=False)
            for base,height,paired in ((71,12,False),(86,14,True)):
                def bells(u,v,lit,paired=paired):
                    for c in ((3.8,11.4) if paired else (7.6,)):
                        col=opening(u,v,c,2,2 if paired else 3,7,MARBLE,lit)
                        if col:return col
                    return marble(u,v,lit)
                block(s,a,b,1.9,2,height,MARBLE,bells,z=z+base)
                for off in (0,1.7):block(s,a+off,b+1.95,.2,.2,height,MARBLE,z=z+base)
                band(s,a-.08,b-.08,2.06,2.16,z+base+height,MARBLE,2)
            hip_roof(s,a-.18,b-.18,2.26,2.36,z+102,5,LEAD)
            cross(s,a+.95,b+1,z+107,6)
        # Both towers flank the transept, a quarter of the way in from the
        # rounded apse. Their centres sit outside the nave/aisle footprint.
        tower(i-1.5)
        for a in (i-1.5,i+6.1):
            block(s,a,j+1.1,3.4,3.1,27,MARBLE,marble,z=z)
            hip_roof(s,a-.1,j+1,3.6,3.3,z+27,12,RED_TILE)
        # Rear apse and the basilica's long aisles. White marble has fine horizontal
        # joints; the previous large ashlar blocks made this modern church medieval.
        cylinder(s,i+4,j+.4,1.9,1.5,z,31,MARBLE,marble,segments=24)
        revolve(s,i+4,j+.4,2,z+31,9,[(0,1),(1,0)],RED_TILE,ribs=0)
        def lower(u,v,lit):
            if lit:
                for c in (8,32,56):
                    col=opening(u,v,c,2,3.8,14,MARBLE,lit)
                    if col:return (GOLD['dark'] if int(u)%4==0 or int(v)%5==0 else WOOD) if col==IRON else col
            else:
                c=(int(u)//13)*13+6.5
                col=opening(u,v,c,5,3,13,MARBLE,lit,grille=True)
                if col:return col
            if int(u)%13 in (0,1):return MARBLE['hi' if lit else 'mid']
            return marble(u,v,lit)
        block(s,i,j+1,W,D-1,27,MARBLE,lower,z=z)
        band(s,i,j+1,W,D-1,z+1,MARBLE,2)
        band(s,i,j+1,W,D-1,z+26,MARBLE,2)
        # Separate lean-to aisle roofs, leaving a continuous raised clerestory.
        for left in (True,False):
            a,b=(i-.1,i+1.9) if left else (i+6.1,i+8.1)
            za,zb=(z+27,z+39) if left else (z+39,z+27)
            pts=[P(s,a,j+.9,za),P(s,a,j+D+.1,za),P(s,b,j+D+.1,zb),P(s,b,j+.9,zb)]
            poly(s,pts,lambda x,y,left=left:RED_TILE['line'] if int(y)%3==0 else RED_TILE['lit' if left else 'dark'])
            seg(s,pts[1],pts[2],RED_TILE['hi'])
        def clerestory(u,v,lit):
            if not lit:
                c=(int(u)//7)*7+3.5
                col=opening(u,v,c,10,2.1,7,MARBLE,lit,grille=True)
                if col:return col
            return marble(u,v,lit)
        block(s,i+1.9,j+1,4.2,D-1,24,MARBLE,clerestory,z=z+27)
        band(s,i+1.9,j+1,4.2,D-1,z+50,MARBLE,1)
        nave_roof(s,i+1.8,j+.9,4.4,D-.8,z+51,13)
        # The near campanile covers the aisle edge; the far one was painted
        # before the nave so its lower shaft cannot leak over the roof.
        tower(i+7.6)
        # NNE entrance locally turned SW: a real open barrel-arched portico, not
        # a painted black doorway. Its carved door is on the recessed rear wall.
        ci,pj=i+4,j+D+1.2
        for a in (i+1.9,i+5.65):
            block(s,a,j+D+.1,.45,1.1,23,MARBLE,marble,z=z)
            band(s,a-.05,j+D+.1,.55,1.1,z+21,MARBLE,2)
        for n in range(20):
            a0,a1=n*math.pi/20,(n+1)*math.pi/20
            outer=[(ci+1.9*math.cos(t),z+21+11*math.sin(t)) for t in (a0,a1)]
            inner=[(ci+1.47*math.cos(t),z+21+8.8*math.sin(t)) for t in (a0,a1)]
            for jj,tone in ((j+D+.1,MARBLE['mid']),(pj,MARBLE['lit'])):
                poly(s,[P(s,u,jj,v) for u,v in outer+inner[::-1]],lambda x,y,tone=tone:tone)
                poly(s,[P(s,u,jj,v) for u,v in outer]+
                     [P(s,u,jj,z+32) for u,v in outer[::-1]],lambda x,y,tone=tone:tone)
            poly(s,[P(s,u,pj,v) for u,v in inner]+[P(s,u,j+D+.1,v) for u,v in inner[::-1]],lambda x,y:MARBLE['dark'])
            poly(s,[P(s,u,pj,v) for u,v in outer]+[P(s,u,j+D+.1,v) for u,v in outer[::-1]],lambda x,y:MARBLE['mid'])
        nave_roof(s,i+1.7,j+D-.1,4.6,1.6,z+32,10)
        # Frieze follows the gable slope; the rose occupies the upper nave gable.
        for a in range(11):
            u=i+1.9+a*.42
            h=z+51+13*(1-abs((u-i-4)/2.2))-2
            seg(s,P(s,u,j+D+.13,h),P(s,u,j+D+.13,h-2),MARBLE['deep'])
        def rose(u,v):return P(s,i+4+u/8,j+D+.14,z+56+v)
        ring=[rose(4.5*math.cos(n*math.tau/32),4.5*math.sin(n*math.tau/32)) for n in range(32)]
        poly(s,ring,lambda x,y:SKYLIGHT['deep'])
        for a,b in zip(ring,ring[1:]+ring[:1]):seg(s,a,b,MARBLE['hi'])
        for n in range(8):
            t=n*math.tau/8
            seg(s,rose(0,0),rose(4*math.cos(t),4*math.sin(t)),MARBLE['lit'])
        for k in range(6):block(s,i+1.5,j+D+1.5+k*.3,5,.35,6-k,MARBLE,z=z)
        cross(s,i+4,j+D+.1,z+64,5)
    scene.add(i+j+W+D+8,draw)


def main():
    for name,builder,(wi,wj),_,_,z in SITES:
        print(preview([lambda s,b=builder,z=z:b(s,4,4,z=z)],'pristina-'+name,
                      size=(340,320),origin=(155,135),tiles=25))
    print(preview([lambda s:townhouse(s,4,4,seed=0),
                   lambda s:townhouse(s,9,4,floors=3,seed=1),
                   lambda s:townhouse(s,7,10,floors=1,seed=3)],'pristina-houses',
                  size=(240,190),origin=(120,45),tiles=19))


# (name, builder, footprint, real (longitude, latitude), scene anchor, elevation)
SITES = [
    ('emin-gjiku', emin_gjiku, (8.8,9), (21.16819,42.66869), (620,120), 8),
    ('imperial-mosque', imperial_mosque, (9,8), (21.1670,42.6670), (480,215), 8),
    ('clock-tower', sahat_kulla, (3.4,3.4), (21.16726,42.66674), (590,270), 8),
    ('newborn', newborn, (15,1), (21.158209,42.660539), (130,270), 0),
    ('national-library', national_library, (12,12), (21.16222,42.65722), (430,405), 0),
    ('mother-teresa', mother_teresa, (8,19), (21.15944,42.65639), (220,460), 0),
]


if __name__ == '__main__':
    main()
