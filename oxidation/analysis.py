import pandas as pd, numpy as np, json
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.optimize import brentq

k=8.617333e-5
def deal_grove(T_C,t_hr=1.0,f=1.0):
    T=T_C+273.15
    B=f*386*np.exp(-0.78/(k*T)); BA=f*9.7e7*np.exp(-2.05/(k*T)); A=B/BA
    return (A/2)*(np.sqrt(1+4*B*t_hr/A**2)-1)*1e4

files={'900C':'/mnt/user-data/uploads/900C_60min_Wet_A0-A15.xlsx',
       '1100C':'/mnt/user-data/uploads/1100C_60min_Wet_A0-A15.xlsx'}
fr=[]
for run,f in files.items():
    df=pd.read_excel(f,header=8); df['Run']=run; fr.append(df)
d=pd.concat(fr,ignore_index=True).rename(columns={'L1 d (A)':'Thk_A','Sample ID':'SID'})
d['Wafer']=d.SID.str.split('_').str[0]; d['Slot']=d.Wafer.str[1:].astype(int)
d['Pt']=d.SID.str.split('_').str[1].astype(int)
d['MeasPos']=d.Pt.map({1:'T',2:'C',3:'B',4:'L',5:'R'})
d['FurnPos']=d.Pt.map({1:'Bottom',2:'Center',3:'Top',4:'Right',5:'Left'})
d['MeasDate']=pd.to_datetime(d['Date/Time']).dt.date.astype(str)
d['SetpointC']=d.Run.map({'900C':900,'1100C':1100}); d['Time_min']=60
EXCL={'900C':['A08','A09','A10','A11'],'1100C':['A00','A01','A02','A03']}
d['MetrologyOK']=~d.apply(lambda r: r.Wafer in EXCL[r.Run],axis=1)
d['Flagged']=(d.Wafer=='A15')|((d.Run=='900C')&(d.Wafer=='A05'))
_e=d.copy()
_e['MetrologyOK']=_e['MetrologyOK'].astype(int); _e['Flagged']=_e['Flagged'].astype(int)
_e[['Run','SetpointC','Time_min','Wafer','Slot','Pt','MeasPos','FurnPos','Thk_A','GOF',
   'Recipe','MeasDate','MetrologyOK','Flagged']].to_csv('out/oxide_tidy_for_JMP.csv',index=False)

S={'primary':d[d.MetrologyOK].copy(),'sensitivity':d[d.MetrologyOK & ~d.Flagged].copy()}
TARGET={'900C':deal_grove(900),'1100C':deal_grove(1100)}
res={'target_A':{k2:round(v,1) for k2,v in TARGET.items()}}

def vc(g):
    n=5; a=g.Slot.nunique(); gm=g.Thk_A.mean(); wm=g.groupby('Slot').Thk_A.mean()
    MSB=n*((wm-gm)**2).sum()/(a-1)
    MSW=((g.Thk_A-g.groupby('Slot').Thk_A.transform('mean'))**2).sum()/(a*(n-1))
    return max((MSB-MSW)/n,0.0),MSW

def components(g):
    v_w,v_i=vc(g); tot=v_w+v_i
    dev=g.Thk_A-g.groupby('Slot').Thk_A.transform('mean')
    pm=dev.groupby(g.FurnPos).transform('mean')
    vp,vr=(pm**2).sum()/len(g),((dev-pm)**2).sum()/len(g)
    sc=v_i/(vp+vr)
    return dict(w2w_pct=100*v_w/tot,pos_pct=100*vp*sc/tot,res_pct=100*vr*sc/tot,
                sd_w2w=v_w**.5,sd_within=v_i**.5,sd_pos=(vp*sc)**.5,sd_res=(vr*sc)**.5)

res['variance_components']={tag:{r:components(g) for r,g in S[tag].groupby('Run')} for tag in S}

s=S['primary']
u=s.groupby(['Run','Slot']).Thk_A.agg(['mean','std','min','max']).reset_index()
u['NU_halfrange_pct']=100*(u['max']-u['min'])/(2*u['mean']); u['NU_1sigma_pct']=100*u['std']/u['mean']
p=s.pivot_table(index=['Run','Slot'],columns='FurnPos',values='Thk_A').reset_index()
uni=u.merge(p,on=['Run','Slot'])
uni['V_TopMinusBottom_A']=uni.Top-uni.Bottom; uni['V_pct']=100*uni.V_TopMinusBottom_A/uni['mean']
uni['H_LeftMinusRight_A']=uni.Left-uni.Right
uni['Target_A']=uni.Run.map(TARGET); uni['Resid_A']=uni['mean']-uni.Target_A
uni['Resid_pct']=100*uni.Resid_A/uni.Target_A
uni['Flagged']=uni.Slot.isin([15])|((uni.Run=='900C')&(uni.Slot==5))
uni.round(2).to_csv('out/wafer_uniformity.csv',index=False)

dg={}
for tag in S:
    dg[tag]={}
    for r,T in [('900C',900),('1100C',1100)]:
        m=S[tag][S[tag].Run==r].Thk_A.mean()
        dg[tag][r]=dict(target=TARGET[r],measured=m,ratio=m/TARGET[r],
            f_pH2O=brentq(lambda f: deal_grove(T,f=f)-m,0.01,1.0),
            dT_C=brentq(lambda x: deal_grove(T+x)-m,-300,50),
            t_eff_min=60*brentq(lambda t: deal_grove(T,t_hr=t)-m,0.005,3.0))
res['deal_grove']=dg

cap={}
for tag in S:
    cap[tag]={}
    for r in ['900C','1100C']:
        g=S[tag][S[tag].Run==r]; tgt=TARGET[r]; mu=g.Thk_A.mean()
        sd_w=vc(g)[1]**.5; sd_o=g.Thk_A.std()
        tols={}
        for tol in (0.05,0.10,0.15):
            L,U=tgt*(1-tol),tgt*(1+tol)
            tols[f'{int(tol*100)}%']=dict(LSL=L,USL=U,Cp=(U-L)/(6*sd_w),Cpk=min(U-mu,mu-L)/(3*sd_w),
                                          Pp=(U-L)/(6*sd_o),Ppk=min(U-mu,mu-L)/(3*sd_o))
        cap[tag][r]=dict(mean=mu,sd_within=sd_w,sd_overall=sd_o,target=tgt,tol=tols)
res['capability']=cap

imr={}
for r in ['900C','1100C']:
    x=s[s.Run==r].groupby('Slot').Thk_A.mean().sort_index()
    mr=x.diff().abs().dropna(); mrbar=mr.mean(); sig=mrbar/1.128
    imr[r]=dict(slots=[int(i) for i in x.index],values=[float(v) for v in x.values],CL=float(x.mean()),
        UCL=float(x.mean()+3*sig),LCL=float(x.mean()-3*sig),MRbar=float(mrbar),
        UCL_MR=float(3.267*mrbar),sigma_hat=float(sig),n=int(len(x)))
res['imr']=imr
json.dump(res,open('out/results.json','w'),indent=2,default=float)

# ================= FIGURES =================
plt.rcParams.update({'font.size':7,'axes.grid':True,'grid.alpha':.3,'figure.dpi':200,
                     'axes.spines.top':False,'axes.spines.right':False,'font.family':'DejaVu Sans'})
C={'900C':'#C1442E','1100C':'#2E5C8A'}; runs=['900C','1100C']
vcp=res['variance_components']['primary']

fig,ax=plt.subplots(1,2,figsize=(7.6,2.05))
b1=[vcp[r]['w2w_pct'] for r in runs]; b2=[vcp[r]['pos_pct'] for r in runs]; b3=[vcp[r]['res_pct'] for r in runs]
ax[0].bar(runs,b1,.5,label='Wafer-to-wafer',color='#7A9CC6')
ax[0].bar(runs,b2,.5,bottom=b1,label='Within-wafer: vertical position',color='#C1442E')
ax[0].bar(runs,b3,.5,bottom=np.add(b1,b2),label='Within-wafer: residual',color='#DCCFB8')
for i in range(2):
    c=0
    for v in (b1[i],b2[i],b3[i]):
        ax[0].text(i,c+v/2,f'{v:.0f}%',ha='center',va='center',fontsize=7.5); c+=v
ax[0].set_ylabel('% of total variance within run'); ax[0].set_ylim(0,100)
ax[0].legend(fontsize=5.8,loc='lower center',bbox_to_anchor=(.5,-.40),frameon=False,ncol=1,handlelength=1.2)
ax[0].set_title('(a) Variance components (metrology-clean, 12 wafers/run)',fontsize=8,loc='left')

ypos={'Top':0,'Center':1,'Bottom':2,'Left':3.6,'Right':4.4}
for r in runs:
    g=s[s.Run==r].copy()
    wm=g.groupby('Slot').Thk_A.transform('mean'); g['pct']=100*(g.Thk_A-wm)/wm
    m=g.groupby('FurnPos').pct.mean(); e=g.groupby('FurnPos').pct.std()
    vy=[ypos[q] for q in ['Top','Center','Bottom']]
    ax[1].errorbar([m[q] for q in ['Top','Center','Bottom']],vy,xerr=[e[q] for q in ['Top','Center','Bottom']],
                   marker='o',ms=4,lw=1.5,capsize=2.5,color=C[r],label=f'{r}, 60 min wet')
    ax[1].errorbar([m[q] for q in ['Left','Right']],[ypos['Left'],ypos['Right']],
                   xerr=[e[q] for q in ['Left','Right']],marker='s',ms=4,ls='none',
                   capsize=2.5,mfc='white',color=C[r])
ax[1].axhline(3.0,color='#999',lw=.7,ls=':')
ax[1].axvline(0,color='k',lw=.8)
ax[1].set_yticks(list(ypos.values())); ax[1].set_yticklabels(list(ypos.keys())); ax[1].invert_yaxis()
ax[1].text(.98,.40,'vertical axis',transform=ax[1].transAxes,fontsize=6.2,color='#888',ha='right')
ax[1].text(.98,.06,'horizontal axis',transform=ax[1].transAxes,fontsize=6.2,color='#888',ha='right')
ax[1].set_xlabel('Deviation from wafer mean (%)  ±1σ across wafers')
ax[1].legend(fontsize=6.2,frameon=False,loc='upper left')
ax[1].set_title('(b) Within-wafer signature, furnace frame',fontsize=8,loc='left')
plt.tight_layout(); plt.savefig('out/fig1_variance_and_profile.png',bbox_inches='tight'); plt.close()

fig,ax=plt.subplots(1,3,figsize=(7.8,1.95))
tt=np.linspace(1,120,300)/60
for r,T in [('900C',900),('1100C',1100)]:
    ax[0].plot(tt*60,[deal_grove(T,t) for t in tt],'--',lw=1.1,color=C[r],label=f'{r} model')
    g=uni[uni.Run==r]
    ax[0].scatter([60]*len(g),g['mean'],s=16,color=C[r],zorder=3,label=f'{r} measured')
ax[0].set_xlabel('Oxidation time at setpoint (min)'); ax[0].set_ylabel('Oxide thickness (Å)')
ax[0].legend(fontsize=5.8,frameon=False); ax[0].set_title('(a) Growth curves',fontsize=8,loc='left')
for r in runs:
    g=uni[uni.Run==r]
    ax[1].scatter(g.Slot[~g.Flagged],g.Resid_pct[~g.Flagged],s=18,color=C[r],label=r,zorder=3)
    ax[1].scatter(g.Slot[g.Flagged],g.Resid_pct[g.Flagged],s=30,facecolors='none',edgecolors=C[r],lw=1.2,zorder=3)
ax[1].axhline(0,color='k',lw=.8); ax[1].set_xlabel('Boat slot (A00 = leading edge)')
ax[1].set_ylabel('Residual vs model (%)'); ax[1].set_ylim(-48,6)
ax[1].legend(fontsize=6.2,frameon=False,loc='lower left')
ax[1].set_title('(b) Model residuals',fontsize=8,loc='left')
ax[2].axvspan(0.9,1.1,color='#9BB89B',alpha=.35,label='Assumed spec ±10%')
ax[2].axvline(1.0,color='k',lw=.8,ls='--')
for r in runs:
    c=cap['primary'][r]; e=3*c['sd_within']/c['target']
    ax[2].errorbar([c['mean']/c['target']],[r],xerr=[[e],[e]],fmt='o',ms=5,color=C[r],capsize=3,lw=1.5)
    ax[2].annotate(f"Cp {c['tol']['10%']['Cp']:.2f}   Cpk {c['tol']['10%']['Cpk']:.2f}",
                   (c['mean']/c['target'],r),textcoords='offset points',xytext=(0,-16),
                   ha='center',fontsize=6.4,color=C[r])
ax[2].set_xlim(0.45,1.28); ax[2].set_ylim(-0.6,1.6); ax[2].set_xlabel('Wafer mean ±3σ$_{within}$ / target')
ax[2].legend(fontsize=6.2,frameon=False,loc='upper left')
ax[2].set_title('(c) Capability',fontsize=8,loc='left')
plt.tight_layout(); plt.savefig('out/fig2_dealgrove_capability.png',bbox_inches='tight'); plt.close()

fig,ax=plt.subplots(2,2,figsize=(7.2,3.3),sharex='col')
for j,r in enumerate(runs):
    a=imr[r]; x=np.array(a['values']); sl=a['slots']
    ax[0,j].plot(sl,x,'-o',ms=4,color=C[r],lw=1.2)
    ax[0,j].axhline(a['CL'],color='k',lw=.9)
    for y in (a['UCL'],a['LCL']): ax[0,j].axhline(y,ls='--',lw=.9,color='#B03A2E')
    for xx,yy in zip(sl,x):
        if yy>a['UCL'] or yy<a['LCL']:
            ax[0,j].scatter([xx],[yy],s=60,facecolors='none',edgecolors='#B03A2E',lw=1.4,zorder=4)
    ax[0,j].text(.99,.88,f"UCL {a['UCL']:.0f} | CL {a['CL']:.0f} | LCL {a['LCL']:.0f} Å   σ̂={a['sigma_hat']:.0f}",
                 transform=ax[0,j].transAxes,ha='right',fontsize=6.2)
    ax[0,j].set_title(f'{r} — individuals (wafer mean), trial limits',fontsize=8,loc='left')
    ax[0,j].set_ylabel('Å')
    mr=np.abs(np.diff(x))
    ax[1,j].plot(sl[1:],mr,'-o',ms=4,color='#555',lw=1.2)
    ax[1,j].axhline(a['MRbar'],color='k',lw=.9); ax[1,j].axhline(a['UCL_MR'],ls='--',lw=.9,color='#B03A2E')
    ax[1,j].set_title(f"Moving range   M̄R {a['MRbar']:.0f} | UCL {a['UCL_MR']:.0f} Å",fontsize=8,loc='left')
    ax[1,j].set_xlabel('Boat slot (load order, A00 = leading edge)'); ax[1,j].set_ylabel('Å')
    ax[1,j].set_xticks(sl); ax[0,j].set_xticks(sl)
    ax[0,j].margins(y=.22)
plt.tight_layout(); plt.savefig('out/fig3_imr.png',bbox_inches='tight'); plt.close()

print(json.dumps({k2:res[k2] for k2 in ['target_A','deal_grove']},indent=1,default=lambda o:round(float(o),3)))
print('\nVARIANCE COMPONENTS');  print(pd.DataFrame(vcp).T.round(1).to_string())
print('\nsensitivity:');          print(pd.DataFrame(res['variance_components']['sensitivity']).T.round(1).to_string())
print('\nUNIFORMITY'); print(uni.groupby('Run')[['NU_halfrange_pct','NU_1sigma_pct','V_pct']].agg(['mean','min','max']).round(2).to_string())
print('\nCAPABILITY primary'); 
for r in runs:
    c=cap['primary'][r]; print(f"  {r}: mean {c['mean']:.0f}  target {c['target']:.0f}  sd_within {c['sd_within']:.1f}  sd_overall {c['sd_overall']:.1f}")
    for t,v in c['tol'].items(): print(f"      ±{t}: Cp {v['Cp']:.2f}  Cpk {v['Cpk']:.2f}  Pp {v['Pp']:.2f}  Ppk {v['Ppk']:.2f}")
print('\nCAPABILITY sensitivity (A05/A15 removed)')
for r in runs:
    c=cap['sensitivity'][r]; v=c['tol']['10%']; print(f"  {r}: mean {c['mean']:.0f} sd_within {c['sd_within']:.1f} Cp {v['Cp']:.2f} Cpk {v['Cpk']:.2f}")
print('\nI-MR'); 
for r in runs:
    a=imr[r]; ooc=[f"A{sl:02d}" for sl,v in zip(a['slots'],a['values']) if v>a['UCL'] or v<a['LCL']]
    print(f"  {r}: n={a['n']} CL {a['CL']:.0f} UCL {a['UCL']:.0f} LCL {a['LCL']:.0f} sigma_hat {a['sigma_hat']:.1f} beyond={ooc or 'none'}")
