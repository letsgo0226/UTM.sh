#!/bin/sh
# Portable form: prefers espeak-ng; falls back to legacy espeak (useful on iSH/older Alpine).
command -v tesseract>/dev/null||exit 2
if command -v espeak-ng>/dev/null;then E=espeak-ng;elif command -v espeak>/dev/null;then E=espeak;else exit 2;fi
d=$(mktemp -d)||exit 3;trap 'rm -rf "$d"' 0
for x in ./*;do [ -f "$x" ]||continue;m=$(file -Lb --mime-type "$x");case $m in application/pdf|image/*|text/*)echo "$x";;esac;done>"$d/F"
[ -s "$d/F" ]||exit 4;echo Files:;nl -ba "$d/F";printf 'File# ';read n;f=$(sed -n "$n p" "$d/F");[ -n "$f" ]||exit 5
tesseract --list-langs 2>/dev/null|sed '1d;/^osd$/d'>"$d/O";echo OCR-languages:;nl -ba "$d/O";printf 'OCR# ';read n;L=$(sed -n "$n p" "$d/O")
$E --voices 2>/dev/null|awk 'NR>1{print $2}'|sort -u>"$d/V";echo TTS-voices:;nl -ba "$d/V";printf 'TTS# ';read n;V=$(sed -n "$n p" "$d/V")
b=${f#./};b=${b%.ocr.txt};b=${b%.*};o=./$b.ocr.txt;w=./$b.ocr.wav;m=$(file -Lb --mime-type "$f");Z=1;Q=1;A=0;:>"$o"
if [ "$m" = application/pdf ];then command -v pdftoppm>/dev/null||exit 7;pdftoppm -r ${DPI:-250} -png "$f" "$d/p"||exit 8;set -- "$d"/p-*.png;elif [ "${m#image/}" != "$m" ];then set -- "$f";else cat "$f">"$o";set --;fi
P=0;for x;do P=$((P+1));echo OCR:$P;for s in 3 6 11;do tesseract "$x" "$d/$P.$s" -l "$L" --psm $s 2>/dev/null||exit 9;tr -s '[:space:]' ' '<"$d/$P.$s.txt">"$d/$P.$s.n";done;cmp -s "$d/$P.3.n" "$d/$P.6.n"&&cmp -s "$d/$P.3.n" "$d/$P.11.n"||Z=0;if cmp -s "$d/$P.3.n" "$d/$P.6.n"||cmp -s "$d/$P.3.n" "$d/$P.11.n";then q=3;elif cmp -s "$d/$P.6.n" "$d/$P.11.n";then q=6;else q=3;Q=0;A=$((A+1));fi;cat "$d/$P.$q.txt">>"$o";done
[ -s "$o" ]||exit 10;tr -s '[:space:]' ' '<"$o">"$d/t";$E -q -x -v "$V" -f "$o">"$d/a";$E -q -x -v "$V" -f "$d/t">"$d/b";cmp -s "$d/a" "$d/b"&&T=1||T=0;tr -s '[:space:]' ' '<"$d/a">"$d/c";tr -s '[:space:]' ' '<"$d/b">"$d/e";cmp -s "$d/c" "$d/e"&&U=1||U=0;$E -v "$V" -s ${RATE:-165} -p ${PITCH:-50} -w "$w" -f "$d/t"||exit 11
h(){ [ "$1" = 1 ]&&echo 0||echo '>0';};[ "$Z$T" = 11 ]&&S=true||S=false;[ "$Q$U" = 11 ]&&R=true||R=false
echo "TXT=$o WAV=$w";echo "OCR=$L TTS=$V ambiguous=$A";echo "H_ocr_strict=$(h $Z) H_tts_strict=$(h $T) H_ocr_task=$(h $Q) H_tts_task=$(h $U)";echo "zero_entropy_strict=$S zero_entropy_task=$R"
