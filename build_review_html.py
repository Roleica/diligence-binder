#!/usr/bin/env python3
"""生成滚轮翻页审核 HTML"""
import json, sys, time
from pathlib import Path
import fitz

# PyInstaller 路径适配
if getattr(sys, 'frozen', False):
    _BASE_DIR = Path(sys._MEIPASS)
else:
    _BASE_DIR = Path(__file__).parent

OUTPUT_DIR = _BASE_DIR / "output_items"
IMG_DIR = OUTPUT_DIR / "page_images"
IMG_DIR.mkdir(parents=True, exist_ok=True)

def collect_and_render():
    pdfs = []
    for d in sorted(OUTPUT_DIR.iterdir()):
        if not d.is_dir(): continue
        ij = d / "intermediate.json"
        if not ij.exists(): continue
        data = json.loads(ij.read_text(encoding="utf-8"))
        pdfs.append(data)
    total = 0
    for pdf_data in pdfs:
        pdf_path = None
        for item in pdf_data.get("items", []):
            fp = item.get("文件路径", "")
            if fp:
                c = _BASE_DIR / fp
                if c.exists(): pdf_path = c; break
        if not pdf_path: continue
        total_pages = len(doc := fitz.open(pdf_path))
        pages_needed = set(range(1, total_pages + 1))
        for pn in pages_needed:
            if pn < 1 or pn > len(doc): continue
            img_file = IMG_DIR / f"{pdf_data['pdf_name']}_p{pn}.jpg"
            if not img_file.exists():
                doc[pn-1].get_pixmap(dpi=120).save(str(img_file))
            total += 1
        doc.close()
    return pdfs, total


def build_html(pdfs):
    import re as re_m
    clean = []
    for pdf in pdfs:
        items = []
        for item in pdf.get("items", []):
            items.append({k: item.get(k, "") for k in [
                "页码","单据序号","单据类型","文件路径",
                "凭证编号","记账日期","公司名称","摘要","金额",
                "发票号码","开票日期","销售方名称","价税合计",
                "回单编号","交易日期","交易金额",
            ]})
        # Load page texts: use from passed data if available, else read from files
        page_texts = pdf.get("texts", {})
        if not page_texts:
            pages_dir = OUTPUT_DIR / pdf["pdf_name"] / "pages"
            if pages_dir.exists():
                for md_file in sorted(pages_dir.glob("p*_markdown.md")):
                    pn = int(md_file.stem.split("_")[0][1:])
                    raw = md_file.read_text(encoding="utf-8")
                    text = re_m.sub(r'<[^>]+>', ' ', raw)
                    text = re_m.sub(r'\s+', ' ', text).strip()
                    page_texts[str(pn)] = text
        clean.append({
            "pdf_name": pdf["pdf_name"],
            "total_pages": pdf.get("total_pages", 0),
            "items": items,
            "texts": page_texts,
        })

    data_json = json.dumps(clean, ensure_ascii=False)

    css = """*{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%;overflow:hidden}
body{font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;background:#1a1a2e}
#app{display:flex;height:100vh}
#sidebar{width:240px;min-width:240px;background:#1a1a2e;color:#aaa;overflow-y:auto;font-size:13px;height:100vh}
#sidebar h3{padding:12px 14px 8px;color:white;font-size:15px}
#sidebar .pdf-group{border-bottom:1px solid #2a2a4e}
#sidebar .pdf-name{padding:8px 14px;font-weight:bold;color:#ddd;cursor:pointer;font-size:13px;word-break:break-all}
#sidebar .pdf-name:hover{background:#2a2a5e}
#sidebar .page-item{padding:5px 14px 5px 26px;cursor:pointer;font-size:12px;color:#888;display:flex;justify-content:space-between}
#sidebar .page-item:hover{background:#2a2a5e;color:#ccc}
#sidebar .page-item.active{background:#e94560;color:white}
#sidebar .page-item.done{color:#34a853}
#sidebar .page-item.done.active{color:white}
#sidebar .page-item .status-dot{font-size:14px;margin-left:4px}
#sidebar .page-item .status-dot.done{color:#34a853}
#sidebar .page-item .status-dot.pending{color:#e94560}
#sidebar .progress-bar{height:3px;background:#333;margin:8px 14px;border-radius:2px;overflow:hidden}
#sidebar .progress-bar div{height:100%;background:#34a853;transition:width 0.3s}
#sidebar .progress-text{font-size:10px;color:#888;padding:0 14px 4px}
#sidebar .stats{padding:10px 14px;font-size:11px;color:#777;position:sticky;bottom:0;background:#1a1a2e;border-top:1px solid #333}
#scroller{flex:1;height:100vh;overflow-y:scroll}
.page-section{height:100vh;display:flex;background:#f0f2f5}
.page-section:nth-child(even){background:#e8eaed}
.page-left{flex:0 0 50%;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:10px;overflow:hidden}
.page-left .label-bar{width:100%;padding:6px 0;font-size:14px;color:#666;text-align:center;flex-shrink:0;font-weight:500}
.page-left .img-wrap{flex:1;display:flex;align-items:center;justify-content:center;overflow:hidden;width:100%}
.page-left img{max-width:100%;max-height:100%;object-fit:contain;box-shadow:0 2px 12px rgba(0,0,0,0.12);border-radius:3px}
.page-right{flex:1;overflow-y:auto;padding:20px 24px;display:flex;flex-direction:column;align-items:center;gap:14px}
.page-right .hint{font-size:13px;color:#aaa;margin-bottom:4px}
.doc-card{background:white;border-radius:8px;box-shadow:0 1px 4px rgba(0,0,0,0.08);overflow:hidden;flex-shrink:0;width:100%;max-width:680px}
.doc-card.V{border-left:5px solid #4a90d9}
.doc-card.I{border-left:5px solid #34a853}
.doc-card.B{border-left:5px solid #f5a623}
.doc-card.O{border-left:5px solid #999}
.doc-card-header{padding:10px 18px;background:#f8f9fa;font-size:15px;font-weight:bold;border-bottom:1px solid #eee;display:flex;align-items:center}
.doc-card-header .badge{font-size:12px;padding:2px 10px;border-radius:10px;color:white;margin-left:8px}
.badge.V{background:#4a90d9}.badge.I{background:#34a853}.badge.B{background:#f5a623}.badge.O{background:#999}
.doc-table{width:100%;border-collapse:collapse;font-size:16px}
.doc-table td{padding:9px 14px;border-bottom:1px solid #f0f0f0}
.doc-table td.lbl{width:95px;color:#777;font-size:14px;text-align:right;background:#fafafa;font-weight:500}
.doc-table td input{width:100%;border:1px solid #ddd;padding:7px 10px;border-radius:4px;font-size:16px;font-family:inherit}
.doc-table td input:focus{border-color:#1a73e8;outline:none;box-shadow:0 0 0 2px rgba(26,115,232,0.15)}
.doc-actions{padding:10px 18px;display:flex;gap:10px;justify-content:flex-end;border-top:1px solid #f0f0f0}
.doc-actions button{padding:6px 18px;border-radius:4px;border:none;cursor:pointer;font-size:14px}
.btn-save{background:#1a73e8;color:white}.btn-save.saved{background:#34a853}
.btn-delete{background:white;color:#e94560;border:1px solid #e94560!important}.btn-delete.del{color:#999;border-color:#ccc!important;text-decoration:line-through;background:#fafafa}
.doc-table td input:focus{border-color:#1a73e8;outline:none}
.doc-actions{padding:5px 12px;display:flex;gap:6px;justify-content:flex-end;border-top:1px solid #f0f0f0}
.doc-actions button{padding:2px 10px;border-radius:3px;border:none;cursor:pointer;font-size:10px}
.btn-save{background:#1a73e8;color:white}.btn-save.saved{background:#34a853}
.btn-undo{background:white;color:#e67700;border:1px solid #e67700!important}
.btn-delete{background:white;color:#e94560;border:1px solid #e94560!important}.btn-delete.del{color:#999;border-color:#ccc!important;text-decoration:line-through;background:#fafafa}
.ptypes{font-size:9px;color:#aaa;margin-left:2px;letter-spacing:1px}
.no-docs{padding:40px;text-align:center;color:#ccc;font-size:16px}
#topbar{position:fixed;top:0;right:0;z-index:100;padding:6px 16px;display:flex;gap:8px}
#topbar button{padding:7px 16px;border-radius:4px;border:none;cursor:pointer;font-size:14px;background:#e94560;color:white;font-weight:bold}
#topbar .pi{font-size:13px;padding:5px 10px;background:rgba(0,0,0,0.6);border-radius:4px;color:white}
.page-toolbar{display:flex;gap:8px;margin-bottom:6px;flex-wrap:wrap}
.page-toolbar button{padding:6px 14px;border-radius:4px;border:1px solid #ddd;cursor:pointer;font-size:13px;background:white}
.page-toolbar button:hover{background:#f0f0f0}
.page-toolbar button.add{background:#1a73e8;color:white;border-color:#1a73e8}
.text-panel{display:none;background:#fafafa;border:1px solid #e0e0e0;border-radius:6px;padding:12px;margin-bottom:8px;max-height:200px;overflow-y:auto}
.text-panel.show{display:block}
.text-panel pre{white-space:pre-wrap;font-size:13px;color:#555;margin:0;font-family:inherit;line-height:1.5}
.text-panel .copy-btn{float:right;font-size:12px;padding:3px 10px;cursor:pointer;background:#eee;border:1px solid #ccc;border-radius:3px}
.new-doc-select{display:none;gap:6px;align-items:center;padding:6px 0}
.new-doc-select.show{display:flex}
.new-doc-select select{padding:4px 10px;border-radius:3px;border:1px solid #ccc;font-size:13px}"""

    js_template = f"""<script>
var ALL_DATA={data_json};
var editState={{}};
try{{var s=localStorage.getItem("rv_snap");if(s)editState=JSON.parse(s)}}catch(e){{}}
function saveState(){{localStorage.setItem("rv_snap",JSON.stringify(editState));updateStats()}}
function esc(s){{return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;")}}

function renderAll(){{
  var nav=document.getElementById("sidebarNav"),sc=document.getElementById("scroller");
  var nh="",mh="";var pid=0,pl=[];
  ALL_DATA.forEach(function(pdf,pi){{
    var pm={{}};pdf.items.forEach(function(it){{var p=it.页码;if(!pm[p])pm[p]=[];pm[p].push(it)}});
    var totalP=pdf.total_pages||0;
    var pns=[];for(var p=1;p<=totalP;p++)pns.push(p);
    var dc=0;pns.forEach(function(p){{if(isDone(pdf.pdf_name,p,pm[p]||[]))dc++}});
    nh+='<div class="pdf-group"><div class="pdf-name" onclick="goPage(\\''+pi+'-'+pns[0]+'\\')">📄 '+pdf.pdf_name+' <span style="font-size:9px;color:#888">'+dc+'/'+pns.length+'</span></div>';
    // Progress bar for this PDF
    var pct=Math.round(dc/pns.length*100);
    nh+='<div class="progress-bar"><div style="width:'+pct+'%"></div></div>';
    nh+='<div class="progress-text">'+dc+'/'+pns.length+' 已审核 ('+pct+'%)</div>';
    pns.forEach(function(pn){{
      pid++;var sid=pi+'-'+pn,items=pm[pn]||[],done=isDone(pdf.pdf_name,pn,items);
      pl.push({{pi:pi,pn:pn,sid:sid}});
      var types=items.map(function(it){{return it.单据类型==='记账凭证'?'记':it.单据类型==='发票'?'发':'回'}}).filter(function(v,i,a){{return a.indexOf(v)===i}}).join('');
      var dot=done?'<span class="status-dot done">●</span>':'<span class="status-dot pending">●</span>';
      nh+='<div class="page-item'+(done?' done':'')+'" id="nv-'+sid+'" onclick="goPage(\\''+sid+'\\')">第'+pn+'页 <span class="ptypes">'+types+'</span> '+dot+'</div>';
      var is='page_images/'+pdf.pdf_name+'_p'+pn+'.jpg';
      var txt=(pdf.texts||{{}})[String(pn)]||"";
      mh+='<div class="page-section" id="sc-'+sid+'"><div class="page-left"><div class="label-bar">📄 '+pdf.pdf_name+' · 第'+pn+'页 ('+items.length+'单)</div><div class="img-wrap"><img src="'+is+'" loading="lazy" onerror="this.style.display=\\'none\\'"></div></div><div class="page-right"><div class="page-toolbar"><button onclick="toggleText(\\''+sid+'\\')">📋 页面文字</button><button class="add" onclick="showNewDoc(\\''+sid+'\\')">+ 新建单据</button></div><div class="new-doc-select" id="nds-'+sid+'"><select id="ndt-'+sid+'"><option value="记账凭证">记账凭证</option><option value="发票">发票</option><option value="银行回单">银行回单</option></select><button onclick="newDoc(\\''+pdf.pdf_name+'\\','+pn+',\\''+sid+'\\')">确认创建</button><button onclick="hideNewDoc(\\''+sid+'\\')">取消</button></div><div class="text-panel show" id="tp-'+sid+'"><button class="copy-btn" onclick="copyText(\\''+sid+'\\')">📋复制</button><pre>'+esc(txt)+'</pre></div><div class="hint">第'+pn+'页 · '+items.length+'个单据</div>';
      if(items.length===0){{mh+='<div class="no-docs">无单据</div>'}}
      else items.forEach(function(item,idx){{mh+=buildCard(pdf.pdf_name,pn,idx,item)}});
      mh+='</div></div>';
    }});
    nh+='</div>';
  }});
  document.getElementById("sidebarNav").innerHTML=nh;
  document.getElementById("scroller").innerHTML=mh;
  window._pl=pl;updateStats();
}}

function buildCard(pdfName,pn,idx,item){{
  var st=((editState[pdfName]||{{}})[pn]||{{}})[idx]||{{}};
  var del=st.deleted,sv=st.saved;
  var dt=item.单据类型,tc=dt==="记账凭证"?"V":dt==="发票"?"I":dt==="银行回单"?"B":"O";
  var fd=[];
  if(dt==="记账凭证")fd=[["凭证编号",item.凭证编号],["记账日期",item.记账日期],["公司名称",item.公司名称],["摘要",item.摘要],["金额",item.金额]];
  else if(dt==="发票")fd=[["发票号码",item.发票号码],["开票日期",item.开票日期],["销售方名称",item.销售方名称],["价税合计",item.价税合计]];
  else if(dt==="银行回单")fd=[["回单编号",item.回单编号],["交易日期",item.交易日期],["交易金额",item.交易金额]];
  else fd=[["备注",item.备注||""]];
  var rows=fd.map(function(f){{
    var l=f[0],v=f[1],ev=st[l]!==undefined?st[l]:v;
    var inp=del?"<s>"+esc(String(ev||""))+"</s>":"<input value=\\""+esc(String(ev||""))+"\\" onchange=\\"editField('"+pdfName+"',"+pn+","+idx+",'"+l+"',this.value)\\""+(sv?' style="background:#e8f5e9"':"")+">";
    return "<tr><td class=lbl>"+l+"</td><td>"+inp+"</td></tr>";
  }}).join("");
  return '<div class="doc-card '+tc+'" id="cd-'+pdfName+'-'+pn+'-'+idx+'"><div class="doc-card-header">#'+(idx+1)+'<span class="badge '+tc+'">'+dt+'</span></div><table class="doc-table">'+rows+'</table><div class="doc-actions"><button class="btn-save'+(sv?' saved':'')+'" onclick="saveItem(\\''+pdfName+'\\','+pn+','+idx+')">'+(sv?'✓已保存':'💾保存')+'</button>'+(sv?'<button class="btn-undo" onclick="undoSave(\\''+pdfName+'\\','+pn+','+idx+')">↩撤销</button>':'')+'<button class="btn-delete'+(del?' del':'')+'" onclick="deleteItem(\\''+pdfName+'\\','+pn+','+idx+')">'+(del?'已删除':'🗑删除')+'</button></div></div>';
}}

function editField(nm,pn,idx,f,v){{if(!editState[nm])editState[nm]={{}};if(!editState[nm][pn])editState[nm][pn]={{}};if(!editState[nm][pn][idx])editState[nm][pn][idx]={{}};editState[nm][pn][idx][f]=v;editState[nm][pn][idx].saved=false;saveState();updateSidebarItem(nm,pn,idx)}}
function saveItem(nm,pn,idx){{if(!editState[nm])editState[nm]={{}};if(!editState[nm][pn])editState[nm][pn]={{}};if(!editState[nm][pn][idx])editState[nm][pn][idx]={{}};editState[nm][pn][idx].saved=true;saveState();refreshCard(nm,pn,idx)}}
function undoSave(nm,pn,idx){{if(!editState[nm])editState[nm]={{}};if(!editState[nm][pn])editState[nm][pn]={{}};if(!editState[nm][pn][idx])editState[nm][pn][idx]={{}};editState[nm][pn][idx].saved=false;saveState();refreshCard(nm,pn,idx)}}
function deleteItem(nm,pn,idx){{if(!editState[nm])editState[nm]={{}};if(!editState[nm][pn])editState[nm][pn]={{}};if(!editState[nm][pn][idx])editState[nm][pn][idx]={{}};editState[nm][pn][idx].deleted=!editState[nm][pn][idx].deleted;saveState();refreshCard(nm,pn,idx)}}
function refreshCard(nm,pn,idx){{var pdf=ALL_DATA.find(function(p){{return p.pdf_name===nm}});if(!pdf)return;var item=pdf.items.find(function(it){{return it.页码===pn&&pdf.items.indexOf(it)===idx}});if(!item)item=pdf.items.filter(function(it){{return it.页码===pn}})[idx];if(!item)return;var old=document.getElementById("cd-"+nm+"-"+pn+"-"+idx);if(!old)return;var tmp=document.createElement("div");tmp.innerHTML=buildCard(nm,pn,idx,item);var neu=tmp.firstChild;old.parentNode.replaceChild(neu,old);updateStats();updateSidebarItem(nm,pn,idx)}}
function updateSidebarItem(nm,pn,idx){{var pdf=ALL_DATA.find(function(p){{return p.pdf_name===nm}});if(!pdf)return;var pi=ALL_DATA.indexOf(pdf);var sid=pi+'-'+pn;var nv=document.getElementById("nv-"+sid);if(!nv)return;var pm={{}};pdf.items.forEach(function(it){{var p=it.页码;if(!pm[p])pm[p]=[];pm[p].push(it)}});var done=isDone(nm,pn,pm[pn]||[]);if(done){{nv.classList.add("done")}}else{{nv.classList.remove("done")}}var types=(pm[pn]||[]).map(function(it){{return it.单据类型==='记账凭证'?'记':it.单据类型==='发票'?'发':'回'}}).filter(function(v,i,a){{return a.indexOf(v)===i}}).join('');var dot=done?'<span class=\"status-dot done\">●</span>':'<span class=\"status-dot pending\">●</span>';nv.innerHTML='第'+pn+'页 <span class=\"ptypes\">'+types+'</span> '+dot;
// Update progress for this PDF group
var pns=Object.keys(pm).map(Number).sort(function(a,b){{return a-b}});var dc=0;pns.forEach(function(p){{if(isDone(nm,p,pm[p]||[]))dc++}});var pct=Math.round(dc/pns.length*100);var allBars=document.querySelectorAll(".progress-bar div");var allTexts=document.querySelectorAll(".progress-text");if(allBars[pi]){{allBars[pi].style.width=pct+"%"}}if(allTexts[pi]){{allTexts[pi].textContent=dc+"/"+pns.length+" 已审核 ("+pct+"%)"}}updateStats()}}
function goPage(sid){{var el=document.getElementById("sc-"+sid);if(el)el.scrollIntoView({{behavior:"smooth"}})}}
function toggleText(sid){{var el=document.getElementById("tp-"+sid);el.classList.toggle("show")}}
function copyText(sid){{var el=document.getElementById("tp-"+sid);if(!el)return;var txt=el.querySelector("pre").textContent;navigator.clipboard.writeText(txt).then(function(){{alert("已复制")}})["catch"](function(){{prompt("请手动复制:",txt)}})}}
function showNewDoc(sid){{document.getElementById("nds-"+sid).classList.add("show")}}
function hideNewDoc(sid){{document.getElementById("nds-"+sid).classList.remove("show")}}
function newDoc(nm,pn,sid){{var type=document.getElementById("ndt-"+sid).value;var pdf=ALL_DATA.find(function(p){{return p.pdf_name===nm}});if(!pdf)return;var newItem={{"页码":pn,"单据类型":type,"凭证编号":"","记账日期":"","公司名称":"","摘要":"","金额":"","发票号码":"","开票日期":"","销售方名称":"","价税合计":"","回单编号":"","交易日期":"","交易金额":""}};pdf.items.push(newItem);var idx=(pdf.items.filter(function(it){{return it.页码===pn}})||[]).length-1;renderAll();setTimeout(function(){{var el=document.getElementById("sc-"+sid);if(el)el.scrollIntoView({{behavior:"smooth"}})}},100)}}
function isDone(nm,pn,items){{var st=(editState[nm]||{{}})[pn]||{{}};var nd=items.filter(function(_,i){{return!(st[i]||{{}}).deleted}});return nd.length>0&&nd.every(function(_){{return(st[items.indexOf(_)]||{{}}).saved}})}}
function updateStats(){{var t=0,d=0;ALL_DATA.forEach(function(pdf){{var pm={{}};pdf.items.forEach(function(it){{pm[it.页码]=true}});Object.keys(pm).forEach(function(pn){{t++;var itms=pdf.items.filter(function(it){{return it.页码===parseInt(pn)}});if(isDone(pdf.pdf_name,parseInt(pn),itms))d++}});}});document.getElementById("stats").textContent=d+"/"+t+" 已审核"}}

var sc=document.getElementById("scroller"),ticking=false;
sc.addEventListener("scroll",function(){{if(!ticking){{requestAnimationFrame(function(){{var secs=document.querySelectorAll(".page-section");var best=null,bd=Infinity;secs.forEach(function(s){{var r=s.getBoundingClientRect();var d=Math.abs(r.top);if(d<bd){{bd=d;best=s}}}});if(best){{var sid=best.id.replace("sc-","");document.querySelectorAll(".page-item.active").forEach(function(el){{el.classList.remove("active")}});var nv=document.getElementById("nv-"+sid);if(nv){{nv.classList.add("active");nv.scrollIntoView({{block:"nearest"}})}}document.getElementById("pi").textContent="第 "+(Array.from(secs).indexOf(best)+1)+"/"+secs.length+" 页"}}ticking=false}});ticking=true}}}});

function exportFinal(){{
  var rows=[];ALL_DATA.forEach(function(pdf){{var pageItems={{}};pdf.items.forEach(function(item){{var p=item.页码;if(!pageItems[p])pageItems[p]=[];pageItems[p].push(item)}});Object.keys(pageItems).forEach(function(pn){{pageItems[pn].forEach(function(item,localIdx){{var st=((editState[pdf.pdf_name]||{{}})[pn]||{{}})[localIdx]||{{}};if(st.deleted)return;var gv=function(f){{return st[f]!==undefined&&st[f]!==null?st[f]:(item[f]||"")}};var V=item.单据类型==="记账凭证",I=item.单据类型==="发票",B=item.单据类型==="银行回单";rows.push({{"文件名":pdf.pdf_name,"页码":item.页码,"单据类型":item.单据类型,"凭证编号":V?gv("凭证编号"):"","记账日期":V?gv("记账日期"):"","公司名称":V?gv("公司名称"):"","摘要":V?gv("摘要"):"","金额":V?gv("金额"):"","发票号码":I?gv("发票号码"):"","开票日期":I?gv("开票日期"):"","销售方名称":I?gv("销售方名称"):"","价税合计":I?gv("价税合计"):"","回单编号":B?gv("回单编号"):"","交易日期":B?gv("交易日期"):"","交易金额":B?gv("交易金额"):""}})}});}});}});if(rows.length===0){{alert("无数据");return}}
  var hdrs=Object.keys(rows[0]);var csv="\\uFEFF"+hdrs.join(",")+"\\r\\n";
  rows.forEach(function(r){{csv+=hdrs.map(function(h){{return "\\""+String(r[h]||"").replace(/"/g,"\\"\\"")+"\\""}}).join(",")+"\\r\\n"}});
  var b=new Blob([csv],{{type:"text/csv;charset=utf-8;"}});var u=URL.createObjectURL(b);var a=document.createElement("a");a.href=u;a.download="审核结果.csv";document.body.appendChild(a);a.click();document.body.removeChild(a);setTimeout(function(){{URL.revokeObjectURL(u)}},200);
}}

renderAll();
</script>"""

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>凭证审核</title>
<style>{css}</style>
</head>
<body>

<div id="app">
  <div id="sidebar">
    <h3>📑 凭证目录</h3>
    <div id="sidebarNav"></div>
    <div class="stats" id="stats"></div>
  </div>
  <div id="scroller"></div>
</div>

<div id="topbar">
  <span class="pi" id="pi">-</span>
  <button onclick="exportFinal()">📥 导出Excel</button>
</div>

{js_template}
</body>
</html>"""

    return html


def main():
    print("生成滚轮翻页审核 HTML...")
    pdfs, img_count = collect_and_render()
    print(f"  {len(pdfs)} PDFs / {img_count} 页面图片")

    html = build_html(pdfs)
    out = OUTPUT_DIR / "审核页面.html"
    out.write_text(html, encoding="utf-8")
    print(f"  生成: {out} ({len(html)} 字符)")


if __name__ == "__main__":
    main()
