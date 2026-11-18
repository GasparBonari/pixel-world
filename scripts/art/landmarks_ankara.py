"""Ankara's hilltop citadel, Ottoman markets and Republican monuments in true (i,j,z).

Two-source fact sheets, terrain and explicit facade snaps: DEVELOPMENT_PLAN.md, Phase 4.
Run this module for six isolated 4× landmark studies, Ankara houses and Pamukkale.
"""
import math
from pathlib import Path

from iso import rgb
from landmarks_paris import P, seg, poly, preview, GLASS
from landmarks_iberia import hip_roof, crenellate, stone_courses, arch_opening, palette_of, tones
from landmarks_slovakia import block, band, pediment
from landmarks_bosnia import cylinder
from landmarks_slovenia import revolve, slab, DOME

STONE = tones('#F5E4C6', '#D6BD96', '#BA9E78', '#967B59', '#6D563D', '#AA8E6B', '#493B2B')
FIELDSTONE = tones('#E2D5BA', '#B4A58B', '#9C8B71', '#776B58', '#534B3D', '#8F7F65', '#39372E')
WHITE = tones('#FFFFF0', '#EEE6D2', '#D7CDB7', '#B5A58C', '#80725C', '#C6B79D', '#514634')
TRAVERTINE = tones('#FFF0C1', '#DFC78D', '#C6A86F', '#A48651', '#766039', '#B99A62', '#524027')
BRICK = tones('#E8B18D', '#BB7D60', '#A3664D', '#7C4938', '#573226', '#92573E', '#42271F')
CLAY = tones('#E9A175', '#BF724B', '#A85C39', '#7E412D', '#552A20', '#954F35', '#47271E')
LEAD = tones('#C8CCC0', '#9EA69D', '#828F88', '#5D716F', '#3F5354', '#74837C', '#2A3C3E')
WOOD = tones('#C7A17B', '#8F6947', '#765237', '#553B2B', '#382A21', '#684A32', '#30251E')
BRONZE = tones('#CBC397', '#9F966B', '#807A56', '#5E6148', '#3E4434', '#717454', '#2B3127')
GOLD = tones('#FFF1AA', '#DEC071', '#B89B50', '#957534', '#695225', '#AD8A42', '#493C23')
ROCK = tones('#DCC9A6', '#B39B7B', '#998467', '#78664F', '#564B39', '#8C785A', '#40392D')
WALLS = [rgb(c) for c in ('#E8DDC5', '#D5C19B', '#F1E8D5', '#CDB397', '#DEC9B2', '#C4C9B3')]
IRON = rgb('#394039')
GROUND = {k:rgb(c) for k,c in {
    'square':'#DDD0B6', 'joint':'#BBA98C', 'rose':'#CCB59B',
    'cobble':'#B9A88F', 'cobble_joint':'#95836C', 'dust':'#CBB58D',
    'garden':'#8B9E67', 'garden_light':'#ADBA84',
    'pool':'#7FC3C5', 'pool_dark':'#4B969D', 'pool_hi':'#CBE8DC',
}.items()}


def windows(material, height, bay=10, floor=13, pointed=False):
    """Divided glazing, dressed jambs, pointed brick heads, sills and spaced ashlar."""
    courses = stone_courses(material, 5, 13)
    def pattern(u,v,lit):
        c,k=int(u)%bay,int(v)%floor
        trim=WHITE['lit' if lit else 'dark']
        top=floor-3-(abs(c-bay/2)*1.1 if pointed else 0)
        if 3<=c<=bay-3 and 3<=k<=top and v<height-3:
            if c in (3,bay-3,bay//2) or k in (3,6,int(top)):return trim
            return GLASS['mid' if lit else 'dark']
        if k==2 and 2<=c<=bay-2:return trim
        return courses(u,v,lit)
    return pattern


def dome(s,ci,cj,r,z,rise,material=LEAD,half=None):
    """A tessellated hemisphere; half selects the real outward half of a semi-dome."""
    if half is None:
        revolve(s,ci,cj,r,z,rise,DOME,material,ribs=4,segments=32)
        return
    faces=[]
    for (t,rr),(nt,nr) in zip(DOME,DOME[1:]):
        for n in range(16):
            a=half-math.pi/2+n*math.pi/16;b=a+math.pi/16
            pts=[P(s,ci+rad*r*math.cos(ang),cj+rad*r*math.sin(ang),z+tt*rise)
                 for tt,rad,ang in ((t,rr,a),(t,rr,b),(nt,nr,b),(nt,nr,a))]
            lit=math.sin((a+b)/2)-.5*math.cos((a+b)/2)>0
            faces.append((math.cos(a)+math.sin(a)+math.cos(b)+math.sin(b),n,pts,lit))
    for _,n,pts,lit in sorted(faces):
        poly(s,pts,lambda x,y,lit=lit:material['line'] if y%6==0 else material['lit' if lit else 'dark'])
        if n%4==0:seg(s,pts[0],pts[3],material['hi' if lit else 'deep'])


def finial(s,i,j,z):
    cylinder(s,i,j,.08,.08,z,3,GOLD,segments=8)
    cylinder(s,i,j,.15,.15,z+3,2,GOLD,segments=12)
    # The crescent is an open curved strip, with both horns, not a Christian cross.
    points=[P(s,i+.23*math.cos(a),j,z+6+2*math.sin(a))
            for a in [math.pi*.3+n*math.pi*1.4/16 for n in range(17)]]
    for a,b in zip(points,points[1:]):seg(s,a,b,GOLD['hi'])


def minaret(s,ci,cj,z,height=98,balconies=3,material=WHITE):
    block(s,ci-.48,cj-.48,.96,.96,12,STONE,stone_courses(STONE,4,9),z=z)
    cylinder(s,ci,cj,.42,.42,z+12,height-27,material,
             lambda u,v,lit:material['line'] if int(u)%5==0 else None,segments=16)
    for n in range(balconies):
        h=z+height*(.37+n*.18)
        for zz,r in ((-3,.46),(-2,.56),(-1,.68),(0,.76)):
            cylinder(s,ci,cj,r,r,h+zz,1,WHITE,segments=16)
        cylinder(s,ci,cj,.67,.67,h+1,4,WHITE,
                 lambda u,v,lit:IRON if int(u)%3==1 and v>1 else None,segments=16)
        cylinder(s,ci,cj,.74,.74,h+5,1,WHITE,segments=16)
    cylinder(s,ci,cj,.42,.42,z+height-16,4,material,windows(material,4,8,9),segments=16)
    revolve(s,ci,cj,.48,z+height-12,16,[(0,1),(1,.02)],LEAD,ribs=4,segments=16)
    finial(s,ci,cj,z+height+4)


def arcade(s,i,j,width,depth,z,height,count,material=WHITE,pointed=False):
    """Separate stone piers and extruded arch spandrels leave genuinely open passages."""
    spacing=width/count
    for n in range(count+1):
        a=i+n*spacing
        cylinder(s,a,j+depth/2,.19,.19,z,height-7,material,segments=12)
        for zz,r in ((0,.29),(height-9,.27),(height-7,.33)):
            block(s,a-r,j+depth/2-.3,r*2,.6,2,material,z=z+zz)
    for n in range(count):
        a=i+n*spacing;b=a+spacing;mid=(a+b)/2
        for k in range(14):
            x0=a+spacing*k/14;x1=a+spacing*(k+1)/14
            def rise(x):
                t=abs((x-mid)/(spacing/2))
                return (1-t)*8 if pointed else math.sqrt(max(0,1-t*t))*7
            h0=height-8+rise(x0);h1=height-8+rise(x1)
            for jj,lit in ((j,False),(j+depth,True)):
                pts=[P(s,x0,jj,z+h0),P(s,x1,jj,z+h1),P(s,x1,jj,z+height+3),P(s,x0,jj,z+height+3)]
                poly(s,pts,lambda x,y,lit=lit:material['lit' if lit else 'dark'])
                seg(s,pts[0],pts[1],material['hi' if lit else 'deep'])
                if k%3==0:seg(s,pts[0],pts[3],material['line'])
            poly(s,[P(s,x0,j,z+h0),P(s,x1,j,z+h1),P(s,x1,j+depth,z+h1),P(s,x0,j+depth,z+h0)],
                 lambda x,y:material['deep'])
    band(s,i-.3,j-.1,width+.6,depth+.2,z+height+3,material,2)


def bayram(scene,i,j,z=10):
    """Brick hip-roof hall, southern domed tomb, one SE two-balcony minaret."""
    w,d,h=8.4,6.4,29
    def draw(s):
        block(s,i,j,w,d,h,BRICK,windows(BRICK,h,11,13,True),z=z+4)
        band(s,i,j,w,d,z+4,STONE,4)
        band(s,i,j,w,d,z+h+3,WOOD,2)
        hip_roof(s,i-.3,j-.3,w+.6,d+.6,z+h+5,13,CLAY)
        # West extension and its glazed upper storey, with a low open SW porch.
        block(s,i-.8,j+1,1.8,d-1,25,BRICK,windows(BRICK,25,10,12,True),z=z+4)
        hip_roof(s,i-1,j+.8,2.2,d-.6,z+30,8,CLAY)
        arcade(s,i-.5,j+d-.4,4.5,1.2,z+1,15,3,STONE)
        hip_roof(s,i-.8,j+d-.6,5.1,1.6,z+21,4,CLAY)
        # Southern tomb: pale cube and one lead dome, distinct from the tiled prayer hall.
        a,b=i+5.4,j+d+.1
        block(s,a,b,2.6,2.6,20,WHITE,windows(WHITE,20,10,12,True),z=z)
        band(s,a,b,2.6,2.6,z+19,STONE,2)
        dome(s,a+1.3,b+1.3,1.5,z+22,12)
        finial(s,a+1.3,b+1.3,z+34)
        # +i runs SE: the minaret is at the tomb's SE (+i) end, never swapped NW.
        minaret(s,i+w+.65,j+d+1.1,z,79,2,BRICK)
    scene.add(i+j+w+d+5,draw)


def citadel(scene,i,j,z=36):
    """Upper Akkale's irregular open rampart and projecting angular bastions on rock."""
    w,d=10.6,8.4
    def draw(s):
        # Empty upper court is intentional: this is a fort, not a roofed palace/keep.
        slab(s,[(i,j+1),(i+8,j),(i+w,j+2),(i+w-.8,j+d),(i+1,j+d)],z,z+4,ROCK)
        def masonry(u,v,lit):
            if int(v)%15 in (9,10):return BRICK['lit' if lit else 'dark']
            if int(v)//5%3==1 and int(u)%23<7:return WHITE['mid' if lit else 'dark']
            if 22<v<29 and int(u)%19 in (6,7):return STONE['deep']
            return stone_courses(STONE,5,12)(u,v,lit)
        for a,b,wi,wj,h in ((i,j+1,8,.65,32),(i,j+1,.7,d-1,31),
                             (i+w-.9,j+2,.7,d-2,34),(i+1,j+d-.7,w-2,.65,28)):
            cover=block(s,a,b,wi,wj,h,STONE,masonry,z=z+4)
            crenellate(s,a,b,wi,wj,z+h+4,STONE,cover,step=6,height=3)
        # Selected upper-fort projections, not a claim to show all 42 inner-wall towers.
        for a,b,h in ((i-.2,j+.6,37),(i+7.3,j-.1,40),(i+w-1.1,j+2.1,35),
                       (i+.8,j+d-1,33),(i+7.3,j+d-1,36)):
            pts=[(a-.6,b),(a+.6,b),(a+1.1,b+.75),(a,b+1.65),(a-.8,b+.8)]
            slab(s,pts,z+4,z+h,STONE,masonry)
            for aa,bb in zip(pts,pts[1:]+pts[:1]):
                for t in (.12,.44,.76):
                    x0=aa[0]+(bb[0]-aa[0])*t;y0=aa[1]+(bb[1]-aa[1])*t
                    block(s,x0-.1,y0-.1,.23,.23,3,STONE,z=z+h)
        # Recessed stone steps climb within the ward, below the parapets.
        for n in range(8):block(s,i+2.1+n*.35,j+2.6, .4,1.1,2+n*2,STONE,z=z+4)
    scene.add(i+j+w+d+3,draw)


def bedesten(scene,i,j,z=14):
    """Mahmut Paşa's low Ottoman market: two rows of five lead domes and striped portal."""
    w,d,h=6.6,12.8,23
    def draw(s):
        openings=windows(FIELDSTONE,h,12,14,True)
        def rubble(u,v,lit):
            opening=openings(u,v,lit)
            if opening:return opening
            if int(v)%4==0 or (int(u)+int(v)//4*5)%11==0:
                return FIELDSTONE['line' if lit else 'deep']
            patch=(int(u)//7*17+int(v)//4*11)%5
            return FIELDSTONE['mid' if lit and patch==1 else 'hi' if lit and patch==3 else
                              'lit' if lit else 'deep' if patch==1 else 'dark']
        block(s,i,j,w,d,h,FIELDSTONE,rubble,z=z)
        band(s,i,j,w,d,z+1,WHITE,2)
        band(s,i,j,w,d,z+h,BRICK,2)
        # Lower perimeter shops retain their clay lean-to appearance around the domed hall.
        for a,b,ww,dd in ((i-.7,j-.4,.8,d+.8),(i+w-.1,j-.4,.8,d+.8),
                           (i-.7,j+d-.1,w+1.4,.8)):
            block(s,a,b,ww,dd,12,FIELDSTONE,rubble,z=z)
            hip_roof(s,a-.1,b-.1,ww+.2,dd+.2,z+12,4,CLAY)
        for row in range(5):
            for col in range(2):
                a=i+1.65+col*3.3;b=j+1.28+row*2.56
                cylinder(s,a,b,1.24,1.24,z+h+1,4,BRICK,segments=16)
                dome(s,a,b,1.4,z+h+5,10)
        # Portal belongs on the short south end; no guessed museum lettering.
        def portal(u,v,lit):
            opening=arch_opening(u,v,12,6,13,WOOD['dark'])
            if opening:
                return WHITE['lit' if lit else 'dark'] if int(u)==12 else opening
            return WHITE['lit' if lit else 'dark'] if int(v)//3%2 else STONE['dark' if lit else 'deep']
        block(s,i+1.6,j+d+.65,3.4,.5,22,STONE,portal,z=z)
        band(s,i+1.6,j+d+.65,3.4,.5,z+21,WHITE,2)
        for n in range(3):block(s,i+1.4-n*.1,j+d+1.2+n*.2,3.8+n*.2,.25,3-n,STONE,z=z)
    scene.add(i+j+w+d+4,draw)


def ethnography(scene,i,j,z=20):
    """Namazgâh museum: four columns/three pointed arches, palmettes and one lead dome."""
    w,d,h=12.4,6.8,27
    def draw(s):
        # Broad low symmetrical wings; open central court remains behind the domed vestibule.
        for a,b,ww,dd in ((i,j,3.4,d),(i+w-3.4,j,3.4,d),(i+3.4,j,w-6.8,2.0)):
            block(s,a,b,ww,dd,h,WHITE,windows(WHITE,h,12,26,True),z=z+6)
            band(s,a,b,ww,dd,z+7,STONE,3)
            band(s,a,b,ww,dd,z+h+5,WHITE,3)
            hip_roof(s,a,b,ww,dd,z+h+8,4,LEAD)
        for a in (i,i+w-3.4):
            # Carved corner aedicules rise above the low eaves, without extra domes.
            pediment(s,a+.1,j+d-.2,3.2,.55,z+h+10,7,WHITE)
            for x in (a+.15,a+2.95):block(s,x,j+d-.12,.22,.24,23,STONE,z=z+10)
        block(s,i+3.4,j+2,5.6,3.9,32,WHITE,windows(WHITE,32,11,14,True),z=z+6)
        cylinder(s,i+6.2,j+4.25,2.05,2.05,z+37,5,WHITE,segments=24)
        cylinder(s,i+6.2,j+4.25,2.17,2.17,z+40,3,BRONZE,
                 lambda u,v,lit:BRONZE['hi' if lit else 'deep'] if int(u)%5==0 else None,segments=24)
        dome(s,i+6.2,j+4.25,2.35,z+43,17)
        # Recessed carved entrance and three true pointed arches on four marble supports.
        block(s,i+4.5,j+6,3.4,.25,24,WOOD,
              lambda u,v,lit:WOOD['hi'] if int(u)%5==0 or int(v)%7==0 else None,z=z+6)
        arcade(s,i+3.6,j+6.3,5.2,1.15,z+6,24,3,WHITE,True)
        # Palmette ridge ornaments are solid tapered stone reliefs, spaced above the arches.
        for a in (i+.3,i+2.9,i+3.7,i+5.1,i+6.5,i+8,i+9.3,i+11.8):
            b=j+7.45 if 3.5<a-i<9 else j+d
            zz=z+36 if 3.5<a-i<9 else z+33
            poly(s,[P(s,a-.24,b,zz),P(s,a,b,zz+4),P(s,a+.24,b,zz),P(s,a,b,zz-1)],
                 lambda x,y:WHITE['hi'] if x%3 else WHITE['mid'])
        for n in range(7):block(s,i+2.9-n*.12,j+7.6+n*.25,6.6+n*.24,.3,7-n,WHITE,z=z)
    scene.add(i+j+w+d+6,draw)


def anitkabir(scene,i,j,z=22):
    """Low travertine mausoleum, eight-by-fourteen colonnades, flat attic and broad stairs."""
    w,d=9.4,13.6
    def draw(s):
        for n in range(3):block(s,i-n*.15,j-n*.15,w+n*.3,d+n*.3,3,TRAVERTINE,z=z+n*3)
        # Hall set well inside the freestanding square colonnade.
        def hall(u,v,lit):
            c=int(u)%18
            if 3<c<13 and 7<v<30:return BRONZE['dark' if lit else 'deep']
            return stone_courses(TRAVERTINE,5,16)(u,v,lit)
        block(s,i+1.5,j+1.4,w-3,d-2.8,35,TRAVERTINE,hall,z=z+9)
        posts=[]
        # Eight on either short face; fourteen on either long face, with paired end posts.
        posts += [(i+.65+k*(w-1.3)/7,b) for b in (j+.35,j+d-.35) for k in range(8)]
        posts += [(a,j+.95+k*(d-1.9)/13) for a in (i+.25,i+w-.25) for k in range(14)]
        for a,b in sorted(posts,key=lambda p:sum(p)):
            block(s,a-.17,b-.17,.34,.34,34,TRAVERTINE,stone_courses(TRAVERTINE,6,12),z=z+9)
        # Roof slabs only span the colonnades; the Hall's separate flat roof fills the centre.
        for a,b,ww,dd in ((i,j,w,.9),(i,j+d-.9,w,.9),(i,j,.9,d),(i+w-.9,j,.9,d)):
            block(s,a,b,ww,dd,7,TRAVERTINE,stone_courses(TRAVERTINE,3,15),z=z+43)
            band(s,a,b,ww,dd,z+49,WHITE,2)
        block(s,i+1.35,j+1.2,w-2.7,d-2.4,6,TRAVERTINE,z=z+44)
        # Muqarnas-inspired cornice teeth stay on the material face below the flat eaves.
        for k in range(18):
            block(s,i+.1+k*(w-.2)/18,j+d-.1,.17,.12,2,WHITE,z=z+46)
        for n in range(10):block(s,i-.2-n*.06,j+d+n*.26,w+.4+n*.12,.3,10-n,TRAVERTINE,z=z)
        for a in (i-1.1,i+w+.2):
            block(s,a,j+d+.25,.9,2.8,10,TRAVERTINE,stone_courses(TRAVERTINE,4,10),z=z)
            # Relief heads and draped bodies bounded by each low stair-side panel.
            for n in range(4):
                x,y=P(s,a+.92,j+d+.6+n*.55,z+6)
                poly(s,[(x-1,y+2),(x-2,y-2),(x,y-4),(x+2,y-2),(x+1,y+2)],
                     lambda x,y:TRAVERTINE['hi'])
        block(s,i+w/2-.4,j+d+1.1,.8,.5,7,WHITE,z=z+2)
    scene.add(i+j+w+d+7,draw)


def kocatepe(scene,i,j,z=12):
    """Prayer hall: four triple-balcony minarets, four half-domes and twelve small domes."""
    w,d=10.6,10.2
    def draw(s):
        block(s,i-.5,j-.5,w+1,d+1,8,STONE,stone_courses(STONE,4,13),z=z)
        # Four square corner pedestals/shafts, back to front around the hall.
        towers=[(i-.2,j-.3),(i+w+.2,j-.3),(i-.2,j+d+.3),(i+w+.2,j+d+.3)]
        # Rear pair precede the prayer hall; the two side/front towers finish last.
        minaret(s,*towers[0],z+8,150,3)
        block(s,i,j,w,d,36,WHITE,windows(WHITE,36,12,14,True),z=z+8)
        for zz in (9,24,43):band(s,i,j,w,d,z+zz,STONE if zz==9 else WHITE,2)
        # Twelve smaller complete cupolas, three along each cardinal side of the upper shell.
        small=[]
        for n in range(3):
            small.extend([(i+2+n*3.2,j+.9),(i+2+n*3.2,j+d-.9),
                          (i+.9,j+2+n*3.1),(i+w-.9,j+2+n*3.1)])
        for a,b in sorted(small,key=lambda p:sum(p)):
            cylinder(s,a,b,.77,.77,z+44,4,WHITE,windows(WHITE,4,7,8),segments=16)
            dome(s,a,b,.88,z+48,7)
        ci,cj=i+w/2,j+d/2
        # Half-domes spring from the central drum, each occupying an outward half-plane.
        for a,b,angle in sorted([(ci-2.25,cj,math.pi),(ci,cj-2.25,-math.pi/2),
                                  (ci+2.25,cj,0),(ci,cj+2.25,math.pi/2)],key=lambda p:sum(p[:2])):
            cylinder(s,a,b,1.8,1.8,z+45,10,WHITE,windows(WHITE,10,9,12,True),segments=24)
            dome(s,a,b,2.2,z+55,18,half=angle)
        cylinder(s,ci,cj,2.35,2.35,z+59,15,WHITE,windows(WHITE,15,8,14,True),segments=32)
        cylinder(s,ci,cj,2.48,2.48,z+72,3,WHITE,segments=32)
        dome(s,ci,cj,2.65,z+75,26)
        finial(s,ci,cj,z+101)
        # Southern qibla side is visible. The actual north entrance is behind the hall.
        block(s,i+3.8,j+d-.1,3,.7,28,WHITE,windows(WHITE,28,12,14,True),z=z+8)
        band(s,i+3.8,j+d-.1,3,.7,z+35,STONE,2)
        for a,b in towers[1:]:minaret(s,a,b,z+8,150,3)
        for n in range(5):block(s,i-.2,j+d+1+n*.25,w+.4,.3,5-n,STONE,z=z)
    scene.add(i+j+w+d+7,draw)


def townhouse(scene,i,j,wi=2.5,wj=3,floors=2,seed=0,z=0):
    """Old Ankara plaster/timber houses: deep eaves, projecting cumba, shop and clay tiles."""
    m=palette_of(WALLS[seed%len(WALLS)]);h=floors*12+3
    dressed=windows(m,h,10,12)
    def pattern(u,v,lit):
        c=int(u)%10
        if int(v) in (11,23) or c==0 and v>10:return WOOD['lit' if lit else 'dark']
        if v<10 and 2<c<8:
            return WOOD['dark'] if seed%2 else GLASS['dark']
        return dressed(u,v,lit)
    def draw(s):
        block(s,i,j,wi,wj,h,m,pattern,z=z)
        band(s,i,j,wi,wj,z+1,STONE,2)
        if floors>1 and seed%3!=2:
            a,b=i+.25,j+wj-.15
            block(s,a,b,wi-.5,.65,11,m,pattern,z=z+13)
            for x in (a,a+wi-.5):
                seg(s,P(s,x,b+.6,z+13),P(s,x,b+.05,z+8),WOOD['dark'],2)
                seg(s,P(s,x,b+.65,z+13),P(s,x,b+.65,z+24),WOOD['dark'])
            band(s,a,b,wi-.5,.65,z+24,WOOD,1)
            hip_roof(s,a-.1,b-.1,wi-.3,.85,z+25,3,CLAY)
        band(s,i,j,wi,wj,z+h,WOOD,2)
        hip_roof(s,i-.25,j-.25,wi+.5,wj+.5,z+h+2,8+seed%3,CLAY)
        block(s,i+wi-.65,j+.4,.4,.45,7,STONE,stone_courses(STONE,3,7),z=z+h+4)
        band(s,i+wi-.65,j+.4,.4,.45,z+h+11,CLAY,2)
    scene.add(i+j+wi+wj+2,draw)


def main():
    for name,builder,_,_,_,z in SITES:
        print(preview([lambda s,b=builder,z=z:b(s,7,7,z=z)],'ankara-'+name,
                      size=(350,310),origin=(175,130),tiles=30))
    print(preview([lambda s,k=k:townhouse(s,3+k*3.6,4,floors=1+k%3,seed=k)
                   for k in range(6)],'ankara-houses',size=(340,240),origin=(80,75),tiles=27))
    import sprites
    im=sprites.pamukkale()
    path=Path(__file__).resolve().parents[2]/'docs/art/capitals/turkey-pamukkale.png'
    im.resize((im.width*4,im.height*4),0).save(path)
    print(path)


# name, builder, footprint, real longitude/latitude, north-up ground anchor, elevation.
SITES = [
    ('bayram',bayram,(8.4,6.4),(32.85778,39.94417),(365,130),10),
    ('citadel',citadel,(10.6,8.4),(32.86500,39.94167),(610,175),36),
    ('bedesten',bedesten,(6.6,12.8),(32.86194,39.93833),(590,270),14),
    ('ethnography',ethnography,(12.4,6.8),(32.854894,39.932668),(225,295),20),
    ('anitkabir',anitkabir,(9.4,13.6),(32.83778,39.92556),(150,445),22),
    ('kocatepe',kocatepe,(10.6,10.2),(32.86083,39.91667),(405,460),12),
]


if __name__=='__main__':
    main()
