"""Luxembourg City's sandstone, slate and Kirchberg architecture in projected (i, j, z).

Original procedural art. Run for eight isolated 4× landmark studies and a house study.
Geographic anchors and architectural references are recorded in DEVELOPMENT_PLAN.md.
"""
import math

import iso
from iso import rgb
from landmarks_paris import P, seg, poly, corners, facade, mansard, preview, GLASS
from landmarks_iberia import hip_roof, stone_courses, arch_opening, palette_of, tones
from landmarks_amsterdam import gable_roof
from landmarks_italy import cylinder, ellipse
from landmarks_denmark import spire
from landmarks_poland import extrude

STONE = tones('#F3E8CB', '#D7C49A', '#BEAA7F', '#998563', '#6C5A41', '#B09A71', '#493E2E')
PALE = tones('#FFF7E4', '#E7DBBC', '#D0C2A1', '#AC9B7C', '#79684E', '#C3B291', '#50432F')
ROCK = tones('#D5C3A0', '#B4A17C', '#998764', '#78664A', '#574A35', '#968260', '#443A2B')
SLATE = tones('#A7B4C0', '#7A8C9E', '#617487', '#43586D', '#2D4052', '#566B80', '#233344')
COPPER = tones('#B9D2BB', '#82AA92', '#648B76', '#416857', '#2D4A3E', '#587D68', '#243D32')
GOLD = tones('#FFF5B7', '#E9C568', '#CDA34C', '#A37C32', '#725421', '#B58D3B', '#513D23')
BRONZE = tones('#A7B394', '#7E9172', '#5F7559', '#40563E', '#2B3E2C', '#53694A', '#223324')
STEEL = tones('#FFFFFF', '#EEF0E6', '#CDD6D3', '#9CAEB1', '#677E89', '#B3C2C1', '#435762')
GLAZE = tones('#D5EBE2', '#A0C5C3', '#729FA7', '#477582', '#2B505F', '#8AB4B8', '#233E4B')
WALLS = [rgb(c) for c in ('#E4CCA5', '#D8B568', '#D2A69B', '#BACAC5', '#E7DDC7', '#B8BE9D')]
IRON, WOOD = rgb('#34404A'), rgb('#6C4E39')
WATER = (rgb('#57878B'), rgb('#3C6A76'), rgb('#C4DCD0'))


def block(s, i, j, wi, wj, height, material=STONE, pattern=None, z=0):
    cover = facade(s, i, j, wi, wj, height, pattern or stone_courses(material, 4, 10), palette=material, z0=z)
    iso.fill(s, list(corners(s, i, j, wi, wj, z+height)), lambda x, y: material['mid'], cover)
    iso.outline(s, cover, material['outline'])
    return cover


def band(s, i, j, wi, wj, z, material=PALE):
    facade(s, i-.07, j-.07, wi+.14, wj+.14, 1.5,
           lambda u,v,lit:material['hi' if lit else 'dark'],palette=material,z0=z)


def windows(material, height, bay=10, floor=13, gothic=False, ornate=False):
    courses = stone_courses(material, 4, 11)
    def pattern(u, v, lit):
        c, v = int(u) % bay, int(v)
        level, trim = v % floor, PALE['lit' if lit else 'dark']
        if v <= 2 or v in (height-1, height-3) or level == 0:
            return trim
        if ornate and c in (0, 1):
            return trim if level % 4 else material['deep']
        top = floor-3-abs(c-bay/2)*(1.05 if gothic else .12)
        if 2 <= c <= bay-2 and 3 <= level <= top and v < height-4:
            if c in (2, bay-2, bay//2) or level in (3, 6, int(top)):
                return trim
            return GLASS['mid' if lit else 'dark']
        return courses(u, v, lit)
    return pattern


def flag(s, i, j, z):
    seg(s, P(s, i, j, z), P(s, i, j, z+14), IRON)
    for n, color in enumerate((rgb('#C85B58'), PALE['hi'], rgb('#78B7D3'))):
        poly(s, [P(s, i+a, j, z+13-n*2-b) for a,b in ((0,0),(1,0),(1,2),(0,2))],lambda x,y,c=color:c)


def townhouse(scene, i, j, wi=2.5, wj=3, floors=3, seed=0):
    """Ville Haute/Grund stucco: dressed sash windows, steep slate, dormers, iron and shops."""
    wall, H = palette_of(WALLS[seed % len(WALLS)]), floors*11+3
    base = windows(wall, H, 10, 11)
    def pattern(u, v, lit):
        c, level = int(u)%10, int(v)%11
        if v < 9 and 2 <= c <= 7:
            if c in (2,7) or int(v) in (1,8):
                return PALE['lit' if lit else 'dark']
            return WOOD if c <= 4 else GLASS['mid' if lit else 'dark']
        if seed%3 == 0 and 12 <= v <= 15 and 1 <= c <= 8:
            return IRON if int(v) in (12,15) or c%3 == 0 else base(u,v,lit)
        return base(u,v,lit)
    def draw(s):
        block(s,i,j,wi,wj,H,wall,pattern)
        for z in (2,H-2):band(s,i,j,wi,wj,z)
        if seed%4 == 0:
            mansard(s,i-.06,j-.06,wi+.12,wj+.12,H,12,.45,roof=SLATE,dormers=6)
        else:
            gable_roof(s,i,j,wi,wj,H,13,SLATE,wall,'point')
            # Small roof dormer, in true volume rather than pasted onto the roof.
            block(s,i+.65,j+wj-.65,.65,.6,5,PALE,windows(PALE,8,5),z=H+3)
            hip_roof(s,i+.6,j+wj-.7,.75,.7,H+8,3,SLATE)
        block(s,i+wi-.65,j+.45,.42,.5,8,STONE,z=H+7)
        band(s,i+wi-.65,j+.45,.42,.5,H+14,SLATE)
    scene.add(i+j+wi+wj,draw)


def palace(scene,i,j):
    """Renaissance frontage: decorated pilasters, twin pointed turrets, stepped gable and balcony."""
    W,D,H=9,3.5,36
    def draw(s):
        block(s,i,j,W,D,H,STONE,windows(STONE,H,9,12,ornate=True))
        mansard(s,i,j,W,D,H,15,.7,roof=SLATE,dormers=8)
        for a in (.3,4.8):
            block(s,i+a,j+D-.9,1.25,1.3,48,STONE,windows(STONE,48,7,12,ornate=True))
            spire(s,i+a+.625,j+D-.25,.95,48,27,SLATE,conical=False)
            seg(s,P(s,i+a+.625,j+D-.25,75),P(s,i+a+.625,j+D-.25,82),GOLD['dark'])
        # Right wing's cut stone attic and three stepped gable levels.
        for n in range(3):
            block(s,i+6+n*.35,j+D-.35,2.6-n*.7,.55,4,STONE,z=H+n*4)
        for a in (6.05,8.5):
            block(s,i+a,j+D-.1,.2,.24,5,PALE,z=H+3)
        for z in (12,24,35):band(s,i,j,W,D,z)
        # Incised Renaissance scroll / diamond panels attached to the lit frontage.
        for a in (1.8,3.1,6.4,7.7):
            for z in (15,27):
                pts=[P(s,i+a+u,j+D+.09,z+v) for u,v in ((0,0),(.28,2),(0,4),(-.28,2))]
                poly(s,pts,lambda x,y:STONE['dark'])
                seg(s,pts[1],pts[3],PALE['hi'])
        block(s,i+5.6,j+D,2.6,.55,2,PALE,z=14)
        for a in range(12):
            seg(s,P(s,i+5.65+a*.22,j+D+.53,16),P(s,i+5.65+a*.22,j+D+.53,21),IRON)
        seg(s,P(s,i+5.6,j+D+.53,21),P(s,i+8.2,j+D+.53,21),IRON)
        flag(s,i+6.9,j+1.7,H+16)
    scene.add(i+j+W+D+2,draw)


def cathedral(scene,i,j):
    """Two tall slate spires and a slender copper crossing spire, Gothic transept, traceried glazing and carved portal."""
    W,D,H=6,8,31
    def draw(s):
        block(s,i+.6,j,W-1.2,D,H,STONE,windows(STONE,H,9,16,True))
        gable_roof(s,i+.6,j,W-1.2,D,H,21,SLATE,STONE,'point')
        block(s,i-.5,j+3.4,W+1,2.7,32,STONE,windows(STONE,32,10,16,True))
        gable_roof(s,i-.5,j+3.4,W+1,2.7,32,17,SLATE,STONE,'point')
        for b in (1,3,6.5):
            block(s,i+W-.25,j+b,.45,.45,25,STONE)
            seg(s,P(s,i+W,j+b,23),P(s,i+W-.8,j+b,33),PALE['lit'],2)
        # West bell tower, east tower and taller crossing tower, distinct heights.
        for a,b,base,rise,size in ((.1,6.6,49,44,1.4),(4,1.3,45,40,1.25),(2.7,3.7,47,31,.85)):
            z=43 if size<1 else 0
            block(s,i+a,j+b,size,size,base-z,STONE,windows(STONE,base-z,7,13,True),z=z)
            band(s,i+a,j+b,size,size,base)
            spire(s,i+a+size/2,j+b+size/2,size*.55,base+2,rise,COPPER if size<1 else SLATE)
            seg(s,P(s,i+a+size/2,j+b+size/2,base+rise+2),P(s,i+a+size/2,j+b+size/2,base+rise+9),GOLD['dark'])
        # Renaissance-framed west entrance, pointed arch with a small traceried rose.
        fj=j+D+.16
        block(s,i+1.7,fj-.4,2.7,.6,26,STONE,windows(STONE,26,10,13,True))
        for r,mat in ((5,STONE['deep']),(3.5,GLAZE['lit'])):
            points=[P(s,i+3+math.cos(t*math.tau/24)*r/8,fj+.21,20+math.sin(t*math.tau/24)*r) for t in range(24)]
            poly(s,points,lambda x,y,c=mat:c)
        for t in range(8):
            a=t*math.tau/8
            seg(s,P(s,i+3,fj+.23,20),P(s,i+3+math.cos(a)*.5,fj+.23,20+math.sin(a)*4),PALE['lit'])
        for a in (2,3,4):
            block(s,i+a-.11,fj+.2,.22,.3,13,PALE)
        for step in range(3):block(s,i+1.5,fj+.3+step*.28,3.1,.3,3-step,STONE)
    scene.add(i+j+W+D+2,draw)


def adolphe_bridge(scene,i,j):
    """Twin parallel masonry arches over the Pétrusse, small approach arcades and suspended path."""
    W,D,deck=12,2.6,46
    def draw(s):
        # Build both complete arched ribs as a 3D spandrel mesh; the void stays open.
        for b in (j,j+D-.4):
            for n in range(96):
                u0,u1=n*W/96,(n+1)*W/96
                def underside(u):
                    if 2 < u < 10:
                        return 5+32*math.sqrt(max(0,1-((u-6)/4)**2))
                    center=(int(u/.66)+.5)*.66
                    return 28+10*math.sqrt(max(0,1-((u-center)/.24)**2)) if abs(u-center)<.24 else 0
                z0,z1=underside(u0),underside(u1)
                front=[P(s,i+u0,b+.4,z0),P(s,i+u1,b+.4,z1),P(s,i+u1,b+.4,deck),P(s,i+u0,b+.4,deck)]
                back=[P(s,i+u0,b,z0),P(s,i+u1,b,z1),P(s,i+u1,b,deck),P(s,i+u0,b,deck)]
                poly(s,back,lambda x,y:STONE['dark'])
                poly(s,[back[0],back[1],front[1],front[0]],lambda x,y:STONE['deep'])
                poly(s,front,lambda x,y:STONE['line'] if int(y)%4==0 else STONE['lit'])
                seg(s,front[0],front[1],PALE['hi'],2)
                if n%4==0:seg(s,front[0],P(s,i+u0,b+.4,min(deck,z0+5)),STONE['dark'])
        for a in (0,10):
            block(s,i+a,j,2,.4,25,STONE)
            block(s,i+a,j+D-.4,2,.4,25,STONE)
        block(s,i,j,W,D,2,STONE,z=deck)
        poly(s,list(corners(s,i+.2,j+.2,W-.4,D-.4,deck+2)),lambda x,y:SLATE['dark'])
        for b in (j,j+D):
            block(s,i,b,W,.14,3,PALE,z=deck+2)
            for a in (.2,2,10,11.8):
                block(s,i+a,b-.1,.3,.3,4,PALE,z=deck+2)
        # Suspended cycle/footway under the deck, with its own railing and hangers.
        block(s,i+1.8,j+1.1,8.4,.6,1,STEEL,z=deck-8)
        for a in range(2,11):
            seg(s,P(s,i+a,j+1.1,deck-8),P(s,i+a,j+1.1,deck),STEEL['dark'])
        for a in (1.5,10.5):
            seg(s,P(s,i+a,j+.2,deck+3),P(s,i+a,j+.2,deck+12),IRON)
            seg(s,P(s,i+a,j+.2,deck+12),P(s,i+a+.5,j+.2,deck+12),IRON)
    scene.add(i+j+W+D+2,draw)


def gelle_fra(scene,i,j):
    """Granite obelisk, solid gilded woman holding a wreath, and bronze mourning soldiers."""
    def draw(s):
        for z,w in ((0,3.8),(2,3.1),(4,2.5)):
            block(s,i+(3.8-w)/2,j+(3.8-w)/2,w,w,2,STONE,z=z)
        block(s,i+1,j+1,1.8,1.8,9,STONE,z=6)
        base=corners(s,i+1.3,j+1.3,1.2,1.2,15)
        top=corners(s,i+1.62,j+1.62,.56,.56,65)
        for indices,key in (((0,1),'mid'),((0,3),'mid'),((3,2),'lit'),((2,1),'dark')):
            a,b=indices;poly(s,[base[a],base[b],top[b],top[a]],lambda x,y,k=key:STONE[k])
        poly(s,list(top),lambda x,y:STONE['hi'])
        # Robe, shoulders, head, bent arms and laurel wreath have filled profiles.
        profile=[(-.3,0),(.3,0),(.2,5),(.28,8),(.15,10),(.15,12),(-.12,12),(-.17,10),(-.28,8),(-.18,4)]
        extrude(s,[(i+1.9+a,66+z) for a,z in profile],j+2,.18,GOLD)
        for sign in (-1,1):
            extrude(s,[(i+1.9+sign*a,66+z) for a,z in ((.18,8),(.6,10),(.48,14),(.3,14),(.38,10),(.1,9))],j+2,.15,GOLD)
        points=[P(s,i+1.9+math.cos(t*math.tau/30)*.5,j+2,81+math.sin(t*math.tau/30)*2.4) for t in range(30)]
        for a,b in zip(points,points[1:]+points[:1]):seg(s,a,b,GOLD['lit'],2)
        for a in (.5,2.7):
            block(s,i+a-.2,j+3,.45,.65,4,BRONZE,z=5)
            extrude(s,[(i+a+u,9+v) for u,v in ((-.25,0),(.35,0),(.15,4),(.22,6),(-.12,7),(-.3,4))],j+3.4,.3,BRONZE)
        # Inscribed remembrance panel, deliberately no invented lettering.
        block(s,i+1.3,j+2.82,1.2,.08,3,BRONZE,z=8)
    scene.add(i+j+8,draw)


def bock(scene,i,j):
    """Sandstone promontory with casemate embrasures, ruined wall and Castle Bridge approach."""
    W,D,H=10,4.5,34
    def draw(s):
        plan=[(0,1),(1,0),(7.5,0),(10,1.4),(9.2,3.4),(7.5,4.5),(1.2,4.3),(-.7,2.6)]
        faces=[]
        for n,(a,b) in enumerate(plan):
            c,d=plan[(n+1)%len(plan)]
            top0,top1=P(s,i+a,j+b,H),P(s,i+c,j+d,H)
            foot0=P(s,i+a+(a-5)*.09,j+b+(b-2)*.11,0)
            foot1=P(s,i+c+(c-5)*.09,j+d+(d-2)*.11,0)
            faces.append((a+b+c+d,[foot0,foot1,top1,top0],n))
        for _,pts,n in sorted(faces):
            lit=n in (5,6,7)
            x0,y0=pts[0];x1,y1=pts[1]
            def texture(x,y,lit=lit):
                t=(x-x0)/(x1-x0) if abs(x1-x0)>.1 else .5
                v=y0+(y1-y0)*t-y
                u=(x-x0) if x1>x0 else (x0-x)
                if 12<v<17 or 25<v<29:
                    if 4<int(u)%18<10:return ROCK['deep']
                layer=int(v+2*math.sin(u/9))%7
                return ROCK['line' if lit else 'deep'] if layer==0 else ROCK['hi' if lit and layer==1 else 'lit' if lit else 'dark']
            poly(s,pts,texture)
            for a,b in zip(pts,pts[1:]+pts[:1]):seg(s,a,b,ROCK['outline'])
        poly(s,[P(s,i+a,j+b,H) for a,b in plan],
             lambda x,y:STONE['lit'] if iso.h01(int(x)//3,int(y)//2,619)<.18 else STONE['mid'])
        # Broken ledges and mineral fissures follow the cliff's projected surfaces.
        for a,b in ((1.4,4.3),(3.6,4.35),(6.3,4.45),(9.2,3.1)):
            chain=[P(s,i+a,j+b,H-3),P(s,i+a+.15,j+b,25),
                   P(s,i+a-.15,j+b+.12,17),P(s,i+a+.1,j+b+.14,5)]
            for p,q in zip(chain,chain[1:]):seg(s,p,q,ROCK['deep'])
            seg(s,P(s,i+a-.2,j+b,18),P(s,i+a+.7,j+b,18),ROCK['hi'])
        for a,length in ((.3,2.2),(3.1,3),(7.3,2.3)):
            block(s,i+a,j+.25,length,.55,8,STONE,z=H+2)
            for q in (0,.7,1.5):
                if q<length:block(s,i+a+q,j+.25,.3,.55,2,STONE,z=H+10)
        # Ruined castle foundations read as broken walls, never a fictitious restored keep.
        block(s,i+1,j+1.2,2.7,.45,5,STONE,z=H+2)
        block(s,i+1,j+1.2,.45,2.2,7,STONE,z=H+2)
        for a in range(7):
            seg(s,P(s,i+1+a,j+D-.3,H+3),P(s,i+1+a,j+D-.3,H+7),IRON)
        seg(s,P(s,i+1,j+D-.3,H+7),P(s,i+7,j+D-.3,H+7),IRON)
        # Castle Bridge's low approach, with a tunnel opening painted on its own face.
        block(s,i-2.4,j+1.2,2.8,1.4,24,STONE,
              lambda u,v,lit:arch_opening(u,v,10,4,11,ROCK['deep']) or stone_courses(STONE,4,10)(u,v,lit),z=8)
        hip_roof(s,i-2.4,j+1.2,2.8,1.4,32,1,STONE)
        for a in range(4):block(s,i+a*2.4,j+D-.2,.35,.5,3,ROCK)
    scene.add(i+j+W+D+2,draw)


def abbey(scene,i,j):
    """Neumünster's pale courtyard wings and adjacent St John's church with its slate spire."""
    W,D=10,7
    def wing(s,a,b,w,d,h):
        block(s,a,b,w,d,h,PALE,windows(PALE,h,9,12))
        hip_roof(s,a,b,w,d,h,11,SLATE)
        for q in (1,w-1):block(s,a+q,b+.5,.35,.4,6,STONE,z=h+5)
    def draw(s):
        wing(s,i,j,W,2.1,26)
        wing(s,i,j+2,2.2,D-2,24)
        wing(s,i+W-2,j+2,2,D-2,25)
        poly(s,list(corners(s,i+2.3,j+2.2,5.5,4.5,1)),lambda x,y:PALE['dark'] if int(x+y)%9==0 else PALE['mid'])
        # St John's belongs to the riverside abbey ensemble, with a separate bell tower.
        block(s,i+W-1,j+3,3.1,5,29,PALE,windows(PALE,29,8,14,True))
        gable_roof(s,i+W-1,j+3,3.1,5,29,18,SLATE,PALE,'point')
        block(s,i+W-1,j+6.2,1.5,1.6,51,PALE,windows(PALE,51,7,13,True))
        band(s,i+W-1,j+6.2,1.5,1.6,51)
        spire(s,i+W-.25,j+7,.9,53,33,SLATE)
        seg(s,P(s,i+W-.25,j+7,86),P(s,i+W-.25,j+7,93),IRON)
        for a in (2.7,5,7.2):
            block(s,i+a,j+4,.7,.7,1,STONE)
    scene.add(i+j+W+D+4,draw)


def glass_peak(s,i,j,wi,wj,base,rise):
    T,R,B,L=corners(s,i,j,wi,wj,base)
    apex=P(s,i+wi/2,j+wj/2,base+rise)
    for a,b,key in ((T,R,'dark'),(T,L,'mid'),(L,B,'lit'),(B,R,'dark')):
        poly(s,[a,b,apex],lambda x,y,k=key:GLAZE[k])
        for n in range(1,7):
            t=n/7
            foot=(a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t)
            seg(s,foot,apex,STEEL['dark'])
        for t in (.25,.5,.75):
            seg(s,(a[0]+(apex[0]-a[0])*t,a[1]+(apex[1]-a[1])*t),
                (b[0]+(apex[0]-b[0])*t,b[1]+(apex[1]-b[1])*t),STEEL['lit'])
        seg(s,a,b,STEEL['lit']);seg(s,a,apex,STEEL['lit'])


def mudam(scene,i,j):
    """Pei's honey limestone galleries, angular glass Grand Hall and faceted roof lantern."""
    W,D=9,6
    def glazing(u,v,lit):
        if 3<v<19 and 3<int(u)%14<11:
            return STEEL['dark'] if int(u)%7==0 or int(v)%6==0 else GLAZE['mid' if lit else 'dark']
        return stone_courses(STONE,5,13)(u,v,lit)
    def draw(s):
        block(s,i,j,W,D,23,STONE,glazing)
        block(s,i-.4,j+1.4,3.2,3.5,25,STONE,glazing)
        block(s,i+W-2.4,j-.4,2.8,4.5,24,STONE,glazing)
        for a,b,w,d,h in ((0,0,W,D,23),(-.4,1.4,3.2,3.5,25),(6.6,-.4,2.8,4.5,24)):
            band(s,i+a,j+b,w,d,h)
        # Cruciform central hall rises above the galleries; triangular glass surfaces
        # follow projected roof geometry, with steel members clipped to each facet.
        glass_peak(s,i+2,j+1.2,4.7,3.8,25,25)
        block(s,i+3.8,j+2.65,.9,.9,8,GLAZE,
              lambda u,v,lit:STEEL['dark'] if int(u)%3==0 or int(v)%4==0 else GLAZE['lit' if lit else 'dark'],z=50)
        glass_peak(s,i+3.75,j+2.6,1,1,58,4)
        # Broad recessed entrance and low stone stair.
        block(s,i+3.1,j+D,2.8,.3,14,GLAZE,lambda u,v,lit:STEEL['dark'] if int(u)%5==0 else GLAZE['dark'])
        for step in range(3):block(s,i+2.7,j+D+.3+step*.3,3.7,.35,3-step,STONE)
    scene.add(i+j+W+D+3,draw)


def philharmonie(scene,i,j):
    """Elliptical white colonnade and sweeping shell of the chamber music hall."""
    ci,cj=i+4.5,j+3
    def draw(s):
        # Actual elliptical plan and glass inner envelope behind the column screen.
        cylinder(s,ci,cj,4.5,2.8,0,2,STEEL)
        cylinder(s,ci,cj,3.9,2.2,2,36,GLAZE,
                 lambda u,v,lit:STEEL['dark'] if int(u)%9==0 else GLAZE['mid' if lit else 'dark'])
        # Rear columns first; front columns after the roof to preserve their silhouette.
        def columns(front):
            for n in range(58):
                angle=n*math.tau/58
                a,b=ci+4.35*math.cos(angle),cj+2.65*math.sin(angle)
                if (a+b>ci+cj)!=front:continue
                x,y=P(s,a,b,2);xt,yt=P(s,a,b,40)
                seg(s,(x+1,y),(xt+1,yt),STEEL['dark'],2)
                seg(s,(x,y),(xt,yt),STEEL['hi'])
        columns(False)
        ellipse(s,ci,cj,4.5,2.8,40,STEEL['lit'])
        ellipse(s,ci,cj,4.25,2.55,41,STEEL['hi'])
        columns(True)
        # The projecting white chamber hall is a curved, pointed shell with a
        # diamond panel grid, built as two independently shaded surface meshes.
        for side in (-1,1):
            for n in range(18):
                for m in range(8):
                    points=[]
                    for nn,mm in ((n,m),(n+1,m),(n+1,m+1),(n,m+1)):
                        t,r=nn/18,mm/8
                        a=ci-3+8*t
                        b=cj+2.8+side*2*(1-r)*math.sin(math.pi*t)+1.1*t
                        z=3+39*math.sin(math.pi*t)**.8*r
                        points.append(P(s,a,b,z))
                    poly(s,points,lambda x,y,k=('lit' if side==1 else 'mid'):STEEL[k])
                    if m%2==0:seg(s,points[0],points[1],STEEL['mid'])
                    if n%3==0:seg(s,points[0],points[3],STEEL['mid'])
        for a in range(3):block(s,i+2+a*.8,j+5.5,.6,.2,9,GLAZE)
    scene.add(i+j+18,draw)


STUDIES = [('palace',palace),('cathedral',cathedral),('adolphe-bridge',adolphe_bridge),
           ('gelle-fra',gelle_fra),('bock',bock),('neumunster',abbey),('mudam',mudam),('philharmonie',philharmonie)]

if __name__ == '__main__':
    for name,builder in STUDIES:
        print(preview([lambda s,b=builder:b(s,3,3)],'luxembourg-'+name,
                      size=(240,220),origin=(105,100),tiles=21))
    print(preview([lambda s:townhouse(s,3,3,seed=0),lambda s:townhouse(s,7,3,seed=3),
                   lambda s:townhouse(s,7,8,floors=2,seed=5)],'luxembourg-houses',
                  size=(240,210),origin=(105,70),tiles=20))
    # Native-size country icon enlarged only by an integer, with transparent margins.
    import sprites
    image = sprites.vianden()
    image.resize((image.width*4,image.height*4),0).save(
        'docs/art/capitals/luxembourg-vianden.png')
