"""Sarajevo's Ottoman, Habsburg and modern landmarks in projected (i, j, z).

Research, two-source coordinates, settings and orientation decisions: DEVELOPMENT_PLAN.md.
Run this module for seven isolated 4× landmark studies and the local house study.
"""
import math
from pathlib import Path

import iso
from iso import rgb, h01
from landmarks_paris import P, seg, poly, corners, preview
from landmarks_iberia import hip_roof, stone_courses, arch_opening, palette_of, tones
from landmarks_italy import ellipse
from landmarks_slovakia import block, band, pediment
from landmarks_slovenia import windows, revolve, statue, DOME
from landmarks_croatia import surface

STONE = tones('#F7F0DF', '#DFD4BA', '#C8BA9E', '#A39478', '#73664F', '#B7A788', '#493E2E')
WHITE = tones('#FFFAED', '#EEE7D4', '#D8CEB7', '#B7AB92', '#83745F', '#C9BBA0', '#514432')
OCHRE = tones('#F8D7A1', '#E0B576', '#C89A61', '#A77949', '#754F30', '#B88A53', '#4B321E')
RED = tones('#DDA58B', '#BC7A60', '#A3644C', '#7F4B39', '#593227', '#955840', '#42271E')
CLAY = tones('#EBA77A', '#C77950', '#AE5F3D', '#87462F', '#5B3021', '#A25436', '#49271C')
LEAD = tones('#B9C1B5', '#8E9B8E', '#778576', '#5D695E', '#3F4B42', '#6B786B', '#29372F')
CATHEDRAL_ROOF = tones('#AEC6B3', '#709783', '#547B68', '#3B5D4F', '#294438', '#5F826F', '#21362E')
COPPER = tones('#BED8C7', '#88B6A0', '#6E9D87', '#4D7766', '#345348', '#608B77', '#263F35')
WOOD = tones('#DBAA79', '#AB764E', '#925F3D', '#71462E', '#4E3021', '#825134', '#3B261D')
BLUE = tones('#CAE3E6', '#82B0BD', '#6596AA', '#426E88', '#284B65', '#537E96', '#1C344D')
STEEL = tones('#F4F4E7', '#CFD8D5', '#AEBFBE', '#859C9C', '#586F75', '#99ADAF', '#344D59')
GOLD = tones('#FFF0B0', '#DDC36F', '#C2A24E', '#977933', '#655023', '#AD8B3D', '#4C3D20')
ROCK = tones('#D8CFB7', '#B5A68C', '#9B8C72', '#7B6D56', '#594F3E', '#8E7E65', '#3E372C')
WALLS = [rgb(c) for c in ('#EEE3CA', '#DBBD8C', '#CFABA0', '#C5CBB5', '#E5CEAA', '#B9C6C0')]
IRON, DARK_GLASS = rgb('#343B3B'), rgb('#293D48')
WATER = (rgb('#648E89'), rgb('#4B746F'), rgb('#CBE1D5'))
GROUND = {k: rgb(v) for k, v in {
    'square': '#D5C9AF', 'square_joint': '#B9AC94', 'cobble': '#B6A994', 'cobble_joint': '#958A79',
    'garden': '#91AE65', 'garden_light': '#B6C585',
}.items()}


def cylinder(s, ci, cj, ri, rj, base, height, material=STONE, pattern=None, segments=32):
    """Polygonal prism, including the kiosk's actual eight flat facets."""
    faces = []
    for n in range(segments):
        a, b = (n+.5)*math.tau/segments, (n+1.5)*math.tau/segments
        va, vb = (ci+ri*math.cos(a), cj+rj*math.sin(a)), (ci+ri*math.cos(b), cj+rj*math.sin(b))
        faces.append((sum(va+vb), n, va, vb, math.sin((a+b)/2)-.5*math.cos((a+b)/2) > 0))
    for _, n, va, vb, lit in sorted(faces):
        pa, pb = P(s, *va, base), P(s, *vb, base)
        def color(x, y, pa=pa, pb=pb, lit=lit, n=n):
            dx = pb[0]-pa[0]
            t = min(1, max(0, (x-pa[0])/dx)) if abs(dx) > .01 else .5
            u, v = (n+t)*(ri+rj)*math.pi*4/segments, pa[1]+t*(pb[1]-pa[1])-y
            return (pattern(u, v, lit) if pattern else None) or material['lit' if lit else 'dark']
        poly(s, [pa, pb, (pb[0], pb[1]-height), (pa[0], pa[1]-height)], color)
        seg(s, pa, (pa[0], pa[1]-height), material['line' if lit else 'deep'])
    poly(s, [P(s, ci+ri*math.cos((n+.5)*math.tau/segments),
                   cj+rj*math.sin((n+.5)*math.tau/segments), base+height) for n in range(segments)],
         lambda x, y: material['mid'])


def wall_edge(s, a, b, base, height, material, pattern=None, lit=True):
    """An arbitrarily oriented vertical 3D wall; u follows its projected edge, v is height."""
    pa, pb = P(s, *a, base), P(s, *b, base)
    if pb[0] < pa[0]:
        pa, pb = pb, pa
    if abs(pb[0]-pa[0]) < .01:
        seg(s, pa, (pa[0], pa[1]-height), material['outline'])
        return  # a north/south wall is edge-on in the north-up projection
    slope = (pb[1]-pa[1])/(pb[0]-pa[0])
    pts = [pa, pb, (pb[0], pb[1]-height), (pa[0], pa[1]-height)]
    joints = stone_courses(material, 4, 11)
    for x, y in iso.polygon_pixels(pts):
        u = x-pa[0]
        v = pa[1]+u*slope-y
        s.put(x, y, (pattern(u, v, lit) if pattern else joints(u, v, lit)) or material['lit' if lit else 'dark'])
    for p, q in zip(pts, pts[1:]+pts[:1]):
        seg(s, p, q, material['outline'])


def crescent(s, position):
    i, j, z = position
    x, y = P(s, i, j, z)
    seg(s, (x, y), (x, y-4), GOLD['dark'])
    for dx, dy in ((1, -4), (0, -5), (-1, -6), (-1, -7), (0, -8), (1, -8)):
        s.put(x+dx, y+dy, GOLD['lit'])


def dome(s, i, j, r, base, rise, material=LEAD):
    faces = []
    for (t, radius), (nt, nr) in zip(DOME, DOME[1:]):
        for n in range(32):
            a, b = n*math.tau/32, (n+1)*math.tau/32
            pts = [P(s, i+rr*r*math.cos(ang), j+rr*r*math.sin(ang), base+tt*rise)
                   for tt, rr, ang in ((t,radius,a),(t,radius,b),(nt,nr,b),(nt,nr,a))]
            light = math.sin((a+b)/2)-.5*math.cos((a+b)/2)
            tone = 'hi' if light > .9 else 'lit' if light > .15 else 'mid' if light > -.4 else 'dark'
            faces.append((math.cos(a)+math.sin(a)+math.cos(b)+math.sin(b), pts, tone, n))
    for _, pts, tone, n in sorted(faces, key=lambda f:f[0]):
        poly(s, pts, lambda x,y,tone=tone: material[tone])
        if n % 4 == 0:
            seg(s,pts[0],pts[3],material['mid' if tone in ('hi','lit') else 'deep'])
    crescent(s, (i, j, base+rise))


def avaz(scene, i, j):
    """Twisted curtain wall, pale helical seams, round crown and one lattice aerial."""
    ci, cj, H = i+2.4, j+2.4, 132
    def draw(s):
        block(s, i-.5, j-.5, 5.8, 5.8, 9, WHITE, windows(WHITE, 9, 8, 8))
        cylinder(s, ci, cj, 2.2, 2.2, 8, 12, BLUE,
                 lambda u, v, lit: STEEL['lit' if lit else 'dark'] if int(u) % 8 == 0 else DARK_GLASS)
        # The corner ribbons turn with height, while the glass mullions stay on each panel.
        for z in range(20, H, 4):
            t0, t1 = (z-20)/(H-20), (z-16)/(H-20)
            angle0, angle1 = -.5+t0*.95, -.5+t1*.95
            faces = []
            for n in range(8):
                a, b = math.tau*n/8, math.tau*(n+1)/8
                pts = [P(s, ci+2.1*math.cos(aa+ang), cj+2.1*math.sin(aa+ang), zz)
                       for aa, ang, zz in ((a, angle0, z), (b, angle0, z),
                                          (b, angle1, z+4), (a, angle1, z+4))]
                light = math.sin((a+b)/2+angle0)-.5*math.cos((a+b)/2+angle0) > 0
                faces.append((sum(p[1] for p in pts), n, pts, light))
            for _, n, pts, light in sorted(faces):
                poly(s, pts, lambda x, y, lit=light, n=n, z=z:
                     BLUE['hi'] if lit and h01(x//3, z//8, n) < .12 else
                     BLUE['lit' if lit else 'dark'] if (int(x)+z//4) % 5 else BLUE['mid' if lit else 'deep'])
                seg(s, pts[0], pts[1], STEEL['dark'])
                seg(s, pts[0], pts[3], STEEL['hi' if light else 'mid'] if n % 2 == 0 else BLUE['deep'])
        cylinder(s, ci, cj, 1.65, 1.65, H, 12, STEEL,
                 lambda u, v, lit: DARK_GLASS if 2 < int(u) % 7 < 5 and v < 10 else None)
        ellipse(s, ci, cj, 1.8, 1.8, H+12, STEEL['lit'])
        for n in range(12):
            t = n*math.tau/12
            seg(s, P(s, ci+1.65*math.cos(t), cj+1.65*math.sin(t), H+12),
                P(s, ci+1.65*math.cos(t), cj+1.65*math.sin(t), H+17), STEEL['mid'])
        for dz in range(0, 24, 4):
            r = .35*(1-dz/27)
            for d in (-1, 1):
                seg(s, P(s, ci+d*r, cj, H+17+dz), P(s, ci-d*r*.8, cj, H+21+dz), STEEL['dark'])
        seg(s, P(s, ci, cj, H+17), P(s, ci, cj, H+47), RED['lit'])
    scene.add(i+j+10, draw)


def sebilj(scene, i, j):
    """Octagonal carved wooden kiosk, oversailing copper eaves, dome and two basins."""
    ci, cj = i+2.1, j+2.1
    def draw(s):
        for r, z in ((2.5, 0), (2.25, 2), (1.95, 4)):
            cylinder(s, ci, cj, r, r, z, 2, STONE, segments=8)
        def carving(u, v, lit):
            c = int(u) % 10
            if int(v) in (1, 2, 17, 18, 23, 24) or c in (0, 1, 9):
                return WOOD['hi' if lit else 'mid']
            if 4 < v < 17 and 2 < c < 8:
                return WOOD['deep'] if (int(u)+int(v)) % 3 == 0 else WOOD['line']
            if 20 < v < 24 and c in (3, 6):
                return DARK_GLASS
            return None
        cylinder(s, ci, cj, 1.55, 1.55, 6, 27, WOOD, carving, segments=8)
        cylinder(s, ci, cj, 2.35, 2.35, 32, 3, WOOD,
                 lambda u, v, lit: WOOD['hi' if lit else 'mid'] if int(u) % 3 else WOOD['deep'], segments=8)
        revolve(s, ci, cj, 2.45, 35, 5, [(0, 1), (1, .65)], COPPER, ribs=2, segments=8)
        dome(s, ci, cj, 1.65, 40, 11, COPPER)
        # Carved pendant dentils hang from the broad octagonal eave.
        for n in range(8):
            t0, t1 = (n+.5)*math.tau/8, (n+1.5)*math.tau/8
            a = P(s,ci+2.35*math.cos(t0),cj+2.35*math.sin(t0),32)
            b = P(s,ci+2.35*math.cos(t1),cj+2.35*math.sin(t1),32)
            if math.cos((t0+t1)/2)+math.sin((t0+t1)/2) < 0:
                continue
            for k in range(0, max(1,int(abs(b[0]-a[0]))), 3):
                t = k/max(1,abs(b[0]-a[0]))
                x,y=a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t
                seg(s,(x,y),(x,y+3),WOOD['lit'])
        for di, dj in ((0, 1.7), (1.7, 0)):
            cylinder(s, ci+di, cj+dj, .5, .5, 4, 4, WHITE, segments=12)
            ellipse(s, ci+di, cj+dj, .38, .38, 8, WATER[0])
            seg(s, P(s, ci+di*.85, cj+dj*.85, 13), P(s, ci+di, cj+dj, 12), GOLD['dark'], 2)
            seg(s, P(s, ci+di, cj+dj, 12), P(s, ci+di, cj+dj, 9), WATER[2])
    scene.add(i+j+9, draw)


def cathedral(scene, i, j):
    """South-facing twin towers and rose front, with the long nave extending north."""
    i, j = i+8, j+8
    A, B = (i+4, j+10), (i+10, j+4)
    NA, NB = (i-5, j+1), (i+1, j-5)
    joints = stone_courses(STONE, 3, 9)
    def draw(s):
        class CathedralView:
            # The actual front faces SSE. Turn the building 15°, while the city stays north-up.
            def screen(self, a, b, elevation=0):
                di, dj = a-i-7, b-j-7
                c, sn = math.cos(-math.pi/12), math.sin(-math.pi/12)
                return original.screen(i+7+di*c-dj*sn, j+7+di*sn+dj*c, elevation)

            def __getattr__(self, name):
                return getattr(original, name)

        original = s
        s = CathedralView()
        # Rounded northern apse behind the long nave, with a lower polygonal metal hood.
        cylinder(s,i-3.2,j-3.2,2.2,2.2,0,29,STONE,
                 windows(STONE,29,10,16,arched=True,width=5),segments=12)
        revolve(s,i-3.2,j-3.2,2.35,29,10,[(0,1),(1,0)],CATHEDRAL_ROOF,ribs=2,segments=12)
        def position(across, north, z=0):
            return i+7+across-north, j+7-across-north, z

        def side(u,v,lit):
            c = u % 8
            distance = abs(c-4)
            if 5 < v < 16+(2.2-distance)*1.7 and distance < 2.2:
                if distance > 1.3 or v < 6 or v > 15+(2.2-distance)*1.7:
                    return OCHRE['lit' if lit else 'dark']
                return DARK_GLASS
            if int(v) in (1,22):
                return OCHRE['lit' if lit else 'dark']
            return joints(u,v,lit)
        # Both aisle walls are real volumes. The west wall is the visible, lit flank:
        # drawing only the eastern wall made the old full-width roof appear to float.
        wall_edge(s, NB, B, 0, 24, STONE, side, False)
        wall_edge(s, NA, A, 0, 24, STONE, side, True)
        for across, lit in ((1.65,False),(-1.65,True)):
            wall_edge(s,position(across,9)[:2],position(across,0)[:2],24,14,STONE,
                      stone_courses(STONE,4,12),lit)

        def roof_slope(outer, inner, low, high, tone):
            start=position(outer,0,low)
            delta=inner-outer
            surface(s,start,(-9,-9,0),(delta,-delta,high-low),
                    lambda u,t: CATHEDRAL_ROOF['line'] if (u*10)%1 < .08 else
                    CATHEDRAL_ROOF[tone] if int(u*10)%3 else CATHEDRAL_ROOF['mid'])
            seg(s,P(s,*start),P(s,*position(outer,9,low)),CATHEDRAL_ROOF['outline'])

        # Narrow high nave and two lower lean-to aisle roofs, as in the real basilican section.
        roof_slope(3,1.65,24,33,'dark')
        roof_slope(-3,-1.65,24,33,'lit')
        for north in (1.2,3,4.8,6.6):
            a,b,_=position(-3.05,north)
            block(s,a-.18,b-.18,.36,.36,23,OCHRE)
            hip_roof(s,a-.23,b-.23,.46,.46,23,3,CATHEDRAL_ROOF)
        # The north-west cross arm projects beyond the aisle and carries a taller pointed window.
        left,right=position(-3.4,9),position(-3.4,7.2)
        wall_edge(s,left[:2],right[:2],0,32,STONE,
                  lambda u,v,lit: DARK_GLASS if 4<u<7 and 10<v<25-abs(u-5.5)*1.8 else joints(u,v,lit))
        crest=P(s,*position(-3.4,8.1,45))
        poly(s,[P(s,*position(-3.4,9,32)),P(s,*position(-3.4,7.2,32)),crest],
             lambda x,y: STONE['lit'])
        for north,key in ((7.2,'lit'),(9,'dark')):
            poly(s,[P(s,*position(-3.4,north,32)),P(s,*position(-1.65,north,32)),
                    P(s,*position(-1.65,8.1,45)),crest],lambda x,y,key=key:CATHEDRAL_ROOF[key])
        roof_slope(1.65,0,38,57,'dark')
        roof_slope(-1.65,0,38,57,'lit')
        seg(s,P(s,*position(0,0,57)),P(s,*position(0,9,57)),CATHEDRAL_ROOF['hi'])
        # Small octagonal ridge turret at the northern end, distinct from the two main towers.
        ti,tj,_=position(0,8.4)
        cylinder(s,ti,tj,.32,.32,57,5,CATHEDRAL_ROOF,
                 lambda u,v,lit: DARK_GLASS if int(u)%3==1 else None,segments=8)
        revolve(s,ti,tj,.42,62,10,[(0,1),(1,0)],CATHEDRAL_ROOF,ribs=2,segments=8)
        seg(s,P(s,ti,tj,72),P(s,ti,tj,77),IRON)
        seg(s,P(s,ti-.15,tj,75),P(s,ti+.15,tj,75),GOLD['lit'])
        def front(u,v,lit):
            c,r=46.4,math.hypot(u-46.4,(v-29)*.95)
            if r<9:
                angle=math.atan2((v-29)*.95,u-c)
                if r>7.4 or r<1.8 or abs(math.sin(angle*4))<.15:
                    return OCHRE['hi']
                return BLUE['mid'] if int(u+v)%4 else BLUE['deep']
            if abs(u-c)<7 and v<13+(7-abs(u-c))*1.3:
                d=abs(u-c)
                return OCHRE['mid'] if d>5 or int(v)==13+int((7-d)*1.3) else WOOD['deep']
            if int(v) in (2,19,39):
                return OCHRE['lit']
            return joints(u,v,lit)
        wall_edge(s,A,B,0,40,STONE,front)
        # Gable and blind lancet tracery above the rose.
        left,right=P(s,*A,40),P(s,*B,40)
        apex=P(s,i+7,j+7,57)
        poly(s,[left,right,apex],lambda x,y: OCHRE['lit'] if int(y)%4 else OCHRE['mid'])
        seg(s,left,apex,WHITE['lit']);seg(s,apex,right,WHITE['lit'])
        for across,height in ((-1.5,5),(-.75,9),(0,13),(.75,9),(1.5,5)):
            points=[P(s,*position(across+a,0,z)) for a,z in
                    ((-.2,42),(.2,42),(.2,42+height-2),(0,42+height),(-.2,42+height-2))]
            poly(s,points,lambda x,y:STONE['mid'])
            for a,b in zip(points,points[1:]+points[:1]):
                seg(s,a,b,OCHRE['hi'])
        # Square west/east towers at equal northing, so neither loses its silhouette behind the nave.
        for ci,cj in ((i+4.4,j+9.6),(i+9.6,j+4.4)):
            def tower(u,v,lit):
                c=int(u)%14
                if 49<v<58 and c in (3,4,8,9):
                    return WOOD['deep'] if int(v)%3 else OCHRE['dark']
                if math.hypot(c-6.5,v-44)<4:
                    return GOLD['lit'] if abs(c-6.5)<1 or abs(v-44)<1 else IRON
                if c in (0,13) or int(v) in (24,36,48,59):
                    return OCHRE['lit' if lit else 'dark']
                if 27<v<36 and abs(c-6.5)<2:
                    return DARK_GLASS
                return joints(u,v,lit)
            block(s,ci-.85,cj-.85,1.7,1.7,60,STONE,tower)
            band(s,ci-.85,cj-.85,1.7,1.7,59,OCHRE,2)
            top=P(s,ci,cj,94)
            T,R,Bc,L=corners(s,ci-.95,cj-.95,1.9,1.9,62)
            for a,b,key in ((T,L,'mid'),(T,R,'dark'),(L,Bc,'lit'),(Bc,R,'dark')):
                poly(s,[a,b,top],lambda x,y,key=key:CATHEDRAL_ROOF[key])
                for k in range(5):
                    t=k/4
                    seg(s,(a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t),top,
                        CATHEDRAL_ROOF['line' if key=='lit' else 'deep'])
            seg(s,P(s,ci,cj,94),P(s,ci,cj,100),IRON)
            seg(s,P(s,ci-.2,cj,98),P(s,ci+.2,cj,98),GOLD['lit'])
        # Projected portal moulding and a small solid robed figure below the rose.
        center=P(s,i+7,j+7,18)
        for dx,dy in ((-2,0),(-1,-1),(0,-2),(1,-1),(2,0)):
            s.put(center[0]+dx,center[1]+dy,STONE['hi'])
        statue(s,i+7.12,j+7.12,17,7,WHITE)
        for n in range(3):
            aa,bb=(i+6+n*.15,j+8+n*.15),(i+8+n*.15,j+6+n*.15)
            wall_edge(s,aa,bb,0,3-n,WHITE)
    scene.add(i+j+23,draw)


def mosque(scene, i, j):
    """True T-plan: main dome, SE half-dome, two side domes, five NW porch domes, one minaret."""
    def draw(s):
        # NW entrance on the hidden -i wall, never moved to the visible qibla side.
        for k in range(4):
            cylinder(s, i+.35, j+1+(k+.5)*1.55, .17, .17, 0, 16, WHITE)
        for b in (j+.1, j+7.9):
            block(s,i,b,2.1,.3,19,STONE)
        for k in range(5):
            cj = j+1+k*1.55
            previous = None
            for n in range(13):
                d = -.7+1.4*n/12
                point = P(s,i+.35,cj+d,11+5*math.sqrt(max(0,1-(d/.7)**2)))
                if previous:
                    seg(s,previous,point,WHITE['lit'],2)
                previous = point
            block(s, i, cj-.7, 2.1, 1.4, 3, STONE, z=16)
            dome(s, i+1.05, cj, .95, 19, 7 if k != 2 else 9)
        def masonry(height):
            joints = stone_courses(STONE, 4, 12)
            def pattern(u,v,lit):
                c,level=int(u)%11,int(v)%16
                if 3<=c<=7 and 3<level<13 and v<height-3:
                    if c in (3,7) or level==4 or level>=11-abs(c-5):
                        return WHITE['lit' if lit else 'dark']
                    return DARK_GLASS
                if int(v) in (1,height-2):
                    return WHITE['lit' if lit else 'dark']
                return joints(u,v,lit)
            return pattern
        body = masonry(34)
        # Two lower lateral rooms stand beside the central domed hall.
        for b in (j, j+6.5):
            block(s, i+2, b, 3.5, 2.6, 23, STONE, masonry(23))
            dome(s, i+3.75, b+1.3, 1.7, 23, 10)
        block(s, i+2, j+2.3, 5.7, 4.5, 34, STONE, body)
        cylinder(s, i+4.85, j+4.55, 2.6, 2.6, 34, 9, WHITE,
                 lambda u, v, lit: arch_opening(int(u) % 9, v, 4.5, 1.5, 5, DARK_GLASS) if v > 1 else None,
                 segments=16)
        dome(s, i+4.85, j+4.55, 2.85, 43, 17)
        # The south-east qibla extension has a half-dome, cut in 3D at its joining plane.
        block(s, i+7.7, j+2.9, 2.4, 3.3, 24, STONE, masonry(24))
        faces = []
        for t in range(6):
            a0, a1 = t*math.pi/12, (t+1)*math.pi/12
            for n in range(16):
                p0, p1 = -math.pi/2+n*math.pi/16, -math.pi/2+(n+1)*math.pi/16
                pts = [P(s, i+7.7+2.35*math.cos(a)*math.cos(p), j+4.55+1.8*math.cos(a)*math.sin(p), 24+14*math.sin(a))
                       for a, p in ((a0, p0), (a0, p1), (a1, p1), (a1, p0))]
                faces.append((sum(q[1] for q in pts), pts, n))
        for _, pts, n in sorted(faces):
            poly(s, pts, lambda x, y, n=n: LEAD['lit' if n > 7 else 'dark'] if int(y) % 5 else LEAD['line'])
            if n % 4 == 0:
                seg(s, pts[0], pts[3], LEAD['hi'])
        # Western entrance corner: octagonal base, tapered stone shaft, ONE balcony and cap.
        mi, mj = i+2.1, j+7
        cylinder(s, mi, mj, .75, .75, 0, 19, STONE, stone_courses(STONE, 4, 8), segments=8)
        cylinder(s, mi, mj, .48, .48, 19, 47, STONE, stone_courses(STONE, 4, 8), segments=12)
        cylinder(s, mi, mj, .8, .8, 65, 3, WHITE, segments=12)
        cylinder(s, mi, mj, .72, .72, 68, 4, WHITE,
                 lambda u, v, lit: IRON if int(u) % 3 == 0 else None, segments=12)
        cylinder(s, mi, mj, .35, .35, 72, 10, STONE)
        revolve(s, mi, mj, .5, 82, 23, [(0, 1), (1, 0)], LEAD, ribs=3, segments=12)
        crescent(s, (mi, mj, 105))
    scene.add(i+j+20, draw)


def city_hall(scene, i, j):
    """Triangular Moorish Revival hall, striped walls, five-bay south loggia and polygonal roof."""
    # West/east ends of a truly south-facing edge, and the northern vertex.
    A, B, N = (i, j+10), (i+10, j), (i-1, j-1)
    def draw(s):
        def stripe(u, v, lit):
            c, level = int(u) % 15, int(v) % 15
            if v < 3 or int(v) in (17, 32, 46):
                return WHITE['lit' if lit else 'dark']
            if 3 <= c <= 10 and 4 < level < 13 and v < 44:
                if c in (3, 10) or level in (5, 12):
                    return WHITE['lit' if lit else 'dark']
                return DARK_GLASS if c != 6 else WOOD['lit']
            if level == 14 and c in (4, 7, 10):
                return RED['dark']
            return OCHRE['lit' if lit else 'dark'] if int(v) % 5 > 1 else RED['lit' if lit else 'dark']
        wall_edge(s, N, B, 0, 45, OCHRE, stripe, False)
        wall_edge(s, N, A, 0, 45, OCHRE, stripe, True)
        block(s, N[0]-.6, N[1]-.6, 1.4, 1.4, 48, OCHRE, stripe)
        hip_roof(s, N[0]-.7, N[1]-.7, 1.6, 1.6, 48, 9, LEAD)
        # Grey roof slopes over the three wings; the atrium has a six-sided roof, not an onion dome.
        center = (i+3.3, j+3.3)
        for a, b, key in ((N, A, 'lit'), (N, B, 'dark'), (A, B, 'mid')):
            poly(s, [P(s, *a, 45), P(s, *b, 45), P(s, *center, 60)],
                 lambda x, y, key=key: LEAD['line'] if int(x+y) % 4 == 0 else LEAD[key])
            seg(s, P(s, *a, 45), P(s, *center, 60), LEAD['hi'])
        revolve(s, *center, 3.0, 49, 21, [(0, 1), (1, .16)], LEAD, ribs=1, segments=6)
        cylinder(s, *center, .37, .37, 70, 4, COPPER, segments=6)
        wall_edge(s, A, B, 0, 45, OCHRE, stripe)
        # Three corner risalits follow the triangular plan, with textured hip roofs.
        for a, b in (A, B):
            block(s, a-.6, b-.6, 1.4, 1.4, 48, OCHRE, stripe)
            hip_roof(s, a-.7, b-.7, 1.6, 1.6, 48, 9, LEAD)
        # Projecting south centre: five real bays on each of two loggia levels.
        L, R = (i+3.15, j+7.4), (i+7.4, j+3.15)
        def loggia(u, v, lit):
            c, level = u % 13.6, v % 19
            if v < 38 and level < 14 and 2.1 < c < 11.5:
                opening = arch_opening(c, level, 6.8, 4.6, 9, DARK_GLASS)
                if opening:
                    return WHITE['mid'] if abs(c-6.8) > 3.8 else opening
            if int(v) in (18, 19, 37, 38, 46, 47):
                return WHITE['hi']
            if v > 38 and 4 < c < 10:
                return RED['mid'] if int(u+v) % 3 else WHITE['lit']
            return stripe(u, v, lit)
        wall_edge(s, L, R, 0, 49, OCHRE, loggia)
        # The central projection has its own shallow hipped roof above the ornamental cornice.
        poly(s,[P(s,*L,49),P(s,*R,49),P(s,i+5.3,j+3.4,59),P(s,i+3.4,j+5.3,59)],
             lambda x,y: LEAD['line'] if int(x+y)%4==0 else LEAD['lit'])
        for a, b in ((A, B), (L, R)):
            pa, pb = P(s, *a, 48), P(s, *b, 48)
            for k in range(int(abs(pb[0]-pa[0]))):
                t = k/max(1, abs(pb[0]-pa[0]))
                x, y = pa[0]+(pb[0]-pa[0])*t, pa[1]+(pb[1]-pa[1])*t
                s.put(x, y, WHITE['lit'])
                if k % 6 < 2:
                    s.put(x, y-2, WHITE['hi'])
        for n in range(3):
            a, b = (L[0]+n*.15, L[1]+n*.15), (R[0]+n*.15, R[1]+n*.15)
            wall_edge(s, a, b, 0, 3-n, WHITE)
    scene.add(i+j+23, draw)


def latin_bridge(scene, i, j):
    """Four unequal open arches, three solid piers with round relief eyes, stone parapets."""
    W, D, H = 8, 1.9, 13
    spans = (0, 12, 30, 49, 64)
    def draw(s):
        # Solid end faces and the farther parapet, then open south-west arch wall.
        wall_edge(s, (i, j), (i, j+D), 0, H, STONE, lit=False)
        wall_edge(s, (i, j), (i+W, j), H, 3, WHITE)
        a = P(s, i, j+D)
        def open_arch(u, v, lit):
            for lo, hi in zip(spans, spans[1:]):
                mid, r = (lo+hi)/2, (hi-lo)/2-1.6
                if abs(u-mid) < r and v < 1+9*math.sqrt(max(0, 1-((u-mid)/r)**2)):
                    return True
            return any(math.hypot(u-k, (v-10)*1.1) < 1.65 for k in spans[1:-1])
        for x, y in iso.polygon_pixels([a, P(s, i+W, j+D), P(s, i+W, j+D,H), P(s, i,j+D,H)]):
            u, v = x-a[0], a[1]+(x-a[0])*.5-y
            if not open_arch(u, v, True):
                s.put(x, y, STONE['line'] if int(v) % 3 == 0 or (int(u)+int(v)//3*4) % 9 == 0 else STONE['lit'])
        poly(s, list(corners(s, i, j, W, D, H)),
             lambda x, y: WHITE['mid'] if (int(x)+int(y)) % 5 else WHITE['line'])
        wall_edge(s, (i, j+D), (i+W, j+D), H, 3, WHITE)
        # Arch voussoirs follow each opening; no painted rectangle fakes the water underneath.
        for lo, hi in zip(spans, spans[1:]):
            mid, r = (lo+hi)/2, (hi-lo)/2-1.6
            prev = None
            for k in range(19):
                u = mid-r+2*r*k/18
                v = 1+9*math.sqrt(max(0, 1-((u-mid)/r)**2))
                point = (a[0]+u, a[1]+u*.5-v)
                if prev:
                    seg(s, prev, point, WHITE['hi'] if k % 2 else STONE['mid'])
                prev = point
    scene.add(i+j+W+D+1, draw)


def museum(scene, i, j):
    """Four separate neo-Renaissance pavilions round the botanical garden; no central dome."""
    W, D, H = 5.7, 3.4, 26
    def draw(s):
        courses = stone_courses(WHITE, 4, 12)
        def pavilion_wall(u,v,lit):
            c,level = int(u)%11,int(v)%13
            trim = WHITE['hi' if lit else 'mid']
            if c in (0,1,10) or int(v) in (1,12,24):
                return trim
            half,du = 2.5,abs(c-5.5)
            top = 8+math.sqrt(max(0,half*half-du*du))*.6
            if du<=half and 3<=level<=top and v<24:
                if du>1.8 or c==5 or level in (3,7) or level>=top-1:
                    return trim
                return DARK_GLASS if not lit else BLUE['dark']
            return courses(u,v,lit)
        # Botanical court, deliberately visible between the low pavilions.
        poly(s, [P(s, a, b) for a, b in ((i+1,j+1),(i+13,j+1),(i+13,j+10),(i+1,j+10))],
             lambda x,y: GROUND['garden'] if (int(x)+2*int(y)) % 7 else GROUND['garden_light'])
        for a, b in ((i,j), (i+8,j), (i,j+8), (i+8,j+8)):
            block(s, a, b, W, D, H, WHITE, pavilion_wall)
            band(s, a, b, W, D, 1, STONE, 2)
            band(s, a, b, W, D, H-2, WHITE, 3)
            hip_roof(s, a-.1, b-.1, W+.2, D+.2, H+1, 5, LEAD)
            # Broad shallow pedimented risalit, paired pilasters and a glazed rooflight.
            block(s, a+1.5, b+D-.25, W-3, .5, H+1, WHITE,
                  windows(WHITE, H+1, 8, 13, arched=True, pilasters=True))
            pediment(s, a+1.25, b+D-.3, W-2.5, .65, H+2, 6, WHITE)
            block(s, a+1.1, b+.7, W-2.2, 1.1, 2, STEEL,
                  lambda u,v,lit: BLUE['lit'] if int(u) % 4 else STEEL['lit'], z=H+4)
            poly(s,list(corners(s,a+1.1,b+.7,W-2.2,1.1,H+6)),
                 lambda x,y: STEEL['lit'] if (int(x)+2*int(y))%5==0 else BLUE['lit'])
        # Low corridors along the sides of the garden connect, but do not merge, the four halls.
        for a in (i+.2, i+12.4):
            block(s, a, j+3.5, 1.1, 4.5, 9, WHITE, windows(WHITE, 9, 7, 8, arched=True))
            hip_roof(s, a-.05, j+3.45, 1.2, 4.6, 9, 3, LEAD)
    scene.add(i+j+26, draw)


def townhouse(scene, i, j, wi=2.6, wj=3, floors=2, seed=0, z=0):
    """Low Bosnian čardak houses/shops, and western Habsburg stucco with restrained ironwork."""
    wall, H = palette_of(WALLS[seed % len(WALLS)]), floors*10+3
    ottoman = seed % 3 != 0
    base = windows(wall, H, 9, 10, width=5, hood=not ottoman)
    def pattern(u, v, lit):
        c = int(u) % 9
        if v < 9 and 2 <= c <= 7:
            if c in (2, 7) or int(v) == 8:
                return WOOD['lit' if lit else 'dark'] if ottoman else WHITE['lit' if lit else 'dark']
            if seed % 2:
                return WOOD['deep'] if c == 5 or int(v) % 3 == 0 else WOOD['mid' if lit else 'dark']
            return DARK_GLASS if int(v) > 2 else wall['deep']
        if ottoman and (int(v) == 11 or c == 0):
            return WOOD['lit' if lit else 'dark']
        return base(u, v, lit)
    def draw(s):
        block(s, i, j, wi, wj, H, wall, pattern, z=z)
        band(s, i, j, wi, wj, z+1, STONE, 2)
        band(s, i, j, wi, wj, z+H-1, WOOD if ottoman else WHITE, 1)
        if ottoman and floors > 1:
            # Timber-supported enclosed upper-storey bay, characteristic of mahalas.
            block(s, i+.5, j+wj-.1, wi-1, .45, 10, wall, base, z=z+H-11)
            for a in (.6, wi-.6):
                seg(s, P(s,i+a,j+wj,z+H-13), P(s,i+a,j+wj+.35,z+H-10), WOOD['dark'])
        hip_roof(s, i-.25, j-.25, wi+.5, wj+.5, z+H, 10 if ottoman else 13, CLAY)
        block(s, i+.3, j+.35, .4, .45, 8, STONE, z=z+H+3)
        band(s, i+.3, j+.35, .4, .45, z+H+10, WHITE, 2)
        if not ottoman and seed % 2 == 0:
            block(s, i+.6, j+wj, wi-1.2, .35, 1, WHITE, z=z+11)
            for a in (.6, .9, 1.3, wi-.6):
                seg(s, P(s,i+a,j+wj+.35,z+12), P(s,i+a,j+wj+.35,z+16), IRON)
            seg(s,P(s,i+.6,j+wj+.35,z+16),P(s,i+wi-.6,j+wj+.35,z+16),IRON)
    scene.add(i+j+wi+wj+1, draw)


def main():
    for name, builder, _, _, _ in SITES:
        print(preview([lambda s, b=builder: b(s, 6, 6)], 'sarajevo-'+name,
                      size=(320, 320), origin=(160, 110 if name == 'cathedral' else 155), tiles=24))
    print(preview([lambda s, k=k: townhouse(s, 3+k*3.4, 4, floors=2+k%2, seed=k)
                   for k in range(6)], 'sarajevo-houses', size=(320, 240), origin=(90, 75), tiles=24))
    import sprites
    image = sprites.stari_most()
    path = Path(__file__).resolve().parents[2]/'docs/art/capitals/bosnia-stari-most.png'
    image.resize((image.width*4, image.height*4), 0).save(path)
    print(path)


# name, builder, footprint, real (longitude, latitude), compressed north-up ground anchor.
SITES = [
    ('avaz', avaz, (5, 5), (18.402111, 43.860750), (100, 194)),
    ('sebilj', sebilj, (4.2, 4.2), (18.431260, 43.859720), (580, 205)),
    ('cathedral', cathedral, (19, 19), (18.425400, 43.859400), (315, 203)),
    ('mosque', mosque, (10.2, 9.1), (18.429028, 43.859170), (470, 260)),
    ('city-hall', city_hall, (11.5, 11.5), (18.433330, 43.859170), (623, 320)),
    ('latin-bridge', latin_bridge, (8, 1.9), (18.428960, 43.857630), (445, 435)),
    ('museum', museum, (13.7, 11.4), (18.402710, 43.854480), (185, 443)),
]


if __name__ == '__main__':
    main()
