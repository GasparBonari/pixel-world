"""Skopje's researched north-up Vardar diorama, built from projected (i, j, z) geometry.

DEVELOPMENT_PLAN.md records independent coordinates, settings, silhouette counts and front turns.
Run for seven isolated 4× landmark studies, local houses and the Kaneo country sprite.
"""
import math
from pathlib import Path

import iso
from iso import rgb
from landmarks_paris import P, seg, poly, corners, preview, GLASS
from landmarks_iberia import hip_roof, crenellate, stone_courses, arch_opening, palette_of, tones
from landmarks_slovakia import block, band, pediment, cross
from landmarks_slovenia import windows, revolve, DOME
from landmarks_bosnia import cylinder, wall_edge
from landmarks_albania import open_arch

STONE = tones('#F4E6CD', '#D9C7A6', '#BFA989', '#9B8467', '#715D46', '#AC9473', '#493B2D')
WHITE = tones('#FFFDF0', '#EEE8D4', '#D7CEB8', '#B6AA94', '#817460', '#C7BBA3', '#514633')
BRICK = tones('#E6B093', '#BF8066', '#A86A50', '#834C39', '#593326', '#965A43', '#43291F')
LEAD = tones('#B9C1BF', '#939F9E', '#77898B', '#586E74', '#3A4E58', '#687D81', '#293B46')
GREEN = tones('#BCC6A4', '#8A9B7B', '#6E8369', '#4C6556', '#34493E', '#60745D', '#263B32')
CLAY = tones('#E9A67A', '#C57C52', '#AC613D', '#83432D', '#5B3021', '#9D5335', '#48281D')
WOOD = tones('#D0AA7B', '#A5774E', '#875C3B', '#63402B', '#432B20', '#775034', '#33221B')
GOLD = tones('#FFF1AF', '#E2C56F', '#C2A24B', '#967731', '#655021', '#AE8D3C', '#4D3D1E')
ROCK = tones('#D9D0B7', '#B3A58B', '#998B72', '#786A52', '#554D3D', '#8B7D63', '#3D372C')
WALLS = [rgb(c) for c in ('#E6D6B3','#D6B590','#ECE4CD','#C6CDB7','#C8A39A','#BBCBCD')]
IRON = rgb('#35413E')
WATER = tuple(rgb(c) for c in ('#608E8B','#487573','#C5DED4'))
GROUND = {k:rgb(v) for k,v in {
    'square':'#DAD0BB','joint':'#BCB199','rose':'#CAB9A8','cobble':'#B7A78D',
    'cobble_joint':'#96866D','garden':'#8BA76B','garden_light':'#AEC284',
}.items()}


def masonry(u,v,lit):
    """Alternating warm rubble and thin red brick ties, clipped by facade()."""
    if int(v)%12 in (0,1):return BRICK['lit' if lit else 'dark']
    return stone_courses(STONE,5,11)(u,v,lit)


def spire(s,ci,cj,z):
    block(s,ci-.53,cj-.53,1.06,1.06,10,STONE,z=z)
    cylinder(s,ci,cj,.43,.43,z+10,53,STONE,stone_courses(STONE,5,10),segments=12)
    for zz,r,h in ((61,.51,2),(63,.65,2),(65,.77,2),(67,.76,2)):
        cylinder(s,ci,cj,r,r,z+zz,h,WHITE,segments=12)
    for n in range(12):
        a=n*math.tau/12
        seg(s,P(s,ci+.72*math.cos(a),cj+.72*math.sin(a),z+68),
            P(s,ci+.72*math.cos(a),cj+.72*math.sin(a),z+73),STONE['deep'])
    cylinder(s,ci,cj,.29,.29,z+69,16,WHITE,stone_courses(WHITE,4,8),segments=12)
    revolve(s,ci,cj,.45,z+85,22,[(0,1),(.15,.92),(1,.02)],LEAD,ribs=4)
    seg(s,P(s,ci,cj,z+107),P(s,ci,cj,z+113),GOLD['dark'])
    x,y=P(s,ci,cj,z+114)
    for dx,dy in ((1,0),(0,-1),(-1,-2),(-1,-3),(0,-4),(1,-4)):s.put(x+dx,y+dy,GOLD['lit'])


def mustafa(scene,i,j,z=0):
    """One main lead dome, triple-domed marble porch, one western minaret after 90° turn."""
    W,D,H=6.7,7.1,34
    def draw(s):
        def openings(u,v,lit):
            for low,high in ((5,17),(22,29)):
                if low<v<high:
                    c=int(u)%15
                    hole=arch_opening(c,v-low,7,2.5,high-low-1,WOOD['deep'])
                    if hole:return WHITE['lit' if lit else 'dark'] if c in (4,10) else hole
            return masonry(u,v,lit)
        block(s,i+.4,j+.3,W-1.2,D-2,H,STONE,openings,z=z)
        band(s,i+.4,j+.3,W-1.2,D-2,z+H-2,WHITE,2)
        ci,cj=i+W/2-.2,j+(D-2)/2+.3
        cylinder(s,ci,cj,2.65,2.65,z+H,7,STONE,masonry,segments=8)
        revolve(s,ci,cj,2.78,z+H+7,22,DOME,LEAD,ribs=4)
        seg(s,P(s,ci,cj,z+H+29),P(s,ci,cj,z+H+35),GOLD['dark'])
        # The real NW porch is turned to SW; keep its four columns and three open arches.
        for n in range(3):
            a=i+.4+n*1.8
            open_arch(s,a,j+D-1.3,1.8,.65,z+3,23,WHITE)
            block(s,a,j+D-1.35,1.8,1.4,2,WHITE,z=z+26)
            revolve(s,a+.9,j+D-.65,.97,z+28,10,DOME,LEAD,ribs=6)
        for n in range(4):
            a=i+.4+n*1.8
            cylinder(s,a,j+D-.75,.13,.13,z+2,19,WHITE,segments=12)
            block(s,a-.22,j+D-.97,.44,.44,2,WHITE,z=z+20)
        spire(s,i+.05,j+D-1.15,z)
        # Recessed central door and carved frame, behind the genuinely open portico.
        block(s,ci-.47,j+D-1.8,.94,.15,15,WHITE,
              lambda u,v,lit:WOOD['deep'] if 1<u<6 and v<13 else WHITE['lit'],z=z)
        for k in range(3):block(s,i+.3,j+D+.05+k*.23,5.5,.28,3-k,STONE,z=z)
    scene.add(i+j+W+D+2,draw)


def kale(scene,i,j,z=0):
    """Long low battlement enclosure, selected square and rounded towers, open archaeology."""
    W,D=12,5.8
    def draw(s):
        poly(s,list(corners(s,i,j,W,D,z)),lambda x,y:GROUND['garden'] if (x+y)%13 else ROCK['mid'])
        # Excavated foundations remain low within the enclosure, rather than a fantasy palace.
        for a,b,w,d in ((i+2,j+1.3,3,.3),(i+2,j+1.3,.3,2),(i+6,j+1.1,3.2,.3),(i+7,j+2.2,2,.3)):
            block(s,a,b,w,d,2,STONE,z=z)
        for a,b,w,d,h in ((i,j,W,.6,17),(i,j,.6,D,17),(i+W-.6,j,.6,D,19),(i,j+D-.65,W,.65,16)):
            block(s,a,b,w,d,h,STONE,stone_courses(STONE,4,13),z=z)
            crenellate(s,a,b,w,d,z+h,STONE,set(),step=6)
        # Two square flank towers, one square middle tower, one rounded western tower.
        towers=[(i+W-1.35,j-.3,1.7,1.7,31),(i+W-1.35,j+D-1.35,1.7,1.7,28),
                (i+5.8,j+D-1.2,1.7,1.7,34)]
        for a,b,w,d,h in sorted(towers,key=lambda p:p[0]+p[1]):
            def slits(u,v,lit):
                if 12<v<22 and int(u)%11 in (5,6):return STONE['deep']
                return stone_courses(STONE,4,12)(u,v,lit)
            block(s,a,b,w,d,h,STONE,slits,z=z)
            band(s,a,b,w,d,z+h-2,STONE,2)
            crenellate(s,a,b,w,d,z+h,STONE,set(),step=4)
        ci,cj=i+.6,j+D-.5
        cylinder(s,ci,cj,1,1,z,25,STONE,stone_courses(STONE,4,11),segments=16)
        for n in range(12):
            a=n*math.tau/12
            block(s,ci+.86*math.cos(a)-.16,cj+.86*math.sin(a)-.16,.32,.32,3,STONE,z=z+25)
        # Buttresses at the lower curtain; the eastern gate is on its hidden side.
        for a in (i+2,i+4,i+9):block(s,a,j+D-.1,.4,.6,11,STONE,z=z)
    scene.add(i+j+W+D+3,draw)


def hammam(scene,i,j,z=0):
    """Thirteen lead domes: two large western changing rooms, eleven small eastern rooms."""
    # These world-space centres put both large domes west of every small dome.
    rooms=[(1.6,5.8,1.55,23,15),(1.7,2.5,1.55,23,15),
           (4.4,4.2,.8,16,8),(4.4,2.35,.75,16,8),(4.4,.6,.65,14,7),
           (6.2,4.2,.75,16,8),(6.2,2.4,.75,17,9),(6.2,.6,.7,14,7),
           (8,4.2,.7,14,7),(8,2.5,.75,16,8),(8,.7,.7,14,7),
           (9.7,3.4,.68,14,7),(9.7,1.4,.7,14,7)]
    def draw(s):
        def walls(u,v,lit):
            # Small dressed arches on the bathhouse's otherwise massive rubble walls.
            c=int(u)%18
            hole=arch_opening(c,v-3,8,2.2,8,WOOD['deep']) if 3<v<14 else None
            return hole or masonry(u,v,lit)
        for ci,cj,r,H,rise in sorted(rooms,key=lambda p:p[0]+p[1]):
            a,b=i+ci-r,j+cj-r
            block(s,a,b,r*2,r*2,H,STONE,walls,z=z)
            band(s,a,b,r*2,r*2,z+H-1,BRICK,1)
            cylinder(s,i+ci,j+cj,r*.98,r*.98,z+H,3,STONE,masonry,segments=8)
            revolve(s,i+ci,j+cj,r*1.02,z+H+3,rise,DOME,LEAD,ribs=6)
            # Three glass roof lights on each large dome, one on each small dome.
            for dx,dy in ((0,0),(-.5,.1),(.1,.5)) if r>1 else ((0,0),):
                cylinder(s,i+ci+dx,j+cj+dy,.09,.09,z+H+rise+1,1.5,WHITE,segments=8)
        # West men's doorway exposed on snapped SW face, northern door naturally hidden.
        open_arch(s,i+.4,j+7.35,1.25,.35,z,17,STONE)
    scene.add(i+j+18,draw)


def dome(s,ci,cj,r,base,rise,material,edge_height=15):
    """Hemisphere clipped by four arched lunettes: curved roof, scalloped concrete eave."""
    faces=[];rim=[]
    def point(t,ang):
        edge=edge_height*abs(math.cos(2*ang))
        height=edge+(rise-edge)*t
        radius=r*math.sqrt(max(0,1-(height/rise)**2))
        return P(s,ci+radius*math.cos(ang),cj+radius*math.sin(ang),base+height)
    for k in range(12):
        for n in range(64):
            a,b=n*math.tau/64,(n+1)*math.tau/64
            pts=[point(k/12,a),point(k/12,b),point((k+1)/12,b),point((k+1)/12,a)]
            light=math.sin((a+b)/2)-.6*math.cos((a+b)/2)
            key='hi' if light>.95 else 'lit' if light>.1 else 'mid' if light>-.45 else 'dark'
            faces.append((math.cos(a)+math.sin(a)+math.cos(b)+math.sin(b),k,pts,key,n))
            if k==0:rim.append((a,b,pts[0],pts[1]))
    for _,k,pts,key,n in sorted(faces,key=lambda p:(p[0],p[1])):
        poly(s,pts,lambda x,y,key=key:material[key])
        if n%8==0:seg(s,pts[0],pts[3],material['mid' if key in ('hi','lit') else 'deep'])
    for a,b,pa,pb in rim:
        if math.cos((a+b)/2)+math.sin((a+b)/2)<0:continue
        seg(s,pa,pb,WHITE['lit'],2)
        seg(s,(pa[0],pa[1]+2),(pb[0],pb[1]+2),WHITE['dark'])


def clement(scene,i,j,z=0):
    """Scalloped green shells, four lanterns; separate NW tapered belfry and clock crown."""
    ci,cj=i+4.1,j+4.1
    def draw(s):
        # OSM puts this separate belfry NW. Architectural drawings confirm a tapered
        # solid shaft with recessed arched panels, an open bell stage and a clock cube.
        ti,tj=i-2.2,j+1.4
        block(s,ti-.35,tj-.35,2.5,2.5,7,STONE,z=z)
        for k in range(6):
            w=2.05-k*.115;inset=(2.05-w)/2
            def shaft(u,v,lit):
                c=u-w*4
                if abs(c)<2.1 and 2<v<11-abs(c)*.7:
                    return STONE['deep'] if abs(c)<1 else STONE['mid']
                if abs(c)<3.1 and 1<v<12:return WHITE['hi' if lit else 'mid']
                return WHITE['lit' if lit else 'dark']
            block(s,ti+inset,tj+inset,w,w,12,WHITE,shaft,z=z+7+k*12)
            band(s,ti+inset,tj+inset,w,w,z+18+k*12,WHITE,1)
        # Separate bell stage, with a real open gap and three bells at staggered heights.
        w=1.5;a,b=ti+.27,tj+.27
        for di,dj in ((0,0),(w-.22,0),(0,w-.22),(w-.22,w-.22)):
            block(s,a+di,b+dj,.22,.22,11,WHITE,z=z+81)
        for h in (80,91):band(s,a-.1,b-.1,w+.2,w+.2,z+h,WHITE,2)
        for di,dj,h in ((.45,.45,84),(.95,.45,86),(.75,1.0,83)):
            cylinder(s,a+di,b+dj,.15,.15,z+h,2.5,GOLD,segments=12)
        # Broad projecting canopy under the four-sided clock cube, flat cap and cross.
        band(s,a-.3,b-.3,w+.6,w+.6,z+94,WHITE,3)
        block(s,a+.1,b+.1,1.3,1.3,12,WHITE,z=z+97)
        for lit in (True,False):
            def point(u,v):
                return P(s,a+.75+u/8 if lit else a+1.4,
                         b+1.4 if lit else b+.75-u/8,z+103+v)
            ring=[point(math.cos(n*math.tau/24)*3.2,math.sin(n*math.tau/24)*3.2) for n in range(24)]
            poly(s,ring,lambda x,y:WHITE['hi'])
            for pa,pb in zip(ring,ring[1:]+ring[:1]):seg(s,pa,pb,STONE['deep'])
            for n in range(12):
                ang=n*math.tau/12
                seg(s,point(math.cos(ang)*2.5,math.sin(ang)*2.5),point(math.cos(ang)*3.1,math.sin(ang)*3.1),IRON)
            seg(s,point(0,0),point(-1.8,1.2),IRON)
            seg(s,point(0,0),point(.3,2.1),IRON)
        band(s,a,b,1.5,1.5,z+109,WHITE,1)
        cross(s,a+.75,b+.75,z+111,GOLD)
        # Far NW arch foot belongs behind the shell, never on top of its roof.
        block(s,ci-3.2,cj-3.2,.4,.4,23,WHITE,z=z)
        cylinder(s,ci,cj,3.0,3.0,z,28,STONE,
                 windows(STONE,28,13,14,arched=True,width=7),segments=32)
        # Main entrance is west, snapped SW. Deep door beneath the shell's open arch.
        block(s,ci-1,j+7.3,2,.22,22,WHITE,
              lambda u,v,lit:WOOD['dark'] if 1<u<14 and v<20 else WHITE['lit'],z=z)
        dome(s,ci,cj,4.25,z+22,25,GREEN)
        # Four small corner lanterns sit below the upper dome, not extra bell towers.
        for a,b in ((ci-2.2,cj-2.2),(ci+2.2,cj-2.2),(ci-2.2,cj+2.2),(ci+2.2,cj+2.2)):
            cylinder(s,a,b,.55,.55,z+39,9,WHITE,
                     lambda u,v,lit:GLASS['dark'] if int(u)%5 in (2,3) and 2<v<7 else None,segments=8)
            revolve(s,a,b,.65,z+48,5,DOME,GREEN,ribs=4)
            cross(s,a,b,z+51,GOLD)
        def drum_glass(u,v,lit):
            c=int(u)%16
            opening=arch_opening(c,v-1,8,6.2,16,GLASS['dark'])
            if opening:
                if abs(c-8)<.6 or int(v)==8:return WHITE['lit' if lit else 'dark']
                return opening
            return WHITE['lit' if lit else 'dark']
        cylinder(s,ci,cj,2.1,2.1,z+45,18,WHITE,drum_glass,segments=32)
        dome(s,ci,cj,2.55,z+63,26,GREEN,edge_height=9)
        cross(s,ci,cj,z+89,GOLD)
        # The white ribs are the actual clipped roof edges, meeting four concrete feet.
        for a,b in ((ci+3,cj-3),(ci-3,cj+3),(ci+3,cj+3)):
            block(s,a-.2,b-.2,.4,.4,23,WHITE,z=z)
            band(s,a-.2,b-.2,.4,.4,z+1,STONE,2)
        for k in range(4):block(s,i+2,j+8.4+k*.22,4,.28,4-k,STONE,z=z)
    scene.add(i+j+20,draw)


def stonebridge(scene,i,j,z=0):
    """Thirteen actual open semicircular arches along +j, solid parapets and cutwaters."""
    W,L,span=1.9,15.6,1.2
    def draw(s):
        # Far parapet first. Every bridge face is a projected/extruded wall, never a cutout.
        block(s,i,j,W*.13,L,3,STONE,stone_courses(STONE,3,10),z=z+13)
        for n in range(13):
            a=j+n*span
            open_arch(s,i,a,span,W,z-3,15,STONE,False)
            if n in (2,4,6,8,10):
                p=[(i+W,a-.19),(i+W+.55,a),(i+W,a+.19)]
                poly(s,[P(s,*q,z+7) for q in p],lambda x,y:STONE['lit'])
                for aa,bb in zip(p,p[1:]+p[:1]):wall_edge(s,aa,bb,z-3,10,STONE,lit=False)
        # Deck stays above arch crowns, with humped central profile.
        for n in range(13):
            base=z+12+2*math.sin((n+.5)*math.pi/13)
            block(s,i,j+n*span,W,span,1,STONE,z=base)
            poly(s,list(corners(s,i+.12,j+n*span,W-.24,span,base+1)),
                 lambda x,y:GROUND['joint'] if (x+3*y)%7==0 else WHITE['mid'])
            block(s,i+W-.18,j+n*span,.18,span,3,STONE,stone_courses(STONE,3,9),z=base+1)
        # Central historic mihrab recess on downstream/SE side, not an invented tower.
        a=j+L*.47
        block(s,i+W-.2,a,.4,.9,13,STONE,
              lambda u,v,lit:WOOD['deep'] if 1<u<6 and v<9 else masonry(u,v,lit),z=z+13)
        hip_roof(s,i+W-.28,a-.08,.56,1.06,z+26,3,STONE)
    scene.add(i+j+W+L+2,draw)


def museum(scene,i,j,z=0):
    """Long waterfront colonnade, triangular pediment and two round domed end pavilions."""
    W,D,H=13,4.5,39
    def draw(s):
        def glazing(u,v,lit):
            if 5<v<35:
                if int(u)%10 in (0,1) or int(v)%14==0:return WHITE['dark']
                return GLASS['dark'] if int(u)%10<6 else LEAD['deep']
            return stone_courses(WHITE,5,13)(u,v,lit)
        block(s,i+.4,j,W-.8,D-1,H,WHITE,glazing,z=z+5)
        hip_roof(s,i+.2,j-.1,W-.4,D-1,z+H+5,5,LEAD)
        for a in (i+1.2,i+W-1.2):
            cylinder(s,a,j+D-1.15,1.3,1.3,z+5,H,WHITE,glazing,segments=24)
        # Deep continuous portico; fluted three-dimensional columns with dressed capitals.
        for k in range(17):
            a=i+.25+k*(W-.5)/16
            cylinder(s,a,j+D-.35,.13,.13,z+8,31,WHITE,
                     lambda u,v,lit:WHITE['mid' if lit else 'deep'] if int(u)%3==0 else None,segments=12)
            block(s,a-.22,j+D-.57,.44,.44,2,WHITE,z=z+7)
            block(s,a-.27,j+D-.62,.54,.54,2.5,WHITE,z=z+39)
            # Volutes are small stone scrolls in the capital, not flat striping on the wall.
            for q in (-.22,.22):cylinder(s,a+q,j+D-.35,.09,.09,z+40,1.5,WHITE,segments=8)
        for h in (42,45,47):band(s,i-.15,j+D-1.55,W+.3,1.8,z+h,WHITE,2)
        pediment(s,i+3.3,j+D-1.55,6.4,1.85,z+49,15,WHITE)
        # Relief medallion and a small sculpted laurel within the triangular tympanum.
        for n in range(16):
            a=n*math.tau/16
            p=P(s,i+6.5+math.cos(a)*.36,j+D+.32,z+55+math.sin(a)*3)
            s.put(*p,STONE['mid'])
        for a in (i+1.2,i+W-1.2):
            cylinder(s,a,j+D-1.15,1.4,1.4,z+H+5,5,WHITE,
                     lambda u,v,lit:LEAD['deep'] if int(u)%6 in (2,3) and 1<v<4 else None,segments=24)
            revolve(s,a,j+D-1.15,1.43,z+H+10,10,DOME,LEAD,ribs=4)
            seg(s,P(s,a,j+D-1.15,z+H+20),P(s,a,j+D-1.15,z+H+25),GOLD['dark'])
        for k in range(5):block(s,i-.2,j+D+.3+k*.25,W+.4,.3,5-k,STONE,z=z)
    scene.add(i+j+W+D+3,draw)


def porta(scene,i,j,z=0):
    """Single marble barrel vault, engaged columns, relief panels, attic medallion; no quadriga."""
    W,D=7.8,2.9
    def relief(u,v,lit):
        base=stone_courses(WHITE,5,13)(u,v,lit)
        c=int(u)%12
        # Dressed rectangular panels with bas-relief figures, restricted to the masonry.
        for low,high in ((6,16),(20,30),(48,58)):
            if low<v<high:
                q=int(v-low)
                if c in (1,10) or q in (1,high-low-1):return STONE['mid']
                if c in (5,6) and q in (6,7):return WHITE['deep']
                if 4<=c<=7 and 2<q<6:return STONE['mid' if lit else 'dark']
        return base
    def draw(s):
        for a in (i,i+W-1.8):
            block(s,a,j,1.8,D,42,WHITE,relief,z=z)
            band(s,a,j,1.8,D,z+2,STONE,3)
        # Solid spandrel on both end faces, above the curve; the passage remains open.
        for along_j,lit in ((0,False),(D,True)):
            curve=[(4.4/2+4.4/2*math.cos(n*math.pi/32),
                    42-4.4*3.5+(4.4*3.5)*math.sin(n*math.pi/32)) for n in range(33)]
            pts=[P(s,i+1.7,j+along_j,z+42),P(s,i+6.1,j+along_j,z+42)]
            pts += [P(s,i+1.7+u,j+along_j,z+v) for u,v in curve]
            poly(s,pts,lambda x,y,lit=lit:WHITE['lit' if lit else 'dark'] if y%5 else WHITE['mid'])
        # Large empty passage and extruded intrados, same width on both ends.
        open_arch(s,i+1.7,j,4.4,D,z,42,WHITE)
        for a in (i+.25,i+1.35,i+W-1.6,i+W-.5):
            cylinder(s,a,j+D+.08,.16,.16,z+4,32,WHITE,
                     lambda u,v,lit:WHITE['mid'] if int(u)%3==0 else None,segments=12)
            block(s,a-.23,j+D-.15,.46,.46,3,WHITE,z=z+35)
            band(s,a-.23,j+D-.15,.46,.46,z+38,WHITE,2)
        for h in (40,43,46):band(s,i-.15,j-.08,W+.3,D+.16,z+h,WHITE,2)
        block(s,i-.05,j-.02,W+.1,D+.04,15,WHITE,relief,z=z+48)
        for h in (61,64,66):band(s,i-.2,j-.15,W+.4,D+.3,z+h,WHITE,2)
        # Central circular attic medallion, projected in the front wall plane.
        center=i+W/2
        for radius,key in ((.55,'mid'),(.43,'lit')):
            pts=[P(s,center+radius*math.cos(a),j+D+.04,z+55+radius*8*math.sin(a))
                 for a in [n*math.tau/32 for n in range(32)]]
            poly(s,pts,lambda x,y,key=key:STONE[key])
        seg(s,P(s,center,j+D+.05,z+52),P(s,center,j+D+.05,z+58),WHITE['hi'])
    scene.add(i+j+W+D+2,draw)


def townhouse(scene,i,j,wi=2.5,wj=3,floors=2,seed=0,z=0):
    """Skopje bazaar houses: overhanging white/tinted upper floors, dark timber and clay hips."""
    material=palette_of(WALLS[seed%len(WALLS)]);H=floors*11+3
    base=windows(material,H,9,11,hood=seed%3==0)
    def pattern(u,v,lit):
        c,level=int(u)%9,int(v)%11
        if v<10:
            if 1<=c<=7:
                if c in (1,7) or int(v)==9:return WOOD['lit' if lit else 'dark']
                return WOOD['dark'] if (int(u)//9+seed)%3==0 else GLASS['dark']
            return stone_courses(STONE,4,10)(u,v,lit)
        if seed%2==0 and c in (0,8):return WOOD['lit' if lit else 'dark']
        return base(u,v,lit)
    def draw(s):
        block(s,i,j,wi,wj,12,STONE,pattern,z=z)
        # Projecting timber-supported living storey is distinctive to the old bazaar.
        block(s,i-.12,j-.12,wi+.24,wj+.24,H-10,material,
              lambda u,v,lit:pattern(u,v+10,lit),z=z+10)
        band(s,i,j,wi,wj,z+1,STONE,2)
        band(s,i-.12,j-.12,wi+.24,wj+.24,z+10,WOOD,1)
        band(s,i-.12,j-.12,wi+.24,wj+.24,z+H-1,WHITE,2)
        for a in (i+.3,i+wi-.4):block(s,a,j+wj,.16,.22,4,WOOD,z=z+7)
        hip_roof(s,i-.32,j-.32,wi+.64,wj+.64,z+H+1,10+seed%3,CLAY)
        block(s,i+wi-.7,j+.4,.42,.48,8,STONE,stone_courses(STONE,3,7),z=z+H+4)
        band(s,i+wi-.7,j+.4,.42,.48,z+H+11,CLAY,2)
        if seed%4==1:
            block(s,i+.5,j+wj+.12,1.1,.42,1.5,WHITE,z=z+12)
            for k in range(6):seg(s,P(s,i+.5+k*.22,j+wj+.54,z+14),P(s,i+.5+k*.22,j+wj+.54,z+18),IRON)
            seg(s,P(s,i+.5,j+wj+.54,z+18),P(s,i+1.6,j+wj+.54,z+18),IRON)
    scene.add(i+j+wi+wj+1,draw)


def main():
    for name,builder,_,_,_,elevation in SITES:
        print(preview([lambda s,b=builder,z=elevation:b(s,6,6,z=z)],'skopje-'+name,
                      size=(320,285),origin=(160,120),tiles=25))
    print(preview([lambda s,k=k:townhouse(s,3+k*3.6,4,floors=1+k%3,seed=k)
                   for k in range(6)],'skopje-houses',size=(340,240),origin=(80,75),tiles=27))
    import sprites
    im=sprites.kaneo();path=Path(__file__).resolve().parents[2]/'docs/art/capitals/macedonia-kaneo.png'
    im.resize((im.width*4,im.height*4),0).save(path);print(path)


# name, builder, footprint, real longitude/latitude, north-up ground anchor, elevation.
SITES = [
    ('mustafa',mustafa,(6.7,7.1),(21.4354104,42.0020253),(555,145),16),
    ('kale',kale,(12,5.8),(21.4335243,42.0008134),(405,225),30),
    ('hammam',hammam,(11,8),(21.4357236,41.9987239),(630,295),0),
    ('clement',clement,(8.2,8.2),(21.4264089,41.9985276),(130,330),0),
    ('stone-bridge',stonebridge,(1.9,15.6),(21.4332409,41.9971170),(370,395),0),
    ('museum',museum,(13,4.5),(21.4344487,41.9968040),(535,420),0),
    ('porta',porta,(7.8,2.9),(21.4324328,41.9944512),(235,485),0),
]


if __name__=='__main__':
    main()
