echo "This will get the data from the web"
echo "How far back do you want to go? Format: -#ofdateunits dateunits \n ie -5 month"
read INPUT
DATE="$(date -d "$INPUT" +%F)"
echo $DATE
echo $DATE
NEWDATE="$(echo $DATE )"
echo $NEWDATE
#mkdir data_in
#./get_list.tcl
#javac get_data.java
#java get_data symbol.list $NEWDATE data_in
#python3 rsi_macro.py symbol.list data_in 14
echo >> config.txt
CONFIG="$(cat config.txt)"
NEWCONFIG="$(echo $CONFIG)" 
echo $NEWCONFIG
python3 -c "import rsi_sim_macro; rsi_sim_macro.main('symbol.list', 'data_in', $NEWCONFIG )" 
