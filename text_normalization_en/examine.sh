#!/usr/bin/env bash
types=(CARDINAL DATE MEASURE PLAIN)
keys=(\: \- no I st II dr No X V III CD vs mr Sun OF id sun IV x sr us SA mrs am AM VI Us op XI VIII VII XII \~ min)

declare -A patterns
pattern0=(\: to)
patterns[\:]=pattern0[@]

pattern1=(\- to)
patterns[\-]=pattern1[@]

pattern2=(no number)
patterns[no]=pattern2[@]

pattern3=(I one)
patterns[I]=pattern3[@]

pattern4=(saint street)
patterns[st]=pattern4[@]

pattern5=(two "the_second")
patterns[II]=pattern5[@]

pattern6=(doctor drive)
patterns[dr]=pattern6[@]

pattern7=(No number)
patterns[No]=pattern7[@]

pattern8=(X ten)
patterns[X]=pattern8[@]

pattern9=(V "the_fifth")
patterns[V]=pattern9[@]

pattern10=(three "third")
patterns[III]=pattern10[@]

pattern11=("c_d" "the_four_hundredth")
patterns[CD]=pattern11[@]

pattern12=(versus "v_s")
patterns[vs]=pattern12[@]

pattern13=(mister "m_r")
patterns[mr]=pattern13[@]

pattern14=(Sun sunday)
patterns[Sun]=pattern14[@]

pattern15=(OF "o_f")
patterns[OF]=pattern15[@]

pattern16=(id "i_d")
patterns[id]=pattern16[@]

pattern17=(sun sunday)
patterns[sun]=pattern17[@]

pattern18=("i_v" "the_fourth")
patterns[IV]=pattern18[@]

pattern19=(x by)
patterns[x]=pattern19[@]

pattern20=(senior "s_r")
patterns[sr]=pattern20[@]

pattern21=(us "u_s")
patterns[us]=pattern21[@]

pattern22=(SA "s_a")
patterns[SA]=pattern22[@]

pattern23=(mrs "m_r_s")
patterns[mrs]=pattern23[@]

pattern24=(am "a_m")
patterns[am]=pattern24[@]

pattern25=(AM "a_m")
patterns[AM]=pattern25[@]

pattern26=(VI "the_sixth")
patterns[VI]=pattern26[@]

pattern27=(Us "u_s")
patterns[Us]=pattern27[@]

pattern28=(op opus)
patterns[op]=pattern28[@]

pattern29=(XI "the_eleventh")
patterns[XI]=pattern29[@]

pattern30=(eight "the_eighth")
patterns[VIII]=pattern30[@]

pattern31=(seven "the_seventh")
patterns[VII]=pattern31[@]

pattern32=("twelve" "the_twelfth")
patterns[XII]=pattern32[@]

pattern33=(tilde to)
patterns[\~]=pattern33[@]

pattern34=(min minute)
patterns[min]=pattern34[@]

for k in "${keys[@]}" ; do
  # printf %s \"${!patterns[$k]}\"
  arr=(${!patterns[$k]})
  key0=$(sed "s/_/ /g" <<< ${arr[0]})
  key1=$(sed "s/_/ /g" <<< ${arr[1]})
  echo -e "${k}\t\t\t\t${key0} \t${key1}"
  for i in "${types[@]}" ; do
    for j in "${types[@]}" ; do
      var0=$(($(pcregrep -M "${i}.*?\n.*?\"${k}\",\"${key0}.*?\n.*?${j}" ./train/en_train.csv | wc -l)/ 3))
      var1=$(($(pcregrep -M "${i}.*?\n.*?\"${k}\",\"${key1}.*?\n.*?${j}" ./train/en_train.csv | wc -l)/ 3))
      echo -e "$i    \t$j    \t$var0\t$var1"
    done
  done
  echo ""
done
