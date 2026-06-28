from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
CH=ROOT/'outputs'/'charts'
OUT=ROOT/'outputs'/'screenshots'
OUT.mkdir(parents=True, exist_ok=True)

W,H=1800,1100
img=Image.new('RGB',(W,H),'#F7FAFC')
d=ImageDraw.Draw(img)
font_reg='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
font_bold='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
F=lambda size,b=False: ImageFont.truetype(font_bold if b else font_reg,size)
NAVY='#0B1F33'; TEAL='#0E7490'; MINT='#14B8A6'; CORAL='#E76F51'; SLATE='#64748B'; WHITE='#FFFFFF'; BORDER='#DDE7EC'
# sidebar
d.rounded_rectangle((25,25,315,H-25),radius=20,fill='#EEF6F8',outline=BORDER,width=2)
d.text((55,55),'DASHBOARD CONTROLS',font=F(18,True),fill=NAVY)
controls=[('Geographic level','Global'),('Trend years','2000–2024'),('Map / ranking year','2024'),('Data snapshot','WHO-derived')]
y=115
for label,value in controls:
 d.text((55,y),label,font=F(15,True),fill=SLATE); y+=28
 d.rounded_rectangle((50,y,285,y+48),radius=10,fill=WHITE,outline=BORDER,width=2)
 d.text((65,y+12),value,font=F(17),fill=NAVY); y+=78
# hero
d.rounded_rectangle((340,25,W-25,185),radius=24,fill=NAVY)
d.text((380,55),'MSBA382 · HEALTHCARE ANALYTICS',font=F(18,True),fill='#9EE7E5')
d.text((380,88),'Global Tuberculosis Burden & Treatment Gaps',font=F(37,True),fill=WHITE)
d.text((380,140),'Executive overview · Global snapshot · 2024',font=F(19),fill='#DCEFF4')
# cards
cards=[('Estimated incident cases','10.55M',CORAL),('Incidence /100k','129.8',TEAL),('Estimated TB deaths','1.20M','#F4A261'),('Coverage','78.9%',MINT),('Notification difference','2.22M',NAVY)]
x0=340; gap=16; cardw=(W-365-gap*4)//5
for i,(lab,val,col) in enumerate(cards):
 x=x0+i*(cardw+gap)
 d.rounded_rectangle((x,210,x+cardw,345),radius=18,fill=WHITE,outline=BORDER,width=2)
 d.rectangle((x,210,x+8,345),fill=col)
 d.text((x+25,235),lab,font=F(15,True),fill=SLATE)
 d.text((x+25,278),val,font=F(29,True),fill=NAVY)
# charts
for path,box in [
 (CH/'global_burden_notifications.png',(340,375,1070,955)),
 (CH/'who_region_profile_2024.png',(1090,375,1775,955)),
]:
 chart=Image.open(path).convert('RGB')
 # crop white margins modestly and fit
 chart.thumbnail((box[2]-box[0]-20,box[3]-box[1]-20))
 d.rounded_rectangle(box,radius=18,fill=WHITE,outline=BORDER,width=2)
 px=box[0]+(box[2]-box[0]-chart.width)//2
 py=box[1]+(box[3]-box[1]-chart.height)//2
 img.paste(chart,(px,py))
# footer note
d.rounded_rectangle((340,980,W-25,1065),radius=16,fill='#FFF6ED',outline='#F2D7C7',width=2)
d.text((370,999),'Interpretation guardrail',font=F(17,True),fill=CORAL)
d.text((370,1028),'Estimated burden minus notified cases is a surveillance signal, not proof that every person was untreated.',font=F(16),fill=NAVY)
img.save(OUT/'dashboard_preview.png',quality=95)
print(OUT/'dashboard_preview.png')
