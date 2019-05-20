all: db allplots
	#done

test:
	for field in 0 1 2 3 4 5; do\
		echo "MapF0$$field \bE07.fits"; \
		echo "bla!" ; \
	done

db:
	echo "db"
	rm SfSim_20110601.db
	python db_create.py
	python sim.py

sfind:
	#sfind
	for field in 0 1 2 3 4 5 6 7 8 9; do\
		sfind in=~/DATA/SfSim/MapF0$${field}E07.mir options=psfsize logfile=sfind_raw.cat alpha=0.5 rmsbox=4800 ;\
		grep -v 'NaN' sfind_raw.cat > sfind_F0$${field}E07.cat ;\
		rm sfind_raw.cat ;\
		python db_ingest.py -s sfind -c sfind_F0$${field}E07.cat -m MapF0$${field}E07.mir ;\
		python db_xmatch.py -s sfind -f $$field ;\
	done

sex:
	#sex
	for field in 0 1 2 3 4 5 6 7 8 9; do\
		sex -c DetectNSigma.sex -THRESH_TYPE ABSOLUTE -DETECT_THRESH 125e-6 -ANALYSIS_THRESH 75e-6 -CATALOG_NAME sex_F0$${field}E07.cat ~/DATA/SfSim/MapF0$${field}E07.fits ;\
		python db_ingest.py -s sex -c sex_F0$${field}E07.cat -m MapF0$${field}E07.mir;\
		python db_xmatch.py -s sex -f $$field;\
	done

imsad:
	#imsad
	for field in 0 1 2 3 4 5 6 7 8 9; do\
		#imsad in=/import/tycho1/hancock/DATA/SfSim/MapF0$${field}E07.mir clip=125e-6 device=/null out=IMSAD_F0$${field}E07.cat ;\
		python db_ingest.py -s imsad -c IMSAD_F0$${field}E07.cat -m MapF0$${field}E07.mir ;\
		python db_xmatch.py -s imsad -f $$field;\
	done


sel:
	#selavy
	#take results from the online interface for selavy
	for field in 0 1 2 3 4 5 6 7 8 9; do\
		python db_ingest.py -s selavy -c selavy/Field0$${field}.cat -m MapF0$${field}E07.mir ;\
		python db_xmatch.py -s selavy -f $$field ;\
	done


tesla:
	#tesla
	#don't re-run it takes about 1/2 hour to complete
	for field in 0 1 2 3 4 5 6 7 8 9; do\
		python db_ingest.py -s tesla -c tesla_F0$${field}E07.cat  -m MapF0$${field}E07.mir;\
		python db_xmatch.py -s tesla -f $$field ;\
	done


fndsou:
	#fndsou
	for field in 0 1 2 3 4 5 6 7 8 9; do\
		python db_ingest.py -s fndsou -c fndsou_F0$${field}E07.cat -m MapF0$${field}E07.mir;\
		python db_xmatch.py -s fndsou -f $$field;\
	done


sim: 	refresh
	python sim.py

strongest:
	for field in 0 1 2 3 4 5 6 7 8 9; do\
		python db_strongest.py -s imsad  -m MapF0$${field}E07.mir ;\
		python db_strongest.py -s sex	 -m MapF0$${field}E07.mir ;\
		python db_strongest.py -s sfind	 -m MapF0$${field}E07.mir ;\
		python db_strongest.py -s selavy -m MapF0$${field}E07.mir ;\
		python db_strongest.py -s tesla	 -m MapF0$${field}E07.mir ;\
		#python db_strongest.py -s fndsou -m MapF0$${field}E07.mir ;\
	done

plot:
	python db_plotter.py -s imsad  
	python db_plotter.py -s sex    
	python db_plotter.py -s selavy 
	python db_plotter.py -s sfind  
	python db_plotter.py -s tesla  
	python db_plotter.py -s fndsou 


ingest: refresh
	for field in 0 1 2 3 4 5 6 7 8 9; do\
		python db_ingest.py -s sfind -c sfind_F0$${field}E07.cat -m MapF0$${field}E07.mir ;\
		python db_xmatch.py -s sfind -f $$field ;\
		python db_ingest.py -s sex -c sex_F0$${field}E07.cat -m MapF0$${field}E07.mir;\
		python db_xmatch.py -s sex -f $$field;\
		python db_ingest.py -s imsad -c IMSAD_F0$${field}E07.cat -m MapF0$${field}E07.mir ;\
		python db_xmatch.py -s imsad -f $$field;\
		python db_ingest.py -s selavy -c selavy/selavy-F0$${field}E07.txt -m MapF0$${field}E07.mir ;\
		python db_xmatch.py -s selavy -f $$field ;\
		python db_ingest.py -s tesla -c tesla_F0$${field}E07.cat  -m MapF0$${field}E07.mir;\
		python db_xmatch.py -s tesla -f $$field ;\
		python db_ingest.py -s fndsou -c fndsou_F0$${field}E07.cat -m MapF0$${field}E07.mir;\
		python db_xmatch.py -s fndsou -f $$field;\
	done

refresh:
	python db_ingest.py -r
	python db_xmatch.py -r

allplots: ingest
	python db_completeness.py > completeness.dat
	cp completeness.dat ~/Dropbox/SF\ paper/.
	python db_sf_multi.py
	#done