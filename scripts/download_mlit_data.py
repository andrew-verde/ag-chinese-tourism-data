import os
import shutil
import urllib.request

links = [
    "https://www.mlit.go.jp/kankocho/content/001977799.pdf",
    "https://www.mlit.go.jp/kankocho/content/001842172.pdf",
    "https://www.mlit.go.jp/kankocho/content/001992596.pptx",
    "https://www.mlit.go.jp/kankocho/content/001977800.pdf",
    "https://www.mlit.go.jp/kankocho/content/001997857.xlsx",
    "https://www.mlit.go.jp/kankocho/content/001996091.pdf",
    "https://www.mlit.go.jp/kankocho/content/001992581.xls",
    "https://www.mlit.go.jp/kankocho/content/001992606.xlsx",
    "https://www.mlit.go.jp/kankocho/content/001992584.pdf",
    "https://www.mlit.go.jp/kankocho/content/001992588.xls",
    "https://www.mlit.go.jp/kankocho/content/001992600.xlsx",
    "https://www.mlit.go.jp/kankocho/content/001992864.pdf",
    "https://www.mlit.go.jp/kankocho/content/001974763.xls",
    "https://www.mlit.go.jp/kankocho/content/001974762.xlsx",
    "https://www.mlit.go.jp/kankocho/content/001974764.pdf",
    "https://www.mlit.go.jp/kankocho/content/001912042.xls",
    "https://www.mlit.go.jp/kankocho/content/001912044.xlsx",
    "https://www.mlit.go.jp/kankocho/content/001912245.pdf",
    "https://www.mlit.go.jp/kankocho/content/001912243.xlsx",
    "https://www.mlit.go.jp/kankocho/content/001912244.xlsx",
    "https://www.mlit.go.jp/kankocho/content/001897812.pdf",
    "https://www.mlit.go.jp/kankocho/content/001879064.xls",
    "https://www.mlit.go.jp/kankocho/content/001884192.pdf",
    "https://www.mlit.go.jp/kankocho/content/001879063.xlsx",
    "https://www.mlit.go.jp/kankocho/content/001856155.pdf",
    "https://www.mlit.go.jp/kankocho/content/001865541.xls",
    "https://www.mlit.go.jp/kankocho/content/001879118.pdf",
    "https://www.mlit.go.jp/kankocho/content/001879117.xlsx",
    "https://www.mlit.go.jp/kankocho/content/001856156.pdf",
    "https://www.mlit.go.jp/kankocho/content/001853638.xls",
    "https://www.mlit.go.jp/kankocho/content/001853632.pdf",
    "https://www.mlit.go.jp/kankocho/content/001854050.xlsx",
    "https://www.mlit.go.jp/kankocho/content/001854414.pdf",
    "https://www.mlit.go.jp/kankocho/content/001853728.pdf",
    "https://www.mlit.go.jp/kankocho/content/001908142.pdf",
    "https://www.mlit.go.jp/kankocho/content/001764512.xls",
    "https://www.mlit.go.jp/kankocho/content/001764508.pdf",
    "https://www.mlit.go.jp/kankocho/content/001854051.xlsx",
    "https://www.mlit.go.jp/kankocho/content/001764510.pdf",
    "https://www.mlit.go.jp/kankocho/content/001750936.xls",
    "https://www.mlit.go.jp/kankocho/content/001750938.pdf",
    "https://www.mlit.go.jp/kankocho/content/001750939.xlsx",
    "https://www.mlit.go.jp/kankocho/content/001750940.pdf",
    "https://www.mlit.go.jp/kankocho/content/001734816.xls",
    "https://www.mlit.go.jp/kankocho/content/001742979.pdf",
    "https://www.mlit.go.jp/kankocho/content/001734817.xlsx",
    "https://www.mlit.go.jp/kankocho/content/001734815.pdf",
    "https://www.mlit.go.jp/kankocho/content/001908145.pdf",
    "https://www.mlit.go.jp/kankocho/content/001908146.pdf",
    "https://www.mlit.go.jp/kankocho/content/001734822.xls",
    "https://www.mlit.go.jp/kankocho/content/001734824.pdf",
    "https://www.mlit.go.jp/kankocho/content/001734823.xlsx",
    "https://www.mlit.go.jp/kankocho/content/001734825.pdf",
    "https://www.mlit.go.jp/kankocho/content/001734828.xls",
    "https://www.mlit.go.jp/kankocho/content/810003967.pdf",
    "https://www.mlit.go.jp/kankocho/content/810003968.xlsx",
    "https://www.mlit.go.jp/kankocho/content/001734829.xls",
    "https://www.mlit.go.jp/kankocho/tokei_hakusyo/content/001633003.pdf",
    "https://www.mlit.go.jp/kankocho/tokei_hakusyo/content/001633186.xlsx",
    "https://www.mlit.go.jp/kankocho/tokei_hakusyo/content/001632946.pdf",
    "https://www.mlit.go.jp/kankocho/content/001734831.xls",
    "https://www.mlit.go.jp/kankocho/tokei_hakusyo/content/001615363.pdf",
    "https://www.mlit.go.jp/kankocho/tokei_hakusyo/content/001615302.pdf",
    "https://www.mlit.go.jp/kankocho/tokei_hakusyo/content/001597395.xls",
    "https://www.mlit.go.jp/kankocho/tokei_hakusyo/content/001609726.pdf",
    "https://www.mlit.go.jp/kankocho/tokei_hakusyo/content/001597740.pdf",
    "https://www.mlit.go.jp/kankocho/tokei_hakusyo/content/001597394.xls",
    "https://www.mlit.go.jp/kankocho/tokei_hakusyo/content/001602158.pdf",
    "https://www.mlit.go.jp/kankocho/tokei_hakusyo/content/001597835.pdf",
    "https://www.mlit.go.jp/kankocho/tokei_hakusyo/content/001597393.xls",
    "https://www.mlit.go.jp/kankocho/tokei_hakusyo/content/001579955.pdf",
    "https://www.mlit.go.jp/kankocho/tokei_hakusyo/content/001579954.pdf",
    "https://www.mlit.go.jp/kankocho/tokei_hakusyo/content/001597392.xls",
    "https://www.mlit.go.jp/kankocho/tokei_hakusyo/content/001514593.pdf",
    "https://www.mlit.go.jp/kankocho/tokei_hakusyo/content/001514594.pdf",
    "https://www.mlit.go.jp/kankocho/tokei_hakusyo/content/001597391.xls",
    "https://www.mlit.go.jp/kankocho/tokei_hakusyo/content/001488162.pdf",
    "https://www.mlit.go.jp/kankocho/tokei_hakusyo/content/001597391.xls",
    "https://www.mlit.go.jp/kankocho/content/001396416.pdf",
    "https://www.mlit.go.jp/kankocho/content/001396836.xls",
    "https://www.mlit.go.jp/kankocho/content/001354360.pdf",
    "https://www.mlit.go.jp/kankocho/content/001368175.xlsx",
    "https://www.mlit.go.jp/kankocho/content/001354358.pdf",
    "https://www.mlit.go.jp/kankocho/content/001335738.xls",
    "https://www.mlit.go.jp/kankocho/content/001345781.pdf",
    "https://www.mlit.go.jp/kankocho/content/001345783.xlsx",
    "https://www.mlit.go.jp/kankocho/content/001335741.pdf",
    "https://www.mlit.go.jp/kankocho/content/001350781.pdf",
    "https://www.mlit.go.jp/kankocho/content/001350782.pdf",
    "https://www.mlit.go.jp/kankocho/content/001335744.xls",
    "https://www.mlit.go.jp/kankocho/content/001345782.pdf",
    "https://www.mlit.go.jp/kankocho/content/001345784.xlsx",
    "https://www.mlit.go.jp/kankocho/content/001335747.pdf",
    "https://www.mlit.go.jp/kankocho/content/001335750.xls",
    "https://www.mlit.go.jp/kankocho/content/001323884.pdf",
    "https://www.mlit.go.jp/kankocho/content/001345785.xlsx",
    "https://www.mlit.go.jp/kankocho/content/001323885.pdf",
    "https://www.mlit.go.jp/kankocho/content/001315370.pdf",
]

def download(url, outdir):
    os.makedirs(outdir, exist_ok=True)
    filename = os.path.basename(url)
    outpath = os.path.join(outdir, filename)
    temp_path = outpath + ".tmp"
    backup_path = outpath + ".bak"

    if os.path.exists(outpath) and os.path.getsize(outpath) > 0:
        print(f"Already exists: {filename}")
        return

    try:
        print(f"Downloading {filename}...")
        urllib.request.urlretrieve(url, temp_path)
        if not os.path.exists(temp_path) or os.path.getsize(temp_path) == 0:
            print(f"Failed {filename}: downloaded file is empty")
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return
        if os.path.exists(outpath):
            shutil.copy2(outpath, backup_path)
            print(f"Backed up previous file: {backup_path}")
        os.replace(temp_path, outpath)
        print(f"Saved: {outpath}")
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        print(f"Failed {filename}: {e}")

if __name__ == '__main__':
    outdir = 'mlit_data'
    for url in links:
        download(url, outdir)
