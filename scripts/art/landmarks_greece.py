"""Athens: Pentelic marble, roofless Acropolis temples and neoclassical Plaka.

Two-source coordinates, architectural counts, settings and deliberate facade turns are in
DEVELOPMENT_PLAN.md, Phase 4. Run this module for seven isolated 4× studies and local houses.
"""
import math
from pathlib import Path

from iso import rgb
from landmarks_paris import P, seg, poly, preview, GLASS
from landmarks_iberia import hip_roof, stone_courses, palette_of, tones
from landmarks_slovakia import block, band, pediment
from landmarks_bosnia import cylinder
from landmarks_slovenia import windows, revolve

MARBLE = tones('#FFFAE9', '#EDE1C7', '#D6C5A5', '#B6A181', '#827052', '#C4B18E', '#51432E')
WHITE = tones('#FFFFF4', '#F5EEDC', '#E1D8C2', '#C4B79C', '#908168', '#D3C5A9', '#574B38')
OCHRE = tones('#FCE7B7', '#E8CF9D', '#D3B680', '#AF8D59', '#7D613B', '#C3A06C', '#574328')
CLAY = tones('#EFB68C', '#CF8A60', '#B36C47', '#8B4C32', '#613322', '#A65E3D', '#4F2B20')
BLUE = tones('#AED2DA', '#709FB5', '#507E9D', '#365B7D', '#233D5B', '#426D8D', '#1D304A')
ROCK = tones('#E9D9B7', '#C8B591', '#AE9873', '#8C7654', '#64543D', '#9D8662', '#4C4131')
WOOD = tones('#B7A08A', '#8B7054', '#71553E', '#513C2B', '#382B21', '#624932', '#30261E')
IRON = rgb('#354448')
WALLS = [rgb(c) for c in ('#F1DBAE', '#D8A182', '#F3EBD5', '#C6D1BE', '#DAC2BE', '#B9CBD0', '#E8C47F')]
GROUND = {k:rgb(v) for k,v in {
    'square':'#E2D6BF', 'joint':'#C3B599', 'rose':'#D3BFA8', 'cobble':'#CABBA0',
    'cobble_joint':'#AB997B', 'garden':'#8D9F65', 'garden_light':'#ADB97B',
    'dry':'#C5B68C', 'dust':'#DDD0AD', 'track':'#67564C', 'track_line':'#B3A391',
}.items()}


def column(s, ci, cj, base, height, radius=.25, material=MARBLE, order='doric'):
    """Tapered, fluted drums with echinus/abacus or paired Ionic volutes."""
    if order != 'doric':
        for dz,r,h in ((0,1.3,1),(1,1.15,1)):
            cylinder(s,ci,cj,radius*r,radius*r,base+dz,h,material,segments=12)
    bottom = base+(2 if order != 'doric' else 0)
    for n in range(6):
        r=radius*(1-.18*n/5)
        def flutes(u,v,lit):
            if int(u)%3==0:return material['mid' if lit else 'deep']
            if int(v)%7==0:return material['line']
            return material['hi' if lit and int(u)%3==1 else 'lit' if lit else 'dark']
        cylinder(s,ci,cj,r,r,bottom+n*(height-4)/6,(height-4)/6+1,material,flutes,segments=12)
    cylinder(s,ci,cj,radius*1.35,radius*1.35,base+height-3,2,material,segments=12)
    block(s,ci-radius*1.5,cj-radius*1.5,radius*3,radius*3,2,material,z=base+height-1)
    if order == 'ionic':
        for side in (-1,1):
            a=ci+side*radius*1.5
            # Scrolls lie in the front capital plane, at either side of the abacus.
            ring=[P(s,a+radius*.52*math.cos(k*math.tau/16),cj+radius*1.5,
                    base+height-1+radius*4*math.sin(k*math.tau/16)) for k in range(16)]
            poly(s,ring,lambda x,y:material['hi'])
            for pa,pb in zip(ring,ring[1:]+ring[:1]):seg(s,pa,pb,material['line'])
            x,y=P(s,a,cj+radius*1.5,base+height-1);s.put(x,y,material['dark'])


def gable(s,i,j,w,d,z,rise,material,roof=None,broken=False):
    """Extruded triangular end walls and pitched roof; a ruin retains only the end."""
    for b,lit in ((j,False),(j+d,True)):
        points=[P(s,i,b,z),P(s,i+w,b,z),P(s,i+w/2,b,z+rise)]
        poly(s,points,lambda x,y,lit=lit:material['lit' if lit else 'dark'] if (x+3*y)%17 else material['mid'])
        for a,c in zip(points,points[1:]+points[:1]):seg(s,a,c,material['hi' if lit else 'line'])
        # Recessed triangular tympanum surrounded by a projecting geison.
        inset=[P(s,i+.5,b+.02,z+2),P(s,i+w-.5,b+.02,z+2),P(s,i+w/2,b+.02,z+rise-3)]
        poly(s,inset,lambda x,y:material['dark' if lit else 'deep'])
        if broken:
            # A missing central upper section, with no invented pedimental statues.
            poly(s,[P(s,i+w*.32,b+.03,z+3),P(s,i+w*.68,b+.03,z+3),P(s,i+w*.5,b+.03,z+rise-3)],
                 lambda x,y:material['mid'])
    if roof:
        for a,b,lit in ((i,i+w/2,True),(i+w/2,i+w,False)):
            pts=[P(s,a,j,z+(rise if a==i+w/2 else 0)),P(s,b,j,z+(rise if b==i+w/2 else 0)),
                 P(s,b,j+d,z+(rise if b==i+w/2 else 0)),P(s,a,j+d,z+(rise if a==i+w/2 else 0))]
            poly(s,pts,lambda x,y,lit=lit:roof['line'] if (x+2*y)%8==0 else roof['hi' if lit and (x-2*y)%11==0 else 'lit' if lit else 'dark'])
        seg(s,P(s,i+w/2,j,z+rise),P(s,i+w/2,j+d,z+rise),roof['hi'])


def temple(scene,i,j,w,d,columns_end,columns_side,height,z,ruined=False):
    """An open 3D peristyle, not columns painted on an opaque facade."""
    def draw(s):
        for k in range(3):block(s,i+k*.14,j+k*.14,w-k*.28,d-k*.28,2,MARBLE,z=z+k*2)
        x0,x1=i+.62,i+w-.62;y0,y1=j+.62,j+d-.62
        # Naos remains inside the peristyle, with fractured lower wall in the ruin.
        block(s,i+1.25,j+1.6,w-2.5,d-3.2,9 if ruined else height-5,MARBLE,
              stone_courses(MARBLE,4,13),z=z+6)
        if ruined:
            for a,b,ww,dd,h in ((i+1.25,j+1.6,.38,2.0,height-7),
                               (i+w-1.63,j+d-3,.38,1.4,height-9)):
                block(s,a,b,ww,dd,h,MARBLE,stone_courses(MARBLE,5,10),z=z+6)
        positions=[(x0+(x1-x0)*k/(columns_end-1),b) for b in (y0,y1) for k in range(columns_end)]
        positions += [(a,y0+(y1-y0)*k/(columns_side-1)) for a in (x0,x1) for k in range(1,columns_side-1)]
        # Every original slot is represented; the southern middle keeps low broken drums.
        for a,b in sorted(positions,key=lambda p:sum(p)):
            damaged=ruined and a==x1 and y0+(y1-y0)*.35<b<y0+(y1-y0)*.61
            column(s,a,b,z+6,9 if damaged else height,.25 if ruined else .22)
        top=z+height+6
        def frieze(u,v,lit):
            c=int(u)%7
            if 2<v<6 and c in (0,1,2):return MARBLE['deep' if c==1 else 'line']
            if 2<v<6 and c==5:return MARBLE['mid']
            return MARBLE['lit' if lit else 'dark']
        # Interrupted south entablature exposes the ruined cella and column drums.
        for a,b,ww,dd in ((i+.25,j+.25,w-.5,.65),(i+.25,j+d-.9,w-.5,.65),
                          (i+.25,j+.25,.65,d-.5)):
            block(s,a,b,ww,dd,8,MARBLE,frieze,z=top)
            band(s,a,b,ww,dd,top+7,WHITE,1)
        if ruined:
            for b,dd in ((j+.25,d*.30),(j+d*.69,d*.28)):
                block(s,i+w-.9,b,.65,dd,8,MARBLE,frieze,z=top)
                band(s,i+w-.9,b,.65,dd,top+7,WHITE,1)
        else:
            block(s,i+w-.9,j+.25,.65,d-.5,8,MARBLE,frieze,z=top)
            band(s,i+w-.9,j+.25,.65,d-.5,top+7,WHITE,1)
        gable(s,i+.16,j+.24,w-.32,d-.48,top+9,10,MARBLE,CLAY if not ruined else None,ruined)
        if ruined:
            for a,b in ((i+w+.2,j+4),(i+.4,j+d+.3)):
                cylinder(s,a,b,.3,.3,z,2,MARBLE,stone_courses(MARBLE,3,7),segments=12)
    scene.add(i+j+w+d+2,draw)


def parthenon(scene,i,j,z=40):
    """Roofless eight-by-seventeen Doric shell, broken southern colonnade and pediments."""
    temple(scene,i,j,5.8,12.2,8,17,38,z,ruined=True)


def hephaestus(scene,i,j,z=16):
    """Six-by-thirteen intact marble peristyle and pitched clay roof above Agoraios Kolonos."""
    temple(scene,i,j,4.7,9.4,6,13,27,z)


def figure(s,ci,cj,z,material=WHITE,kind='standing',height=18):
    """Solid sculpted volumes: draped torso, head, bent arms, skirt/legs; never a stick."""
    seated=kind=='seated'
    if seated:block(s,ci-.25,cj-.3,.5,.65,6,material,z=z)
    # Flared draped lower body, shoulders and rounded head.
    for n in range(4):
        width=.52-n*.065
        block(s,ci-width/2,cj-.18,width,.35,height*.13,material,
              lambda u,v,lit:material['line'] if int(u)%3==0 else None,z=z+n*height*.13)
    block(s,ci-.2,cj-.17,.4,.34,height*.29,material,z=z+height*.48)
    cylinder(s,ci,cj,.18,.18,z+height*.8,height*.2,material,segments=12)
    for a,b in ((ci-.3,cj-.03),(ci+.25,cj+.05)):
        block(s,a,b,.14,.16,height*.3,material,z=z+height*.4)
    if kind=='athena':
        cylinder(s,ci-.3,cj+.22,.24,.14,z+height*.25,height*.35,material,segments=12)
        seg(s,P(s,ci+.42,cj,z+height*.2),P(s,ci+.42,cj,z+height*1.35),material['dark'])
        block(s,ci-.14,cj-.15,.28,.3,2,material,z=z+height)
    if kind=='apollo':
        for a in (ci+.29,ci+.57):seg(s,P(s,a,cj,z+height*.35),P(s,a,cj,z+height*.78),material['mid'])
        seg(s,P(s,ci+.29,cj,z+height*.78),P(s,ci+.57,cj,z+height*.78),material['hi'])


def erechtheion(scene,i,j,z=32):
    """Roofless Ionic naos, north porch and six solid Caryatids on the SW south porch."""
    W,D=7.2,6.4
    def draw(s):
        block(s,i+.3,j+.3,W-.6,D-1.5,7,MARBLE,stone_courses(MARBLE,4,12),z=z)
        # Main east doorway is on -j and remains hidden. Broken roof leaves the cella open.
        for a,b,w,d,h in ((i+.4,j+.5,.4,D-2,30),(i+W-.8,j+.5,.4,D-2,32),
                           (i+.4,j+.5,W-.8,.4,32)):
            block(s,a,b,w,d,h,MARBLE,stone_courses(MARBLE,4,13),z=z+7)
            band(s,a,b,w,d,z+h+6,WHITE,2)
        # Six eastern Ionic columns, behind the cella, with their carved architrave.
        for k in range(6):column(s,i+.65+k*(W-1.3)/5,j+.08,z+7,34,.21,order='ionic')
        band(s,i+.2,j-.18,W-.4,.65,z+41,WHITE,4)
        # Lower north porch is on the -i side; four across + two returns.
        north=[(i-1.4,j+.7+k*1.03) for k in range(4)]+[(i-.25,j+.7),(i-.25,j+3.79)]
        for a,b in sorted(north,key=lambda p:sum(p)):column(s,a,b,z,39,.22,order='ionic')
        block(s,i-1.8,j+.3,2.3,4.0,4,WHITE,z=z+39)
        band(s,i-1.8,j+.3,2.3,4,z+43,WHITE,2)
        # The southwest corner is at -i on a south-facing +j wall. Four in front,
        # two behind: all six carry the entablature, rather than six poles.
        a,b=i+.1,j+D-1.25
        block(s,a-.2,b-.2,3.5,2,10,MARBLE,stone_courses(MARBLE,4,10),z=z+1)
        positions=[(a+.25+k*.85,b+1.45) for k in range(4)]+[(a+.25,b+.2),(a+2.8,b+.2)]
        for ci,cj in sorted(positions,key=lambda p:sum(p)):
            figure(s,ci,cj,z+11,height=19)
            cylinder(s,ci,cj,.22,.22,z+30,2,MARBLE,segments=12)
        block(s,a-.3,b-.3,3.7,2.25,4,WHITE,stone_courses(WHITE,2,8),z=z+32)
        for h in (31,36,38):band(s,a-.3,b-.3,3.7,2.25,z+h,WHITE,1)
        # Surviving western engaged order and moulded podium; no imaginary gabled roof.
        for k in range(4):column(s,i+3.6+k*.85,j+D-1.65,z+15,25,.18,order='ionic')
    scene.add(i+j+W+D+3,draw)


def winds(scene,i,j,z=0):
    """Octagonal clock tower: eight wind reliefs, sundials, facet roof and south annex."""
    ci,cj=i+2.5,j+2.5;R=2.3
    def draw(s):
        # North-west and north-east entrances stay behind the octagon.
        for di,dj in ((-2.1,0),(0,-2.1)):
            block(s,ci+di-.65,cj+dj-.65,1.3,1.3,3,MARBLE,z=z)
            for a,b in ((ci+di-.45,cj+dj-.45),(ci+di+.45,cj+dj+.45)):
                column(s,a,b,z+3,20,.15,MARBLE,'ionic')
            block(s,ci+di-.7,cj+dj-.7,1.4,1.4,3,WHITE,z=z+24)
        cylinder(s,ci,cj,R+.25,R+.25,z,3,MARBLE,segments=8)
        def carving(u,v,lit):
            c=int(u)%14
            if 39<v<50:
                q=int(v)-39
                if (c-7)**2+(q-8)**2<4:return MARBLE['hi' if lit else 'mid']
                if 5<=c<=9 and 2<q<7:return MARBLE['hi' if lit else 'mid']
                if q in (4,5) and 1<c<12:return MARBLE['mid' if lit else 'line']
                return MARBLE['dark' if lit else 'deep']
            if 17<v<35:
                # The carved sundial rays stay clipped to each octagonal wall panel.
                if any(abs((v-34)-slope*(c-7))<.5 for slope in (-3,-1.4,1.4,3)):
                    return MARBLE['line']
            return stone_courses(MARBLE,5,13)(u,v,lit)
        cylinder(s,ci,cj,R,R,z+3,51,MARBLE,carving,segments=8)
        for zz,r in ((41,R+.08),(53,R+.18),(56,R+.3)):
            cylinder(s,ci,cj,r,r,z+zz,2,WHITE,segments=8)
        # Each of eight compass faces carries one wind figure in its own plane.
        for n in range(8):
            a,b=(n+.5)*math.tau/8,(n+1.5)*math.tau/8
            if math.cos((a+b)/2)+math.sin((a+b)/2)<0:continue
            va=(ci+R*math.cos(a),cj+R*math.sin(a))
            vb=(ci+R*math.cos(b),cj+R*math.sin(b))
            def point(u,v):return P(s,va[0]+(vb[0]-va[0])*u,va[1]+(vb[1]-va[1])*u,z+v)
            # Head, fluttering drapery and outstretched arm in shallow bas-relief.
            poly(s,[point(u,v) for u,v in ((.25,43),(.4,49),(.62,49),(.8,44),(.6,44),(.43,42))],
                 lambda x,y:WHITE['lit'])
            poly(s,[point(.5+math.cos(k*math.tau/12)*.12,50+math.sin(k*math.tau/12)*1.1) for k in range(12)],
                 lambda x,y:WHITE['hi'])
            seg(s,point(.3,47),point(.15,49),WHITE['hi'])
            seg(s,point(.58,47),point(.86,48),WHITE['hi'])
            seg(s,point(.43,44),point(.65,46),MARBLE['line'])
            for u in (.12,.3,.5,.7,.88):
                seg(s,point(.5,38),point(u,27+abs(u-.5)*7),MARBLE['line'])
        # Low southern annex is in front of the main tower, below the sundial panels.
        cylinder(s,ci+1.75,cj+1.75,.85,.85,z,23,MARBLE,stone_courses(MARBLE,4,10),segments=16)
        revolve(s,ci+1.75,cj+1.75,.88,z+23,3,[(0,1),(1,0)],MARBLE,ribs=0,segments=16)
        revolve(s,ci,cj,R+.35,z+58,10,[(0,1),(1,0)],MARBLE,ribs=1,segments=8)
        # No Triton: the ancient bronze vane is no longer on the building.
    scene.add(i+j+12,draw)


def academy(scene,i,j,z=0):
    """Six Ionic portico columns, sculpted pediment, low wings and four philosopher/deity figures."""
    W,D=13,5.6
    def draw(s):
        for a in (i,i+W-3.7):
            block(s,a,j+.1,3.7,3.4,24,WHITE,windows(WHITE,24,10,12,pilasters=True),z=z+4)
            band(s,a,j+.1,3.7,3.4,z+28,WHITE,2)
            hip_roof(s,a-.1,j,3.9,3.6,z+30,6,CLAY)
        block(s,i+3.6,j,5.8,3.6,35,WHITE,
              lambda u,v,lit:WOOD['deep'] if 15<u<25 and v<24 else stone_courses(WHITE,5,13)(u,v,lit),z=z+5)
        for k in range(6):
            column(s,i+3.65+k*1.14,j+4.7,z+8,31,.25,WHITE,'ionic')
        block(s,i+3.25,j+3.4,6.5,1.9,5,WHITE,z=z+40)
        band(s,i+3.25,j+3.4,6.5,1.9,z+45,WHITE,2)
        gable(s,i+3.15,j+.05,6.7,5.35,z+47,13,WHITE,CLAY)
        # Coloured frieze and solid miniature figures in the pediment plane.
        for a in range(6):
            figure(s,i+4.35+a*.85,j+5.39,z+49,WHITE,height=4+max(0,2-abs(a-2.5))*2)
        seg(s,P(s,i+3.4,j+5.4,z+45),P(s,i+9.6,j+5.4,z+45),CLAY['deep'])
        seg(s,P(s,i+3.4,j+5.4,z+46),P(s,i+9.6,j+5.4,z+46),BLUE['dark'])
        # Athena NW (-i); Apollo SE (+i), verified from the OSM statue nodes.
        for a,kind in ((i+.6,'athena'),(i+W-.6,'apollo')):
            block(s,a-.42,j+4.9,.84,.84,5,WHITE,z=z+3)
            column(s,a,j+5.32,z+8,58,.31,WHITE,'ionic')
            figure(s,a,j+5.32,z+68,WHITE,kind,17)
        for k in range(6):block(s,i+3.1,j+5.45+k*.25,6.8,.3,7-k,WHITE,z=z)
        for a in (i+2.2,i+10.8):
            block(s,a-.48,j+6.7,.96,.9,6,WHITE,stone_courses(WHITE,3,8),z=z)
            figure(s,a,j+7.1,z+6,WHITE,'seated',13)
    scene.add(i+j+W+D+5,draw)


def flag(s,i,j,z):
    """Greek flag: nine blue/white stripes and the white cross in a blue canton."""
    seg(s,P(s,i,j,z),P(s,i,j,z+21),IRON)
    for row in range(9):
        for col in range(15):
            color=BLUE['dark'] if row%2==0 else WHITE['hi']
            if row<5 and col<6:color=WHITE['hi'] if row==2 or col in (2,3) else BLUE['dark']
            x,y=P(s,i+col/8,j,z+20-row)
            s.put(x,y,color)


def parliament(scene,i,j,z=0):
    """Broad three-storey ochre palace, six-column west portico, tomb and Greek flag."""
    W,D,H=13.2,6,43
    def draw(s):
        block(s,i,j,W,D,H,OCHRE,windows(OCHRE,H,10,14,hood=True),z=z+8)
        for zz in (8,22,36,51):band(s,i,j,W,D,z+zz,WHITE,2)
        hip_roof(s,i-.12,j-.12,W+.24,D+.24,z+H+9,8,CLAY)
        # Projecting west front and restrained central portico; no invented dome.
        block(s,i+4.1,j+D-.4,5,1,28,WHITE,
              lambda u,v,lit:WOOD['dark'] if int(u)%10 in (4,5,6) and v<20 else None,z=z+8)
        for k in range(6):column(s,i+4.25+k*.95,j+D+.85,z+8,28,.2,WHITE)
        band(s,i+3.8,j+D-.55,5.6,1.75,z+37,WHITE,3)
        pediment(s,i+3.65,j+D-.5,5.9,1.8,z+41,9,WHITE)
        for k in range(6):block(s,i+.8,j+D+1.5+k*.22,W-1.6,.3,7-k,WHITE,z=z)
        # Tomb wall below the palace terrace, reclining hoplite carved within its face.
        def relief(u,v,lit):
            if 15<u<46 and 3<v<11:
                if (u-40)**2+(v-7)**2<7 or 20<u<40 and 4<v<7:return MARBLE['dark']
                if abs(v-(u-17)*.16-3)<1 and 17<u<34:return MARBLE['line']
            return stone_courses(MARBLE,4,15)(u,v,lit)
        block(s,i+2.5,j+D+2.8,8.2,.45,14,MARBLE,relief,z=z)
        for a in (i+.5,i+W-1):block(s,a,j+D+2.5,.5,.9,4,WHITE,z=z)
        flag(s,i+W/2,j+2,z+H+17)
    scene.add(i+j+W+D+7,draw)


def stadium(scene,i,j,z=0):
    """Marble horseshoe: open NW, long axis +i to SE, curved sphendon and stepped aisles."""
    L,W=12.5,7.5
    # Local a follows +i (SE); b follows +j (SW). The open end is a=0, facing NW.
    straight=L-W/2
    def curve(r):
        points=[(i,j+W/2-r),(i+straight,j+W/2-r)]
        points += [(i+straight+r*math.cos(a),j+W/2+r*math.sin(a))
                   for a in [-math.pi/2+k*math.pi/24 for k in range(25)]]
        points.append((i,j+W/2+r));return points
    def draw(s):
        outline=curve(W/2)
        poly(s,[P(s,*p,z) for p in outline],lambda x,y:GROUND['track'])
        # Curved lane marks surround an earth infield; no football field invented here.
        for r in (1.55,1.75,1.95):
            path=curve(r)
            for a,b in zip(path,path[1:]):seg(s,P(s,*a,z+.2),P(s,*b,z+.2),GROUND['track_line'])
        poly(s,[P(s,i+.5,j+W/2-1.3,z+.4),P(s,i+straight,j+W/2-1.3,z+.4)] +
             [P(s,i+straight+1.3*math.cos(a),j+W/2+1.3*math.sin(a),z+.4)
              for a in [-math.pi/2+k*math.pi/24 for k in range(25)]]+[P(s,i+.5,j+W/2+1.3,z+.4)],
             lambda x,y:GROUND['dust'])
        # A solid coursed marble retaining shell supports the high outer seating.
        outer=curve(3.79)
        for a,b in zip(outer,outer[1:]):
            pa,pb=P(s,*a,z),P(s,*b,z)
            lit=(b[0]-a[0])-(b[1]-a[1])>0
            def shell(x,y,pa=pa,pb=pb,lit=lit):
                t=(x-pa[0])/(pb[0]-pa[0]) if abs(pb[0]-pa[0])>.01 else .5
                height=pa[1]+t*(pb[1]-pa[1])-y
                return MARBLE['line'] if int(height)%5==0 else MARBLE['lit' if lit else 'dark']
            poly(s,[pa,pb,(pb[0],pb[1]-24.6),(pa[0],pa[1]-24.6)],shell)
        # Radial seating facets, each with a tread and a shaded riser, sorted in 3D.
        faces=[]
        for n in range(12):
            r0=2.05+n*.145;r1=r0+.145;h=(n+1)*2.05
            inner,outer=curve(r0),curve(r1)
            for k in range(len(inner)-1):
                a,b=inner[k:k+2];c,d=outer[k:k+2]
                depth=sum(a+b+c+d)
                faces.append((depth,h,a,b,c,d,k,n))
        for _,h,a,b,c,d,k,n in sorted(faces):
            lit=(b[0]-a[0])-(b[1]-a[1])>0
            poly(s,[P(s,*a,z+h-2.05),P(s,*b,z+h-2.05),P(s,*b,z+h),P(s,*a,z+h)],
                 lambda x,y,lit=lit:WHITE['mid' if lit else 'dark'])
            poly(s,[P(s,*a,z+h),P(s,*b,z+h),P(s,*d,z+h),P(s,*c,z+h)],
                 lambda x,y,n=n:WHITE['hi' if n%3 else 'lit'])
            if n==5:seg(s,P(s,*a,z+h),P(s,*b,z+h),MARBLE['line'])
            if k in (0,4,9,14,19,25):seg(s,P(s,*a,z+h),P(s,*c,z+h),MARBLE['line'])
        # Exposed cut ends show actual stacked marble rather than a flat front cut-out.
        for side in (-1,1):
            a=(i,j+W/2+side*2.05);b=(i,j+W/2+side*3.79)
            poly(s,[P(s,*a,z),P(s,*b,z),P(s,*b,z+24.6)],
                 lambda x,y:MARBLE['lit'] if (x+2*y)%7 else MARBLE['line'])
    scene.add(i+j+L+W+3,draw)


def townhouse(scene,i,j,wi=2.5,wj=3,floors=2,seed=0,z=0):
    """Plaka neoclassical houses: ochre/pastel plaster, shutters, iron balconies, clay roofs."""
    material=palette_of(WALLS[seed%len(WALLS)]);H=floors*12+3
    dressed=windows(material,H,10,12,hood=True)
    def pattern(u,v,lit):
        c,level=int(u)%10,int(v)%12
        if v<10:
            if 2<c<8:return WOOD['dark'] if seed%2 else GLASS['dark']
            if c in (2,8):return WHITE['lit' if lit else 'dark']
        if v>12 and c in (1,9) and 4<level<10:return BLUE['lit' if lit else 'dark']
        return dressed(u,v,lit)
    def draw(s):
        block(s,i,j,wi,wj,H,material,pattern,z=z)
        band(s,i,j,wi,wj,z+1,MARBLE,2)
        band(s,i,j,wi,wj,z+H-1,WHITE,2)
        if seed%3==0:
            pediment(s,i+.1,j+wj-.15,wi-.2,.35,z+H+1,5,WHITE)
        if floors>1 and seed%3!=2:
            block(s,i+.5,j+wj+.1,1.3,.55,1.5,WHITE,z=z+13)
            for k in range(7):seg(s,P(s,i+.5+k*.215,j+wj+.65,z+15),P(s,i+.5+k*.215,j+wj+.65,z+20),IRON)
            seg(s,P(s,i+.5,j+wj+.65,z+20),P(s,i+1.8,j+wj+.65,z+20),IRON)
            for a in (i+.5,i+1.6):block(s,a,j+wj,.15,.45,3,WHITE,z=z+10)
        hip_roof(s,i-.16,j-.16,wi+.32,wj+.32,z+H+2,8+seed%3,CLAY)
        # Terracotta antefixes along the eaves and capped masonry chimney.
        for a in (i+.2,i+wi/2,i+wi-.2):block(s,a,j+wj,.12,.15,2,CLAY,z=z+H+3)
        block(s,i+wi-.65,j+.4,.4,.45,7,WHITE,stone_courses(WHITE,3,7),z=z+H+4)
        band(s,i+wi-.65,j+.4,.4,.45,z+H+11,CLAY,2)
    scene.add(i+j+wi+wj+2,draw)


def main():
    for name,builder,_,_,_,z in SITES:
        print(preview([lambda s,b=builder,z=z:b(s,7,7,z=z)],'athens-'+name,
                      size=(340,285),origin=(170,130),tiles=30))
    print(preview([lambda s,k=k:townhouse(s,3+k*3.6,4,floors=1+k%3,seed=k)
                   for k in range(6)],'athens-houses',size=(340,240),origin=(80,75),tiles=27))
    import sprites
    im=sprites.meteora();path=Path(__file__).resolve().parents[2]/'docs/art/capitals/greece-meteora.png'
    im.resize((im.width*4,im.height*4),0).save(path);print(path)


# name, builder, footprint, real longitude/latitude, north-up ground anchor, elevation.
SITES = [
    ('academy',academy,(13,5.6),(23.73417,37.98000),(450,120),0),
    ('hephaestus',hephaestus,(4.7,9.4),(23.7213917,37.9756167),(100,210),16),
    ('parliament',parliament,(13.2,6),(23.73694,37.97528),(590,230),0),
    ('winds',winds,(5,5),(23.7270701,37.974256),(405,300),0),
    ('erechtheion',erechtheion,(7.2,6.4),(23.7265,37.9721),(180,380),32),
    ('parthenon',parthenon,(5.8,12.2),(23.7266,37.9715),(315,440),40),
    ('stadium',stadium,(12.5,7.5),(23.74111,37.96833),(600,465),0),
]


if __name__=='__main__':
    main()
