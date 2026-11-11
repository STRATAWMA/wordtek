# Berkas sumber

| Berkas | Asal |
|---|---|
| `model.mct` | ekspor MCT awal dari pengguna (`6052454f-B100.mct`) |
| `new.mct` | ekspor MCT setelah beban dimasukkan (`2cec71e8-B100_NEW.mct`) |

Keduanya dibutuhkan pipeline dan tidak boleh dihapus:

```
parse.py   model.mct -> geom.json          (geometri)
calc.py    -> res.json                     (perhitungan pembebanan)
build.py   new.mct  -> fix.json            (model terkoreksi)
final.py   -> B100_FINAL / _1_STRUKTUR / _2_BEBAN.mct
xls.py     -> Pembebanan_Jembatan_Rangka_100m.xlsx
audit.py   cek zona satuan tiap blok MCT
verify2.py analisis rangka 3D + cek kekuatan, membaca B100_FINAL.mct saja
cmp.py     bandingkan gaya batang hasil verify2 dengan hasil midas
cmp_norl.py  sama, tetapi rigid link dipaksa nonaktif (uji hipotesis)
```
