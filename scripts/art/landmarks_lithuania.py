"""Vilnius: sculpted Baroque plaster, brick Gothic and hilltop monuments in (i,j,z).

Eight landmark studies precede integration; north-up anchors and references are in
DEVELOPMENT_PLAN.md. Art is original, rendered at native resolution.
"""
import math
from pathlib import Path

import iso
from iso import rgb
from landmarks_paris import P, seg, poly, facade, preview, GLASS
from landmarks_iberia import hip_roof, stone_courses, arch_opening, palette_of, tones
from landmarks_amsterdam import gable_roof
from landmarks_italy import cylinder, ellipse, column
from landmarks_denmark import spire, clock
from landmarks_slovakia import block, band, pediment
from landmarks_estonia import lifted

STONE = tones('#E7E1CF', '#C9C3AC', '#AFAB93', '#8D927F', '#626D5B', '#9CA087', '#414C3A')
WHITE = tones('#FFF9E9', '#EEE5D0', '#D9CCB4', '#B7AA92', '#817660', '#C7B89B', '#514735')
BRICK = tones('#E9AA82', '#BC6C49', '#A35237', '#7B392D', '#542A25', '#924731', '#41271F')
CLAY = tones('#F2AF79', '#CF794A', '#B35D38', '#89412C', '#5D2D23', '#A34F32', '#4B281F')
COPPER = tones('#BDD3BC', '#80A591', '#618574', '#3E6257', '#29483D', '#53766A', '#253C32')
DARK = tones('#A3ADA6', '#758A80', '#576E64', '#354F45', '#243A30', '#4B6559', '#203328')
GOLD = tones('#FFF0AD', '#E6C56B', '#C7A24B', '#997731', '#6D5425', '#AD8D3E', '#514022')
BLUE = tones('#DCE7E5', '#B8CECF', '#98B2B6', '#749296', '#4D6D72', '#89A5A9', '#344D54')
WALLS = [rgb(c) for c in ('#E7D7B5', '#D4B678', '#CDA594', '#B8C5AE', '#D6C5C0', '#C9D3CE', '#BB8C71')]
IRON, WOOD = rgb('#354239'), rgb('#674732')
WATER = (rgb('#4C828D'), rgb('#396371'), rgb('#C1DADD'))


def windows(material, height, bay=10, floor=12, gothic=False):
    joints = stone_courses(material, 3 if material == BRICK else 5, 10)
    def pattern(u, v, lit):
        c, level = int(u) % bay, int(v) % floor
        trim = WHITE['lit' if lit else 'dark']
        if v < 2 or int(v) in (height-1, height-3):
            return trim
        top = floor-3-abs(c-bay/2)*.95 if gothic else floor-3
        if 2 <= c <= bay-2 and 3 <= level <= top and v < height-4:
            if c in (2, bay-2, bay//2) or level in (3, 6, int(top)):
                if gothic:
                    return BRICK['hi' if lit else 'mid']
                return STONE['lit' if lit else 'dark'] if material == WHITE else trim
            # Deep glazing reads as dressed openings against white Renaissance plaster.
            if material == WHITE:
                return GLASS['mid'] if c == 3 and level == top-1 and lit else DARK['dark']
            return GLASS['mid' if lit else 'dark']
        return joints(u, v, lit) if material in (STONE, BRICK) else None
    return pattern


def cross(s, i, j, base, height=9, material=GOLD):
    block(s, i-.09, j-.09, .18, .18, height, material, z=base)
    block(s, i-.4, j-.09, .8, .18, 1.5, material, z=base+height*.64)


def figure(s, i, j, z, height=10, material=WHITE):
    # Filled drapery, shoulders, head and folded arm, with shaded side thickness.
    block(s, i-.22, j-.17, .44, .34, height*.6, material, z=z)
    block(s, i-.3, j-.18, .6, .36, height*.16, material, z=z+height*.58)
    cylinder(s, i, j, .18, .17, z+height*.76, height*.2, material)
    seg(s, P(s, i-.22, j+.2, z+height*.65), P(s, i+.15, j+.2, z+height*.4), material['dark'], 2)


def flag(s, i, j, z):
    seg(s, P(s,i,j,z), P(s,i,j,z+20), IRON)
    for n,c in enumerate((GOLD['lit'], rgb('#558256'), rgb('#B85144'))):
        poly(s, [P(s,i+a,j,z+19-n*2.4-b) for a,b in ((0,0),(1.5,0),(1.5,2.4),(0,2.4))], lambda x,y,c=c:c)


def cap(s, ci, cj, radius, base, rise, material=DARK):
    """Baroque bell-shaped cap, contracting to a neck with raised copper seams."""
    levels = [(0,1),(.13,1.12),(.36,.88),(.6,.46),(.75,.37),(1,.12)]
    for (t,r),(nt,nr) in zip(levels,levels[1:]):
        for n in range(24):
            a,b=n*math.tau/24,(n+1)*math.tau/24
            pts=[P(s,ci+rr*radius*math.cos(ang),cj+rr*radius*math.sin(ang),base+tt*rise)
                 for tt,rr,ang in ((t,r,a),(t,r,b),(nt,nr,b),(nt,nr,a))]
            key='lit' if math.sin((a+b)/2)-.5*math.cos((a+b)/2)>0 else 'dark'
            poly(s,pts,lambda x,y,key=key:material['line'] if int(y)%5==0 else material[key])
            if n%4==0:seg(s,pts[0],pts[3],material['hi' if key=='lit' else 'deep'])


def townhouse(scene,i,j,wi=2.5,wj=3,floors=3,seed=0):
    """Vilnius plaster houses: Baroque attic scrolls, clay hips/gables, occasional iron balconies."""
    wall,height=palette_of(WALLS[seed%len(WALLS)]),floors*10+3
    base=windows(wall,height,10,10)
    def pattern(u,v,lit):
        c,level=int(u)%10,int(v)%10
        trim=WHITE['lit' if lit else 'dark']
        if v<9 and 2<=c<=7:
            if c in (2,7) or int(v) in (1,8):return trim
            return WOOD if (int(u)//10+seed)%3==0 else GLASS['dark']
        if v>=10 and level==2 and 1<=c<=8 and seed%4==0:return IRON
        if level==9 and 2<=c<=7:return trim
        return base(u,v,lit)
    def draw(s):
        block(s,i,j,wi,wj,height,wall,pattern)
        band(s,i,j,wi,wj,1,STONE,2);band(s,i,j,wi,wj,height-1,WHITE)
        if seed%3==0:
            gable_roof(s,i,j,wi,wj,height,15,CLAY,wall,'bell')
            fj=j+wj+.08
            for a in (.3,wi-.3):
                # Volutes in the actual gable plane.
                for n in range(15):
                    t=n*.38;r=2*(1-n/20)
                    x,y=P(s,i+a,fj,height+5)
                    s.put(x+math.cos(t)*r,y+math.sin(t)*r,WHITE['hi'])
        else:
            hip_roof(s,i,j,wi,wj,height,13,CLAY)
            if seed%3==1:
                block(s,i+.5,j+wj-.5,.65,.55,5,wall,windows(wall,8,5,8),z=height+3)
                hip_roof(s,i+.45,j+wj-.55,.75,.65,height+8,4,CLAY)
        block(s,i+wi-.65,j+.4,.4,.5,9,BRICK,z=height+5)
        band(s,i+wi-.65,j+.4,.4,.5,height+13,STONE,2)
    scene.add(i+j+wi+wj,draw)


def gediminas(scene,i,j,z=0):
    """Octagonal red-brick Upper Castle tower, stone foot, open terrace and tricolour."""
    def draw(s):
        # Low ruin and retaining stonework anchor the tower on its landscaped hill.
        block(s,i+.8,j+1.1,5.1,3.7,10,STONE)
        block(s,i+4.3,j+.8,2.4,.65,17,BRICK,stone_courses(BRICK,3,9),z=4)
        ci,cj=i+2.8,j+2.8
        def octagonal(base,height,material,openings=False):
            faces=[]
            for n in range(8):
                a,b=(n+.5)*math.tau/8,(n+1.5)*math.tau/8
                va=(ci+2.15*math.cos(a),cj+2.15*math.sin(a));vb=(ci+2.15*math.cos(b),cj+2.15*math.sin(b))
                faces.append((sum(va+vb),n,va,vb))
            cover=set()
            for _,n,va,vb in sorted(faces):
                pa,pb=P(s,*va,base),P(s,*vb,base)
                lit=va[1]+vb[1]>2*cj
                def color(x,y,pa=pa,pb=pb,lit=lit):
                    t=(x-pa[0])/(pb[0]-pa[0]) if abs(pb[0]-pa[0])>.01 else .5
                    v=pa[1]+t*(pb[1]-pa[1])-y
                    if openings and .38<t<.65 and any(z<v<z+8 for z in (12,28)):
                        return material['deep']
                    return stone_courses(material,3,8)(x,v,lit) or material['lit' if lit else 'dark']
                pts=[pa,pb,P(s,*vb,base+height),P(s,*va,base+height)]
                iso.fill(s,pts,color,cover)
                seg(s,pts[0],pts[3],material['line'])
            iso.outline(s,cover,material['outline'])
        octagonal(5,10,STONE);octagonal(15,40,BRICK,True)
        ellipse(s,ci,cj,2,2,55,BRICK['deep'])
        # Solid low parapet, flat observation terrace and small dark drainage openings.
        octagonal(55,4,BRICK)
        ellipse(s,ci,cj,1.75,1.75,59.2,STONE['dark'])
        flag(s,ci,cj,60)
    scene.add(i+j+15,lifted(draw,z))


def cathedral(scene,i,j):
    """Six-column cathedral, three pediment saints, Casimir chapel and separate round belfry."""
    def draw(s):
        block(s,i+3,j,7,8,35,WHITE,windows(WHITE,35,12,25))
        hip_roof(s,i+3,j,7,8,35,12,DARK)
        for z in (2,32):band(s,i+3,j,7,8,z,STONE,2)
        for a in range(6):column(s,i+3.35+a*1.28,j+9,2,29,WHITE,.44)
        band(s,i+2.9,j+7.8,7.2,1.6,31,WHITE,3)
        pediment(s,i+2.8,j+7.8,7.4,1.6,34,15,WHITE)
        for a,h in ((3.1,10),(6.5,13),(9.8,10)):
            figure(s,i+a,j+9.1,35+(14 if a==6.5 else 0),h)
        cross(s,i+6.8,j+9.1,61,10)
        # Projecting St Casimir chapel with ribbed cupola, drum and lantern.
        block(s,i+8.1,j+.3,2.8,3,26,WHITE,windows(WHITE,26,9,14))
        cylinder(s,i+9.5,j+1.8,1.1,1.1,26,8,WHITE,windows(WHITE,12,7,12))
        cap(s,i+9.5,j+1.8,1.25,34,14,DARK);cross(s,i+9.5,j+1.8,48)
        # Belfry stands southwest of the cathedral; round lower masonry, octagonal upper tiers.
        ci,cj=i+1,j+8
        cylinder(s,ci,cj,1.15,1.15,0,27,WHITE,windows(WHITE,30,12,20))
        for z,r,h in ((27,1.03,15),(42,.86,15)):
            cylinder(s,ci,cj,r,r,z,h,WHITE,
                     lambda u,v,lit: arch_opening(int(u)%9,v,4.5,2,9,IRON) if v>3 else None)
            ellipse(s,ci,cj,r+.12,r+.12,z+h,WHITE['hi'])
        clock(s,ci,cj+1.03,3,35)
        cap(s,ci,cj,.95,57,16,DARK);cross(s,ci,cj,73,8)
    scene.add(i+j+25,draw)


def palace(scene,i,j):
    """Reconstructed Renaissance courtyard palace: white ranges, attic parapets and domed turret."""
    def draw(s):
        for a,b,w,d in ((i,j,11,2),(i,j+2,2,4),(i+9,j+2,2,4),(i+2,j+5,7,2)):
            block(s,a,b,w,d,33,WHITE,windows(WHITE,33,10,11))
            hip_roof(s,a,b,w,d,33,7,DARK)
            for z in (2,12,24,32):band(s,a,b,w,d,z,STONE)
            # Recessed attic panels and parapet crest cover the low roof's eave.
            facade(s,a-.05,b+d,w+.1,.13,6,
                   lambda u,v,lit:STONE['dark'] if int(u)%7 in (2,3,4) and 1<v<4 else WHITE['lit'],palette=WHITE,z0=33)
        block(s,i+7.2,j+.3,2.1,2.1,43,WHITE,windows(WHITE,43,8,12))
        cap(s,i+8.25,j+1.35,1.1,43,15,DARK)
        cylinder(s,i+8.25,j+1.35,.23,.23,58,6,WHITE)
        spire(s,i+8.25,j+1.35,.4,64,8,DARK)
        for a,b in ((1,1),(4,1),(9.5,5.5)):
            block(s,i+a,j+b,.4,.4,8,WHITE,z=36)
        # Rusticated central portal; the courtyard is visibly open behind it.
        facade(s,i+4.4,j+7.08,2,.12,16,
               lambda u,v,lit:arch_opening(u,v,8,4.5,9,WOOD) or stone_courses(STONE,3,8)(u,v,lit),palette=WHITE)
        pediment(s,i+4.3,j+7.02,2.2,.23,16,5,WHITE)
    scene.add(i+j+22,draw)


def st_anne(scene,i,j):
    """Flamboyant Gothic: three perforated brick turrets, ogee arches, tracery and buttresses."""
    def draw(s):
        block(s,i,j,5.5,8,37,BRICK,windows(BRICK,37,13,30,True))
        gable_roof(s,i,j,5.5,8,37,24,CLAY,BRICK)
        for b in (.6,2.7,4.8,6.9):
            block(s,i+5.25,j+b,.7,.55,29,BRICK,stone_courses(BRICK,3,8))
            spire(s,i+5.6,j+b+.25,.42,29,8,BRICK)
        fj=j+8.1
        def front(u,v,lit):
            # Three actual lancets under ogee heads; no motif spills onto the side wall.
            for center in (8,22,36):
                d=abs(u-center)
                if d<5 and 3<v<17-d*.9:return WOOD if v<11 else BRICK['deep']
                if d<5 and 23<v<46-d*1.4:
                    return BRICK['hi'] if d>3.5 or int(u-center)%3==0 or int(v)%8==0 else GLASS['dark']
            if int(v) in (19,21,47):return BRICK['hi']
            return stone_courses(BRICK,3,9)(u,v,True)
        facade(s,i,j+7.95,5.5,.2,49,lambda u,v,lit:front(u,v,lit) if lit else stone_courses(BRICK,3,9)(u,v,lit),palette=BRICK)
        # Curved brick ogee hoods and thin clustered piers frame the three front bays.
        for a in (1,2.75,4.5):
            for sign in (-1,1):
                prev=None
                for n in range(17):
                    t=n/16;u=a+sign*.65*(1-t);z=43+13*t-3*math.sin(math.pi*t)
                    p=P(s,i+u,fj,z)
                    if prev:seg(s,prev,p,BRICK['hi'])
                    prev=p
        for a,h in ((.25,65),(2.75,79),(5.25,65)):
            block(s,i+a-.35,j+7.6,.7,.7,h-12,BRICK,windows(BRICK,h,6,16,True))
            for z in (36,49,h-13):band(s,i+a-.35,j+7.6,.7,.7,z,BRICK)
            # Open belfry fingers, joined at their tops; sky stays visible between.
            for da,db in ((-.32,-.32),(.32,-.32),(-.32,.32),(.32,.32)):
                block(s,i+a+da-.07,j+7.95+db-.07,.14,.14,13,BRICK,z=h-12)
                spire(s,i+a+da,j+7.95+db,.15,h+1,9,BRICK)
            spire(s,i+a,j+7.95,.48,h+1,15,BRICK)
            cross(s,i+a,j+7.95,h+16,6,IRON_RAMP)
    scene.add(i+j+22,draw)


IRON_RAMP=palette_of(IRON)


def st_johns(scene,i,j):
    """University church, undulating Baroque front and separate five-stage campanile."""
    def draw(s):
        block(s,i+2.6,j,5.5,7,36,WHITE,windows(WHITE,36,12,24))
        gable_roof(s,i+2.6,j,5.5,7,36,21,CLAY,WHITE)
        fj=j+7.15
        for a in (2.7,3.8,5.4,7,8):
            column(s,i+a,fj,2,34,WHITE,.3)
        for z in (19,35):band(s,i+2.5,j+6.8,5.8,.5,z,WHITE,2)
        for a,h in ((2.9,8),(4.1,16),(5.35,21),(6.6,16),(7.8,8)):
            block(s,i+a-.32,j+6.9,.64,.4,h,WHITE,z=37)
            cap(s,i+a,j+7.1,.38,37+h,4,DARK)
        for a in (3.5,5.3,7.2):figure(s,i+a,fj+.12,23,8)
        cross(s,i+5.35,fj,62,9)
        # Detached belfry on the west side. Receding, dressed stages and curved copper cap.
        ci,cj=i+.7,j+5.6
        z=0
        for n,(w,h) in enumerate(((2,24),(1.85,23),(1.6,21),(1.3,18),(1,13))):
            block(s,ci-w/2,cj-w/2,w,w,h,WHITE,
                  lambda u,v,lit,h=h: arch_opening(int(u)%10,v-5,5,2,h-10,IRON) if v>5 else None,z=z)
            for da,db in ((-w/2,w/2),(w/2,w/2),(w/2,-w/2)):
                block(s,ci+da-.09,cj+db-.09,.18,.18,h,STONE,z=z)
            band(s,ci-w/2,cj-w/2,w,w,z+h-1,WHITE,2)
            if n==2:clock(s,ci,cj+w/2+.02,3,z+10)
            z+=h
        cap(s,ci,cj,.75,z,16,COPPER);cross(s,ci,cj,z+16,10)
    scene.add(i+j+24,draw)


def town_hall(scene,i,j):
    """Gucevičius' six-column neoclassical portico, city shield and broad steps."""
    def draw(s):
        block(s,i,j,8.5,5,30,WHITE,windows(WHITE,30,11,13))
        hip_roof(s,i,j,8.5,5,30,12,CLAY)
        for z in (2,15,28):band(s,i,j,8.5,5,z,STONE)
        for a in range(6):column(s,i+1.2+a*1.2,j+6,3,26,WHITE,.48)
        band(s,i+.7,j+4.8,7,1.5,28,WHITE,3)
        pediment(s,i+.6,j+4.8,7.2,1.5,31,12,WHITE)
        # Heraldic shield: projected filled relief with an inset Saint Christopher silhouette.
        poly(s,[P(s,i+4.2+a,j+6.34,z) for a,z in ((-.35,36),(.35,36),(.35,32),(0,30),(-.35,32))],lambda x,y:STONE['lit'])
        figure(s,i+4.2,j+6.36,31,4,STONE)
        for n in range(4):block(s,i+.5,j+6.2+n*.25,7.5,.3,4-n,STONE)
        flag(s,i+4.2,j+2.5,42)
    scene.add(i+j+20,draw)


def gate_of_dawn(scene,i,j):
    """True open gateway, blue-white chapel, three arched windows, icon and gold inscription marks."""
    def draw(s):
        W,D=6,2.5
        # Two piers and a roof-level lintel: the street opening remains genuinely empty.
        for a in (0,4.3):block(s,i+a,j,1.7,D,21,STONE)
        block(s,i,j,W,D,7,STONE,z=21)
        # Curved voussoirs join the piers above the round-headed passage.
        for n in range(20):
            a,b=n*math.pi/20,(n+1)*math.pi/20
            for front,tone in ((j,STONE['dark']),(j+D+.02,STONE['lit'])):
                pts=[P(s,i+3+r*math.cos(t),front,13+r*8*math.sin(t)) for r,t in ((1.3,a),(1.3,b),(1.7,b),(1.7,a))]
                poly(s,pts,lambda x,y,tone=tone:tone)
        block(s,i,j,W,D,24,BLUE,windows(BLUE,24,12,20),z=28)
        fj=j+D+.1
        for a in (.3,1.7,4.3,5.7):column(s,i+a,fj,29,22,WHITE,.22)
        # Three arched glazed windows; central gilded icon is clipped to its opening.
        for a in (1,3,5):
            def opening(u,v,lit,a=a):
                c=u-4
                inside=abs(c)<3 and (v<12 or v<12+math.sqrt(max(0,9-c*c)))
                if inside:
                    if a==3 and 4<v<12 and abs(c)<1.8:return GOLD['lit'] if int(v)%3 else GOLD['dark']
                    return GLASS['dark'] if int(u)%3 else IRON
                return None
            facade(s,i+a-.5,fj,1,.08,16,opening,palette=WHITE,z0=30)
        band(s,i,j,W,D,51,WHITE,2)
        hip_roof(s,i-.1,j-.1,W+.2,D+.2,53,12,DARK)
        pediment(s,i-.1,j+D-.1,W+.2,.2,53,12,WHITE)
        for a in (.4,1.2,2,3.8,4.6,5.4):
            seg(s,P(s,i+a,fj,48),P(s,i+a+.25,fj,48),GOLD['lit'])
        # Iron balcony and red flowers below the chapel windows.
        band(s,i+.4,fj,5.2,.35,28,STONE)
        for a in range(19):
            seg(s,P(s,i+.4+a*.28,fj+.4,28),P(s,i+.4+a*.28,fj+.4,31),IRON)
            if a%3==0:s.put(*P(s,i+.4+a*.28,fj+.4,31),BRICK['lit'])
        block(s,i+2.65,j+.9,.7,.6,9,WHITE,
              lambda u,v,lit: arch_opening(u,v,2.8,1.8,4,IRON) or None,z=63)
        band(s,i+2.65,j+.9,.7,.6,72,WHITE)
        cross(s,i+3,j+1.2,73,9)
    scene.add(i+j+18,draw)


def three_crosses(scene,i,j,z=0):
    """Three monumental concrete crosses sharing a stepped curved hilltop plinth."""
    def draw(s):
        for z,r,h in ((0,2.3,3),(3,1.9,3),(6,1.6,3)):
            cylinder(s,i+2.5,j+2.5,r,r*.7,z,h,STONE)
        for a,b,h in ((i+.9,j+2.3,33),(i+2.5,j+2.8,44),(i+4.1,j+2.3,33)):
            block(s,a-.18,b-.2,.36,.4,h,WHITE,z=8)
            block(s,a-.85,b-.2,1.7,.4,5,WHITE,z=8+h*.67)
            # Sculpted flared feet tie the three stems to the common base.
            block(s,a-.35,b-.27,.7,.54,7,WHITE,z=8)
    scene.add(i+j+15,lifted(draw,z))


# name, builder, footprint, real (longitude,latitude), compressed north-up ground anchor, hilltop
# elevation (Castle Hill and the higher Hill of Three Crosses).
SITES=[
    ('gediminas',gediminas,(7,6),(25.29069,54.68676),(480,150),30),
    ('three-crosses',three_crosses,(5,5),(25.2975,54.68639),(652,216),38),
    ('palace',palace,(11,7.5),(25.28889,54.68611),(390,250),0),
    ('cathedral',cathedral,(11,10),(25.28778,54.68583),(200,315),0),
    ('st-anne',st_anne,(6,9),(25.29326,54.68304),(565,365),0),
    ('st-johns',st_johns,(9,8),(25.28833,54.6825),(345,445),0),
    ('town-hall',town_hall,(9,7.5),(25.28694,54.67806),(100,465),0),
    ('gate-of-dawn',gate_of_dawn,(6,3),(25.28954,54.67432),(465,490),0),
]


def main():
    for name,builder,_,_,_,_ in SITES:
        print(preview([lambda s,b=builder:b(s,4,4)],'vilnius-'+name,
                      size=(290,310),origin=(135,175),tiles=21))
    print(preview([lambda s,n=n:townhouse(s,3+n*3,3,2.5,3,2+n%2,n) for n in range(5)],
                  'vilnius-houses',size=(280,230),origin=(70,80),tiles=22))
    import sprites
    sprite=sprites.trakai()
    path=Path(__file__).resolve().parents[2]/'docs/art/capitals/lithuania-trakai.png'
    sprite.resize((sprite.width*4,sprite.height*4),0).save(path)
    print(path)


if __name__=='__main__':main()
