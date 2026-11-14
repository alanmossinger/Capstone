from xml.sax.saxutils import escape as esc
W=[2500,2760,4100]
MAR='<w:tcMar><w:top w:w="40" w:type="dxa"/><w:left w:w="80" w:type="dxa"/><w:bottom w:w="40" w:type="dxa"/><w:right w:w="80" w:type="dxa"/></w:tcMar>'
def run(t,b=False,i=False,color=None,sz=None,mono=False):
    rp=''
    if mono: rp+='<w:rFonts w:ascii="Consolas" w:eastAsia="Consolas" w:hAnsi="Consolas" w:cs="Consolas"/>'
    if b: rp+='<w:b/><w:bCs/>'
    if i: rp+='<w:i/><w:iCs/>'
    if color: rp+=f'<w:color w:val="{color}"/>'
    if sz: rp+=f'<w:sz w:val="{sz}"/><w:szCs w:val="{sz}"/>'
    return f'<w:r>{"<w:rPr>"+rp+"</w:rPr>" if rp else ""}<w:t xml:space="preserve">{esc(t)}</w:t></w:r>'
def rich(t,sz=None,color=None,bold=False):
    import re
    out='';B=bold;I=False
    for part in re.split(r'(\*\*|\*|`.+?`)',t):
        if not part: continue
        if part=='**': B=not B
        elif part=='*': I=not I
        elif part.startswith('`'): out+=run(part[1:-1],mono=True,sz=(sz or 19),color=color)
        else: out+=run(part,sz=sz,color=color,b=B,i=I)
    return out
def para(t,ppr=''): return f'<w:p>{"<w:pPr>"+ppr+"</w:pPr>" if ppr else ""}{rich(t)}</w:p>'
def cell(t,w,fill=None,span=None,color=None,bold=False,keep=False):
    tp=f'<w:tcW w:w="{w}" w:type="dxa"/>'
    if span: tp+=f'<w:gridSpan w:val="{span}"/>'
    if fill: tp+=f'<w:shd w:val="clear" w:color="auto" w:fill="{fill}"/>'
    tp+=MAR+'<w:vAlign w:val="center"/>'
    ps=''.join(f'<w:p><w:pPr>{"<w:keepNext/>" if keep else ""}<w:spacing w:before="40" w:after="40"/></w:pPr>{rich(x,sz=17,color=color,bold=bold)}</w:p>' for x in t.split('\n'))
    return f'<w:tc><w:tcPr>{tp}</w:tcPr>{ps}</w:tc>'
def row(cells,header=False):
    return f'<w:tr><w:trPr><w:cantSplit/>{"<w:tblHeader/>" if header else ""}</w:trPr>{"".join(cells)}</w:tr>'
def table(rows):
    x='<w:tbl><w:tblPr><w:tblW w:w="9360" w:type="dxa"/><w:tblBorders>'+''.join(f'<w:{s} w:val="single" w:sz="4" w:space="0" w:color="BFBFBF"/>' for s in ['top','left','bottom','right','insideH','insideV'])+'</w:tblBorders><w:tblLayout w:type="fixed"/><w:tblCellMar><w:left w:w="10" w:type="dxa"/><w:right w:w="10" w:type="dxa"/></w:tblCellMar><w:tblLook w:val="0000" w:firstRow="0" w:lastRow="0" w:firstColumn="0" w:lastColumn="0" w:noHBand="0" w:noVBand="0"/></w:tblPr><w:tblGrid>'+''.join(f'<w:gridCol w:w="{w}"/>' for w in W)+'</w:tblGrid>'
    x+=row([cell(h,w,fill='1F3864',color='FFFFFF',bold=True) for h,w in zip(['Dataset and source','What it holds','Why the project used it'],W)],header=True)
    for r in rows:
        if isinstance(r,str): x+=row([cell(r,9360,fill='D9E2F3',span=3,bold=True,keep=True)])
        else: x+=row([cell(c,w) for c,w in zip(r,W)])
    return x+'</w:tbl>'

ROWS=[
"A. The interconnection queue — the power-side candidates and the completion models",
("**N1. LBNL *Queued Up*, 2025 edition** — project-level data file, requests through the end of 2024.\nLawrence Berkeley National Laboratory (Rand et al., 2025). emp.lbl.gov/queues",
 "One row per interconnection request in U.S. queues: 36,441 requests, 31 fields — entry, agreement, withdrawal and operation dates, region, state and county, technology, capacity, status.",
 "The study population. It is the only public, national, project-level record of the queues, so every completion and timing model is fitted and tested on it (13,366 requests in CAISO, ERCOT and PJM for the timing models; all regions for the “ever built” classifier). The release is frozen, so no registered result can move with a later download."),
("**N2. LBNL *Queued Up*, 2024 edition** — data file, requests through the end of 2023 (revision r1, August 2024).\nLawrence Berkeley National Laboratory. emp.lbl.gov/queues",
 "The same project-level record one edition earlier.",
 "It is what was public on the decision date, 1 January 2025. With N3 it fixes what a committee could have read that day, so the candidates are chosen without hindsight. No model is fitted on it."),
("**N3. ERCOT Generation Interconnection Status reports**, the eight monthly reports of April–November 2024.\nERCOT. ercot.com/gridinfo/resource",
 "Every request in ERCOT’s queue in each month: size, technology, study phase and whether the interconnection agreement is signed.",
 "The candidate universe on the decision date: the 1,441 live requests of 20 MW and more from which the twenty power candidates are drawn, and the agreement status each one’s chance of operating is conditioned on."),
("**N4. LBNL *Queued Up*, 2026 edition** — data file, requests through the end of 2025.\nLawrence Berkeley National Laboratory with GridTracker (Rand et al., 2026); CC BY 4.0. emp.lbl.gov/queues",
 "38,201 requests, 30 fields, plus the edition’s published summary sheets.",
 "Outcomes only: reconciling the two editions, the check of the models in MISO and SPP (criteria C13–C14), and what happened to the queue in 2025 for the one-year-on check. No registered model is fitted or scored on it."),
("**N5. The ISOs’ own queue files**, snapshots of October 2026: CAISO public queue report, PJM queue export, ERCOT GIS report.\ncaiso.com, pjm.com, ercot.com (CAISO read with `gridstatus` 0.36.0)",
 "2,278 CAISO requests, 9,263 PJM queue positions and 1,996 ERCOT requests, with study-phase and agreement fields the LBNL file does not carry.",
 "To measure which milestones after entry the ISOs’ files can date for the 2017–2019 test cohort, before any of them was allowed into the two-years-in (landmark) model."),
("**N6. EIA-860M, inventory of operable generators**, July 2026.\nU.S. Energy Information Administration, API v2. eia.gov/electricity/data/eia860m",
 "28,324 operable generators: plant, technology, capacity, operating month, county, coordinates, balancing authority.",
 "The operating fleet the queue is compared with: the map, the crosswalk from EIA technologies to LBNL types, the test of whether EIA operating dates can fill the dates LBNL lacks, the generators behind the Texas plants, and installed capacity by state for capacity factors (with N18)."),
("**N7. Cartographic boundary files, 2020** — counties and states, 1:20,000,000.\nU.S. Census Bureau. census.gov",
 "County and state outlines.",
 "The LBNL file gives a county code for 91% of requests and no coordinates; the county is the finest position the public data allow, so these files place each request on the map (Figure E1)."),
"B. Oil and gas — the lease-side candidates",
("**N8. BSEE OGOR-A production**, 2010–2024, one file per year (2025 kept apart).\nBureau of Safety and Environmental Enforcement. data.bsee.gov",
 "Monthly oil, gas and water volumes and days on production per well completion on federal offshore leases, with lease, operator and area; 203,963 lease-months once summed to leases.",
 "The only public lease-level production record. It gives the twenty lease candidates, the output forecasts and the decline baseline against which each redevelopment is valued. The 2025 file is read only by the post-hoc forward check."),
("**N9. WTI Cushing and Henry Hub spot prices**, monthly.\nU.S. Energy Information Administration. eia.gov/dnav",
 "Monthly averages of daily spot prices: oil in $/bbl from 1986, gas in $/MMBtu from 1997.",
 "The prices that turn lease output into revenue and set the gas plant’s fuel cost; two of the three price series in the forecast contests and in the 2,000 scenarios."),
"C. The Texas power market and its plants",
("**N10. ERCOT day-ahead settlement point prices**, hourly, 2018–2024 (2025 kept apart).\nERCOT public market information. ercot.com/mktinfo",
 "Hourly day-ahead prices at ERCOT’s hubs and load zones.",
 "The third price series of the forecasts and scenarios, and the hourly 2024 basis on which every power candidate is valued. The 2025 file is read only by the post-hoc forward check."),
("**N11. ERCOT hourly wind and solar generation**, 2024.\nERCOT, read with `gridstatus`. ercot.com",
 "System-wide wind and solar output in each hour of 2024.",
 "Capture prices: what solar and wind actually earn against the flat hub price (92% and 83%), measured instead of assumed."),
("**N12. EIA-923 plant generation, Texas**, monthly, 2018–2024.\nU.S. Energy Information Administration, API v2. eia.gov/electricity/data/eia923",
 "186,744 rows of net generation and fuel use by plant, fuel and prime mover.",
 "The plant-output forecast contests — the one place where machine learning beat the baselines — and the observed output behind the plant features."),
("**N13. eGRID2023 plant file** (revision 1, January 2025).\nU.S. Environmental Protection Agency. epa.gov/egrid",
 "For each plant: CO₂ rate (lb/MWh), heat rate, capacity factor, primary fuel, coordinates.",
 "Emission factors for the optimizer’s emissions cap on the gas plants. They are used as rates, not as forecasts."),
"D. Valuation inputs — what a plant costs and earns",
("**N14. NREL Annual Technology Baseline 2024** (v3).\nNational Renewable Energy Laboratory. atb.nrel.gov",
 "Capital cost, fixed and variable operating cost and heat rate by technology and year.",
 "The public cost basis for a new plant: the company’s own costs are not public, so every plant is valued on the ATB’s Moderate scenario."),
("**N15. LBNL interconnection cost data, PJM** (2023).\nLawrence Berkeley National Laboratory. emp.lbl.gov",
 "Interconnection cost estimates in $/kW for 1,127 PJM projects, by study.",
 "The cost of the grid connection itself, which the ATB does not carry, in the plant valuation of Part I."),
("**N16. ICE daily hub prices**, 2017–2025, as republished by EIA.\nU.S. Energy Information Administration. eia.gov/electricity/wholesale",
 "Daily traded on-peak electricity prices by hub.",
 "Hub prices for the three-region valuation of Part I, and the ERCOT North price for the years before the hourly files begin."),
("**N17. *2024 State of the Market Report for PJM*, Section 5.**\nMonitoring Analytics (2025). monitoringanalytics.com",
 "Capacity-market revenue by year and capacity ratings by technology class.",
 "Capacity revenue, which decides the value of gas and storage in PJM."),
("**N18. EIA annual net generation by state and fuel**, 2024.\nU.S. Energy Information Administration, API v2. eia.gov/opendata",
 "Annual generation by state and energy source.",
 "With installed capacity from N6, the capacity factor each technology actually achieves in each state."),
("**N19. Consumer Price Index, CPI-U**, monthly, 2016–2024 (series CUUR0000SA0).\nU.S. Bureau of Labor Statistics. bls.gov",
 "The all-items index for urban consumers.",
 "One dollar year. Prices are put in 2024 dollars and the ATB’s 2022-dollar costs are converted with it (ratio 1.08)."),
("**N20. IRS Notice 2025-42.**\nU.S. Department of the Treasury. irs.gov",
 "A rule text, not a data table: when construction is taken to begin for the wind and solar tax credits.",
 "The dates behind the tax-credit cases — today’s credits, and the 2027 deadline run as a stress."),
]
head=('<w:p><w:pPr><w:pStyle w:val="Heading2"/></w:pPr><w:bookmarkStart w:id="9001" w:name="_Toc_AppendixN"/>'
      +run('Appendix N — The datasets used, and why')+'<w:bookmarkEnd w:id="9001"/></w:p>')
body=head
body+=para("The project reads twenty sources, and every one is public. This appendix lists each of them once: what it holds and why the project needed it. They fall into four groups that follow the decision — the queue requests that become the power candidates, the leases that become the oil and gas candidates, the Texas market both are sold into, and the costs and revenues that turn a forecast into a value. Each row names the publisher and where the file is published; how to obtain each file, its terms of use and its known limits are in `data/README.md`, and notebook 01 loads and checks them.")
body+=table(ROWS)
body+='<w:p><w:pPr><w:spacing w:after="240"/></w:pPr>'+run("Table N1. Every dataset the project read, what it holds and why it was used. N1–N7 serve the queue models and the map, N8–N9 the leases, N10–N13 the Texas market and N14–N20 the valuation.",i=True,color='595959',sz=18)+'</w:p>'
body+=para("**Three rules governed how the data were used.** *One decision date.* Only what was public on 1 January 2025 may choose or value a candidate, which is why three editions of the LBNL file appear: the 2024 edition and ERCOT’s 2024 reports say what a committee could see, the 2025 edition trains and tests the models, and the 2026 edition is read only for outcomes. The 2025 production and price files are stored in a separate folder so that no training table can read them. *Fixed files.* Each raw file is recorded with its SHA-256 hash in `data/raw_manifest.csv` (111 files) and is never edited; the notebooks stop if a file on disk is not the one recorded. *Labelled numbers.* Every dollar figure built from these sources carries its provenance — OBSERVED, DERIVED, FORECAST or ASSUMED.")
body+=para("**What the public data do not hold.** Redevelopment costs of the leases and the company’s own plant costs are not public, so they are assumptions with stated ranges (Appendix K.3.3). The LBNL file has no coordinates, and it dates operation and withdrawal reliably only in CAISO, ERCOT and PJM. The offshore record covers federal leases only, and its prices are hub benchmarks, not realized prices. The sources describe projects, plants, leases and markets; none describes individual people.")
body+=para("**Terms.** The federal sources (EIA, BSEE, EPA, NREL, the Census Bureau, BLS, the IRS) are public-domain or public U.S. Government works; the LBNL 2026 file is licensed CC BY 4.0; the ISO and market-monitor files are public under their publishers’ terms of use. Raw files are not redistributed with the repository; derived tables, results and figures are, with citation.")
idx=('<w:p><w:pPr><w:pStyle w:val="ListParagraph"/><w:numPr><w:ilvl w:val="0"/><w:numId w:val="9"/></w:numPr><w:spacing w:after="80"/></w:pPr>'
     +run('Appendix N — The datasets used, and why',b=True)+run(': the twenty public sources the project read, what each holds and why it was needed, with the rules that governed their use.')+'</w:p>')
import zipfile,sys,hashlib
SRC,DST=sys.argv[1],sys.argv[2]
zin=zipfile.ZipFile(SRC)
x=zin.read('word/document.xml').decode('utf8')
a='and what a board should require before real use.</w:t></w:r></w:p>'
assert x.count(a)==1; x=x.replace(a,a+idx)
import re
m=re.search(r'<w:p [^>]*><w:pPr><w:pStyle w:val="Heading2"/></w:pPr><w:bookmarkStart w:id="14" w:name="_Toc244535013"/><w:r><w:t>References',x)
assert m; x=x[:m.start()]+body+x[m.start():]
data=x.encode('utf8')
with zipfile.ZipFile(DST,'w',zipfile.ZIP_DEFLATED) as zout:
    for it in zin.infolist():
        if it.is_dir(): continue
        zout.writestr(it, data if it.filename=='word/document.xml' else zin.read(it.filename), compress_type=zipfile.ZIP_DEFLATED)
print('doc sha', hashlib.sha256(data).hexdigest())
assert zipfile.ZipFile(DST).testzip() is None
