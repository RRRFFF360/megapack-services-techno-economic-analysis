"""Qualitative decision framework, independent of dispatch model outputs."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

def main():
    root=Path(__file__).resolve().parents[1]
    fig,ax=plt.subplots(figsize=(12,7.6),facecolor='#fbfcf9');ax.set_facecolor('#fbfcf9')
    ax.set(xlim=(0,10),ylim=(0,10));ax.set_xticks([0,10],['Low','High']);ax.set_yticks([0,10],['Low','High'])
    ax.set_xlabel("Customer's internal service capability",fontsize=13,labelpad=12)
    ax.set_ylabel('Revenue sensitivity to downtime / performance loss',fontsize=12,labelpad=14)
    ax.axhline(5,color='#ccd7cc',ls='--',lw=1);ax.axvline(5,color='#ccd7cc',ls='--',lw=1)
    ax.spines[['top','right']].set_visible(False)
    def box(x,y,w,h,title,body,color):
        ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.14',facecolor=color,edgecolor='#8fa89a',lw=1))
        ax.text(x+.18,y+h-.32,title,fontsize=12,weight='bold',va='top',color='#173d2c')
        ax.text(x+.18,y+h-.95,body,fontsize=10.5,va='top',linespacing=1.5,color='#294b3a')
    box(.4,5.6,4.0,2.2,'Tesla-Managed','Direct OEM relationship preference;\ncompare with qualified third parties.','#e0ece1')
    box(.4,1.1,4.0,2.5,'Certified Third-Party','Provider flexibility; potentially lower\ntotal cost needs matched bids.\nAlso feasible at high revenue exposure.','#ecf1e8')
    box(5.6,2.2,3.8,5.5,'Certified In-House','Mature internal service organization.\n\nFeasible across exposure levels;\nhigh exposure requires stronger\ncoverage and escalation.\n\nOutsourcing remains an option.','#dce9e1')
    ax.annotate('',xy=(4.8,8.1),xytext=(4.8,1),arrowprops=dict(arrowstyle='<->',color='#59755f',lw=1.4))
    ax.text(.5,9.25,'Higher exposure raises service requirements under EVERY delivery model',fontsize=11,color='#173d2c')
    fig.suptitle('Customer segmentation → service delivery options',fontsize=20,weight='bold',x=.52,y=.96,color='#163d2c')
    fig.text(.15,.035,'Conceptual hypotheses, not measured clusters or exclusive quadrants.\nOutsourced options overlap; placement does not rank uptime, cost or provider quality.',fontsize=10,color='#52625b')
    fig.subplots_adjust(left=.15,right=.96,top=.87,bottom=.19)
    fig.savefig(root/'figures/customer_segmentation.png',dpi=180);plt.close(fig)
if __name__=='__main__':main()
