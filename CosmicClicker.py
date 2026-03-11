#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║                       Cosmic Clicker                         ║
║        A Procedural Cosmic Fireworks Engine Disguised        ║
║                    as a Clicker Game  v5                     ║
╚══════════════════════════════════════════════════════════════╝

Requirements: pip install pygame
Run:          python CosmicClicker.py

Controls:
  Left-click game area  → trigger chain reactions
  Hold left-click       → rapid fire
  Click upgrades        → purchase
  Mouse wheel           → scroll upgrade panel
  [P]                   → Prestige (Reality Collapse)
  [S]                   → Save game
  [L]                   → Load game
  [Esc]                 → Quit

NEW in v5:
  • Void Crystals appear randomly; click for 10x energy boost & intensified visuals!
  • Upgrade panel filters (click category buttons at top)
  • Every upgrade now gives a non‑visual benefit (FX unlocks add +1% energy per level)
  • Combo numbers are formatted (1K, 2.5M, etc.) and colored by suffix.
  • Text truncation prevents UI overflow
  • Filter buttons now use abbreviated labels for a cleaner fit.
  • Removed floating combo text to reduce clutter.

NEW in this mod:
  • Every upgrade level now gives +1% to all click and auto income (universal multiplier).
  • Added three new FX types: Void Tendrils, Prism Beams, and Galactic Swirls.
  • These new FX are unlocked by and scale with the Void Engine, Prism Emitter, and Spiral Weaver upgrades.
  • Added a new color palette (PAL_GALAXY) for cosmic variety.
"""

import pygame, math, random, sys, json, os, time
from collections import deque
from typing import List, Tuple

# ─────────────────────────────────────────────────────────────
# CONSTANTS (optimised for performance & variety)
# ─────────────────────────────────────────────────────────────
FPS = 60
WIDTH, HEIGHT = 1280, 800
BG = (2, 2, 8)

MAX_CHAIN_DEPTH = 8
MAX_FX = 2000                # comfortable limit
MAX_SPAWN = 40               # increased slightly for variety
CHAIN_DECAY = 0.78

SAVE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hyper_save.json")

# Void Crystal settings (replaces golden cookie placeholder)
CRYSTAL_SPAWN_MIN = 30        # seconds
CRYSTAL_SPAWN_MAX = 90
CRYSTAL_LIFETIME = 10
CRYSTAL_BUFF_DURATION = 5
CRYSTAL_BUFF_MULT = 10

# ── Colors ──
WHITE  = (255,255,255)
YELLOW = (255,220,50)
ORANGE = (255,140,30)
RED    = (255,50,30)
PINK   = (255,80,180)
MAGENTA= (220,40,220)
PURPLE = (150,40,255)
BLUE   = (40,120,255)
CYAN   = (40,220,255)
GREEN  = (40,255,120)
LIME   = (180,255,30)
ELECTRIC=(120,180,255)
PLASMA = (180,100,255)
GOLD   = (255,200,50)
TEAL   = (0,200,180)
CRIMSON= (180,20,60)
VIOLET = (200,80,255)
INDIGO = (80,0,200)
SILVER = (200,210,220)
EMBER  = (255,100,20)
ICE    = (180,230,255)
VOID   = (40,0,80)
DARK_RED=(120,10,20)
AURORA = (100,255,180)
FIREWORK= (255,150,255)
NEBULA_PINK = (200,100,200)
SOLAR = (255,180,50)
QUANTUM = (0,255,200)
DREAM = (150,50,255)

PAL_FIRE    = [WHITE, YELLOW, ORANGE, RED, PINK]
PAL_ELEC    = [WHITE, CYAN, BLUE, ELECTRIC, PURPLE]
PAL_PLASMA  = [WHITE, MAGENTA, PLASMA, PURPLE, BLUE]
PAL_COSMIC  = [WHITE, GOLD, CYAN, GREEN, PINK, MAGENTA]
PAL_NOVA    = [WHITE, WHITE, YELLOW, CYAN, MAGENTA, BLUE]
PAL_VOID    = [PURPLE, INDIGO, VOID, MAGENTA, BLUE]
PAL_ICE     = [WHITE, ICE, CYAN, BLUE, TEAL]
PAL_EMBER   = [WHITE, YELLOW, EMBER, ORANGE, RED, CRIMSON]
PAL_RAINBOW = [RED, ORANGE, YELLOW, GREEN, CYAN, BLUE, PURPLE, PINK]
PAL_GOLD    = [WHITE, GOLD, YELLOW, ORANGE]
PAL_TOXIC   = [WHITE, LIME, GREEN, TEAL, CYAN]
PAL_AURORA  = [WHITE, AURORA, CYAN, GREEN, TEAL]
PAL_FIREWORK= [WHITE, FIREWORK, PINK, MAGENTA, YELLOW]
PAL_NEBULA  = [PURPLE, NEBULA_PINK, PINK, MAGENTA, VIOLET]
PAL_SOLAR   = [WHITE, SOLAR, GOLD, ORANGE, RED]
PAL_QUANTUM = [WHITE, QUANTUM, CYAN, BLUE, PURPLE]
PAL_DREAM   = [WHITE, DREAM, PINK, MAGENTA, VIOLET]
PAL_GALAXY  = [VOID, PURPLE, INDIGO, MAGENTA, PINK]  # new

ALL_PALETTES = [PAL_FIRE, PAL_ELEC, PAL_PLASMA, PAL_COSMIC, PAL_NOVA,
                PAL_VOID, PAL_ICE, PAL_EMBER, PAL_RAINBOW, PAL_GOLD, PAL_TOXIC,
                PAL_AURORA, PAL_FIREWORK, PAL_NEBULA, PAL_SOLAR, PAL_QUANTUM, PAL_DREAM,
                PAL_GALAXY]  # added new palette

# ─────────────────────────────────────────────────────────────
# BIG NUMBER FORMAT & SUFFIX COLORS
# ─────────────────────────────────────────────────────────────
_SFX = ["","K","M","B","T","Qa","Qi","Sx","Sp","Oc","No","Dc",
        "UDc","DDc","TDc","QaDc","QiDc","SxDc","SpDc","OcDc","NoDc",
        "Vg","UVg","DVg","TVg","QaVg","QiVg","SxVg","SpVg","OcVg","NoVg",
        "Tg","UTg","DTg","TTg","QaTg","QiTg","SxTg","SpTg","OcTg","NoTg",
        "Qd","UQd","DQd","TQd","QaQd","QiQd","SxQd","SpQd","OcQd","NoQd",
        "Qq","UQq","DQq","INF"]

# Colors for each suffix (index i corresponds to _SFX[i])
_SUFFIX_COLORS = [
    WHITE,      # ""
    GREEN,      # K
    BLUE,       # M
    RED,        # B
    ORANGE,     # T
    CYAN,       # Qa
    MAGENTA,    # Qi
    YELLOW,     # Sx
    PINK,       # Sp
    PURPLE,     # Oc
    TEAL,       # No
    GOLD,       # Dc
    ELECTRIC,   # UDc
    PLASMA,     # DDc
    VIOLET,     # TDc
    INDIGO,     # QaDc
    CRIMSON,    # QiDc
    AURORA,     # SxDc
    FIREWORK,   # SpDc
    NEBULA_PINK,# OcDc
    SOLAR,      # NoDc
    QUANTUM,    # Vg
    DREAM,      # UVg
    WHITE,      # DVg ... (you can expand as needed)
    WHITE,
    WHITE,
    WHITE,
    WHITE,
    WHITE,
    WHITE,
    WHITE,
    WHITE,
    WHITE,
    WHITE,
    WHITE,
    WHITE,
    WHITE,
    WHITE,
    WHITE,
    WHITE,
    WHITE,
    WHITE,
    WHITE,
    WHITE,
    WHITE,
    WHITE,
    WHITE,
    WHITE,
]

def fmt(n):
    if n < 0: return "-"+fmt(-n)
    if n < 1000:
        return f"{n:.0f}" if abs(n-round(n))<0.05 else f"{n:.1f}"
    i=0
    while n>=1000 and i<len(_SFX)-1:
        n/=1000; i+=1
    if n>=100: return f"{n:.0f}{_SFX[i]}"
    if n>=10:  return f"{n:.1f}{_SFX[i]}"
    return f"{n:.2f}{_SFX[i]}"

def suffix_index_from_value(val):
    """Return the suffix index for a given number (same logic as fmt)."""
    if val < 1000:
        return 0
    i = 0
    while val >= 1000 and i < len(_SFX)-1:
        val /= 1000
        i += 1
    return i

# ─────────────────────────────────────────────────────────────
# GLOW CACHE (moderate radius)
# ─────────────────────────────────────────────────────────────
_glow={}
def glow_surf(r, c, inten=1.0):
    r=max(2,min(r,100))        # balanced
    k=(r,c,int(inten*10))
    if k in _glow: return _glow[k]
    s=pygame.Surface((r*2,r*2),pygame.SRCALPHA)
    for i in range(r,0,-2):
        a=int(min(255,(1-i/r)*120*inten))
        rc=min(255,int(c[0]*inten)); gc=min(255,int(c[1]*inten)); bc=min(255,int(c[2]*inten))
        pygame.draw.circle(s,(rc,gc,bc,a),(r,r),i)
    _glow[k]=s
    if len(_glow)>400:
        for kk in list(_glow.keys())[:100]: del _glow[kk]
    return s

# ─────────────────────────────────────────────────────────────
# LERP HELPERS
# ─────────────────────────────────────────────────────────────
def lerp_color(a,b,t):
    t=max(0,min(1,t))
    return (int(a[0]+(b[0]-a[0])*t), int(a[1]+(b[1]-a[1])*t), int(a[2]+(b[2]-a[2])*t))

def palette_sample(pal, t):
    t=max(0,min(0.999,t))
    idx=t*(len(pal)-1)
    lo=int(idx); hi=min(lo+1,len(pal)-1)
    return lerp_color(pal[lo],pal[hi],idx-lo)

def clamp_color(c):
    return (max(0,min(255,int(c[0]))),max(0,min(255,int(c[1]))),max(0,min(255,int(c[2]))))

# ─────────────────────────────────────────────────────────────
# BASE FX + POOL
# ─────────────────────────────────────────────────────────────
class FX:
    __slots__=['x','y','vx','vy','life','max_life','depth','energy','alive','color','size']
    def __init__(self):
        self.alive=False; self.x=self.y=self.vx=self.vy=0.0
        self.life=self.max_life=1.0; self.depth=0; self.energy=0.0
        self.color=WHITE; self.size=2.0
    def init(self,x,y,d=0,e=0):
        self.x,self.y=x,y; self.depth=d; self.energy=e; self.alive=True; return self
    def update(self,dt):
        self.life-=dt
        if self.life<=0: self.alive=False
    def t(self): return max(0,self.life/self.max_life) if self.max_life>0 else 0
    def draw(self,scr): pass

class Pool:
    def __init__(self,factory,n=200):
        self.fac=factory; self.pool=deque(factory() for _ in range(n)); self.active=[]
    def get(self):
        return self.pool.pop() if self.pool else self.fac()
    def spawn(self,o): self.active.append(o)
    def update(self,dt):
        keep=[]
        for o in self.active:
            if o.alive:
                o.update(dt)
                if o.alive: keep.append(o)
                else: self.pool.append(o)
            else: self.pool.append(o)
        self.active=keep
    def draw(self,scr):
        for o in self.active:
            if o.alive: o.draw(scr)
    @property
    def count(self): return len(self.active)

# ─────────────────────────────────────────────────────────────
# FX CLASSES (existing, plus new ones below)
# ─────────────────────────────────────────────────────────────

class Particle(FX):
    __slots__=FX.__slots__+['friction','do_glow','gravity','trail','max_trail']
    def __init__(self):
        super().__init__(); self.friction=0.98; self.do_glow=False; self.gravity=0
        self.trail=[]; self.max_trail=0
    def setup(self,x,y,vx,vy,life,color,sz=2,glow=False,grav=0,depth=0,trail=0):
        self.init(x,y,depth); self.vx,self.vy=vx,vy; self.life=self.max_life=life
        self.color=color; self.size=sz; self.do_glow=glow; self.gravity=grav
        self.trail=[]; self.max_trail=trail; return self
    def update(self,dt):
        if self.max_trail>0:
            self.trail.append((self.x,self.y))
            if len(self.trail)>self.max_trail: self.trail.pop(0)
        self.x+=self.vx*dt*60; self.y+=self.vy*dt*60
        self.vy+=self.gravity*dt*60; self.vx*=self.friction; self.vy*=self.friction
        super().update(dt)
    def draw(self,scr):
        t=self.t(); sz=max(1,int(self.size*(0.3+0.7*t)))
        for i,(tx,ty) in enumerate(self.trail):
            f=i/max(1,len(self.trail)); a=f*t
            c=clamp_color((self.color[0]*a,self.color[1]*a,self.color[2]*a))
            pygame.draw.circle(scr,c,(int(tx),int(ty)),max(1,int(sz*f*0.7)))
        if self.do_glow and sz>2:
            scr.blit(glow_surf(sz*3,self.color,t*0.7),(int(self.x)-sz*3,int(self.y)-sz*3),
                     special_flags=pygame.BLEND_ADD)
        c=clamp_color((self.color[0]*t+200*(1-t)*0.15,self.color[1]*t,self.color[2]*t))
        if sz<=1:
            try: scr.set_at((int(self.x),int(self.y)),c)
            except: pass
        else:
            pygame.draw.circle(scr,c,(int(self.x),int(self.y)),sz)
            pygame.draw.circle(scr,WHITE,(int(self.x),int(self.y)),max(1, min(2, sz//3)))

class Explosion(FX):
    __slots__=FX.__slots__+['max_r','pal','ring','flash']
    def __init__(self):
        super().__init__(); self.max_r=40; self.pal=PAL_FIRE; self.ring=False; self.flash=False
    def setup(self,x,y,r=40,life=0.5,pal=None,depth=0,energy=0,ring=False,flash=False):
        self.init(x,y,depth,energy); self.max_r=r; self.life=self.max_life=life
        self.pal=pal or PAL_FIRE; self.ring=ring; self.flash=flash; return self
    def draw(self,scr):
        t=self.t(); p=1-t; r=int(self.max_r*p)
        if r<2: return
        c=palette_sample(self.pal,p)
        if self.flash and t>0.85:
            pygame.draw.circle(scr,WHITE,(int(self.x),int(self.y)),r, max(1, int(r*0.1)))
            return
        if self.ring:
            th=max(1,int(r*0.15*t))
            pygame.draw.circle(scr,c,(int(self.x),int(self.y)),r,th)
            if r>15:
                scr.blit(glow_surf(r,c,t*0.3),(int(self.x)-r,int(self.y)-r),
                         special_flags=pygame.BLEND_ADD)
        else:
            scr.blit(glow_surf(r,c,t*1.2),(int(self.x)-r,int(self.y)-r),
                     special_flags=pygame.BLEND_ADD)

class Shockwave(FX):
    __slots__=FX.__slots__+['max_r','thick','distort']
    def __init__(self):
        super().__init__(); self.max_r=100; self.thick=3; self.distort=False
    def setup(self,x,y,r=100,life=0.8,color=CYAN,thick=3,depth=0,distort=False):
        self.init(x,y,depth); self.max_r=r; self.life=self.max_life=life
        self.color=color; self.thick=thick; self.distort=distort; return self
    def draw(self,scr):
        t=self.t(); r=int(self.max_r*(1-t))
        if r<3: return
        th=max(2,int(self.thick*t)+1)
        c=clamp_color((self.color[0]*t,self.color[1]*t,self.color[2]*t))
        pygame.draw.circle(scr,c,(int(self.x),int(self.y)),r,th)
        cw=clamp_color((min(255,self.color[0]*t*1.5+80*t),min(255,self.color[1]*t*1.5+80*t),min(255,self.color[2]*t*1.5+80*t)))
        pygame.draw.circle(scr,cw,(int(self.x),int(self.y)),max(2,r-th//2),max(1,th//2))
        if self.distort and r>10:
            r2=int(r*0.7)
            c2=clamp_color((self.color[0]*t*0.4,self.color[1]*t*0.4,self.color[2]*t*0.4))
            pygame.draw.circle(scr,c2,(int(self.x),int(self.y)),r2,max(1,th-1))
        if r>8:
            scr.blit(glow_surf(min(r+6, 100),self.color,t*0.3),(int(self.x)-min(r+6,100),int(self.y)-min(r+6,100)),
                     special_flags=pygame.BLEND_ADD)

class PrismBurst(FX):
    __slots__=FX.__slots__+['radius','rot','points']
    def __init__(self):
        super().__init__(); self.radius=20; self.rot=0; self.points=3
    def setup(self,x,y,r=20,pts=3,life=1.0,color=PINK,depth=0):
        self.init(x,y,depth); self.radius=r; self.points=pts; self.life=self.max_life=life
        self.color=color; self.rot=random.uniform(0,6.28); return self
    def update(self,dt):
        self.rot+=3*dt; super().update(dt)
    def draw(self,scr):
        t=self.t(); r=self.radius*t
        if r<2: return
        pts=[]
        for i in range(self.points):
            a=self.rot+i*(6.28/self.points)
            pts.append((self.x+math.cos(a)*r, self.y+math.sin(a)*r))
        pygame.draw.polygon(scr, self.color, pts, max(1,int(2*t)))
        scr.blit(glow_surf(min(int(r), 80),self.color,t*0.5),(int(self.x-min(r,80)),int(self.y-min(r,80))),special_flags=pygame.BLEND_ADD)

class Starburst(FX):
    __slots__=FX.__slots__+['radius','inner_ratio','points','rot','speed']
    def __init__(self):
        super().__init__()
        self.radius=20
        self.inner_ratio=0.5
        self.points=5
        self.rot=0
        self.speed=2
    def setup(self,x,y,radius=20,points=5,inner_ratio=0.5,life=1.0,color=PINK,depth=0):
        self.init(x,y,depth)
        self.radius=radius
        self.inner_ratio=inner_ratio
        self.points=points
        self.life=self.max_life=life
        self.color=color
        self.rot=random.uniform(0,6.28)
        self.speed=random.uniform(1,3)
        return self
    def update(self,dt):
        self.rot+=self.speed*dt
        super().update(dt)
    def draw(self,scr):
        t=self.t()
        r=self.radius*t
        if r<2: return
        pts=[]
        for i in range(self.points*2):
            angle = self.rot + i*math.pi/self.points
            rad = r * (self.inner_ratio if i%2 else 1.0)
            pts.append((self.x+math.cos(angle)*rad, self.y+math.sin(angle)*rad))
        c=clamp_color((self.color[0]*t, self.color[1]*t, self.color[2]*t))
        pygame.draw.polygon(scr, c, pts, max(1,int(2*t)))
        scr.blit(glow_surf(min(int(r*1.2), 80), self.color, t*0.5),
                 (int(self.x - min(r*1.2,80)), int(self.y - min(r*1.2,80))),
                 special_flags=pygame.BLEND_ADD)

class Nebula(FX):
    __slots__=FX.__slots__+['max_r','drift_x','drift_y']
    def __init__(self):
        super().__init__(); self.max_r=100; self.drift_x=self.drift_y=0
    def setup(self,x,y,r=100,life=3.0,color=PURPLE,depth=0):
        self.init(x,y,depth); self.max_r=min(r, 120); self.life=self.max_life=life
        self.color=color; self.drift_x=random.uniform(-10,10); self.drift_y=random.uniform(-10,10)
        return self
    def update(self,dt):
        self.x+=self.drift_x*dt; self.y+=self.drift_y*dt; super().update(dt)
    def draw(self,scr):
        t=self.t(); p=1-t
        alpha = math.sin(t * 3.14)
        r = int(self.max_r * (0.5 + 0.5*p))
        if r<5: return
        c=(self.color[0], self.color[1], self.color[2])
        scr.blit(glow_surf(min(r, 100),c,alpha*0.3),(int(self.x-min(r,100)),int(self.y-min(r,100))),special_flags=pygame.BLEND_ADD)

class Lightning(FX):
    __slots__=FX.__slots__+['segs','branches','thick','ex','ey']
    def __init__(self):
        super().__init__(); self.segs=[]; self.branches=[]; self.thick=1; self.ex=self.ey=0
    def setup(self,x,y,ex,ey,life=0.25,color=ELECTRIC,depth=0,thick=2):
        self.init(x,y,depth); self.ex,self.ey=ex,ey; self.life=self.max_life=life
        self.color=color; self.thick=thick; self._gen(); return self
    def _gen(self):
        self.segs=[]; self.branches=[]
        dx,dy=self.ex-self.x,self.ey-self.y; d=math.hypot(dx,dy)
        if d<1: return
        n=max(4,int(d/30)); pts=[(self.x,self.y)]
        for i in range(1,n):
            f=i/n
            pts.append((self.x+dx*f+random.gauss(0,d*0.1),self.y+dy*f+random.gauss(0,d*0.1)))
        pts.append((self.ex,self.ey)); self.segs=pts
        for i in range(1, len(pts)-1):
            if random.random() < 0.5:
                px, py = pts[i]
                bex = px + random.gauss(0, 40)
                bey = py + random.gauss(0, 40)
                br = [(px, py)]
                for j in range(1, random.randint(2,4)):
                    f2 = j / 4.0
                    br.append((px + (bex - px) * f2 + random.gauss(0, 8),
                            py + (bey - py) * f2 + random.gauss(0, 8)))
                self.branches.append(br)

    def draw(self, scr):
        t = self.t()
        if len(self.segs) < 2: return
        a = min(1, t * 2.5)
        c = clamp_color((self.color[0]*a, self.color[1]*a,self.color[2]*a))
        cw = clamp_color((255*a, 255*a, 255*a))
        th = max(1, int(self.thick * a))

        gl_r = max(4, th*3)
        scr.blit(glow_surf(min(gl_r, 60), self.color, a*0.6), (int(self.x - min(gl_r,60)), int(self.y - min(gl_r,60))), special_flags=pygame.BLEND_ADD)
        scr.blit(glow_surf(min(gl_r, 60), self.color, a*0.8), (int(self.ex - min(gl_r,60)), int(self.ey - min(gl_r,60))), special_flags=pygame.BLEND_ADD)
        if t > 0.5:
            ir = int(gl_r * 0.4 * t)
            if ir > 1:
                pygame.draw.circle(scr, cw, (int(self.ex), int(self.ey)), ir)

        pts = [(int(p[0]), int(p[1])) for p in self.segs]
        pygame.draw.lines(scr, c, False, pts, th + 2)
        pygame.draw.lines(scr, cw, False, pts, max(1, th))

        for br in self.branches:
            bp = [(int(p[0]), int(p[1])) for p in br]
            if len(bp) >= 2:
                pygame.draw.lines(scr, c, False, bp, max(1, th))
            
class FractalLightning(FX):
    __slots__=FX.__slots__+['branches','thick']
    def __init__(self):
        super().__init__(); self.branches=[]; self.thick=2
    def setup(self,x,y,radius=80,num_branches=5,life=0.4,color=ELECTRIC,depth=0):
        self.init(x,y,depth); self.life=self.max_life=life; self.color=color
        self.thick=2; self.branches=[]
        num_branches = min(num_branches, 4)
        for _ in range(num_branches):
            a=random.uniform(0,6.28); d=random.uniform(radius*0.4,radius)
            ex,ey=x+math.cos(a)*d,y+math.sin(a)*d
            pts=[(x,y)]; cx2,cy2=x,y; steps=random.randint(4,8)
            for j in range(1,steps+1):
                f=j/steps
                cx2=x+(ex-x)*f+random.gauss(0,radius*0.12)
                cy2=y+(ey-y)*f+random.gauss(0,radius*0.12)
                pts.append((cx2,cy2))
                if random.random()<0.2:
                    sub=[(cx2,cy2)]
                    for _ in range(random.randint(2,3)):
                        cx2+=random.gauss(0,15); cy2+=random.gauss(0,15); sub.append((cx2,cy2))
                    self.branches.append(sub)
            self.branches.append(pts)
        return self
    def draw(self,scr):
        t=self.t(); a=min(1,t*3)
        c=clamp_color((self.color[0]*a,self.color[1]*a,self.color[2]*a))
        cw=clamp_color((255*a,255*a,255*a))
        th=max(2,int(self.thick*a))
        for br in self.branches:
            pts=[(int(p[0]),int(p[1])) for p in br]
            if len(pts)>=2:
                pygame.draw.lines(scr,c,False,pts,th+2)
                pygame.draw.lines(scr,cw,False,pts,max(1,th-1))

class Meteor(FX):
    __slots__=FX.__slots__+['trail','angle','speed']
    def __init__(self):
        super().__init__(); self.trail=[]; self.speed=5; self.angle=0
    def setup(self,x,y,angle,speed=6,life=1.5,color=ORANGE,depth=0,energy=0):
        self.init(x,y,depth,energy); self.angle=angle; self.speed=speed
        self.vx=math.cos(angle)*speed; self.vy=math.sin(angle)*speed
        self.life=self.max_life=life; self.color=color; self.trail=[]
        self.size=random.uniform(3,7); return self
    def update(self,dt):
        self.trail.append((self.x,self.y))
        if len(self.trail)>6: self.trail.pop(0)
        self.x+=self.vx*dt*60; self.y+=self.vy*dt*60; self.vy+=0.05*dt*60
        if self.x<-60 or self.x>WIDTH+60 or self.y>HEIGHT+60: self.alive=False; return
        super().update(dt)
    def draw(self,scr):
        t=self.t()
        for i,(tx,ty) in enumerate(self.trail):
            f=i/max(1,len(self.trail)); r=max(1,int(self.size*f*t))
            c=clamp_color((self.color[0]*f*t,self.color[1]*f*t,self.color[2]*f*t))
            pygame.draw.circle(scr,c,(int(tx),int(ty)),r)
        sz=max(1,int(self.size*t))
        pygame.draw.circle(scr,WHITE,(int(self.x),int(self.y)),max(1, min(2, sz//3)))
        scr.blit(glow_surf(min(sz*3, 60),self.color,t),(int(self.x)-min(sz*3,60),int(self.y)-min(sz*3,60)),
                 special_flags=pygame.BLEND_ADD)

class Comet(FX):
    __slots__=FX.__slots__+['trail','angle','speed']
    def __init__(self):
        super().__init__(); self.trail=[]; self.speed=3; self.angle=0
    def setup(self,x,y,angle,speed=3,life=3.0,color=CYAN,depth=0):
        self.init(x,y,depth); self.angle=angle; self.speed=speed
        self.vx=math.cos(angle)*speed; self.vy=math.sin(angle)*speed
        self.life=self.max_life=life; self.color=color; self.trail=[]; self.size=4; return self
    def update(self,dt):
        self.trail.append((self.x,self.y))
        if len(self.trail)>15: self.trail.pop(0)
        self.x+=self.vx*dt*60; self.y+=self.vy*dt*60
        self.angle+=random.gauss(0,0.02)
        self.vx=math.cos(self.angle)*self.speed; self.vy=math.sin(self.angle)*self.speed
        if self.x<-80 or self.x>WIDTH+80 or self.y<-80 or self.y>HEIGHT+80:
            self.alive=False; return
        super().update(dt)
    def draw(self,scr):
        t=self.t()
        for i,(tx,ty) in enumerate(self.trail):
            f=i/max(1,len(self.trail)); a=f*t*0.6
            c=clamp_color((self.color[0]*a,self.color[1]*a,self.color[2]*a))
            pygame.draw.circle(scr,c,(int(tx),int(ty)),max(1,int(3*f*t)))
        sz=max(2,int(self.size*t))
        scr.blit(glow_surf(min(sz*4, 80),self.color,t*0.8),(int(self.x)-min(sz*4,80),int(self.y)-min(sz*4,80)),
                 special_flags=pygame.BLEND_ADD)
        pygame.draw.circle(scr,WHITE,(int(self.x),int(self.y)),max(1, min(2, sz//3)))

class OrbitStar(FX):
    __slots__=FX.__slots__+['cx','cy','orbit_r','angle','speed','sz']
    def __init__(self):
        super().__init__(); self.cx=self.cy=0; self.orbit_r=30; self.angle=0; self.speed=2; self.sz=3
    def setup(self,cx,cy,r=30,speed=2,life=4.0,color=GOLD,sz=3,depth=0):
        self.cx,self.cy=cx,cy; self.orbit_r=min(r, 60); self.angle=random.uniform(0,6.28)
        self.speed=speed; self.life=self.max_life=life; self.color=color; self.sz=sz
        self.alive=True; self.depth=depth
        self.x=cx+math.cos(self.angle)*self.orbit_r; self.y=cy+math.sin(self.angle)*self.orbit_r; return self
    def update(self,dt):
        self.angle+=self.speed*dt
        self.x=self.cx+math.cos(self.angle)*self.orbit_r
        self.y=self.cy+math.sin(self.angle)*self.orbit_r
        super().update(dt)
    def draw(self,scr):
        t=self.t(); sz=max(1,int(self.sz*t))
        scr.blit(glow_surf(min(sz*3, 50),self.color,t*0.6),(int(self.x)-min(sz*3,50),int(self.y)-min(sz*3,50)),
                 special_flags=pygame.BLEND_ADD)
        pygame.draw.circle(scr,self.color,(int(self.x),int(self.y)),sz)
        pygame.draw.circle(scr,WHITE,(int(self.x),int(self.y)),max(1, min(2, sz//3)))

class FloatText(FX):
    __slots__=FX.__slots__+['text','font']
    def __init__(self):
        super().__init__(); self.text=""; self.font=None
    def setup(self,x,y,text,color=GOLD,life=1.2,font=None):
        self.init(x,y); self.text=text; self.color=color; self.life=self.max_life=life
        self.font=font; self.vy=-1.5; return self
    def update(self,dt):
        self.y+=self.vy*dt*60; self.vy*=0.97; super().update(dt)
    def draw(self,scr):
        if not self.font: return
        t=self.t(); s=self.font.render(self.text,True,self.color); s.set_alpha(int(255*min(1,t*2)))
        scr.blit(s,(int(self.x)-s.get_width()//2,int(self.y)))

class GravityWell(FX):
    __slots__=FX.__slots__+['radius','strength','angle']
    def __init__(self):
        super().__init__(); self.radius=50; self.strength=1; self.angle=0
    def setup(self,x,y,r=50,strength=1,life=3,color=PURPLE,depth=0):
        self.init(x,y,depth); self.radius=min(r, 80); self.strength=strength
        self.life=self.max_life=life; self.color=color; self.angle=0; return self
    def update(self,dt):
        self.angle+=3*dt; super().update(dt)
    def draw(self,scr):
        t=self.t(); r=int(self.radius*t)
        if r<3: return
        scr.blit(glow_surf(min(r, 70),self.color,t*0.4),(int(self.x)-min(r,70),int(self.y)-min(r,70)),
                 special_flags=pygame.BLEND_ADD)
        for i in range(4):
            a=self.angle+i*(math.pi/2)
            for j in range(8):
                f=j/8; sr=r*f
                px=self.x+math.cos(a+f*5)*sr; py=self.y+math.sin(a+f*5)*sr
                sz=max(1,int(2*t*(1-f)))
                c=clamp_color((self.color[0]*t*(1-f),self.color[1]*t*(1-f),self.color[2]*t*(1-f)))
                pygame.draw.circle(scr,c,(int(px),int(py)),sz)

class Beam(FX):
    __slots__=FX.__slots__+['ex','ey','thick']
    def __init__(self):
        super().__init__(); self.ex=self.ey=0; self.thick=3
    def setup(self,x,y,ex,ey,life=0.4,color=CYAN,thick=3,depth=0):
        self.init(x,y,depth); self.ex,self.ey=ex,ey; self.life=self.max_life=life
        self.color=color; self.thick=thick; return self
    def draw(self,scr):
        t=self.t(); th=max(2,int(self.thick*t))
        c=clamp_color((self.color[0]*t,self.color[1]*t,self.color[2]*t))
        cw=clamp_color((220*t,235*t,255*t))
        pygame.draw.line(scr,c,(int(self.x),int(self.y)),(int(self.ex),int(self.ey)),th+3)
        pygame.draw.line(scr,cw,(int(self.x),int(self.y)),(int(self.ex),int(self.ey)),max(1,th))
        gr=max(6,th*2)
        scr.blit(glow_surf(min(gr, 50),self.color,t*0.7),(int(self.x)-min(gr,50),int(self.y)-min(gr,50)),special_flags=pygame.BLEND_ADD)
        scr.blit(glow_surf(min(gr, 50),self.color,t*0.9),(int(self.ex)-min(gr,50),int(self.ey)-min(gr,50)),special_flags=pygame.BLEND_ADD)

class CosmicRift(FX):
    __slots__=FX.__slots__+['length','angle','thick']
    def __init__(self):
        super().__init__(); self.length=60; self.angle=0; self.thick=3
    def setup(self,x,y,length=60,angle=0,life=2.0,color=PURPLE,depth=0):
        self.init(x,y,depth); self.length=min(length, 100); self.angle=angle
        self.life=self.max_life=life; self.color=color; self.thick=3; return self
    def draw(self,scr):
        t=self.t(); hl=self.length*0.5
        x1=self.x-math.cos(self.angle)*hl; y1=self.y-math.sin(self.angle)*hl
        x2=self.x+math.cos(self.angle)*hl; y2=self.y+math.sin(self.angle)*hl
        pulse=0.5+0.5*math.sin(self.life*15)
        th=max(1,int(self.thick*t*pulse+2*t))
        c=clamp_color((self.color[0]*t,self.color[1]*t,self.color[2]*t))
        pygame.draw.line(scr,c,(int(x1),int(y1)),(int(x2),int(y2)),th+2)
        pygame.draw.line(scr,WHITE,(int(x1),int(y1)),(int(x2),int(y2)),max(1,th-1))
        scr.blit(glow_surf(min(int(self.length*0.4), 70),self.color,t*0.5),
                 (int(self.x-min(self.length*0.4,70)),int(self.y-min(self.length*0.4,70))),
                 special_flags=pygame.BLEND_ADD)
        for i in range(3):
            f=(i/3 - 0.5)*2
            px=self.x+math.cos(self.angle)*hl*f
            py=self.y+math.sin(self.angle)*hl*f
            off=math.sin(self.life*8+i*2)*8*t
            px+=math.cos(self.angle+1.57)*off
            py+=math.sin(self.angle+1.57)*off
            sz=max(1,int(2*t))
            pygame.draw.circle(scr,c,(int(px),int(py)),sz)

class EnergySpiral(FX):
    __slots__=FX.__slots__+['radius','spin_speed','angle','arms']
    def __init__(self):
        super().__init__(); self.radius=40; self.spin_speed=4; self.angle=0; self.arms=3
    def setup(self,x,y,radius=40,arms=3,life=2.5,color=CYAN,depth=0):
        self.init(x,y,depth); self.radius=min(radius, 70); self.arms=min(arms, 4)
        self.life=self.max_life=life; self.color=color
        self.angle=0; self.spin_speed=random.uniform(3,6); return self
    def update(self,dt):
        self.angle+=self.spin_speed*dt; super().update(dt)
    def draw(self,scr):
        t=self.t(); r=int(self.radius*t)
        if r<3: return
        scr.blit(glow_surf(min(int(r*0.6), 60),self.color,t*0.3),
                 (int(self.x-min(r*0.6,60)),int(self.y-min(r*0.6,60))),special_flags=pygame.BLEND_ADD)
        for arm in range(self.arms):
            base_a=self.angle+arm*(6.28/self.arms)
            for j in range(15):
                f=j/15; sr=r*f; a=base_a+f*3
                px=self.x+math.cos(a)*sr; py=self.y+math.sin(a)*sr
                sz=max(1,int(3*t*(1-f*0.5)))
                af=t*(1-f*0.3)
                c=clamp_color((self.color[0]*af,self.color[1]*af,self.color[2]*af))
                pygame.draw.circle(scr,c,(int(px),int(py)),sz)

class PulseRing(FX):
    __slots__=FX.__slots__+['max_r','num_rings']
    def __init__(self):
        super().__init__(); self.max_r=80; self.num_rings=4
    def setup(self,x,y,max_r=80,num_rings=4,life=1.0,color=GOLD,depth=0):
        self.init(x,y,depth); self.max_r=min(max_r, 100); self.num_rings=min(num_rings, 3)
        self.life=self.max_life=life; self.color=color; return self
    def draw(self,scr):
        t=self.t(); p=1-t
        for i in range(self.num_rings):
            phase=(p+i*0.15)%1.0; r=int(self.max_r*phase)
            if r<3: continue
            rt=1-phase
            c=clamp_color((self.color[0]*rt*t,self.color[1]*rt*t,self.color[2]*rt*t))
            pygame.draw.circle(scr,c,(int(self.x),int(self.y)),r,max(1,int(2*rt*t)))

class BlackHole(FX):
    __slots__=FX.__slots__+['radius','angle']
    def __init__(self):
        super().__init__(); self.radius=30; self.angle=0
    def setup(self,x,y,radius=30,life=4.0,depth=0):
        self.init(x,y,depth); self.radius=min(radius, 50); self.life=self.max_life=life
        self.color=VOID; self.angle=0; return self
    def update(self,dt):
        self.angle+=2*dt; super().update(dt)
    def draw(self,scr):
        t=self.t(); r=int(self.radius*t)
        if r<3: return
        pygame.draw.circle(scr,(5,0,15),(int(self.x),int(self.y)),max(2,r//2))
        for i in range(20):
            a=self.angle+i*0.21
            d=r*(0.6+0.4*math.sin(a*3+self.life*10))
            px=self.x+math.cos(a)*d; py=self.y+math.sin(a)*d*0.4
            f=0.5+0.5*math.sin(a*5); c=lerp_color(PURPLE,ORANGE,f)
            af=t*0.7; c=clamp_color((c[0]*af,c[1]*af,c[2]*af))
            pygame.draw.circle(scr,c,(int(px),int(py)),max(1,int(2*t)))
        scr.blit(glow_surf(min(r+5, 60),PURPLE,t*0.4),(int(self.x)-min(r+5,60),int(self.y)-min(r+5,60)),
                 special_flags=pygame.BLEND_ADD)

# --- NEW FX CLASSES (added for variety) ---
class VoidTendrils(FX):
    """Multiple dark tendrils reaching out from a point (unlocked by Void Engine)."""
    __slots__ = FX.__slots__ + ['num_tendrils', 'length', 'angle']
    def __init__(self):
        super().__init__()
        self.num_tendrils = 5
        self.length = 50
        self.angle = 0
    def setup(self, x, y, num=5, length=50, life=1.0, color=VOID, depth=0):
        self.init(x, y, depth)
        self.num_tendrils = min(num, 8)
        self.length = min(length, 80)
        self.life = self.max_life = life
        self.color = color
        self.angle = random.uniform(0, 6.28)
        return self
    def update(self, dt):
        self.angle += 2 * dt
        super().update(dt)
    def draw(self, scr):
        t = self.t()
        for i in range(self.num_tendrils):
            a = self.angle + i * (2*math.pi/self.num_tendrils)
            end_x = self.x + math.cos(a) * self.length * t
            end_y = self.y + math.sin(a) * self.length * t
            c = clamp_color((self.color[0]*t, self.color[1]*t, self.color[2]*t))
            pygame.draw.line(scr, c, (int(self.x), int(self.y)), (int(end_x), int(end_y)), max(1, int(3*t)))
            # small glow at tip
            scr.blit(glow_surf(10, self.color, t*0.5), (int(end_x)-10, int(end_y)-10), special_flags=pygame.BLEND_ADD)

class PrismBeam(FX):
    """A central beam that splits into colored beams (unlocked by Prism Emitter)."""
    __slots__ = FX.__slots__ + ['beams', 'angle', 'length']
    def __init__(self):
        super().__init__()
        self.beams = 3
        self.angle = 0
        self.length = 60
    def setup(self, x, y, beams=3, length=60, life=0.8, color=WHITE, depth=0):
        self.init(x, y, depth)
        self.beams = min(beams, 5)
        self.length = min(length, 80)
        self.life = self.max_life = life
        self.color = color
        self.angle = random.uniform(0, 6.28)
        return self
    def update(self, dt):
        self.angle += 4 * dt
        super().update(dt)
    def draw(self, scr):
        t = self.t()
        pal = [RED, ORANGE, YELLOW, GREEN, CYAN, BLUE, PURPLE]
        for i in range(self.beams):
            a = self.angle + i * (2*math.pi/self.beams)
            end_x = self.x + math.cos(a) * self.length * t
            end_y = self.y + math.sin(a) * self.length * t
            c = pal[i % len(pal)]
            c = clamp_color((c[0]*t, c[1]*t, c[2]*t))
            pygame.draw.line(scr, c, (int(self.x), int(self.y)), (int(end_x), int(end_y)), max(1, int(4*t)))
            scr.blit(glow_surf(12, c, t*0.6), (int(end_x)-12, int(end_y)-12), special_flags=pygame.BLEND_ADD)
            
class GalacticSwirl(FX):
    """A rotating spiral of particles (unlocked by Spiral Weaver)."""
    __slots__ = FX.__slots__ + ['arms', 'radius', 'angle']
    def __init__(self):
        super().__init__()
        self.arms = 3
        self.radius = 40
        self.angle = 0
    def setup(self, x, y, arms=3, radius=40, life=2.0, color=CYAN, depth=0):
        self.init(x, y, depth)
        self.arms = min(arms, 5)
        self.radius = min(radius, 70)
        self.life = self.max_life = life
        self.color = color
        self.angle = random.uniform(0, 6.28)
        return self
    def update(self, dt):
        self.angle += 3 * dt
        super().update(dt)
    def draw(self, scr):
        t = self.t()
        r = self.radius * t
        for arm in range(self.arms):
            base_a = self.angle + arm * (2*math.pi/self.arms)
            for j in range(12):
                f = j / 12
                a = base_a + f * 8
                d = r * f
                px = self.x + math.cos(a) * d
                py = self.y + math.sin(a) * d
                sz = max(1, int(3 * t * (1 - f)))
                af = t * (1 - f*0.5)
                c = clamp_color((self.color[0]*af, self.color[1]*af, self.color[2]*af))
                pygame.draw.circle(scr, c, (int(px), int(py)), sz)

class ScreenFlash(FX):
    __slots__=FX.__slots__+['intensity']
    def __init__(self):
        super().__init__(); self.intensity=0.3
    def setup(self,intensity=0.3,life=0.15,color=WHITE):
        self.alive=True; self.life=self.max_life=life; self.color=color
        self.intensity=intensity; self.x=self.y=0; self.depth=0; return self
    def draw(self,scr):
        t=self.t(); a=int(self.intensity*255*t)
        if a>1:
            overlay=pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA)
            overlay.fill((*self.color,min(255,a)))
            scr.blit(overlay,(0,0))

# --- Void Crystal (replaces golden cookie placeholder) ---
class VoidCrystal(FX):
    __slots__ = FX.__slots__ + ['lifetime']
    def __init__(self):
        super().__init__()
        self.lifetime = CRYSTAL_LIFETIME
    def setup(self, x, y):
        self.init(x, y)
        self.life = self.max_life = self.lifetime
        self.color = (140, 0, 255)  # deep purple
        return self
    def draw(self, scr):
        t = self.t()
        # pulsing size and glow
        pulse = 0.8 + 0.4 * math.sin(self.life * 8)
        r = int(20 * pulse)
        # glow
        scr.blit(glow_surf(r*2, (140,0,255), t), (int(self.x)-r*2, int(self.y)-r*2), special_flags=pygame.BLEND_ADD)
        # main crystal (a star shape)
        points = []
        for i in range(5):
            angle = self.life * 2 + i * (2*math.pi/5)
            points.append((self.x + math.cos(angle)*r, self.y + math.sin(angle)*r))
            angle += math.pi/5
            points.append((self.x + math.cos(angle)*r*0.5, self.y + math.sin(angle)*r*0.5))
        pygame.draw.polygon(scr, (180, 100, 255), points)
        pygame.draw.polygon(scr, CYAN, points, 2)

# ─────────────────────────────────────────────────────────────
# UPGRADE DEFINITIONS (rebalanced multipliers)
# ─────────────────────────────────────────────────────────────
def U(name,desc,cost,cg,pw,pg,cat="click",color=WHITE,combo=0):
    return dict(name=name,desc=desc,base_cost=cost,cost_growth=cg,
                base_power=pw,power_growth=pg,cat=cat,color=color,combo=combo)

UPGRADE_DEFS = [
    # ── CLICK POWER ──
    U("Click Power","+1 base click damage",15,1.18,1,1.0,"click",YELLOW,0),  # fixed growth to 1.0 for flat +1 per level
    U("Click Burst","+3 particles per click",75,1.22,3,1.05,"click",ORANGE,0),
    U("Double Tap","x1.5 click energy",600,1.3,1.5,1.02,"click",GOLD,0),
    U("Finger Storm","clicks create sparks",8000,1.35,1,1.08,"click",ELECTRIC,0),
    U("Power Fist","x2 click base",1e5,1.42,2,1.03,"click",RED,0),
    U("Thunder Touch","clicks cause mini-lightning",5e6,1.48,1,1.06,"click",CYAN,0),
    U("Cosmic Finger","x3 click multiplier",1e9,1.55,3,1.02,"click",MAGENTA,0),
    U("Galaxy Punch","clicks cause shockwaves",5e12,1.6,1,1.04,"click",PURPLE,0),
    U("Reality Tap","x10 click power",1e17,1.7,10,1.01,"click",PINK,0),
    U("Omega Click","x50 click devastation",1e23,1.85,50,1.01,"click",WHITE,0),

    # ── COMBO BUILDERS ──
    U("Combo Catalyst","+100 combo per manual click",1500,1.4,100,1.0,"combo",ORANGE,0),
    U("Combo Master","+1K combo per manual click",5e6,1.5,1000,1.0,"combo",RED,0),
    U("Combo Lord","+10K combo per manual click",1e11,1.6,10000,1.0,"combo",MAGENTA,0),
    U("Combo God","+100K combo per manual click",1e16,1.65,100000,1.0,"combo",CYAN,0),
    U("Combo Singularity","+1M combo per click",1e22,1.7,1000000,1.0,"combo",WHITE,0),

    # ── AUTO CLICKERS ──
    U("Auto Clicker","+1 click/sec",150,1.2,1,1.12,"auto",GREEN,0),
    U("Rapid Fire","+3 auto clicks/sec",2000,1.28,3,1.08,"auto",LIME,0),
    U("Auto Burst","auto clicks explode",2.5e4,1.35,1,1.06,"auto",CYAN,0),
    U("Machine Gun","+10 auto clicks/sec",5e5,1.4,10,1.05,"auto",TEAL,0),
    U("Turbo Engine","+25 auto clicks/sec",5e7,1.48,25,1.04,"auto",BLUE,0),
    U("Quantum Auto","auto clicks chain react",5e10,1.55,1,1.03,"auto",PLASMA,0),
    U("Infinity Trigger","+100 auto clicks/sec",5e14,1.6,100,1.03,"auto",VIOLET,0),
    U("Temporal Clicker","auto clicks warp time",1e19,1.7,1,1.02,"auto",MAGENTA,0),

    # ── CHAIN REACTION ──
    U("Chain Amplifier","+5% chain probability",500,1.32,0.05,1.0,"chain",ELECTRIC,0),
    U("Chain Depth","+1 max chain depth",5000,2.2,1,1.0,"chain",BLUE,0),
    U("Echo Chamber","chains echo 20% louder",8e4,1.4,0.2,1.0,"chain",CYAN,0),
    U("Cascade Engine","x1.5 chain energy",2e6,1.5,1.5,1.01,"chain",TEAL,0),
    U("Resonance Field","+10% chain prob",1e8,1.5,0.10,1.0,"chain",ELECTRIC,0),
    U("Infinity Chain","+3 max depth",5e11,2.5,3,1.0,"chain",PURPLE,0),
    U("Paradox Loop","chains can re-trigger",1e15,1.7,1,1.0,"chain",MAGENTA,0),
    U("Chain Singularity","x5 chain everything",1e20,2.5,5,1.0,"chain",WHITE,0),

    # ── FX UNLOCKS (now give +1% energy per level) ──
    U("Lightning Rod","unlock lightning arcs, +1% energy/level",800,1.3,1.01,1.0,"fx",ELECTRIC,0),
    U("Shockwave Gen","unlock shockwaves, +1% energy/level",1e4,1.38,1.01,1.0,"fx",CYAN,0),
    U("Plasma Reactor","unlock plasma rings, +1% energy/level",2e5,1.42,1.01,1.0,"fx",PLASMA,0),
    U("Meteor Engine","unlock meteors, +1% energy/level",5e6,1.48,1.01,1.0,"fx",ORANGE,0),
    U("Star Forge","unlock orbiting stars, +1% energy/level",2e8,1.5,1.01,1.0,"fx",GOLD,0),
    U("Gravity Engine","unlock gravity wells, +1% energy/level",1e10,1.55,1.01,1.0,"fx",PURPLE,0),
    U("Beam Storm","unlock energy beams, +1% energy/level",5e11,1.58,1.01,1.0,"fx",CYAN,0),
    U("Fractal Core","unlock fractal lightning, +1% energy/level",5e13,1.6,1.01,1.0,"fx",ELECTRIC,0),
    U("Prism Emitter","unlock geometric prism bursts, +1% energy/level",1e14,1.6,1.01,1.0,"fx",PINK,0),
    U("Starburst Emitter","unlock starburst patterns, +1% energy/level",2e14,1.6,1.01,1.0,"fx",PINK,0),
    U("Comet Summoner","unlock comets, +1% energy/level",5e15,1.62,1.01,1.0,"fx",ICE,0),
    U("Rift Opener","unlock cosmic rifts, +1% energy/level",5e17,1.65,1.01,1.0,"fx",PURPLE,0),
    U("Spiral Weaver","unlock energy spirals, +1% energy/level",5e19,1.65,1.01,1.0,"fx",CYAN,0),
    U("Nebula Cloud","unlock cosmic nebula gas, +1% energy/level",1e20,1.65,1.01,1.0,"fx",PURPLE,0),
    U("Pulse Master","unlock pulse rings, +1% energy/level",5e21,1.68,1.01,1.0,"fx",GOLD,0),
    U("Nova Core","unlock supernovae, +1% energy/level",5e23,1.7,1.01,1.0,"fx",WHITE,0),
    U("Void Engine","unlock black holes, +1% energy/level",5e26,1.72,1.01,1.0,"fx",VOID,0),
    U("Flash Bang","unlock screen flashes, +1% energy/level",5e30,1.75,1.01,1.0,"fx",WHITE,0),

    # ── FX AMPLIFIERS (rebalanced) ──
    U("Lightning Amp","+50% lightning branches",6000,1.4,1.5,1.03,"amp",ELECTRIC,0),
    U("Explosion Size","+15% explosion radius",3e4,1.38,0.15,1.0,"amp",ORANGE,0),
    U("Particle Flood","+50% particle count",4e5,1.42,1.5,1.02,"amp",YELLOW,0),
    U("Shockwave Power","+20% shockwave size",8e6,1.45,0.2,1.0,"amp",CYAN,0),
    U("Meteor Rain","+1 meteor per chain (max 3)",2e8,1.5,1,1.05,"amp",RED,0),
    U("Star Cluster","+1 star per spawn",5e9,1.52,1,1.03,"amp",GOLD,0),
    U("Beam Width","+25% beam thickness",2e11,1.55,0.25,1.0,"amp",TEAL,0),
    U("Gravity Strength","x1.5 well pull force",1e13,1.58,1.5,1.02,"amp",PURPLE,0),
    U("Rift Length","+25% rift size",1e15,1.58,0.25,1.0,"amp",VIOLET,0),
    U("Nova Yield","x1.5 nova explosion size",1e18,1.62,1.5,1.02,"amp",WHITE,0),
    U("FX Variety","unlock rare FX patterns",1e22,1.65,1,1.0,"amp",PINK,0),
    U("Color Spectrum","more color variety",1e27,1.68,1,1.0,"amp",MAGENTA,0),

    # ── MULTIPLIERS (rebalanced to gradual increases) ──
    U("Energy Mult I","+10% energy per level",3000,2.8,1.1,1.0,"mult",GOLD,0),
    U("Energy Mult II","+15% energy per level",5e5,3.5,1.15,1.0,"mult",GOLD,0),
    U("Energy Mult III","+20% energy per level",5e8,4.0,1.2,1.0,"mult",GOLD,0),
    U("Energy Mult IV","+30% energy per level",5e12,5.0,1.3,1.0,"mult",GOLD,0),
    U("Energy Mult V","+50% energy per level",5e17,6.0,1.5,1.0,"mult",GOLD,0),
    U("Energy Mult VI","+100% energy per level",5e24,7.0,2.0,1.0,"mult",GOLD,0),

    # ── COSMIC / ENDGAME (rebalanced to gradual increases) ──
    U("Cosmic Reactor","x1.5 chain energy per level",1e13,4.0,1.5,1.0,"cosmic",MAGENTA,0),
    U("Dimension Fold","x1.3 auto click power per level",1e16,4.5,1.3,1.0,"cosmic",PURPLE,0),
    U("Universe Engine","x1.4 click power per level",1e20,5.5,1.4,1.0,"cosmic",CYAN,0),
    U("Reality Warper","x1.6 everything per level",1e25,6.5,1.6,1.0,"cosmic",PINK,0),
    U("Void Harvester","x1.8 energy gain per level",1e30,8.0,1.8,1.0,"cosmic",VOID,0),
    U("Omega Singularity","x2.0 all power per level",1e36,10.0,2.0,1.0,"cosmic",WHITE,0),
    U("Eternity Gate","x2.5 ascension per level",1e44,14.0,2.5,1.0,"cosmic",GOLD,0),
    U("Infinity Core","x3.0 power per level",1e55,20.0,3.0,1.0,"cosmic",WHITE,0),
]

# Sort all upgrades by base cost
UPGRADE_DEFS.sort(key=lambda d: d['base_cost'])

# Generate true exponential combo requirements
_combo_req = 10.0
for i, u_def in enumerate(UPGRADE_DEFS):
    if i < 4:
        u_def['combo'] = 0 # First few are free
    else:
        val = int(_combo_req)
        # Round large numbers gracefully to look clean
        if val >= 1000:
            pow10 = int(math.log10(val))
            factor = 10 ** (pow10 - 1)
            val = round(val / factor) * factor
        elif val >= 100:
            val = round(val, -1)
        
        u_def['combo'] = val
        _combo_req *= 1.35 # Exponential Growth factor

class UpgradeState:
    def __init__(self, d):
        self.name=d['name']; self.desc=d['desc']; self.base_cost=d['base_cost']
        self.cost_growth=d['cost_growth']; self.base_power=d['base_power']
        self.power_growth=d['power_growth']; self.cat=d['cat']
        self.color=d['color']; self.combo=d['combo']; self.level=0
    @property
    def cost(self): return self.base_cost*(self.cost_growth**self.level)
    @property
    def power(self): return self.base_power*(self.power_growth**self.level)
    def can_buy(self, e): return e>=self.cost

# ─────────────────────────────────────────────────────────────
# MAIN GAME
# ─────────────────────────────────────────────────────────────
class Game:
    def __init__(self):
        pygame.init()
        global WIDTH, HEIGHT
        info=pygame.display.Info()
        WIDTH, HEIGHT = info.current_w, info.current_h
        self.scr=pygame.display.set_mode((WIDTH,HEIGHT),pygame.FULLSCREEN)
        pygame.display.set_caption("Cosmic Clicker")
        self.clock=pygame.time.Clock()
        self.running=True

        self.font_xl=pygame.font.SysFont("Arial",42,True)
        self.font_lg=pygame.font.SysFont("Arial",28,True)
        self.font_md=pygame.font.SysFont("Arial",18,True)
        self.font_sm=pygame.font.SysFont("Arial",14)
        self.font_xs=pygame.font.SysFont("Arial",12)

        self.reset_state()
        self.bg_stars=[(random.randint(0,WIDTH),random.randint(0,HEIGHT),
                        random.uniform(0.5,2),random.uniform(0.3,1)) for _ in range(100)]
        self.time=0.0
        self.save_msg=""; self.save_msg_timer=0

        # Void Crystal (replaces golden cookie placeholder)
        self.crystal = None
        self.crystal_spawn_timer = random.uniform(CRYSTAL_SPAWN_MIN, CRYSTAL_SPAWN_MAX)
        self.crystal_buff_timer = 0.0
        self.crystal_mult = 1.0

        # Upgrade panel filter
        self.filter = "all"  # all, click, auto, chain, fx, amp, mult, cosmic, combo
        # Use abbreviated labels for buttons
        self.filter_buttons = ["All","Clk","Auto","Chn","FX","Amp","Mult","Cos","Cmb"]
        self.filter_map = {
            "All": "all",
            "Clk": "click",
            "Auto": "auto",
            "Chn": "chain",
            "FX": "fx",
            "Amp": "amp",
            "Mult": "mult",
            "Cos": "cosmic",
            "Cmb": "combo"
        }

        # Increase panel width for better readability
        self.panel_w = 350
        self.game_w = WIDTH - self.panel_w

    def reset_state(self):
        self.energy=0.0; self.total_energy=0.0; self.combo=0; self.max_combo=0
        self.combo_timer=0.0; self.combo_decay=0.8; self.clicks=0; self.auto_timer=0.0
        self.chaos_energy=0.0; self.prestige_count=0; self.chaos_mult=1.0
        self.play_time=0.0
        self.galaxy_boost = 0.0

        self.upgrades=[UpgradeState(d) for d in UPGRADE_DEFS]

        # FX Pools — slightly larger for variety
        self.particles = Pool(Particle, 500)
        self.explosions = Pool(Explosion, 100)
        self.shockwaves = Pool(Shockwave, 50)
        self.lightnings = Pool(Lightning, 25)
        self.fractals = Pool(FractalLightning, 20)
        self.meteors = Pool(Meteor, 25)
        self.comets = Pool(Comet, 15)
        self.orbits = Pool(OrbitStar, 25)
        self.texts = Pool(FloatText, 25)
        self.wells = Pool(GravityWell, 15)
        self.beams = Pool(Beam, 25)
        self.rifts = Pool(CosmicRift, 15)
        self.spirals = Pool(EnergySpiral, 15)
        self.pulses = Pool(PulseRing, 15)
        self.blackholes = Pool(BlackHole, 8)
        self.flashes = Pool(ScreenFlash, 5)
        self.prisms = Pool(PrismBurst, 15)
        self.nebulas = Pool(Nebula, 10)
        self.starbursts = Pool(Starburst, 15)

        # NEW FX pools
        self.tendrils = Pool(VoidTendrils, 15)
        self.prismbeams = Pool(PrismBeam, 15)
        self.galactics = Pool(GalacticSwirl, 15)

        # Rendering Order
        self.all_pools=[
            self.nebulas,       
            self.blackholes,
            self.wells,
            self.orbits,        
            self.rifts,
            self.beams,
            self.shockwaves,
            self.spirals,
            self.pulses,
            self.prisms,
            self.starbursts,
            self.explosions,    
            self.lightnings,    
            self.fractals,
            self.meteors,       
            self.comets,
            self.particles,
            self.texts,         
            self.flashes,
            # new FX (drawn on top)
            self.tendrils,
            self.prismbeams,
            self.galactics
        ]

        self.spawn_budget=0; self.scroll=0
        self.hovered=-1
        self.shake=0; self.sx=0; self.sy=0; self.bg_pulse=0.0
        self.max_scroll=0

    # ── Stat Helpers ──
    def ulv(self,name):
        for u in self.upgrades:
            if u.name==name: return u.level
        return 0
    def upow(self,name):
        for u in self.upgrades:
            if u.name==name and u.level>0: return u.power
        return 0
    def has(self,name): return self.ulv(name)>0

    def click_power(self):
        base = 1.0; mult = 1.0
        base += self.upow("Click Power") * self.ulv("Click Power")
        if self.has("Power Fist"): mult *= self.upow("Power Fist")
        if self.has("Double Tap"): mult *= self.upow("Double Tap")
        if self.has("Cosmic Finger"): mult *= self.upow("Cosmic Finger")
        if self.has("Reality Tap"): mult *= self.upow("Reality Tap")
        if self.has("Omega Click"): mult *= self.upow("Omega Click")
        if self.has("Universe Engine"): mult *= self.upow("Universe Engine")
        combo_m = 1 + min(self.combo, 1000) * 0.005
        upgrade_mult = 1.0 + 0.01 * sum(u.level for u in self.upgrades)
        galaxy_m = 1.0 + self.galaxy_boost
        return base * mult * combo_m * self.chaos_mult * self.energy_mult() * self.crystal_mult * upgrade_mult * galaxy_m * self.fury()   # <-- added fury
    
    def energy_mult(self):
        m=1.0
        # multiplier upgrades (categories "mult" and "cosmic") – each level multiplies by base_power
        for u in self.upgrades:
            if u.cat in ("mult","cosmic") and u.level>0:
                m *= (u.base_power ** u.level)
        # FX upgrades give 1% per level (base_power^level)
        for u in self.upgrades:
            if u.cat == "fx" and u.level>0:
                m *= (u.base_power ** u.level)
        return m

    def auto_cps(self):
        t = 0
        for n in ["Auto Clicker","Rapid Fire","Machine Gun","Turbo Engine","Infinity Trigger"]:
            t += self.upow(n) * self.ulv(n)
        dim = self.upow("Dimension Fold") if self.has("Dimension Fold") else 1
        temp = self.upow("Temporal Clicker") * self.ulv("Temporal Clicker") if self.has("Temporal Clicker") else 0
        upgrade_mult = 1.0 + 0.01 * sum(u.level for u in self.upgrades)
        galaxy_m = 1.0 + self.galaxy_boost
        return (t + temp) * self.chaos_mult * dim * self.energy_mult() * self.crystal_mult * upgrade_mult * galaxy_m * self.fury()   # <-- added fury

    def chain_prob(self):
        b=0.0
        b+=self.upow("Chain Amplifier")*self.ulv("Chain Amplifier")
        b+=self.upow("Resonance Field")*self.ulv("Resonance Field")
        b+=self.upow("Echo Chamber")*self.ulv("Echo Chamber")*0.5
        return min(b, 0.5)

    def max_depth(self):
        d=MAX_CHAIN_DEPTH
        d+=self.ulv("Chain Depth")*int(max(1,self.upow("Chain Depth")))
        d+=self.ulv("Infinity Chain")*int(max(1,self.upow("Infinity Chain")))
        return min(d, 12)

    def particle_mult(self):
        m=1.0
        if self.has("Particle Flood"): m*=self.upow("Particle Flood")
        if self.has("FX Overload"): m*=self.upow("FX Overload")
        return min(m, 2.5)

    def explosion_scale(self):
        s = 1.0
        s += self.upow("Explosion Size") * self.ulv("Explosion Size")
        if self.has("Nova Yield"):
            s *= self.upow("Nova Yield")
        return min(s, 2.0)

    def fury(self):
        total_levels=sum(u.level for u in self.upgrades)
        upgrade_fury=1.0+total_levels*0.01
        prestige_fury=1.0+self.prestige_count*0.15
        combo_fury = 1.0 + self.max_combo * 0.00005
        live_fury = 1.0 + self.combo * 0.00008
        return upgrade_fury*prestige_fury*combo_fury*live_fury

    def vscale(self):
        f = self.fury()
        base = 1.0 + math.log10(max(1.0, f)) * 0.8
        if self.crystal_buff_timer > 0:
            base *= 1.5  # amplify visuals during buff
        return base

    @property
    def variety_factor(self):
        base = 1.0
        if self.has("FX Variety"):
            base *= 1.5
        base += min(0.8, self.fury() * 0.1)
        return min(2.0, base)

    # ── FX Budget ──
    def fx_count(self):
        return sum(p.count for p in self.all_pools)
    def can_spawn(self):
        return self.fx_count()<MAX_FX and self.spawn_budget>0
    def use(self,n=1): self.spawn_budget-=n

    # ── Chain Reaction Engine ──
    def chain(self, x, y, depth=0, energy=1.0):
        if depth > self.max_depth() or not self.can_spawn():
            return
        prob = max(0.1, (0.5 + self.chain_prob()) * (CHAIN_DECAY ** depth))
        vs = self.vscale()
        cs = 1 + min(self.combo, 500) * 0.005 * vs
        ce = self.upow("Cascade Engine") if self.has("Cascade Engine") else 1
        energy *= ce
        paradox = self.has("Paradox Loop") and random.random() < 0.05 * prob
        sm = self.upow("Chain Singularity") if self.has("Chain Singularity") else 1

        def up_mult(name, base=0.2):
            return 1.0 + base * self.ulv(name)

        if depth == 0:
            self._explosion(x, y, depth, energy * sm)
            if self.can_spawn():
                self._shockwave(x, y, int(30 + 10 * vs), depth)
            if self.can_spawn() and random.random() < prob * 0.02 * up_mult("Thunder Touch"):
                tx = x + random.gauss(0, 80) * cs
                ty = y + random.gauss(0, 80) * cs
                tx = max(10, min(self.game_w - 10, tx))
                ty = max(10, min(HEIGHT - 10, ty))
                self._lightning(x, y, tx, ty, depth)
                if random.random() < prob * 0.1:
                    self.chain(tx, ty, depth + 1, energy * 0.8)
            if self.can_spawn() and random.random() < prob * 0.3 * up_mult("Galaxy Punch"):
                self._shockwave(x, y, int(50 * cs), depth)
            if self.can_spawn() and random.random() < 0.2 * up_mult("Plasma Reactor"):
                self._plasma(x, y, int(40 * cs), depth)

        if self.can_spawn() and random.random() < prob * 0.0005 * (up_mult("Lightning Rod") * 0.1):
            tx = x + random.gauss(0, 80) * cs
            ty = y + random.gauss(0, 80) * cs
            tx = max(10, min(self.game_w - 10, tx))
            ty = max(10, min(HEIGHT - 10, ty))
            self._lightning(x, y, tx, ty, depth)
            if random.random() < prob * 0.1:
                self.chain(tx, ty, depth + 1, energy * 0.7)

        if depth >= 0 and self.can_spawn() and random.random() < prob * 0.3 * up_mult("Shockwave Gen") * self.variety_factor:
            r = int((30 + 20 * cs) * (1 + self.upow("Shockwave Power") * self.ulv("Shockwave Power")))
            self._shockwave(x, y, min(r, 120), depth)

        if depth >= 0 and self.can_spawn() and random.random() < prob * 0.15 * up_mult("Fractal Core"):
            self._fractal(x, y, int(30 * cs), depth)

        if depth >= 0 and self.can_spawn() and random.random() < prob * 0.2 * up_mult("Plasma Reactor") * self.variety_factor:
            self._plasma(x, y, int(40 * cs), depth)

        if depth >= 0 and self.can_spawn() and random.random() < prob * 0.2 * up_mult("Prism Emitter") * self.variety_factor:
            self._prism(x, y, depth)

        if depth >= 0 and self.can_spawn() and random.random() < prob * 0.2 * up_mult("Starburst Emitter") * self.variety_factor:
            self._starburst(x, y, depth)

        if depth >= 1 and self.can_spawn() and random.random() < prob * 0.4:
            ox = x + random.gauss(0, 40)
            oy = y + random.gauss(0, 40)
            self._explosion(ox, oy, depth, energy * 0.4 * sm)
            if random.random() < prob * 0.3:
                self.chain(ox, oy, depth + 1, energy * 0.4)

        if depth >= 0 and self.can_spawn() and random.random() < prob * 0.15 * up_mult("Meteor Engine") * self.variety_factor:
            extra = int(self.upow("Meteor Rain") * self.ulv("Meteor Rain"))
            for _ in range(1 + min(extra, 2)):
                if not self.can_spawn():
                    break
                self._meteor(x, y, random.uniform(-3.14, 3.14), depth, energy * 0.3)

        if depth >= 0 and self.can_spawn() and random.random() < prob * 0.15 * up_mult("Comet Summoner") * self.variety_factor:
            self._comet(x, y, depth)

        if depth >= 0 and self.can_spawn() and random.random() < prob * 0.15 * up_mult("Star Forge") * self.variety_factor:
            extra = int(self.upow("Star Cluster") * self.ulv("Star Cluster"))
            self._orbit_stars(x, y, depth, 1 + min(extra, 3))

        if depth >= 0 and self.can_spawn() and random.random() < prob * 0.15 * up_mult("Spiral Weaver") * self.variety_factor:
            self._spiral(x, y, depth)

        if depth >= 2 and self.can_spawn() and random.random() < prob * 0.15 * up_mult("Pulse Master") * self.variety_factor:
            self._pulse(x, y, depth)

        if depth >= 2 and self.can_spawn() and random.random() < prob * 0.15 * up_mult("Gravity Engine") * self.variety_factor:
            self._gravity_well(x, y, depth)

        if depth >= 2 and self.can_spawn() and random.random() < prob * 0.15 * up_mult("Beam Storm") * self.variety_factor:
            ex = random.randint(20, self.game_w - 20)
            ey = random.randint(20, HEIGHT - 20)
            thick = 2 + int(self.upow("Beam Width") * self.ulv("Beam Width") * 1)
            self._beam(x, y, ex, ey, depth, thick)
            if random.random() < prob * 0.3:
                self.chain(ex, ey, depth + 1, energy * 0.3)

        if depth >= 2 and self.can_spawn() and random.random() < prob * 0.15 * up_mult("Rift Opener") * self.variety_factor:
            length = 40 + int(self.upow("Rift Length") * self.ulv("Rift Length") * 20)
            self._rift(x, y, min(length, 80), depth)

        if depth >= 2 and self.can_spawn() and random.random() < prob * 0.15 * up_mult("Nova Core") * self.variety_factor:
            self._nova(x, y, depth, energy * sm)

        if depth >= 2 and self.can_spawn() and random.random() < prob * 0.15 * up_mult("Nebula Cloud") * self.variety_factor:
            self._nebula(x, y, depth)

        if depth >= 3 and self.can_spawn() and random.random() < prob * 0.12 * up_mult("Void Engine") * self.variety_factor:
            self._blackhole(x, y, depth)

        # --- NEW FX SPAWNS (tied to respective upgrades) ---
        if depth >= 2 and self.can_spawn() and random.random() < prob * 0.1 * up_mult("Void Engine") * self.variety_factor:
            tendril = self.tendrils.get()
            tendril.setup(x, y, random.randint(4,7), random.uniform(40,70), random.uniform(0.8,1.5), random.choice([VOID,PURPLE,INDIGO]), depth)
            self.tendrils.spawn(tendril)

        if depth >= 1 and self.can_spawn() and random.random() < prob * 0.12 * up_mult("Prism Emitter") * self.variety_factor:
            beam = self.prismbeams.get()
            beam.setup(x, y, random.randint(3,5), random.uniform(50,80), random.uniform(0.5,1.0), random.choice([WHITE,GOLD,CYAN]), depth)
            self.prismbeams.spawn(beam)

        if depth >= 1 and self.can_spawn() and random.random() < prob * 0.15 * up_mult("Spiral Weaver") * self.variety_factor:
            swirl = self.galactics.get()
            swirl.setup(x, y, random.randint(3,5), random.uniform(30,60), random.uniform(1.2,2.0), random.choice([CYAN,PINK,PURPLE]), depth)
            self.galactics.spawn(swirl)

        if depth >= 4 and self.can_spawn() and random.random() < prob * 0.12 * up_mult("Flash Bang") * self.variety_factor:
            self._flash()

        if paradox and depth > 1:
            self.chain(x + random.gauss(0, 20), y + random.gauss(0, 20), max(0, depth - 2), energy * 0.5)

    # ── Spawn Helpers (unchanged, but with buff amplification) ──
    def _explosion(self,x,y,d,e):
        if not self.can_spawn(): return
        self.use()
        vs=self.vscale()
        r=int(random.uniform(20,40)*vs*self.explosion_scale())
        r = min(r, 100)
        pal=random.choice(ALL_PALETTES)
        ex=self.explosions.get()
        ex.setup(x,y,r,random.uniform(0.3,0.4+vs*0.05),pal,d,e,flash=random.random()<min(0.1,0.02*vs))
        self.explosions.spawn(ex)

        if self.can_spawn() and r>20 and random.random()<0.5:
            self.use()
            ring=self.explosions.get()
            ring_pal=random.choice([PAL_ELEC,PAL_PLASMA,PAL_ICE,pal])
            ring.setup(x,y,int(r*1.2),random.uniform(0.4,0.6),ring_pal,d,ring=True)
            self.explosions.spawn(ring)

        n=int(random.randint(5,8)*vs*self.particle_mult())
        n = min(n, 15)
        ag=self.has("Chaos Particles")
        glow_chance=min(0.7,0.25+vs*0.05)
        for _ in range(min(n,self.spawn_budget,30)):
            if not self.can_spawn(): break
            self.use()
            a=random.uniform(0,6.28)
            kind=random.random()
            if kind<0.3:
                sp=random.uniform(3,6)*vs
                p=self.particles.get()
                p.setup(x,y,math.cos(a)*sp,math.sin(a)*sp,random.uniform(0.15,0.3),
                        random.choice([WHITE,YELLOW,CYAN]),random.uniform(1,2),True,0,d,0)
                p.friction=0.95
            elif kind<0.6:
                sp=random.uniform(2,4)*vs
                p=self.particles.get()
                p.setup(x,y,math.cos(a)*sp,math.sin(a)*sp,random.uniform(0.4,0.8+vs*0.05),
                        random.choice(pal),random.uniform(2,3),ag or random.random()<glow_chance,
                        random.uniform(0.02,0.04),d,random.randint(3,6))
            else:
                sp=random.uniform(0.5,2)*vs
                p=self.particles.get()
                p.setup(x,y,math.cos(a)*sp,math.sin(a)*sp,random.uniform(0.5,1.0+vs*0.1),
                        random.choice(pal),random.uniform(2,3+vs*0.3),True,
                        random.uniform(0,0.02),d,0)
            self.particles.spawn(p)

        self.shake=max(self.shake,min(8,1+d+vs*0.3)); self.bg_pulse=max(self.bg_pulse,min(1,0.1+vs*0.03))

    def _lightning(self,x,y,ex,ey,d):
        if not self.can_spawn(): return
        self.use()
        vs=self.vscale()
        l=self.lightnings.get()
        c=random.choice([ELECTRIC,CYAN,BLUE,WHITE,PURPLE])
        th = max(1, int(1 + self.combo*0.001 + self.ulv("Lightning Amp")*0.5 + vs*0.3))
        th = min(th, 4)
        l.setup(x,y,ex,ey,random.uniform(0.15,0.2+vs*0.02),c,d,th)
        self.lightnings.spawn(l)

    def _fractal(self,x,y,r,d):
        if not self.can_spawn(): return
        self.use()
        vs=self.vscale()
        fl=self.fractals.get()
        fl.setup(x,y,int(min(r, 80)*vs),random.randint(3,int(4+vs)),random.uniform(0.3,0.3+vs*0.05),
                 random.choice([ELECTRIC,CYAN,WHITE]),d)
        self.fractals.spawn(fl)

    def _shockwave(self,x,y,r,d):
        if not self.can_spawn(): return
        self.use()
        vs=self.vscale()
        r = min(int(r*vs), 120)
        s=self.shockwaves.get()
        s.setup(x,y,r,random.uniform(0.5,0.6+vs*0.1),random.choice([CYAN,BLUE,ELECTRIC,WHITE,TEAL]),
                max(2,int(2+vs*0.3)),d,distort=random.random()<min(0.6,0.1+vs*0.03))
        self.shockwaves.spawn(s)

    def _plasma(self,x,y,r,d):
        if not self.can_spawn(): return
        self.use()
        vs=self.vscale()
        r = min(int(r*vs), 80)
        e=self.explosions.get()
        e.setup(x,y,r,random.uniform(0.5,0.7+vs*0.1),PAL_PLASMA,d,ring=True)
        self.explosions.spawn(e)
        
    def _prism(self, x, y, d):
        if not self.can_spawn(): return
        self.use()
        vs=self.vscale()
        pr=self.prisms.get()
        pr.setup(x,y,int(min(random.uniform(20,30)*vs, 60)),random.randint(3,5),random.uniform(0.5,1.0+vs*0.05),
                 random.choice([PINK, TEAL, MAGENTA, CYAN]),d)
        self.prisms.spawn(pr)

    def _starburst(self, x, y, d):
        if not self.can_spawn(): return
        self.use()
        vs=self.vscale()
        sb=self.starbursts.get()
        sb.setup(x,y,min(random.uniform(20,30)*vs, 50),random.randint(5,7),random.uniform(0.3,0.5),
                 random.uniform(0.6,1.0+vs*0.05), random.choice([PINK, MAGENTA, GOLD, CYAN]), d)
        self.starbursts.spawn(sb)

    def _nebula(self, x, y, d):
        if not self.can_spawn(): return
        self.use()
        vs=self.vscale()
        n=self.nebulas.get()
        n.setup(x,y,min(int(random.uniform(60,100)*vs), 120),random.uniform(2.0,3.0),
                random.choice([PURPLE, VOID, INDIGO, MAGENTA]),d)
        self.nebulas.spawn(n)

    def _meteor(self,x,y,a,d,e):
        if not self.can_spawn(): return
        self.use()
        vs=self.vscale()
        m=self.meteors.get()
        m.setup(x,y,a,random.uniform(4,5+vs),random.uniform(1,1.2+vs*0.2),
                random.choice([ORANGE,RED,YELLOW,GOLD,EMBER]),d,e)
        m.size=random.uniform(3,4+vs)
        self.meteors.spawn(m)

    def _comet(self,x,y,d):
        if not self.can_spawn(): return
        self.use()
        vs=self.vscale()
        c=self.comets.get()
        c.setup(x,y,random.uniform(0,6.28),random.uniform(2,2.5+vs*0.5),random.uniform(2,2.5+vs*0.3),
                random.choice([CYAN,ICE,BLUE,WHITE,TEAL]),d)
        c.size=2+vs*0.5
        self.comets.spawn(c)

    def _orbit_stars(self,x,y,d,n=3):
        vs=self.vscale()
        for _ in range(n):
            if not self.can_spawn(): break
            self.use()
            s=self.orbits.get()
            s.setup(x,y,min(random.uniform(15,30+vs*8), 50),random.uniform(1.5,2.5+vs*0.3),
                    random.uniform(2,2.5+vs*0.4),
                    random.choice([GOLD,CYAN,PINK,WHITE,GREEN,YELLOW]),
                    random.uniform(2,2.5+vs*0.5),d)
            self.orbits.spawn(s)

    def _gravity_well(self,x,y,d):
        if not self.can_spawn(): return
        self.use()
        vs=self.vscale()
        g=self.wells.get()
        st=1+self.upow("Gravity Strength")*self.ulv("Gravity Strength")*0.3+vs*0.1
        g.setup(x,y,min(random.uniform(30,40+vs*10), 70),st,random.uniform(2,2.5+vs*0.3),
                random.choice([PURPLE,MAGENTA,BLUE,INDIGO]),d)
        self.wells.spawn(g)

    def _beam(self,x,y,ex,ey,d,thick=3):
        if not self.can_spawn(): return
        self.use()
        vs=self.vscale()
        b=self.beams.get()
        b.setup(x,y,ex,ey,random.uniform(0.2,0.25+vs*0.05),
                random.choice([CYAN,ELECTRIC,WHITE,PINK,GOLD]),int(min(thick*vs*0.5+1, 5)),d)
        self.beams.spawn(b)

    def _rift(self,x,y,length,d):
        if not self.can_spawn(): return
        self.use()
        vs=self.vscale()
        r=self.rifts.get()
        r.setup(x,y,int(min(length*vs, 70)),random.uniform(0,3.14),random.uniform(1.5,1.8+vs*0.2),
                random.choice([PURPLE,VOID,MAGENTA,INDIGO]),d)
        self.rifts.spawn(r)

    def _spiral(self,x,y,d):
        if not self.can_spawn(): return
        self.use()
        vs=self.vscale()
        s=self.spirals.get()
        s.setup(x,y,min(random.uniform(30,35+vs*10), 60),random.randint(2,int(2+vs*0.5)),
                random.uniform(1.5,1.8+vs*0.2),
                random.choice([CYAN,ELECTRIC,PINK,GOLD,GREEN]),d)
        self.spirals.spawn(s)

    def _pulse(self,x,y,d):
        if not self.can_spawn(): return
        self.use()
        vs=self.vscale()
        p=self.pulses.get()
        p.setup(x,y,random.randint(40,int(60+vs*20)),random.randint(2,int(3+vs*0.4)),
                random.uniform(0.8,1+vs*0.1),
                random.choice([GOLD,CYAN,PINK,WHITE]),d)
        self.pulses.spawn(p)

    def _nova(self,x,y,d,e):
        if not self.can_spawn(): return
        self.use()
        vs=self.vscale()
        r=int(min(random.uniform(60,100)*vs*self.explosion_scale(), 150))
        ex=self.explosions.get()
        ex.setup(x,y,r,random.uniform(0.6,0.8+vs*0.1),PAL_NOVA,d,e,flash=True)
        self.explosions.spawn(ex)
        num_rings=int(2+vs*0.3)
        for i in range(num_rings):
            if self.can_spawn():
                self.use()
                s=self.shockwaves.get()
                c=random.choice([WHITE,CYAN,MAGENTA,GOLD])
                s.setup(x,y,min(r+i*int(15+vs*3), 150),0.6+i*0.1,c,max(2,int(2+vs*0.3)),d,distort=True)
                self.shockwaves.spawn(s)
        for _ in range(int(1 + vs * 0.5)):
            if not self.can_spawn(): break
            a=random.uniform(0,6.28); dist=random.uniform(30,60)*vs
            self._lightning(x,y,x+math.cos(a)*dist,y+math.sin(a)*dist,d)
        for _ in range(int(5+vs*2)):
            if not self.can_spawn(): break
            self.use()
            a=random.uniform(0,6.28); sp=random.uniform(3,6)*vs
            p=self.particles.get()
            p.setup(x,y,math.cos(a)*sp,math.sin(a)*sp,random.uniform(0.5,1.0),
                    random.choice(PAL_NOVA),random.uniform(2,4),True,
                    random.uniform(0.01,0.03),d,random.randint(4,8))
            self.particles.spawn(p)
        self.shake=min(20,5+d*1.5+vs); self.bg_pulse=1.0

    def _blackhole(self,x,y,d):
        if not self.can_spawn(): return
        self.use()
        vs=self.vscale()
        bh=self.blackholes.get()
        bh.setup(x,y,min(random.uniform(20,25+vs*8), 45),random.uniform(3,3.5+vs*0.5),d)
        self.blackholes.spawn(bh)

    def _flash(self):
        if not self.can_spawn(): return
        self.use()
        vs=self.vscale()
        fl=self.flashes.get()
        fl.setup(min(0.3,random.uniform(0.1,0.12+vs*0.02)),
                 random.uniform(0.1,0.1+vs*0.01),
                 random.choice([WHITE,CYAN,GOLD]))
        self.flashes.spawn(fl)

    def float_text(self,x,y,text,color=GOLD):
        ft=self.texts.get()
        ft.setup(x+random.gauss(0,5),y+random.gauss(0,5),text,color,font=self.font_md)
        self.texts.spawn(ft)

    # ── Void Crystal handling (replaces golden cookie placeholder) ──
    def spawn_crystal(self):
        if self.crystal is not None:
            return
        x = random.randint(50, self.game_w - 50)
        y = random.randint(50, HEIGHT - 50)
        crystal = VoidCrystal()
        crystal.setup(x, y)
        self.crystal = crystal

    def activate_crystal_buff(self):
        self.crystal_buff_timer = CRYSTAL_BUFF_DURATION
        self.crystal_mult = CRYSTAL_BUFF_MULT
        # Massive visual celebration
        self.spawn_budget = MAX_SPAWN * 2
        self._nova(self.crystal.x, self.crystal.y, 0, 10000)
        for _ in range(10):
            a = random.uniform(0, 6.28)
            d = random.uniform(50, 200)
            self._lightning(self.crystal.x, self.crystal.y,
                            self.crystal.x + math.cos(a)*d,
                            self.crystal.y + math.sin(a)*d, 0)
        self._flash()
        self.float_text(self.crystal.x, self.crystal.y-50, "VOID SURGE!", (180,100,255))
        self.crystal = None

    # ── Click ──
    def do_click(self, x, y, auto=False):
        if x > self.game_w: 
            return

        # Check crystal click
        if not auto and self.crystal is not None:
            dx = x - self.crystal.x
            dy = y - self.crystal.y
            if math.hypot(dx, dy) < 30:  # radius
                self.activate_crystal_buff()
                # Still give click energy but with buff active

        power = self.click_power()
        self.energy += power
        self.total_energy += power
        self.clicks += 1

        if not auto:
            combo_gain = 1
            if self.has("Combo Catalyst"): combo_gain += int(self.upow("Combo Catalyst") * self.ulv("Combo Catalyst"))
            if self.has("Combo Master"): combo_gain += int(self.upow("Combo Master") * self.ulv("Combo Master"))
            if self.has("Combo Lord"): combo_gain += int(self.upow("Combo Lord") * self.ulv("Combo Lord"))
            if self.has("Combo God"): combo_gain += int(self.upow("Combo God") * self.ulv("Combo God"))
            if self.has("Combo Singularity"): combo_gain += int(self.upow("Combo Singularity") * self.ulv("Combo Singularity"))
            
            self.combo += combo_gain
            self.combo_timer = self.combo_decay

        self.max_combo = max(self.max_combo, self.combo)
        self.float_text(x, y - 20, f"+{fmt(power)}", GOLD)
        self.spawn_budget = MAX_SPAWN
        self.chain(x, y, 0, power)

        # Ambient FX on every click
        vs = self.vscale()
        for _ in range(random.randint(1, 2)):
            if not self.can_spawn(): break
            self.use()
            a = random.uniform(0, 6.28)
            sp = random.uniform(4, 8) * vs
            p = self.particles.get()
            p.setup(x, y, math.cos(a)*sp, math.sin(a)*sp, random.uniform(0.1, 0.25),
                    random.choice([WHITE, GOLD, YELLOW, CYAN]),
                    random.uniform(1, 2), True, 0, 0, 0)
            p.friction = 0.92
            self.particles.spawn(p)

        if self.can_spawn() and random.random()<0.5:
            self.use()
            pr = self.pulses.get()
            pr.setup(x, y, int(20 + vs*5), 2, 0.3, random.choice([GOLD, WHITE, CYAN]), 0)
            self.pulses.spawn(pr)

        if self.has("Click Burst"):
            n=int(self.upow("Click Burst")*self.ulv("Click Burst"))
            for _ in range(min(n,15)):
                if not self.can_spawn(): break
                self.use()
                a=random.uniform(0,6.28); sp=random.uniform(2,5)
                p=self.particles.get()
                p.setup(x,y,math.cos(a)*sp,math.sin(a)*sp,random.uniform(0.3,0.6),
                        random.choice(random.choice(ALL_PALETTES)),random.uniform(2,4),True)
                self.particles.spawn(p)

        if self.has("Finger Storm") and self.can_spawn():
            for _ in range(int(2+vs)):
                if not self.can_spawn(): break
                self.use()
                a=random.uniform(0,6.28); sp=random.uniform(3,6)
                p=self.particles.get()
                p.setup(x,y,math.cos(a)*sp,math.sin(a)*sp,random.uniform(0.2,0.4),
                        random.choice([ELECTRIC,CYAN,WHITE]),random.uniform(1,2),True,0,0,
                        random.randint(3,5))
                self.particles.spawn(p)

    # ── Prestige ──
    def can_prestige(self): return self.total_energy>=1e6
    def do_prestige(self):
        if not self.can_prestige(): return
        gained=math.log10(max(1,self.total_energy))*(1+self.prestige_count*0.3)
        old_ce=self.chaos_energy+gained; old_pc=self.prestige_count+1
        old_cm=1+old_ce*0.1; old_pt=self.play_time
        cx,cy=self.game_w//2,HEIGHT//2
        self.spawn_budget=MAX_SPAWN
        self._nova(cx,cy,0,1000)
        for _ in range(5):
            a=random.uniform(0,6.28); d=random.uniform(50,150)
            self._lightning(cx,cy,cx+math.cos(a)*d,cy+math.sin(a)*d,1)
        self._flash(); self.shake=20
        self.reset_state()
        self.chaos_energy=old_ce; self.prestige_count=old_pc
        self.chaos_mult=old_cm; self.play_time=old_pt
        self.save_msg="REALITY COLLAPSED!"; self.save_msg_timer=3

    # ── Save / Load ──
    def save_game(self):
        data={"energy":self.energy,"total_energy":self.total_energy,
              "combo":self.combo,"max_combo":self.max_combo,"clicks":self.clicks,
              "chaos_energy":self.chaos_energy,"prestige_count":self.prestige_count,
              "chaos_mult":self.chaos_mult,"play_time":self.play_time,
              "upgrades":{u.name:u.level for u in self.upgrades}}
        try:
            with open(SAVE_FILE,"w") as f: json.dump(data,f,indent=2)
            self.save_msg="Game Saved!"; self.save_msg_timer=2
        except Exception as e:
            self.save_msg=f"Save failed: {e}"; self.save_msg_timer=3

    def load_game(self):
        try:
            with open(SAVE_FILE,"r") as f: data=json.load(f)
            self.energy=data.get("energy",0); self.total_energy=data.get("total_energy",0)
            self.combo=data.get("combo",0); self.max_combo=data.get("max_combo",0)
            self.clicks=data.get("clicks",0); self.chaos_energy=data.get("chaos_energy",0)
            self.prestige_count=data.get("prestige_count",0)
            self.chaos_mult=data.get("chaos_mult",1); self.play_time=data.get("play_time",0)
            self.galaxy_boost = data.get("galaxy_boost", 0)
            ulvs=data.get("upgrades",{})
            for u in self.upgrades: u.level=ulvs.get(u.name,0)
            self.save_msg="Game Loaded!"; self.save_msg_timer=2
        except FileNotFoundError:
            self.save_msg="No save file found"; self.save_msg_timer=2
        except Exception as e:
            self.save_msg=f"Load failed: {e}"; self.save_msg_timer=3

    # ── Update ──
    def update(self,dt):
        self.time+=dt; self.play_time+=dt; self.spawn_budget=MAX_SPAWN

        # Void Crystal spawn
        if self.crystal is None:
            self.crystal_spawn_timer -= dt
            if self.crystal_spawn_timer <= 0:
                self.spawn_crystal()
                self.crystal_spawn_timer = random.uniform(CRYSTAL_SPAWN_MIN, CRYSTAL_SPAWN_MAX)
        else:
            # Update crystal life
            self.crystal.update(dt)
            if not self.crystal.alive:
                self.crystal = None

        # Buff timer
        if self.crystal_buff_timer > 0:
            self.crystal_buff_timer -= dt
            if self.crystal_buff_timer <= 0:
                self.crystal_mult = 1.0
                self.crystal_buff_timer = 0

        if self.combo>0:
            self.combo_timer-=dt
            if self.combo_timer<=0:
                drain=max(2,int(self.combo*0.05))
                self.combo=max(0,self.combo-drain)
                self.combo_timer=0.1

        auto=self.auto_cps()
        if auto>0:
            self.auto_timer+=dt
            interval=1.0/min(auto,20)
            while self.auto_timer>=interval:
                self.auto_timer-=interval
                self.do_click(random.randint(50,self.game_w-50),
                              random.randint(50,HEIGHT-50),True)

        for pool in self.all_pools: pool.update(dt)

        for m in self.meteors.active:
            if m.alive and m.y>HEIGHT-20:
                self.spawn_budget=min(20,MAX_SPAWN)
                ix,iy=m.x,HEIGHT-20
                self._explosion(ix,iy,3,m.energy)
                if self.can_spawn():
                    self._shockwave(ix,iy,int(40+m.size*5),3)
                for _ in range(random.randint(3,5)):
                    if not self.can_spawn(): break
                    self.use()
                    a=random.uniform(-3.14,-0.1) if random.random()<0.5 else random.uniform(-3.0,0.0)
                    sp=random.uniform(3,6)
                    p=self.particles.get()
                    p.setup(ix,iy,math.cos(a)*sp,math.sin(a)*sp-1,random.uniform(0.3,0.6),
                            random.choice([ORANGE,YELLOW,RED,EMBER]),random.uniform(1,2),True,
                            0.05,3,random.randint(2,4))
                    self.particles.spawn(p)
                if random.random()<0.3: self.chain(ix,iy,3,m.energy)
                m.alive=False

        # gravity well influence — limit to first 50 particles
        for w in self.wells.active:
            if not w.alive: continue
            wt=w.t()
            for p in self.particles.active[:50]:
                if not p.alive: continue
                dx=w.x-p.x; dy=w.y-p.y; d=max(5,math.hypot(dx,dy))
                if d<w.radius*1.5:
                    f=w.strength*wt*0.2/max(1,d*0.1)
                    p.vx+=dx/d*f; p.vy+=dy/d*f

        # black hole pull — limit to first 50 particles
        for bh in self.blackholes.active:
            if not bh.alive: continue
            bt=bh.t()
            for p in self.particles.active[:50]:
                if not p.alive: continue
                dx=bh.x-p.x; dy=bh.y-p.y; d=max(5,math.hypot(dx,dy))
                if d<bh.radius*2.5:
                    f=bt*0.3/max(1,d*0.05)
                    p.vx+=dx/d*f; p.vy+=dy/d*f
                    if d<bh.radius*0.2: p.alive=False

        if self.shake>0:
            self.shake*=0.9; self.sx=random.gauss(0,self.shake); self.sy=random.gauss(0,self.shake)
            if self.shake<0.3: self.shake=0; self.sx=self.sy=0
        self.bg_pulse*=0.95
        if self.save_msg_timer>0: self.save_msg_timer-=dt

    # Helper to truncate text
    def truncate_text(self, text, font, max_width):
        if font.size(text)[0] <= max_width:
            return text
        # Binary search for the longest prefix that fits
        lo, hi = 0, len(text)
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if font.size(text[:mid] + "...")[0] <= max_width:
                lo = mid
            else:
                hi = mid - 1
        return text[:lo] + "..."

    # ── Draw ──
    def draw(self):
        p=min(1,self.bg_pulse); vs=self.vscale()
        bg_r=int(BG[0]+15*p+min(10,vs*1.5))
        bg_g=int(BG[1]+3*p+min(3,vs*0.5))
        bg_b=int(BG[2]+20*p+min(25,vs*5.0))
        self.scr.fill((min(255,bg_r),min(255,bg_g),min(255,bg_b)))

        # Crystal overlay tint during buff
        if self.crystal_buff_timer > 0:
            tint = pygame.Surface((WIDTH,HEIGHT), pygame.SRCALPHA)
            tint.fill((140,0,255, 30))  # purple tint
            self.scr.blit(tint, (0,0))

        for sx,sy,sz,b in self.bg_stars:
            tw=0.5+0.5*math.sin(self.time*b*2+sx)
            c=int(min(255,50*b*tw+30*p+vs*6))
            pygame.draw.circle(self.scr,(c,c,min(255,int(c*1.1))),(sx,sy),max(1,int(sz)))

        ox,oy=int(self.sx),int(self.sy)
        for pool in self.all_pools:
            for fx in pool.active:
                if fx.alive:
                    fx.x+=ox; fx.y+=oy; fx.draw(self.scr); fx.x-=ox; fx.y-=oy

        # Draw crystal
        if self.crystal and self.crystal.alive:
            self.crystal.x += ox
            self.crystal.y += oy
            self.crystal.draw(self.scr)
            self.crystal.x -= ox
            self.crystal.y -= oy

        self._draw_panel()
        self._draw_hud()

    def _draw_hud(self):
        if self.combo>0:
            # Format combo with suffix and choose color based on suffix index
            suffix_idx = suffix_index_from_value(self.combo)
            combo_color = _SUFFIX_COLORS[suffix_idx] if suffix_idx < len(_SUFFIX_COLORS) else WHITE
            ct = f"x{fmt(self.combo)}"
            sc=min(1.2,1+self.combo*0.0005)
            cf=pygame.font.SysFont("Arial",min(int(42*sc),70),True)
            cs2=cf.render(ct,True,combo_color); cs2.set_alpha(180)
            self.scr.blit(cs2,(self.game_w//2-cs2.get_width()//2,12))
            bw=min(self.game_w-40,300); bx=self.game_w//2-bw//2; by=16+cs2.get_height()
            fill=self.combo_timer/self.combo_decay
            pygame.draw.rect(self.scr,(30,30,40),(bx,by,bw,3))
            pygame.draw.rect(self.scr,combo_color,(bx,by,int(bw*fill),3))

        # Buff indicator
        if self.crystal_buff_timer > 0:
            gt = f"VOID SURGE! {self.crystal_buff_timer:.1f}s"
            gtxt = self.font_md.render(gt, True, (180,100,255))
            self.scr.blit(gtxt, (self.game_w//2 - gtxt.get_width()//2, 80))

        es=self.font_xl.render(fmt(self.energy),True,GOLD)
        self.scr.blit(es,(self.game_w//2-es.get_width()//2,HEIGHT-60))
        el=self.font_sm.render("ENERGY",True,(150,130,80))
        self.scr.blit(el,(self.game_w//2-el.get_width()//2,HEIGHT-22))

        f=self.fury()
        fury_c=palette_sample(PAL_RAINBOW,min(0.99,(f-1)*0.03)) if f>1 else (60,60,70)
        fx=self.font_xs.render(f"FX:{self.fx_count()} FPS:{int(self.clock.get_fps())} FURY:x{f:.1f}",True,fury_c)
        self.scr.blit(fx,(5,HEIGHT-18))

        if self.can_prestige():
            pt2=0.5+0.5*math.sin(self.time*3)
            pc=(int(200*pt2),int(50*pt2),int(220*pt2))
            prestige_text = self.font_sm.render("[P] REALITY COLLAPSE", True, pc)
            self.scr.blit(prestige_text, ((self.game_w - prestige_text.get_width()) // 2, HEIGHT-85))

        if self.chaos_energy>0:
            self.scr.blit(self.font_xs.render(
                f"Chaos: {fmt(self.chaos_energy)} (x{self.chaos_mult:.1f}) Prestiges: {self.prestige_count}",
                True,MAGENTA),(5,5))

        if self.save_msg_timer>0:
            a=min(255,int(self.save_msg_timer*255))
            sm=self.font_md.render(self.save_msg,True,GREEN); sm.set_alpha(a)
            self.scr.blit(sm,(self.game_w//2-sm.get_width()//2,HEIGHT//2-20))

        instruction_text = self.font_xs.render("[S]ave [L]oad [P]restige [Esc]Quit", True, (45,45,55))
        self.scr.blit(instruction_text, ((self.game_w - instruction_text.get_width()) // 2, HEIGHT-100))

    def _draw_panel(self):
        pr=pygame.Rect(self.game_w,0,self.panel_w,HEIGHT)
        pygame.draw.rect(self.scr,(10,10,18),pr)
        pygame.draw.line(self.scr,(40,40,60),(self.game_w,0),(self.game_w,HEIGHT),1)

        x0=self.game_w+8; y=8-self.scroll

        # Filter buttons
        btn_w = (self.panel_w - 16) // len(self.filter_buttons)
        mx,my = pygame.mouse.get_pos()
        for i, label in enumerate(self.filter_buttons):
            btn_rect = pygame.Rect(x0 + i*btn_w, y, btn_w, 20)
            if btn_rect.collidepoint(mx, my) and mx > self.game_w:
                if pygame.mouse.get_pressed()[0]:
                    self.filter = self.filter_map[label]
            col = GOLD if self.filter == self.filter_map[label] else (80,80,100)
            pygame.draw.rect(self.scr, (20,20,30), btn_rect, 1)
            # Center text in button
            txt = self.font_xs.render(label, True, col)
            txt_rect = txt.get_rect(center=btn_rect.center)
            self.scr.blit(txt, txt_rect)
        y += 25

        stats=[f"Click: {fmt(self.click_power())}",f"Auto: {fmt(self.auto_cps())}/s",
               f"Best Combo: {self.max_combo}",f"Chain: +{int(self.chain_prob()*100)}%  Depth: {self.max_depth()}",
               f"Fury: x{self.fury():.1f}",
               f"Clicks: {self.clicks}",f"Time: {int(self.play_time//60)}m{int(self.play_time%60):02d}s"]
        for s in stats:
            if 0<=y<HEIGHT: self.scr.blit(self.font_xs.render(s,True,(140,140,160)),(x0,y))
            y+=15
        y+=6

        if 0<=y<HEIGHT:
            self.scr.blit(self.font_md.render("── UPGRADES ──",True,(100,100,130)),(x0,y))
        y+=24

        self.hovered = -1
        cat_tags={"click":"CLK","auto":"AUTO","chain":"CHN","fx":"FX",
                  "amp":"AMP","mult":"MULT","cosmic":"CSM","combo":"CMB"}

        # Filter upgrades
        filtered_upgrades = [u for u in self.upgrades if self.filter == "all" or u.cat == self.filter]

        max_width = self.panel_w - 20  # leave margin

        for i,u in enumerate(filtered_upgrades):
            # combo lock
            if u.combo>self.max_combo and u.level==0:
                if 0<=y<HEIGHT:
                    self.scr.blit(self.font_xs.render(f"??? (combo {fmt(u.combo)})",True,(35,35,45)),(x0,y))
                y+=18; continue

            ih=44; rect=pygame.Rect(x0-3,y,self.panel_w-14,ih)
            hov=rect.collidepoint(mx,my) and mx>self.game_w
            can=u.can_buy(self.energy)
            if hov: self.hovered = i  # index in filtered list

            if 0<=y<HEIGHT and y+ih>0:
                if hov and can: pygame.draw.rect(self.scr,(25,35,40),rect,border_radius=3)
                elif hov: pygame.draw.rect(self.scr,(20,18,25),rect,border_radius=3)
                nc=u.color if can else (65,65,75)
                tag=cat_tags.get(u.cat,"?")

                # Truncate name if too long
                name_text = f"[{tag}] {u.name} [{u.level}]"
                name_disp = self.truncate_text(name_text, self.font_sm, max_width)
                self.scr.blit(self.font_sm.render(name_disp, True, nc), (x0, y+1))

                # Truncate description
                desc_disp = self.truncate_text(u.desc, self.font_xs, max_width)
                self.scr.blit(self.font_xs.render(desc_disp, True, (75,75,95)), (x0, y+17))

                cost_text = f"Cost: {fmt(u.cost)}"
                cost_disp = self.truncate_text(cost_text, self.font_xs, max_width)
                cc2=GOLD if can else (55,45,30)
                self.scr.blit(self.font_xs.render(cost_disp, True, cc2), (x0, y+31))
            y+=ih+2

        y+=15
        if 0<=y<HEIGHT:
            self.scr.blit(self.font_md.render("── PRESTIGE ──",True,(130,50,150)),(x0,y))
        y+=24
        if self.can_prestige() and 0<=y<HEIGHT:
            gained=math.log10(max(1,self.total_energy))*(1+self.prestige_count*0.3)
            self.scr.blit(self.font_sm.render(f"[P] +{fmt(gained)} Chaos",True,MAGENTA),(x0,y))
        elif 0<=y<HEIGHT:
            self.scr.blit(self.font_xs.render(f"Need {fmt(1e6)} total energy",True,(50,50,60)),(x0,y))
        y+=30
        self.max_scroll=max(0,y+self.scroll-HEIGHT+50)

    # ── Main Loop ──
    def run(self):
        if os.path.exists(SAVE_FILE): self.load_game()

        while self.running:
            dt=min(self.clock.tick(FPS)/1000.0,0.05)

            for ev in pygame.event.get():
                if ev.type==pygame.QUIT: self.running=False
                elif ev.type==pygame.KEYDOWN:
                    if ev.key==pygame.K_ESCAPE: self.running=False
                    elif ev.key==pygame.K_p: self.do_prestige()
                    elif ev.key==pygame.K_s: self.save_game()
                    elif ev.key==pygame.K_l: self.load_game()
                elif ev.type==pygame.MOUSEBUTTONDOWN:
                    if ev.button==1:
                        mx2,my2=ev.pos
                        if mx2<self.game_w:
                            self.do_click(mx2,my2)
                        elif self.hovered>=0:
                            filtered = [u for u in self.upgrades if self.filter == "all" or u.cat == self.filter]
                            if self.hovered < len(filtered):
                                u = filtered[self.hovered]
                                # Check both energy and max_combo requirement
                                if u.can_buy(self.energy) and self.max_combo >= u.combo:
                                    self.energy -= u.cost
                                    u.level += 1
                                    # If it's a multiplier upgrade, show a confirmation
                                    if u.cat in ("mult", "cosmic"):
                                        self.float_text(mx2, my2-30, f"x{u.power:.1f} ALL!", GOLD)
                    elif ev.button==4: self.scroll=max(0,self.scroll-35)
                    elif ev.button==5: self.scroll=min(self.max_scroll,self.scroll+35)

            if pygame.mouse.get_pressed()[0]:
                mx2,my2=pygame.mouse.get_pos()
                if mx2<self.game_w and random.random()<0.2:
                    self.do_click(mx2+random.gauss(0,3),my2+random.gauss(0,3),auto=True)

            self.update(dt)
            self.draw()
            pygame.display.flip()

        self.save_game()
        pygame.quit(); sys.exit()

if __name__=="__main__":

    Game().run()

