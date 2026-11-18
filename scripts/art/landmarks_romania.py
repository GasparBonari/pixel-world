"""Bucharest's limestone palaces and Brâncovenesc churches in true (i,j,z).

Two-source fact sheets, setting, counts and explicit facade turns: DEVELOPMENT_PLAN.md, Phase 4.
Run this module to regenerate seven isolated 4× studies, houses and the Bran country sprite.
"""
import math
from pathlib import Path

from iso import rgb
from landmarks_paris import P, seg, poly, mansard, preview, GLASS
from landmarks_iberia import hip_roof, stone_courses, arch_opening, palette_of, tones
from landmarks_slovakia import block, band, pediment
from landmarks_bosnia import cylinder
from landmarks_slovenia import revolve, balustrade, DOME
from landmarks_greece import column

STONE = tones('#FFF3DA', '#E7D3AD', '#CDB790', '#AA8F68', '#7A6246', '#BCA17B', '#51402D')
MARBLE = tones('#FFFEF0', '#EEE7D2', '#D8CDB3', '#B8A98D', '#84765D', '#CCBCA0', '#514733')
WHITE = tones('#FFFFF3', '#F3EBD9', '#DDD2BC', '#BDAE94', '#8B7C65', '#D0C1A7', '#554936')
OCHRE = tones('#FFF0C5', '#EBD3A1', '#D0B27D', '#AC8959', '#795E39', '#C09C68', '#534027')
CLAY = tones('#EAB68D', '#CB8A60', '#B36E49', '#885037', '#5D3527', '#A65F41', '#4E2C22')
ZINC = tones('#CFD2CC', '#9FAAA4', '#82908B', '#616F6A', '#414D4A', '#74837D', '#303C39')
DOME_GLASS = tones('#DAF0EA', '#B0D0CC', '#8FB4B4', '#638D94', '#41646E', '#729D9F', '#2E4851')
GOLD = tones('#FFF2B4', '#E3C77A', '#C6A257', '#9D793B', '#6A512B', '#B88C46', '#4D3C28')
ROCK = tones('#DED3BA', '#BAAC8E', '#A19172', '#807154', '#5A503B', '#918164', '#423B2C')
WALLS = [rgb(c) for c in ('#E7D7B7', '#CFB58D', '#E2B8A4', '#C7CBB5', '#D4C3CE', '#F0E7D2', '#BBC9C9')]
IRON, WOOD, ICON_BLUE = rgb('#35413F'), rgb('#74513C'), rgb('#486B83')
GROUND = {k:rgb(c) for k,c in {
    'square':'#DBD0B9', 'joint':'#B9AD96', 'rose':'#CDB8A4', 'cobble':'#BFB49F',
    'cobble_joint':'#9D917E', 'garden':'#91A773', 'garden_light':'#B2BE8D',
    'water':'#638E88', 'water_dark':'#456E70', 'water_hi':'#C5DCD2',
}.items()}


def windows(material, height, bay=10, floor=12, arched=False, pilasters=False):
    """Dressed two-pane openings, individual lintels/sills, rustication and cornices."""
    joints=stone_courses(material,5,13)
    def pattern(u,v,lit):
        c,k=int(u)%bay,int(v)%floor
        trim=MARBLE['lit' if lit else 'dark']
        if v<2 or int(v) in (height-2,height-1):return trim
        if pilasters and c in (0,1):return MARBLE['hi' if lit and c==0 else 'mid']
        top=floor-3-abs(c-bay/2)*.45 if arched else floor-4
        edge=2 if bay<9 else 3
        if edge<=c<=bay-edge and 3<=k<=top and v<height-3:
            if c in (edge,bay-edge,bay//2) or k in (3,6,int(top)):return trim
            return GLASS['mid' if lit else 'dark']
        if k==2 and 2<=c<=bay-2:return MARBLE['hi' if lit else 'mid']
        if k==floor-2 and 2<=c<=bay-2 and v<height-3:return trim
        return joints(u,v,lit)
    return pattern


def cross(s,i,j,z):
    seg(s,P(s,i,j,z),P(s,i,j,z+6),ZINC['deep'])
    seg(s,P(s,i-.18,j,z+4),P(s,i+.18,j,z+4),WHITE['hi'])


def roundel(s,ci,cj,z,radius,along_i=True,material=GOLD):
    """Shallow sculpted/mosaic portrait medallion in its wall plane, not a freestanding stick."""
    ring=[P(s,ci+radius*math.cos(t*math.tau/24)/8 if along_i else ci,
            cj if along_i else cj+radius*math.cos(t*math.tau/24)/8,
            z+radius*math.sin(t*math.tau/24)) for t in range(24)]
    poly(s,ring,lambda x,y:material['lit'] if (x+2*y)%5 else material['dark'])
    for a,b in zip(ring,ring[1:]+ring[:1]):seg(s,a,b,material['outline'])
    x,y=P(s,ci,cj,z)
    for dx,dy in ((0,-1),(0,0),(-1,1),(0,1),(1,1),(-1,2),(0,2),(1,2)):
        s.put(x+dx,y+dy,STONE['hi' if dx<1 else 'dark'])


def triumph(scene,i,j,z=0):
    """Single open barrel arch, heavy sculpted piers, portrait roundels and inscribed attic."""
    w,d,h=7.8,3.4,57
    def draw(s):
        for a in (i,i+5.4):
            block(s,a,j,2.4,d,39,STONE,stone_courses(STONE,5,12),z=z)
            band(s,a,j,2.4,d,z+1,MARBLE,2)
            # Relief groups are broad shallow bodies with heads, drapery and shields.
            for n in range(3):
                ci=a+.65+n*.53;cj=j+d+.03
                x,y=P(s,ci,cj,z+19+n%2*3)
                poly(s,[(x-2,y+8),(x-3,y),(x-1,y-3),(x+2,y-2),(x+3,y+7)],
                     lambda x,y:MARBLE['lit'] if (x+y)%4 else STONE['mid'])
                cylinder(s,ci,cj,.14,.08,z+22+n%2*3,3,MARBLE,segments=8)
                seg(s,P(s,ci-.12,cj,z+15),P(s,ci+.15,cj,z+21),STONE['line'])
            roundel(s,a+1.2,j+d+.04,z+33,3)
        # Extruded voussoirs: open below the semicircle, real intrados/return faces.
        centre=i+w/2;radius=1.5;spring=23
        for n in range(18):
            a=centre-radius+2*radius*n/18;b=centre-radius+2*radius*(n+1)/18
            za=spring+math.sqrt(max(0,1-((a-centre)/radius)**2))*13
            zb=spring+math.sqrt(max(0,1-((b-centre)/radius)**2))*13
            for side,lit in ((j,False),(j+d,True)):
                pts=[P(s,a,side,z+za),P(s,b,side,z+zb),P(s,b,side,z+41),P(s,a,side,z+41)]
                poly(s,pts,lambda x,y,lit=lit:STONE['lit' if lit else 'dark'])
                seg(s,pts[0],pts[3],STONE['line'])
            poly(s,[P(s,a,j,z+za),P(s,b,j,z+zb),P(s,b,j+d,z+zb),P(s,a,j+d,z+za)],
                 lambda x,y:STONE['deep'] if (x+y)%7 else STONE['dark'])
            seg(s,P(s,a,j+d,z+za),P(s,b,j+d,z+zb),MARBLE['hi'])
        block(s,i,j,w,d,h-40,STONE,stone_courses(STONE,5,16),z=z+40)
        for zz in (40,43,55):band(s,i,j,w,d,z+zz,MARBLE,2)
        # Inscriptions and side friezes are bounded relief panels, never invented text.
        for a in range(4,58):
            if a%4==0:continue
            seg(s,P(s,i+a/8,j+d+.03,z+48),P(s,i+a/8,j+d+.03,z+50),STONE['deep'])
        roundel(s,i+w+.02,j+d/2,z+47,4,False,STONE)
    scene.add(i+j+w+d,draw)


def athenaeum(scene,i,j,z=0):
    """Circular hall, one ribbed dome with oculi, six Ionic portico columns, five mosaics."""
    w,d=8.6,8.5
    def draw(s):
        ci,cj=i+w/2,j+3.8
        cylinder(s,ci,cj,3.65,3.65,z+3,33,OCHRE,windows(OCHRE,33,11,13,True,True),segments=48)
        cylinder(s,ci,cj,3.8,3.8,z+35,3,MARBLE,segments=48)
        cylinder(s,ci,cj,3.2,3.2,z+38,10,WHITE,
                 lambda u,v,lit:MARBLE['dark'] if int(u)%11==0 else
                 GLASS['dark'] if 2<v<7 and abs(int(u)%11-5)<2 else None,segments=48)
        revolve(s,ci,cj,3.35,z+48,21,[(0,1),(.18,.96),(.55,.72),(.82,.4),(1,.05)],ZINC,ribs=3,segments=48)
        cylinder(s,ci,cj,.3,.3,z+69,3,ZINC,segments=12)
        # Side vestibules and recessed wall behind the open colonnade.
        vestibule_wall=windows(OCHRE,29,11,13)
        block(s,i,j+5.4,w,2.0,29,OCHRE,
              lambda u,v,lit: WOOD if lit and 3<v<22 else vestibule_wall(u,v,lit),z=z+3)
        for n in range(5):roundel(s,i+1.3+n*1.5,j+7.42,z+25,2.6,True,GOLD)
        for n in range(6):column(s,i+.8+n*(w-1.6)/5,j+8,z+4,29,.32,MARBLE,'ionic')
        block(s,i+.35,j+7.6,w-.7,1,4,MARBLE,z=z+33)
        pediment(s,i+.25,j+7.5,w-.5,1.15,z+37,10,MARBLE)
        # Recessed tympanum and three geison lines.
        pts=[P(s,i+1,j+8.66,z+39),P(s,i+w-1,j+8.66,z+39),P(s,ci,j+8.66,z+44)]
        poly(s,pts,lambda x,y:MARBLE['dark'])
        for n in range(4):block(s,i+.5-n*.15,j+8.4+n*.22,w-1+n*.3,.25,4-n,MARBLE,z=z)
    scene.add(i+j+w+d+2,draw)


def royal_palace(scene,i,j,z=0):
    """Broad U-shaped museum palace, with open east court, giant pilasters and balustrades."""
    w,d,h=7.6,12.8,31
    def draw(s):
        wall=windows(WHITE,h,10,13,True,True)
        for a,b,wi,wj in ((i,j,2.4,d),(i+2.4,j,w-2.4,2.5),(i+2.4,j+d-2.5,w-2.4,2.5)):
            block(s,a,b,wi,wj,h,WHITE,wall,z=z)
            band(s,a,b,wi,wj,z+13,MARBLE,1)
            band(s,a,b,wi,wj,z+h-1,MARBLE,2)
            hip_roof(s,a,b,wi,wj,z+h+1,3,ZINC)
            balustrade(s,(a+wi,b),(a+wi,b+wj),z+h+2,3,MARBLE,3)
            balustrade(s,(a,b+wj),(a+wi,b+wj),z+h+2,3,MARBLE,3)
        # Central eastern facade: six giant pilasters on the shaded wall, balcony and canopy.
        for n in range(6):
            b=j+3.5+n*1.15
            block(s,i+2.4,b,.24,.26,19,MARBLE,z=z+11)
        block(s,i+2.4,j+4.4,.9,4,2,MARBLE,z=z+14)
        balustrade(s,(i+3.3,j+4.4),(i+3.3,j+8.4),z+16,3,MARBLE,3)
        block(s,i+2.4,j+5.3,1.2,2.2,2,ZINC,z=z+10)
        for b in (j+5.3,j+7.5):seg(s,P(s,i+3.5,b,z+2),P(s,i+3.5,b,z+10),IRON)
        # A low stepped court preserves the U rather than filling it with a single roof.
        for n in range(3):block(s,i+2.5+n*.35,j+4.8, .35,3.2,3-n,MARBLE,z=z)
    scene.add(i+j+w+d+2,draw)


def cec_palace(scene,i,j,z=0):
    """Five domes, central glazed iron hall and an east entrance beneath a segmental gable."""
    w,d,h=7.3,8,29
    def draw(s):
        wall=windows(STONE,h,10,13,True,True)
        block(s,i,j,w,d,h,STONE,wall,z=z)
        band(s,i,j,w,d,z+12,MARBLE,2);band(s,i,j,w,d,z+h-1,MARBLE,2)
        hip_roof(s,i,j,w,d,z+h,5,ZINC)
        # Four corner pavilions, drawn around the central dome rather than hiding behind it.
        for a,b in sorted(((i,j),(i+w-2.1,j),(i,j+d-2.1),(i+w-2.1,j+d-2.1)),key=lambda p:sum(p)):
            block(s,a,b,2.1,2.1,35,STONE,windows(STONE,35,9,13,True,True),z=z)
            band(s,a,b,2.1,2.1,z+34,MARBLE,2)
            revolve(s,a+1.05,b+1.05,1.3,z+36,12,[(0,1),(.25,.95),(.75,.55),(1,.16)],ZINC,ribs=3)
            cylinder(s,a+1.05,b+1.05,.2,.2,z+48,3,STONE,segments=12)
            roundel(s,a+1.05,b+2.13,z+29,2.4,True,STONE)
        ci,cj=i+3.6,j+4
        cylinder(s,ci,cj,2.1,2.1,z+33,10,STONE,windows(STONE,10,8,10,True,True))
        revolve(s,ci,cj,2.35,z+43,23,[(0,1),(.2,.96),(.55,.8),(.83,.44),(1,.12)],DOME_GLASS,ribs=2,segments=40)
        cylinder(s,ci,cj,.4,.4,z+66,4,ZINC,segments=12)
        revolve(s,ci,cj,.6,z+70,4,DOME,ZINC,ribs=3)
        # East (+i) entrance arch, paired composite columns along +j, carved clock panel.
        a=i+w+.2;b=j+2.1;span=3.8
        def entrance(u,v,lit):
            if lit or not (6<u<24 and 2<v<31):
                return None
            if int(u) in (7,15,23) or int(v) in (3,11,22,30):
                return MARBLE['mid']
            if 11<v<30:
                return GLASS['dark'] if int(v)%6 else ZINC['deep']
            if int(u)%4==0 and int(v)%4==0:
                return GOLD['lit']
            return WOOD
        block(s,i+w-.1,b,.35,span,35,STONE,entrance,z=z)
        for n in (0,.45,span-.45,span):
            column(s,a+.6,b+n,z+3,31,.23,MARBLE,'ionic')
            # Leaf-shaped relief above the volutes abbreviates the composite capital.
            for off in (-.16,0,.16):
                seg(s,P(s,a+.6+off,b+n,z+31),P(s,a+.6,b+n,z+34),MARBLE['hi'])
        block(s,a,b-.25,.9,span+.5,3,MARBLE,z=z+34)
        # An extruded semicircular segmental pediment above the paired columns.
        for front in (a,a+.9):
            pts=[P(s,front,b-.25,z+37),P(s,front,b+span+.25,z+37)]
            pts += [P(s,front,b+span/2+(span/2+.25)*math.cos(t*math.pi/24),z+37+13*math.sin(t*math.pi/24)) for t in range(25)]
            poly(s,pts,lambda x,y:STONE['dark'] if front==a+.9 else STONE['mid'])
            for pa,pb in zip(pts[2:],pts[3:]):seg(s,pa,pb,MARBLE['hi'])
        roundel(s,a+.92,b+span/2,z+42,4,False,MARBLE)
        x,y=P(s,a+.94,b+span/2,z+42);seg(s,(x,y),(x,y-2),IRON);seg(s,(x,y),(x+2,y+1),IRON)
        for n in range(3):block(s,a+.8+n*.25,b+.3,.3,span-.6,3-n,MARBLE,z=z)
    scene.add(i+j+w+d+4,draw)


def painted_church(material,height,bay=11):
    joints=stone_courses(material,4,12)
    def pattern(u,v,lit):
        c=int(u)%bay
        if int(v) in (2,3,12,13,height-2):return MARBLE['hi' if lit else 'mid']
        if 15<v<height-3:
            # Blue-ground floral scrolls and bounded saint medallions below the eaves.
            if (c-5)**2+((v-19)*.8)**2<8:
                return GOLD['hi'] if int(v)>19 else ICON_BLUE if c%3 else CLAY['lit']
            if c in (0,1):return material['mid']
        if 4<v<11 and abs(c-5)<2:return WOOD if c==5 else material['deep']
        return joints(u,v,lit)
    return pattern


def church_tower(s,ci,cj,z,r,height,material=WHITE,roof=ZINC):
    # Each octagonal facet has its own recessed arched niche and dressed slender opening.
    bay=r*math.pi
    def niche(u,v,lit):
        c=u%bay-bay/2
        half=bay*.31
        crown=height-5+math.sqrt(max(0,1-(c/half)**2))*2
        if abs(c)<half and 3<v<crown:
            if abs(c)>half*.65 or int(v)==3 or v>crown-2:
                return material['mid' if lit else 'deep']
            if 8<v<height-8 and abs(c)<half*.35:
                return material['deep']
            return material['dark' if lit else 'mid']
        return material['hi' if lit and u%bay<.6 else 'lit' if lit else 'dark']
    cylinder(s,ci,cj,r,r,z,height,material,niche,segments=8)
    cylinder(s,ci,cj,r*1.12,r*1.12,z+height,2,MARBLE,segments=8)
    revolve(s,ci,cj,r*1.2,z+height+2,6,[(0,1),(.3,.8),(.75,.35),(1,.08)],roof,ribs=2,segments=16)
    cross(s,ci,cj,z+height+8)


def stavropoleos(scene,i,j,z=0):
    """Small trefoil church, octagonal cupola and open carved/scalloped western porch."""
    w,d,h=4.6,7.6,24
    def draw(s):
        # East apse, then nave with projecting lateral apses.
        cylinder(s,i+w/2,j+.8,1.7,1.3,z,21,STONE,painted_church(STONE,21),segments=20)
        block(s,i+.35,j+.8,w-.7,4.9,h,STONE,painted_church(STONE,h),z=z)
        for a in (i+.35,i+w-.35):
            cylinder(s,a,j+3.2,.85,1.25,z,21,STONE,painted_church(STONE,21),segments=16)
            revolve(s,a,j+3.2,1.1,z+21,5,DOME,CLAY,ribs=4,segments=16)
        hip_roof(s,i-.1,j+.45,w+.2,5.6,z+h,9,CLAY)
        church_tower(s,i+w/2,j+2.8,z+31,.85,13,STONE,CLAY)
        block(s,i,j+5.7,w,1.9,3,MARBLE,z=z)
        block(s,i+.1,j+5.8,w-.2,.3,19,STONE,painted_church(STONE,19),z=z+3)
        # Four sculpted columns, three scalloped open arches. No painted black fake porch.
        for n in range(4):
            a=i+.25+n*(w-.5)/3
            cylinder(s,a,j+d-.1,.15,.15,z+3,14,MARBLE,
                     lambda u,v,lit:STONE['line'] if (int(u)+int(v))%4==0 else None,segments=12)
            block(s,a-.23,j+d-.33,.46,.46,2,STONE,z=z+17)
        for n in range(3):
            a=i+.25+n*(w-.5)/3;b=a+(w-.5)/3
            for k in range(16):
                t=k/15;zz=z+17+3*math.sin(t*math.pi)-.6*math.cos(t*math.pi*6)
                seg(s,P(s,a+(b-a)*t,j+d-.1,zz),P(s,a+(b-a)*t,j+d-.1,z+23),STONE['lit'])
        block(s,i,j+5.7,w,1.9,7,STONE,painted_church(STONE,7),z=z+21)
        for n in range(6):roundel(s,i+.3+n*(w-.6)/5,j+d+.02,z+25,1.8,True,GOLD)
        band(s,i,j+5.7,w,1.9,z+28,STONE,1)
        hip_roof(s,i-.12,j+5.5,w+.24,2.25,z+29,5,CLAY)
    scene.add(i+j+w+d+2,draw)


def parliament(scene,i,j,z=0):
    """Vast broad east facade, lower wings, layered setbacks and central monumental balcony."""
    w,d=10.5,20
    def draw(s):
        # Each upper mass steps inward, keeping the layered silhouette instead of one box.
        tiers=[(i,j,w,d,23,0),(i+.5,j+.4,w-1,d-.8,19,23),
               (i+1.1,j+4.2,w-2.2,d-8.4,19,42),(i+1.8,j+5.8,w-3.6,d-11.6,13,61)]
        for a,b,wi,wj,h,base in tiers:
            block(s,a,b,wi,wj,h,MARBLE,windows(MARBLE,h,10,11,False,True),z=z+base)
            band(s,a,b,wi,wj,z+base+h-1,WHITE,2)
            balustrade(s,(a+wi,b),(a+wi,b+wj),z+base+h+1,3,MARBLE,4)
            balustrade(s,(a,b+wj),(a+wi,b+wj),z+base+h+1,3,MARBLE,4)
        # Paired giant columns articulate the eastern central front, kept shallow to reveal it.
        for n in range(6):
            b=j+6.2+n*1.52
            for off in (0,.38):column(s,i+w-.1,b+off,z+24,25,.19,WHITE)
        block(s,i+w-.1,j+5.6,.65,9,3,WHITE,z=z+50)
        block(s,i+w+.1,j+7.1,1,5.6,3,MARBLE,z=z+23)
        balustrade(s,(i+w+1.1,j+7.1),(i+w+1.1,j+12.7),z+26,4,WHITE,3)
        # Monumental ground portal, cornices, rusticated podium and forecourt stair flights.
        for b in (j+7.7,j+11.1):column(s,i+w+.4,b,z+2,20,.28,MARBLE)
        for n in range(5):block(s,i+w+.3+n*.3,j+7,.35,6,5-n,WHITE,z=z)
    scene.add(i+j+w+d+4,draw)


def patriarchal_cathedral(scene,i,j,z=0):
    """Historic white trefoil cathedral: four polygonal towers, west icon porch, lead roofs."""
    w,d,h=6.2,10.2,25
    def draw(s):
        cylinder(s,i+w/2,j+.7,2.1,1.3,z,23,WHITE,painted_church(WHITE,23),segments=24)
        block(s,i+.4,j+.8,w-.8,6.8,h,WHITE,painted_church(WHITE,h),z=z)
        for a in (i+.4,i+w-.4):
            cylinder(s,a,j+3,.9,1.4,z,23,WHITE,painted_church(WHITE,23),segments=20)
            revolve(s,a,j+3,1.2,z+23,5,DOME,ZINC,ribs=3)
        hip_roof(s,i,j+.3,w,7.6,z+h,7,ZINC)
        # Eastern nave dome at the rear; west pronaos and its two smaller lateral towers.
        for a,b,r,base,hh in sorted(((i+w/2,j+2.6,1.0,31,27),
                                    (i+w/2,j+6.4,.94,31,25),
                                    (i+1.1,j+7.4,.64,29,22),
                                    (i+w-1.1,j+7.4,.64,29,22)),key=lambda p:sum(p[:2])):
            church_tower(s,a,b,z+base,r,hh)
        # Open west porch with six columns; icons sit above arches, not in the openings.
        block(s,i,j+7.8,w,2.4,3,MARBLE,z=z)
        block(s,i+.2,j+7.9,w-.4,.25,21,WHITE,painted_church(WHITE,21),z=z+3)
        for n in range(6):
            a=i+.25+n*(w-.5)/5
            cylinder(s,a,j+d-.15,.17,.17,z+3,14,MARBLE,segments=12)
            block(s,a-.24,j+d-.39,.48,.48,2,WHITE,z=z+17)
        for n in range(5):
            a=i+.25+n*(w-.5)/5;b=a+(w-.5)/5
            for k in range(13):
                t=k/12;zz=z+17+3*math.sin(t*math.pi)
                seg(s,P(s,a+(b-a)*t,j+d-.15,zz),P(s,a+(b-a)*t,j+d-.15,z+23),WHITE['lit'])
        block(s,i,j+7.8,w,2.4,9,WHITE,painted_church(WHITE,9),z=z+23)
        for n in range(11):roundel(s,i+.3+n*(w-.6)/10,j+d+.02,z+28,1.7,True,GOLD)
        band(s,i,j+7.8,w,2.4,z+32,MARBLE,2)
        hip_roof(s,i-.1,j+7.7,w+.2,2.6,z+34,3,ZINC)
        for n in range(3):block(s,i+1-n*.25,j+d+n*.25,w-2+n*.5,.3,3-n,MARBLE,z=z)
    scene.add(i+j+w+d+3,draw)


def townhouse(scene,i,j,wi=2.5,wj=3,floors=2,seed=0,z=0):
    """Lipscani Belle Époque/neo-Romanian houses: stucco hoods, shops, iron balconies and dormers."""
    material=palette_of(WALLS[seed%len(WALLS)]);h=floors*11+4
    base=windows(material,h,10,11,seed%3==0)
    def wall(u,v,lit):
        c=int(u)%10
        if v<10 and 2<=c<=7:
            if c in (2,7) or int(v)==9:return MARBLE['lit' if lit else 'dark']
            return WOOD if (int(u)//10+seed)%3==0 else GLASS['mid' if lit else 'dark']
        return base(u,v,lit)
    def draw(s):
        block(s,i,j,wi,wj,h,material,wall,z=z)
        band(s,i,j,wi,wj,z+1,ROCK,2);band(s,i,j,wi,wj,z+h-1,WHITE,2)
        if seed%3:
            mansard(s,i-.05,j-.05,wi+.1,wj+.1,z+h,12,.65,roof=ZINC,dormers=8)
        else:hip_roof(s,i-.08,j-.08,wi+.16,wj+.16,z+h,12,CLAY)
        # Projecting iron balcony on consoles and its two stone corbels.
        if floors>1 and seed%2==0:
            block(s,i+.4,j+wj,wi-.8,.4,1,MARBLE,z=z+13)
            for a in (i+.5,i+wi-.5):block(s,a,j+wj,.2,.25,3,STONE,z=z+10)
            for n in range(9):
                a=i+.4+(wi-.8)*n/8
                seg(s,P(s,a,j+wj+.4,z+14),P(s,a,j+wj+.4,z+18),IRON)
            seg(s,P(s,i+.4,j+wj+.4,z+18),P(s,i+wi-.4,j+wj+.4,z+18),IRON)
        block(s,i+wi-.7,j+.5,.4,.4,8,STONE,z=z+h+4)
        band(s,i+wi-.7,j+.5,.4,.4,z+h+11,MARBLE,2)
        if seed%7==0:
            pediment(s,i+.2,j+wj-.3,wi-.4,.35,z+h,7,WHITE)
    scene.add(i+j+wi+wj+1,draw)


# name, builder, footprint, true (longitude,latitude), compressed north-up ground anchor, elevation.
SITES = [
    ('triumph',triumph,(7.8,3.4),(26.0781528,44.4671639),(100,130),0),
    ('athenaeum',athenaeum,(8.6,9.3),(26.0973,44.4413),(535,176),0),
    ('royal-palace',royal_palace,(7.6,12.8),(26.095943,44.439362),(350,238),0),
    ('cec-palace',cec_palace,(9.2,8),(26.0965,44.4320),(430,318),0),
    ('stavropoleos',stavropoleos,(4.6,7.6),(26.0987944,44.4318222),(650,360),0),
    ('parliament',parliament,(12.5,20),(26.08750,44.42750),(235,442),16),
    ('patriarchal-cathedral',patriarchal_cathedral,(6.2,11),(26.0978222,44.4245944),(550,480),18),
]


def main():
    for name,builder,_,_,_,_ in SITES:
        print(preview([lambda s,b=builder:b(s,4,4)],'bucharest-'+name,
                      size=(330,300),origin=(165,120),tiles=26))
    print(preview([lambda s,n=n:townhouse(s,3+n*3.8,3,floors=1+n%3,seed=n)
                   for n in range(7)],'bucharest-houses',size=(340,240),origin=(70,90),tiles=28))
    import sprites
    if hasattr(sprites,'bran'):
        im=sprites.bran();p=Path(__file__).resolve().parents[2]/'docs/art/capitals/romania-bran.png'
        im.resize((im.width*4,im.height*4),0).save(p);print(p)


if __name__=='__main__':main()
