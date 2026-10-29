# 資料のテキストを、助成金ごとの1ファイルにまとめる（bots/seibi.<番号>.txt）
import os,re,sys,glob,unicodedata
S=sys.argv[1]; OUT=sys.argv[2]
NAMES={"01":"スポットワーカー","02":"外国人労働者","03":"副業・兼業","04":"採用力強化","05":"就職チャレンジ","06":"業務改善・賃上げ(A)","07":"業務改善・賃上げ(B)","08":"人への投資"}
SKIP={"01":["（様式第１号）　申込書","（様式第４号）　交付申請兼完了実績報告書"]}  # 記載例があるので空の様式は省く
MASK=[("0776-20-0390","（記入例の電話番号）"),("rousei@pref.fukui.lg.jp","（記入例のメール）"),("xxxx-yyy@zzz.ne.jp","（記入例のメール）")]
def label(fn):
    b=fn
    for k,v in [("交付事務マニュアル","交付事務マニュアル"),("交付要領","交付要領"),("支給要綱","支給要綱"),("チラシ","チラシ"),("Ｑ＆Ａ","Q&A"),("チェックリスト","提出書類チェックリスト"),("計算シート","補助対象経費計算シート")]:
        if k in b:
            kind = re.search(r"（[^）]*型）", b)  # 「チラシ（一般型）」「チラシ（その他型）」のように種類があれば残す
            return ("記載例 " if "記載例" in b else "")+v+(kind.group(0) if kind else "")
    m=re.search(r"様式[第]?\s*([0-9０-９１-９・]+)",b)
    name=re.sub(r"^[0-9_ ]+","",b)
    name=re.sub(r"[（(]R8[^）)]*[）)]|R8_?|v$","",name).strip()
    return name
def clean(t):
    for a,b in MASK: t=t.replace(a,b)
    out=[]
    for line in t.splitlines():
        if re.search(r"[･・.]{6,}",line): continue   # 目次の点線
        line=re.sub(r"[ 　]{3,}","  ",line).rstrip()
        line=re.sub(r"(?<=[^\x00-\x7f]) (?=[^\x00-\x7f ])","",line)  # 1文字ずつ空白が入った PDF をつなぐ
        if not line.strip(): continue
        out.append(line)
    return "\n".join(out)
for n,short in NAMES.items():
    parts=[]
    files=sorted(glob.glob(f"{S}/{n}/txt/*.txt"),key=lambda f:(0 if re.search("要領|要綱",f) else 1 if "チラシ" in f else 2 if "Ｑ＆Ａ" in f else 3 if "マニュアル" in f else 4, f))
    for f in files:
        b=os.path.basename(f)[:-4]
        if b in SKIP.get(n,[]): continue
        parts.append(f"=== {short}｜{label(b)} ===\n{clean(open(f,encoding='utf-8').read())}")
    open(f"{OUT}/seibi.{n}.txt","w",encoding="utf-8").write("\n\n".join(parts)+"\n")
    print(n,len(open(f"{OUT}/seibi.{n}.txt",encoding='utf-8').read()),[p.split(' ===')[0][4:] for p in parts])
