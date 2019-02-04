Loop, 7
{
    if(A_Index == 1) {
		Run, http://ebird.org/ebird/alert/summary?sid=SN10387 ; TX
	}
	if(A_Index == 2) {
		Run, http://ebird.org/ebird/alert/summary?sid=SN10380 ; OK
	}
	if(A_Index == 3) {
		Run, http://ebird.org/ebird/alert/summary?sid=SN10376 ; NM
	}
	if(A_Index == 4) {
		Run, http://ebird.org/ebird/alert/summary?sid=SN10349 ; CO
	}
	if(A_Index == 5) {
		Run, http://ebird.org/ebird/alert/summary?sid=SN10360 ; KS
	}
	if(A_Index == 6) {
		Run, http://ebird.org/ebird/alert/summary?sid=SN10346 ; AR
	}
	if(A_Index == 7) {
		Run, http://ebird.org/ebird/alert/summary?sid=SN10362 ; LA
	}
	Sleep, 10000
	Send, ^a
	Sleep, 500
	Send, ^c
	Sleep, 500
	Send, ^w
	Run, C:\Users\Caleb\Documents\Python\eBirdLiferAlert\raw.txt
	Sleep, 3000
	Send, ^{End}
	Send, ^v
	Sleep, 500
	Send, ^s
	Send, !{F4}
}